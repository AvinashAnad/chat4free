FROM python:3.10-slim

WORKDIR /app
COPY . .

# Install dependencies including libcurl
RUN apt-get update && apt-get install -y \
    git curl build-essential cmake python3-dev libcurl4-openssl-dev && \
    pip install --no-cache-dir -r requirements.txt

# Build llama.cpp
RUN git clone https://github.com/ggerganov/llama.cpp /app/llama.cpp && \
    cd /app/llama.cpp && mkdir build && cd build && \
    cmake .. && cmake --build . --config Release

# Download model
RUN mkdir -p /app/models
RUN curl -L -o /app/models/llama-model.gguf https://huggingface.co/TheBloke/Llama-3-OpenOrca-GGUF/resolve/main/llama-3-8B-openorca.Q4_K_M.gguf?download=true

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
