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
from fastapi import FastAPI, HTTPException
from transformers import TextIteratorStreamer
from threading import Thread
from ShareLMAPI.server.load_model import ModelLoader
from pydantic import BaseModel
from typing import List, Dict, Optional
from fastapi.responses import StreamingResponse, JSONResponse
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

model_loader = ModelLoader()

class DialogueMessage(BaseModel):
    role: str
    content: str

class GenerateRequest(BaseModel):
    dialogue_history: List[DialogueMessage]
    max_length: int = 50
    temperature: float = 1.0
    streamer: Optional[bool] = True
    generation_kwargs: Optional[Dict] = {}

@app.post("/generate_stream")
async def generate_stream(request: GenerateRequest):
    try:
        tokenizer = model_loader.tokenizer
        model = model_loader.model
        
        messages = [{"role": msg.role, "content": msg.content} for msg in request.dialogue_history]
        
        inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(model.device)

        generation_kwargs = {
            "inputs": inputs,
            "attention_mask": (inputs != tokenizer.pad_token_id).long(),
            "max_new_tokens": request.max_length,
            "temperature": request.temperature,
            "do_sample": True,
            **request.generation_kwargs
        }

        streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
        generation_kwargs["streamer"] = streamer

        thread = Thread(target=model.generate, kwargs=generation_kwargs)
        thread.start()

        return StreamingResponse(streamer, media_type="text/plain")
    except Exception as e:
        logger.error(f"Error in generate_stream: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating text")
    
@app.post("/generate")
async def generate(request: GenerateRequest):
    try:
        tokenizer = model_loader.tokenizer
        model = model_loader.model
        
        messages = [{"role": msg.role, "content": msg.content} for msg in request.dialogue_history]
        
        inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(model.device)

        generation_kwargs = {
            "inputs": inputs,
            "attention_mask": (inputs != tokenizer.pad_token_id).long(),
            "max_new_tokens": request.max_length,
            "temperature": request.temperature,
            "do_sample": True,
            **request.generation_kwargs
        }

        outputs = model.generate(**generation_kwargs)
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return JSONResponse(content={"generated_text": generated_text})
    except Exception as e:
        logger.error(f"Error in generate: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating text")