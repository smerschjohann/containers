FROM ollama/ollama:latest@sha256:b165fa2700dc374f8d4f9e8314d81c7be75487c76eee2b46ef4b511a496b736c AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"