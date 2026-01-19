FROM docker.io/library/traefik:v3.6.7@sha256:ebe7d3fc715e28f033cea8265e9105b9d64705867f5b916e2d9ed0b62c530192 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

