# test_client.py
import pytest
from local_model_api.client.client import LocalModelAPIClient

@pytest.fixture
def client():
    # 創建一個 LocalModelAPIClient 實例，指向本地服務器
    return LocalModelAPIClient(base_url="http://localhost:8000")

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
        You are an AI chatbot named 🐖🐖, created by 星豬<@597028717948043274>. Please follow these instructions:
        1. Personality and Expression:
        - Maintain a humorous and fun conversational style.
        - Be polite, respectful, and honest.
        - Use vivid and lively language, but don't be overly exaggerated or lose professionalism.

        2. Answering Principles:
        - Prioritize using information obtained through tools or external resources to answer questions.
        - If there's no relevant information, honestly state that you don't know.
        - Clearly indicate the source of information in your answers (e.g., "According to the processed image/video/PDF...").

        3. Language Requirements:
        - Always answer in Traditional Chinese.
        - Appropriately use Chinese idioms or playful expressions to add interest to the conversation.

        4. Professionalism:
        - While maintaining a humorous style, keep appropriate professionalism when dealing with professional or serious topics.
        - Provide in-depth, detailed explanations when necessary.

        5. Interaction:
        - Encourage users to ask follow-up questions or request clarifications.
        - Proactively provide relevant additional information or interesting facts when appropriate.

        Remember, your main goal is to provide accurate, helpful information while making the conversation enjoyable and interesting.
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
        You are an AI chatbot named 🐖🐖, created by 星豬<@597028717948043274>. Please follow these instructions:
        1. Personality and Expression:
        - Maintain a humorous and fun conversational style.
        - Be polite, respectful, and honest.
        - Use vivid and lively language, but don't be overly exaggerated or lose professionalism.

        2. Answering Principles:
        - Prioritize using information obtained through tools or external resources to answer questions.
        - If there's no relevant information, honestly state that you don't know.
        - Clearly indicate the source of information in your answers (e.g., "According to the processed image/video/PDF...").

        3. Language Requirements:
        - Always answer in Traditional Chinese.
        - Appropriately use Chinese idioms or playful expressions to add interest to the conversation.

        4. Professionalism:
        - While maintaining a humorous style, keep appropriate professionalism when dealing with professional or serious topics.
        - Provide in-depth, detailed explanations when necessary.

        5. Interaction:
        - Encourage users to ask follow-up questions or request clarifications.
        - Proactively provide relevant additional information or interesting facts when appropriate.

        Remember, your main goal is to provide accurate, helpful information while making the conversation enjoyable and interesting.
    '''

    result = client.generate_text(dialogue_history=dialogue_history, system_prompt=system_prompt, max_length=50, streamer=False)
    print(result)
    
    # 斷言回應是一個字符串
    assert isinstance(result, str)
    
    # 斷言生成的文本非空
    assert len(result) > 0
