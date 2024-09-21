# local_model_api/client/client.py
import requests
import logging

class LocalModelAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)

    def generate_text(self, prompt=None, dialogue_history=None, system_prompt=None, max_length=50, temperature=1.0, streamer=True, generation_kwargs=None):
        """
        生成文本,支持單個 prompt 或對話歷史列表的傳輸,並且可選擇系統提示詞,支援流式輸出或非流式輸出。
        
        :param prompt: 單個提示詞（如果使用對話歷史,可以留空）
        :param dialogue_history: 包含多輪對話的 list[dict],每個 dict 包含 'role' 和 'content' 字段
        :param system_prompt: 一個可選的系統提示詞,用來作為對話的第一條信息
        :param max_length: 最大生成 token 數量
        :param temperature: 控制生成隨機性的參數
        :param streamer: 是否啟用流式輸出,默認為 True
        :param generation_kwargs: 傳遞到模型的其他生成參數
        :return: 流式生成的文本或完整生成的文本
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if dialogue_history:
            messages.extend([{"role": msg["role"], "content": msg["content"]} for msg in dialogue_history])
        elif prompt:
            messages.append({"role": "user", "content": prompt})
        else:
            raise ValueError("Either 'prompt' or 'dialogue_history' must be provided.")

        payload = {
            "dialogue_history": messages,
            "max_length": max_length,
            "temperature": temperature,
            "streamer": streamer,
            "generation_kwargs": generation_kwargs or {}
        }

        try:
            response = requests.post(f"{self.base_url}/generate_stream", json=payload, stream=streamer)
            response.raise_for_status()

            if streamer:
                return self._handle_streaming_response(response)
            else:
                return response.json()["generated_text"]
        except requests.RequestException as e:
            self.logger.error(f"Error in generate_text: {str(e)}")
            raise

    def _handle_streaming_response(self, response):
        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            if chunk:
                yield chunk