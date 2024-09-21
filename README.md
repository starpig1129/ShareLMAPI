# ShareLMAPI

ShareLMAPI 是一個本地語言模型共享 API，通過 FastAPI 提供接口，讓不同程式可以共用同一個本地模型，減少資源消耗。支持流式生成和多種模型配置方式。

## 目錄

- [功能特點](#功能特點)
- [安裝](#安裝)
- [配置](#配置)
- [使用](#使用)
- [API 說明](#api-說明)
- [客戶端使用](#客戶端使用)
- [測試](#測試)
- [貢獻](#貢獻)
- [許可協議](#許可協議)

## 功能特點

- 支持多種模型加載方式：默認、BitsAndBytes 量化、PEFT
- 支持流式和非流式文本生成
- 支持對話歷史和系統提示詞
- 易於配置和擴展

## 安裝

### 1. 克隆項目

```bash
git clone https://github.com/yourusername/ShareLMAPI.git
cd ShareLMAPI
```

### 2. 安裝依賴

項目依賴可以通過 Conda 或 Pip 來安裝。

使用 Conda 安裝：

```bash
conda env create -f environment.yml
conda activate ShareLMAPI
```
### 3. 安裝本地開發環境

如果你計劃開發此套件，請使用以下命令安裝此包：

```bash
pip install -e .
```

## 配置

1. 導航到 `configs` 目錄並打開 `model_config.yaml`。
2. 根據您的需求修改配置。您可以指定：
   - 模型名稱
   - 加載方法（default、bitsandbytes 或 peft）
   - 設備（CPU 或 CUDA）
   - 其他模型特定設置

## 使用

### 啟動模型伺服器

首先，啟動模型伺服器來加載和管理語言模型：

```bash
uvicorn ShareLMAPI.server.model_server:app --host 0.0.0.0 --port 5000
```

### 啟動前端 API 伺服器

在模型伺服器運行後，啟動前端伺服器來處理客戶端的請求：

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker ShareLMAPI.server.server:app --bind 0.0.0.0:8000

```

## API 說明

### 1. `/generate_stream`

生成模型回應，支持流式和非流式輸出。

* **方法**：`POST`
* **URL**：`http://localhost:8000/generate_stream`
* **參數**：
   * `dialogue_history`：對話歷史（可選）
   * `prompt`：用戶輸入的提示詞（如果未提供對話歷史）
   * `max_length`：生成的最大 token 數量
   * `temperature`：生成隨機性的控制參數
   * `streamer`：是否使用流式輸出（布爾值）
   * `generation_kwargs`：其他生成參數（可選）

* **請求範例**：

```bash
curl -X POST "http://localhost:8000/generate_stream" \
-H "Content-Type: application/json" \
-d '{
  "prompt": "Once upon a time",
  "max_length": 50,
  "temperature": 1.0,
  "streamer": true
}'
```

* **回應**： 
  - 流式模式：文本將逐步返回到客戶端
  - 非流式模式：完整的生成文本將作為 JSON 響應返回

## 客戶端使用

以下是如何使用 `ShareLMClient` 調用 API 的示例：

```python
from local_model_api.client.client import ShareLMClient

# 創建 API 客戶端
client = ShareLMClient(base_url="http://localhost:8000")

# 流式生成
for chunk in client.generate_text("Once upon a time", max_length=50, streamer=True):
    print(chunk, end='', flush=True)

# 非流式生成
response = client.generate_text("What is the capital of France?", max_length=50, streamer=False)
print(response)

# 使用對話歷史
dialogue_history = [
    {"role": "user", "content": "Hi, who are you?"},
    {"role": "assistant", "content": "I'm an AI assistant. How can I help you today?"},
    {"role": "user", "content": "Can you explain quantum computing?"}
]
response = client.generate_text(dialogue_history=dialogue_history, max_length=200, streamer=False)
print(response)
```

## 測試

在項目根目錄中運行以下命令來執行測試：

```bash
pytest -s tests/test_client.py
```

這將運行測試並顯示輸出結果。

## 貢獻

歡迎任何形式的貢獻。請遵循以下步驟：

1. Fork 本倉庫
2. 創建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打開一個 Pull Request

## 許可協議

此項目基於 MIT 許可協議開放源代碼。查看 [LICENSE](LICENSE) 文件來了解更多細節。