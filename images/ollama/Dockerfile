FROM ollama/ollama:latest@sha256:bf65a7c25eb4561131ccbecd81991a5fdb37d8970958a3877533358ff28e0620 AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"