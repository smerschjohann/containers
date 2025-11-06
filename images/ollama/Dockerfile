FROM ollama/ollama:latest@sha256:e8c3d1f6ad16323bc40dc63eff0701d4fc32113f75a86b54b3e836eef8290de6 AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"