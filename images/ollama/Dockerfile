FROM ollama/ollama:latest@sha256:5600a652d1081050f398152127c584222546354491f27fe47ccbc6351bc870bd AS app

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# load model and store in image
RUN ollama serve & \
    serve_pid=$!; sleep 15; \
    ollama pull aratan/DeepSeek-R1-32B-Uncensored:latest; sleep 5; \
    kill $serve_pid; sleep 10; \
    echo "download completed"