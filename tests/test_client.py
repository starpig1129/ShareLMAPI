import pytest
import time
from ShareLMAPI.client import ShareLMClient
import requests
import logging
ADMIN_KEY = "your_secure_admin_key_here"  # This should match the admin_key in api_config.yaml
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
@pytest.fixture(scope="module")
def client():
    client = ShareLMClient(base_url="http://localhost:8000", admin_key=ADMIN_KEY)
    response = client.add_api_key(user_id="test_user", api_key="test_api_key")
    assert response in [{"message": "API key added successfully"}, {"message": "API key already exists"}]
    client.api_key = "test_api_key"
    return client

def test_add_api_key(client):
    response = client.add_api_key(user_id="another_user", api_key="another_api_key")
    assert response in [{"message": "API key added successfully"}, {"message": "API key already exists"}]

def test_add_api_key_without_admin_key():
    non_admin_client = ShareLMClient(base_url="http://localhost:8000")
    with pytest.raises(ValueError, match="Admin key is required to add API keys"):
        non_admin_client.add_api_key(user_id="user", api_key="key")

def test_generate_text_with_valid_api_key(client):
    response = client.generate_text(prompt="Hello, world!", max_length=20, streamer=False)
    assert isinstance(response, str)
    assert len(response) > 0

def test_generate_text_with_invalid_api_key():
    invalid_client = ShareLMClient(base_url="http://localhost:8000", api_key="invalid_api_key")
    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        invalid_client.generate_text(prompt="Hello, world!", max_length=20, streamer=False)
    assert exc_info.value.response.status_code == 403

def test_generate_text_without_api_key():
    no_key_client = ShareLMClient(base_url="http://localhost:8000")
    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        no_key_client.generate_text(prompt="Hello, world!", max_length=20, streamer=False)
    assert exc_info.value.response.status_code == 400

def test_rate_limiting(client):
    logger.info("Starting rate limiting test")
    # This test assumes the rate limit is set to 60 requests per minute with a burst limit of 100
    for i in range(100):
        logger.debug(f"Sending request {i+1}")
        response = client.generate_text(prompt="Test", max_length=5, streamer=False)
        assert isinstance(response, str)
    
    logger.info("Sent 100 requests, attempting to send the 101st request")
    # The 101st request should fail due to rate limiting
    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        client.generate_text(prompt="Test", max_length=5, streamer=False)
    assert exc_info.value.response.status_code == 429
    logger.info("Rate limit test passed successfully")

    # Wait for the rate limit to reset
    logger.info("Waiting for rate limit to reset")
    time.sleep(61)  # Wait for 61 seconds to ensure the rate limit window has passed

    # This request should succeed
    logger.info("Sending request after rate limit reset")
    response = client.generate_text(prompt="Test", max_length=5, streamer=False)
    assert isinstance(response, str)
    logger.info("Post-reset request successful")

def test_streaming_generation_with_valid_api_key(client):
    chunks = list(client.generate_text(prompt="Stream test", max_length=20, streamer=True))
    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)

def test_generate_text_with_dialogue_history(client):
    dialogue_history = [
        {"role": "user", "content": "What's the weather like?"},
        {"role": "assistant", "content": "I'm sorry, I don't have real-time weather information. Is there anything else I can help you with?"},
        {"role": "user", "content": "Tell me a joke instead."}
    ]
    response = client.generate_text(dialogue_history=dialogue_history, max_length=50, streamer=False)
    assert isinstance(response, str)
    assert len(response) > 0

if __name__ == "__main__":
    pytest.main([__file__])