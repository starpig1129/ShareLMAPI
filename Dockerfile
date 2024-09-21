# 使用 conda-forge 提供的 Miniconda 基礎映像
FROM continuumio/miniconda3

# 設置工作目錄
WORKDIR /app

# 複製 environment.yml 到工作目錄
COPY environment.yml /app/environment.yml

# 使用 Conda 創建環境並激活它
RUN conda env create -f environment.yml

# 激活環境
SHELL ["conda", "run", "-n", "ShareLMAPI", "/bin/bash", "-c"]

# 複製當前目錄的所有內容到容器內部
COPY . /app

# 安裝 bitsandbytes 和其他使用 pip 安裝的依賴
RUN pip install --no-cache-dir bitsandbytes peft torch

# Expose 8000 端口以便訪問
EXPOSE 8000

# 使用 Gunicorn 和 Uvicorn 運行 FastAPI 應用
CMD ["conda", "run", "-n", "ShareLMAPI", "gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "ShareLMAPI.server.model_server:app", "--bind", "0.0.0.0:8000"]
