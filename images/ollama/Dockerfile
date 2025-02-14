FROM ollama/ollama:latest AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; \
    kill $serve_pid
