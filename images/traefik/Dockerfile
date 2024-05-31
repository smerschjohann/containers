FROM docker.io/library/traefik:v3.0.1@sha256:9ad110e745f68e15c09a4d6ccc0dc3cd674ab21466c0884b8e7823a445ac4d25 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
