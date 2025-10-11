FROM ollama/ollama:latest@sha256:e43c26d2d1ebc726bc932166d2979086310b2f9c5ccd64fb06b55d1ea2c4f2cc AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"