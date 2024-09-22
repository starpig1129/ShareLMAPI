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
    # Create a ShareLMClient instance pointing to the local server
    return ShareLMClient(base_url="http://localhost:8000")

def test_generate_text_single_prompt_streaming(client):
    """Test text generation with a single prompt (streaming mode)"""
    chunks = []
    for chunk in client.generate_text(prompt="Please introduce yourself", max_length=50, streamer=True):
        print(chunk, end='', flush=True)  # Each streaming chunk will be printed
        chunks.append(chunk)
    print("\n" + "===" * 20)
    
    # Combine all streaming chunks into a complete text
    full_text = ''.join(chunks)
    
    # Assert that the response is a string
    assert isinstance(full_text, str)
    
    # Assert that the generated text is not empty
    assert len(full_text) > 0

def test_generate_text_single_prompt_non_streaming(client):
    """Test text generation with a single prompt (non-streaming mode)"""
    result = client.generate_text(prompt="Please introduce yourself", max_length=50, streamer=False)
    print(result)
    
    # Assert that the response is a string
    assert isinstance(result, str)
    
    # Assert that the generated text is not empty
    assert len(result) > 0

def test_generate_text_with_dialogue_history_and_system_prompt_streaming(client):
    """Test text generation with dialogue history and system prompt (streaming mode)"""
    dialogue_history = [
        {"role": "user", "content": "Can you introduce yourself?"}
    ]
    
    system_prompt = '''
        You are an AI chatbot named 🐖🐖
    '''

    chunks = []
    for chunk in client.generate_text(dialogue_history=dialogue_history, system_prompt=system_prompt, max_length=50, streamer=True):
        print(chunk, end='', flush=True)  # Each streaming chunk will be printed
        chunks.append(chunk)
    print("\n" + "===" * 20)
    
    # Combine all streaming chunks into a complete text
    full_text = ''.join(chunks)
    
    # Assert that the response is a string
    assert isinstance(full_text, str)
    
    # Assert that the generated text is not empty
    assert len(full_text) > 0

def test_generate_text_with_dialogue_history_and_system_prompt_non_streaming(client):
    """Test text generation with dialogue history and system prompt (non-streaming mode)"""
    dialogue_history = [
        {"role": "user", "content": "Can you introduce yourself?"}
    ]
    
    system_prompt = '''
        You are an AI chatbot named 🐖🐖
    '''

    result = client.generate_text(dialogue_history=dialogue_history, system_prompt=system_prompt, max_length=50, streamer=False)
    print(result)
    
    # Assert that the response is a string
    assert isinstance(result, str)
    
    # Assert that the generated text is not empty
    assert len(result) > 0