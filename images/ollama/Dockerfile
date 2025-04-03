FROM ollama/ollama:latest@sha256:476b956cbe76f22494f08400757ba302fd8ab6573965c09f1e1a66b2a7b0eb77 AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"