FROM ollama/ollama:latest@sha256:76d0c003b27db65170e88ab319ff19c9bcee41ecb8177c52ab06921dfa13abdf AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"