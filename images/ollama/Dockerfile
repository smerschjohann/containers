FROM ollama/ollama:latest@sha256:0ff452f6a4c3c5bb4ab063a1db190b261d5834741a519189ed5301d50e4434d1 AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"