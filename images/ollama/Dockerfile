FROM ollama/ollama:latest@sha256:44893537fcc6f100b70ceb7f5c9fd8f787ba58f9f8ce73bf4a48a5b05fd8c422 AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"