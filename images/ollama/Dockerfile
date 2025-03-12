FROM ollama/ollama:latest@sha256:5ff3909f83e01e5a13a0caa8269b484059e841abd9cfe9a86b079b5eae315866 AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"