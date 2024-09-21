from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import yaml
import logging

logger = logging.getLogger(__name__)

class ModelLoader:
    def __init__(self, config_path="configs/model_config.yaml"):
        self.config = self.load_config(config_path)
        self.model = None
        self.tokenizer = None
        self.load_model_and_tokenizer()

    def load_config(self, config_path):
        try:
            with open(config_path, "r") as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            raise

    def load_model_and_tokenizer(self):
        try:
            model_name = self.config["model"]["name"]
            loading_method = self.config["model"]["loading_method"]

            self.tokenizer = AutoTokenizer.from_pretrained(model_name)

            if loading_method == "default":
                self.model = self._load_default_model(model_name)
            elif loading_method == "bitsandbytes":
                self.model = self._load_bitsandbytes_model(model_name)
            elif loading_method == "peft":
                self.model = self._load_peft_model(model_name)
            else:
                raise ValueError(f"Unsupported loading method: {loading_method}")

            self.model.eval()
        except Exception as e:
            logger.error(f"Error loading model and tokenizer: {str(e)}")
            raise

    def _load_default_model(self, model_name):
        return AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto" if self.config["model"]["default"]["device"] == "cuda" else None,
            torch_dtype="auto" if self.config["model"]["default"]["device"] == "cuda" else None
        )

    def _load_bitsandbytes_model(self, model_name):
        quant_config = BitsAndBytesConfig(
            quant_type=self.config["model"]["bitsandbytes"]["quantization_config"]["quant_type"]
        )
        return AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=quant_config,
            device_map="auto" if self.config["model"]["bitsandbytes"]["device"] == "cuda" else None,
            torch_dtype="auto" if self.config["model"]["bitsandbytes"]["device"] == "cuda" else None
        )

    def _load_peft_model(self, model_name):
        base_model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto" if self.config["model"]["peft"]["device"] == "cuda" else None,
            torch_dtype="auto" if self.config["model"]["peft"]["device"] == "cuda" else None
        )
        peft_type = self.config["model"]["peft"]["peft_type"]
        if peft_type == "lora":
            return PeftModel.from_pretrained(
                base_model,
                model_name,  
                **self.config["model"]["peft"]["peft_config"]
            )
        else:
            raise ValueError(f"Unsupported PEFT type: {peft_type}")

    def update_model_settings(self, new_settings: dict):
        try:
            self.config["model"].update(new_settings)
            self.load_model_and_tokenizer()
        except Exception as e:
            logger.error(f"Error updating model settings: {str(e)}")
            raise