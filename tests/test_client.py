# MIT License

# Copyright (c) 2024 starpig1129

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# test_client.py
import pytest
from ShareLMAPI.client import ShareLMClient

@pytest.fixture
def client():
    # 創建一個 LocalModelAPIClient 實例，指向本地服務器
    return ShareLMClient(base_url="http://localhost:8000")

def test_generate_text_single_prompt_streaming(client):
    """測試使用單個 prompt 的文本生成功能（流式模式）"""
    chunks = []
    for chunk in client.generate_text(prompt="自我介紹一下", max_length=50, streamer=True):
        print(chunk, end='', flush=True)  # 每個流式片段都會被打印出來
        chunks.append(chunk)
    print("\n" + "===" * 20)
    
    # 組合所有流式片段為一個完整的文本
    full_text = ''.join(chunks)
    
    # 斷言回應是一個字符串
    assert isinstance(full_text, str)
    
    # 斷言生成的文本非空
    assert len(full_text) > 0

def test_generate_text_single_prompt_non_streaming(client):
    """測試使用單個 prompt 的文本生成功能（非流式模式）"""
    result = client.generate_text(prompt="自我介紹一下", max_length=50, streamer=False)
    print(result)
    
    # 斷言回應是一個字符串
    assert isinstance(result, str)
    
    # 斷言生成的文本非空
    assert len(result) > 0

def test_generate_text_with_dialogue_history_and_system_prompt_streaming(client):
    """測試使用對話歷史和系統提示詞的文本生成功能（流式模式）"""
    dialogue_history = [
        {"role": "user", "content": "請問你能自我介紹嗎？"}
    ]
    
    system_prompt = '''
        You are an AI chatbot named 🐖🐖
    '''

    chunks = []
    for chunk in client.generate_text(dialogue_history=dialogue_history, system_prompt=system_prompt, max_length=50, streamer=True):
        print(chunk, end='', flush=True)  # 每個流式片段都會被打印出來
        chunks.append(chunk)
    print("\n" + "===" * 20)
    
    # 組合所有流式片段為一個完整的文本
    full_text = ''.join(chunks)
    
    # 斷言回應是一個字符串
    assert isinstance(full_text, str)
    
    # 斷言生成的文本非空
    assert len(full_text) > 0

def test_generate_text_with_dialogue_history_and_system_prompt_non_streaming(client):
    """測試使用對話歷史和系統提示詞的文本生成功能（非流式模式）"""
    dialogue_history = [
        {"role": "user", "content": "請問你能自我介紹嗎？"}
    ]
    
    system_prompt = '''
        You are an AI chatbot named 🐖🐖
    '''

    result = client.generate_text(dialogue_history=dialogue_history, system_prompt=system_prompt, max_length=50, streamer=False)
    print(result)
    
    # 斷言回應是一個字符串
    assert isinstance(result, str)
    
    # 斷言生成的文本非空
    assert len(result) > 0
