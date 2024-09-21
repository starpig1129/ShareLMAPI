# Dockerfile

FROM continuumio/miniconda3

# 設置工作目錄
WORKDIR /app

# 複製環境文件並安裝依賴
COPY environment.yml .
RUN conda env create -f environment.yml
RUN echo "source activate ShareLMAPI" > ~/.bashrc
ENV PATH /opt/conda/envs/ShareLMAPI/bin:$PATH

# 複製項目文件
COPY . .

# 安裝 pip 依賴（如果有）
RUN pip install --no-cache-dir bitsandbytes peft

# 暴露API端口
EXPOSE 8000

# 啟動Gunicorn伺服器
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "local_model_api.server:app", "--bind", "0.0.0.0:8000"]
