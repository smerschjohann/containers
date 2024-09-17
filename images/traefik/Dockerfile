FROM docker.io/library/traefik:v3.1.3@sha256:aa0b5b366e198602e5aa507ec94dfee05c12dd0044796763f4606f6b7936c9a9 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
