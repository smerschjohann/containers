FROM ollama/ollama:latest@sha256:74a0929e1e082a09e4fdeef8594b8f4537f661366a04080e600c90ea9f712721 AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"