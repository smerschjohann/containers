FROM base as code

ARG CODE_SERVER_VERSION=4.17.0

USER root
RUN if [[ "$TARGETARCH" == "arm64" ]]; then \
        DOCKERARCH="aarch64"; GOARCH="arm64"; \
    else \
        DOCKERARCH="x86_64"; GOARCH="amd64"; \
    fi; \
    curl -LO https://github.com/coder/code-server/releases/download/v${CODE_SERVER_VERSION}/code-server-${CODE_SERVER_VERSION}-${GOARCH}.rpm && \
    dnf install -y code-server*.rpm && rm code-server*.rpm && \
    dnf clean all && \
  	rm -rf /var/cache/yum
RUN chmod a+x /usr/bin/*
USER coder
EXPOSE 8080/tcp
CMD [ "/usr/bin/code-server" ]