# local_model_api/client/client.py
import requests

class LocalModelAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def generate_text(self, prompt, max_length=50, temperature=1.0):
        response = requests.post(f"{self.base_url}/generate_stream", json={
            "prompt": prompt,
            "max_length": max_length,
            "temperature": temperature
        }, stream=True)

        # 如果狀態碼不為 200，則拋出異常
        if response.status_code != 200:
            raise ValueError(f"Error: {response.status_code}, {response.text}")

        # 使用 yield 從流中逐步返回每個片段
        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            if chunk:
                yield chunk


# 用法示例
if __name__ == "__main__":
    client = LocalModelAPIClient()
    
    # 更新模型設置，例如切換到 BitsAndBytes 載入方式
    new_settings = {
        "loading_method": "bitsandbytes"
    }
    update_response = client.update_model_settings(new_settings)
    print(update_response)
    
    # 生成文本並設置不同的生成參數
    generated = client.generate_text(
        prompt="Once upon a time",
        max_length=100,
        temperature=0.7
    )
    print("\nGenerated Text:\n", generated)
