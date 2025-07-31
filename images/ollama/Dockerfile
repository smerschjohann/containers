FROM ollama/ollama:latest@sha256:67642615c0fe816cdedefda19c3a82f85bc99bf54c82af2d0f63df2842d4fb48 AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"