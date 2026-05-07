FROM ollama/ollama:latest@sha256:6077dbbd6508dce8973f8b91c30d8026b1279ab0483e15f0dfad469dba676c2f AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"