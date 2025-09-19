FROM ollama/ollama:latest@sha256:14def4e0b9ac8c91b3ec6f7fa7684c924ffe244541d5fd827d9b89035cc33310 AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"