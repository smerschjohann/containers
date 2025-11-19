FROM docker.io/library/traefik:v3.6.2@sha256:c025135278d10f0fb6e54cb2b2dbadb3c3f0381a2c508cd74c06a74cb5a0e828 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

