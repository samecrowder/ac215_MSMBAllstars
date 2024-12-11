FROM ollama/ollama:latest

# Install NVIDIA Container Toolkit dependencies
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

# Configure Ollama
ENV OLLAMA_KEEP_ALIVE=24h
ARG LLM_MODEL

# Create model directory
RUN mkdir -p /root/.ollama/models

# download the model
RUN ollama serve & server=$! ; sleep 5 ; ollama pull $LLM_MODEL ; kill $server

# Make sure the model files persist
VOLUME /root/.ollama/models

# Set CUDA environment variables
ENV CUDA_VISIBLE_DEVICES=0
