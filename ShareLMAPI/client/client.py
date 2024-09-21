import requests
import logging

class ShareLMClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)

    def generate_text(self, prompt=None, dialogue_history=None, system_prompt=None, max_length=50, temperature=1.0, streamer=False, generation_kwargs=None):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if dialogue_history:
            messages.extend(dialogue_history)
        elif prompt:
            messages.append({"role": "user", "content": prompt})
        else:
            raise ValueError("Either 'prompt' or 'dialogue_history' must be provided.")

        payload = {
            "dialogue_history": messages,
            "max_length": max_length,
            "temperature": temperature,
            "generation_kwargs": generation_kwargs or {}
        }

        try:
            if streamer:
                response = requests.post(f"{self.base_url}/generate_stream", json=payload, stream=True)
                response.raise_for_status()
                return self._handle_streaming_response(response)
            else:
                response = requests.post(f"{self.base_url}/generate", json=payload)
                response.raise_for_status()
                return response.json()["generated_text"]
        except requests.RequestException as e:
            self.logger.error(f"Error in generate_text: {str(e)}")
            raise

    def _handle_streaming_response(self, response):
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                yield chunk.replace('\n', '')