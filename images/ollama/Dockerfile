FROM ollama/ollama:latest@sha256:be17b353bf3cfab0b6980530284e64716a57589ed753a82d9a6a2a5fa9a61a31 AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"