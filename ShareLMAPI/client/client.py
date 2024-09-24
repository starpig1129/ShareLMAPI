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
import requests
import logging

class ShareLMClient:
    def __init__(self, base_url, api_key=None, admin_key=None):
        self.base_url = base_url
        self.api_key = api_key
        self.admin_key = admin_key
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

        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key

        try:
            if streamer:
                response = requests.post(f"{self.base_url}/generate_stream", json=payload, stream=True, headers=headers)
                response.raise_for_status()
                return self._handle_streaming_response(response)
            else:
                response = requests.post(f"{self.base_url}/generate", json=payload, headers=headers)
                response.raise_for_status()
                return response.json()["generated_text"]
        except requests.RequestException as e:
            self.logger.error(f"Error in generate_text: {str(e)}")
            raise

    def _handle_streaming_response(self, response):
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                yield chunk.replace('\n', '')

    def add_api_key(self, user_id: str, api_key: str):
        if not self.admin_key:
            raise ValueError("Admin key is required to add API keys")
        
        headers = {"X-Admin-Key": self.admin_key}
        try:
            response = requests.post(f"{self.base_url}/add_api_key", params={"user_id": user_id, "api_key": api_key}, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Error adding API key: {str(e)}")
            raise