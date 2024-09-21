# local_model_api/sever/model_server.py
from fastapi import FastAPI
from transformers import TextIteratorStreamer
from threading import Thread
from local_model_api.sever.load_model import ModelLoader
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

app = FastAPI()

# 創建 ModelLoader 實例
model_loader = ModelLoader()

# 定義請求數據模式
class GenerateRequest(BaseModel):
    prompt: str
    max_length: int = 50
    temperature: float = 1.0

# 使用 TextIteratorStreamer 進行流式生成
@app.post("/generate_stream")
async def generate_stream(request: GenerateRequest):
    """使用 TextIteratorStreamer 生成文本流"""
    tokenizer = model_loader.tokenizer
    model = model_loader.model
    
    # 構建輸入數據
    inputs = tokenizer(request.prompt, return_tensors="pt").to(model.device)
    
    # 設置 streamer，跳過提示部分和特殊字符
    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

    # 設置生成參數
    generation_kwargs = {
        "inputs": inputs["input_ids"],
        "attention_mask": (inputs["input_ids"] != tokenizer.pad_token_id).long(),
        "max_new_tokens": request.max_length,
        "temperature": request.temperature,
        "streamer": streamer,
        "do_sample": True
    }
    
    # 在新線程中運行模型生成
    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()

    # 使用 StreamingResponse 將流式生成的內容返回
    return StreamingResponse(streamer, media_type="text/plain")
