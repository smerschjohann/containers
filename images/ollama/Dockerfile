FROM ollama/ollama:latest@sha256:96b7667cb536ab69bfd5cc0c2bd1e29602218e076fe6d34f402b786f17b4fde0 AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"