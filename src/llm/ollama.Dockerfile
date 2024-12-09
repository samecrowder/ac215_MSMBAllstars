FROM ollama/ollama:latest

# Install NVIDIA Container Toolkit dependencies
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

# space separated list of models to download
ARG MODELS="llama3.2:1b"
ENV OLLAMA_KEEP_ALIVE=24h

# Create model directory
RUN mkdir -p /root/.ollama/models

# download the selected models
RUN ollama serve & server=$! ; sleep 5 ; for m in $MODELS ; do ollama pull $m ; done ; kill $server

# Make sure the model files persist
VOLUME /root/.ollama/models

# Set CUDA environment variables
ENV CUDA_VISIBLE_DEVICES=0
