import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import yaml

class ModelLoader:
    def __init__(self, config_path="configs/model_config.yaml"):
        self.config = self.load_config(config_path)
        self.model = None
        self.tokenizer = None
        self.load_model_and_tokenizer()

    def load_config(self, config_path):
        """加載配置文件"""
        with open(config_path, "r") as file:
            return yaml.safe_load(file)

    def load_model_and_tokenizer(self):
        """根據配置加載模型和 tokenizer"""
        model_name = self.config["model"]["name"]
        loading_method = self.config["model"]["loading_method"]

        # 加載分詞器
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        # 根據配置加載模型
        if loading_method == "default":
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto" if self.config["model"]["default"]["device"] == "cuda" else None,
                torch_dtype="auto" if self.config["model"]["default"]["device"] == "cuda" else None
            )
        elif loading_method == "bitsandbytes":
            quant_config = BitsAndBytesConfig(
                quant_type=self.config["model"]["bitsandbytes"]["quantization_config"]["quant_type"]
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=quant_config,
                device_map="auto" if self.config["model"]["bitsandbytes"]["device"] == "cuda" else None,
                torch_dtype="auto" if self.config["model"]["bitsandbytes"]["device"] == "cuda" else None
            )
        elif loading_method == "peft":
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto" if self.config["model"]["peft"]["device"] == "cuda" else None,
                torch_dtype="auto" if self.config["model"]["peft"]["device"] == "cuda" else None
            )
            peft_type = self.config["model"]["peft"]["peft_type"]
            if peft_type == "lora":
                self.model = PeftModel.from_pretrained(
                    self.model,
                    model_name,  # 這裡應該是 PEFT 模型的路徑或名稱
                    **self.config["model"]["peft"]["peft_config"]
                )
        else:
            raise ValueError(f"Unsupported loading method: {loading_method}")

        self.model.eval()

    def update_model_settings(self, new_settings: dict):
        """更新模型設定並重新加載模型"""
        self.config["model"].update(new_settings)
        self.load_model_and_tokenizer()

    def load_adaptive_model(self, adaptive_setting):
        """自適應模型加載"""
        model_name = self.config["adaptive_models"].get(adaptive_setting, self.config["model"]["name"])
        self.config["model"]["name"] = model_name
        self.load_model_and_tokenizer()

    def generate_text(self, prompt, max_length=50, temperature=1.0):
        """根據提示生成文本"""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            inputs["input_ids"],
            max_length=max_length,
            temperature=temperature,
            do_sample=True
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
