FROM docker.io/library/traefik:v3.6.7@sha256:140d1fe3ba042682b8c93e8d0fdff043f9d6b27654bd9e84599d7ed220cf2ec7 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

