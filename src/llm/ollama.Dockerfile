FROM ollama/ollama
# space separated list of models to download
ARG MODELS="llama3.2:1b"
ENV OLLAMA_KEEP_ALIVE=24h
# downlaod the selected models
RUN ollama serve & server=$! ; sleep 5 ; for m in $MODELS ; do ollama pull $m ; done ; kill $server
