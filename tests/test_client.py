# test_client.py
import pytest
from local_model_api.client.client import LocalModelAPIClient

@pytest.fixture
def client():
    # 創建一個 LocalModelAPIClient 實例，指向本地服務器
    return LocalModelAPIClient(base_url="http://localhost:8000")

def test_generate_text(client):
    # 測試生成文本的功能，捕捉流式輸出
    chunks = []
    for chunk in client.generate_text("自我介紹一下", max_length=500):
        print(chunk, end='',flush=True)  # 每個流式片段都會被打印出來
        chunks.append(chunk)
    
    # 組合所有流式片段為一個完整的文本
    full_text = ''.join(chunks)
    
    # 斷言回應是一個字符串
    assert isinstance(full_text, str)
    
    # 斷言生成的文本非空
    assert len(full_text) > 0
