FROM ollama/ollama:latest@sha256:889ae74bdb4aa541044574d3e5e5dedde3c682c8b7918b6792aa031e7dfc8f06 AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"