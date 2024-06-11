FROM docker.io/library/traefik:v3.0.2@sha256:3732c254a40f4b0743ef29458e214a1a952e0e68806a6f7b8d9cca00a4bae90e AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
