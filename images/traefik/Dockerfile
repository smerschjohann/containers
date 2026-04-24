FROM docker.io/library/traefik:v3.6.14@sha256:1c1be62608b6a484c585a917203b01a8226cff13df6a2a78705eeb66b52e667e AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

