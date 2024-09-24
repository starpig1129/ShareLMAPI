import requests
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse
import logging
import yaml
from ShareLMAPI.server.auth import auth_middleware, admin_auth_middleware, add_api_key_to_db, verify_api_key, check_rate_limit

app = FastAPI()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def load_config(config_path="configs/model_config.yaml"):
    try:
        with open(config_path, "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        raise

config = load_config()
MODEL_SERVER_URL = config["model_server"]["model_server_url"]

def call_model_server(endpoint, payload, stream=False):
    try:
        response = requests.post(f"{MODEL_SERVER_URL}/{endpoint}", json=payload, stream=stream)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logger.error(f"Error calling model server: {str(e)}")
        raise HTTPException(status_code=500, detail="Error calling model server")

@app.post("/generate_stream")
async def generate_stream(request: Request, auth: str = Depends(auth_middleware)):
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
async def generate(request: Request, auth: str = Depends(auth_middleware)):
    try:
        api_key = request.state.api_key
        logger.debug(f"Received generate request with API key: {api_key}")
        
        # Explicitly check rate limit
        try:
            check_rate_limit(api_key)
        except HTTPException as e:
            logger.warning(f"Rate limit exceeded for API key: {api_key}")
            raise e

        body = await request.json()
        payload = {
            "dialogue_history": body.get("dialogue_history", []),
            "max_length": body.get("max_length", 50),
            "temperature": body.get("temperature", 1.0),
            "generation_kwargs": body.get("generation_kwargs", {})
        }
        response = call_model_server("generate", payload)
        return JSONResponse(content=response.json())
    except HTTPException as e:
        logger.error(f"HTTP exception in generate: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Error in generate: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/add_api_key")
async def add_api_key(user_id: str, api_key: str, admin_auth: str = Depends(admin_auth_middleware)):
    try:
        # Check if the API key already exists
        if verify_api_key(api_key):
            return {"message": "API key already exists"}
        
        # If it doesn't exist, add it
        add_api_key_to_db(user_id, api_key)
        return {"message": "API key added successfully"}
    except HTTPException as e:
        # Re-raise HTTP exceptions from add_api_key_to_db
        raise e
    except Exception as e:
        logger.error(f"Error adding API key: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")