# local_model_api/server/server.py
import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

MODEL_SERVER_URL = "http://localhost:5000"

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