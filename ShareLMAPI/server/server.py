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
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import logging
import yaml
app = FastAPI()
logger = logging.getLogger(__name__)

def load_config(config_path="configs/model_config.yaml"):
    try:
        with open(config_path, "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        raise

config = load_config()
MODEL_SERVER_URL = config["server"]["model_server_url"]

def call_model_server(endpoint, payload, stream=False):
    try:
        response = requests.post(f"{MODEL_SERVER_URL}/{endpoint}", json=payload, stream=stream)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logger.error(f"Error calling model server: {str(e)}")
        raise HTTPException(status_code=500, detail="Error calling model server")

@app.post("/generate_stream")
async def generate_stream(request: Request):
    try:
        body = await request.json()
        payload = {
            "dialogue_history": body.get("dialogue_history", []),
            "max_length": body.get("max_length", 50),
            "temperature": body.get("temperature", 1.0),
            "generation_kwargs": body.get("generation_kwargs", {})
        }
        response = call_model_server("generate_stream", payload, stream=True)
        return StreamingResponse(response.iter_content(chunk_size=1024), media_type="text/plain")
    except Exception as e:
        logger.error(f"Error in generate_stream: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/generate")
async def generate(request: Request):
    try:
        body = await request.json()
        payload = {
            "dialogue_history": body.get("dialogue_history", []),
            "max_length": body.get("max_length", 50),
            "temperature": body.get("temperature", 1.0),
            "generation_kwargs": body.get("generation_kwargs", {})
        }
        response = call_model_server("generate", payload)
        return JSONResponse(content=response.json())
    except Exception as e:
        logger.error(f"Error in generate: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")