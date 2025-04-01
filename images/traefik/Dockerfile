FROM docker.io/library/traefik:v3.3.5@sha256:104204dadedf5d1284f8ef8f97f705649ac81aa6f7a6c9abf13e2c59245b8abc AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
