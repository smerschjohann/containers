FROM docker.io/library/traefik:v3.3.3@sha256:f1fdee7fda041872cff24e36a08f45ca53f006ded88f743a8e30e3d87ca52b48 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
