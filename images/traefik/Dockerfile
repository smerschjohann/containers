FROM docker.io/library/traefik:v3.0.1@sha256:7ca3233c2d4d862db071aceba4355bb430065ec00d818b6b4724c09f2a6a2783 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
