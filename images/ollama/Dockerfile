FROM ollama/ollama:latest@sha256:d42df3fe2285ca1f9f3b6f90dce394d73d7dd024a63104f9a5056ce1da4db1be AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"