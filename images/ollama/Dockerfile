FROM ollama/ollama:latest@sha256:ceaad0844eda02ddc59d9b40551de7264a564ba7a16a90e241d1c582f0df992d AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"