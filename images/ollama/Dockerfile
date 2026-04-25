FROM ollama/ollama:latest@sha256:2038a264392af4d21f7f14e1568e8dd9aa0f2bd0f31d7d9a59a8cca1e9829663 AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"