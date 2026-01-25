FROM ollama/ollama:latest@sha256:e0ae5354a9e4c85160df4698a45ae360cd0c12ef90e484b12fc870c28f491892 AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"