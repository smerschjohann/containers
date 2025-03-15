FROM ollama/ollama:latest@sha256:5592e1b526d0081b9768c6122338d2cf79c4192f0aa34909dd2f97398295ca9d AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"