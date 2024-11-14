FROM docker.io/library/traefik:v3.2.0@sha256:d12741b971f5c833919db2b680191dc23d5d96ef17e41a914e3c593a8c663ac4 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
