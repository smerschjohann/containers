FROM docker.io/library/traefik:v3.6.4@sha256:beebe9d00a6f7cd8cf35581eb9c065d30d1ac0b961a5561fb106c64d10d8d76d AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

