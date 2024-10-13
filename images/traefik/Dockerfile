FROM docker.io/library/traefik:v3.1.6@sha256:f703a2ac2ddf75f6e06c9cccac7f158765e2ab42d642b04e79e2e3d7355c2ddc AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
