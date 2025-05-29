FROM ollama/ollama:latest@sha256:e2c9ab127d555aa671d06d2a48ab58a2e544bbdaf6fa93313dbb4fb8bb73867c AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"