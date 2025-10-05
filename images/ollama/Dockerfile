FROM ollama/ollama:latest@sha256:c622a7adec67cf5bd7fe1802b7e26aa583a955a54e91d132889301f50c3e0bd0 AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"