FROM ollama/ollama:latest@sha256:82956f40bb1f307c77f7a8c3ed91c7a37e072ed757ff143e34210a7b991b9480 AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; \
    kill $serve_pid
