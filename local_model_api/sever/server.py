# local_model_api/sever/server.py
import requests
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

app = FastAPI()

# 調用模型伺服器的生成 API
def call_model_server_stream(prompt, max_length=50, temperature=1.0):
    response = requests.post("http://localhost:5000/generate_stream", json={
        "prompt": prompt,
        "max_length": max_length,
        "temperature": temperature
    }, stream=True)

    # 檢查伺服器回應狀態和內容
    if response.status_code != 200:
        raise ValueError(f"模型伺服器返回錯誤狀態碼: {response.status_code}, 回應內容: {response.text}")

    return response.iter_content(chunk_size=1024, decode_unicode=True)

# 支援流式輸出
@app.post("/generate_stream")
async def generate_stream(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "")
    max_length = body.get("max_length", 50)
    temperature = body.get("temperature", 1.0)

    # 流式生成回應
    return StreamingResponse(call_model_server_stream(prompt, max_length, temperature), media_type="text/plain")

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
