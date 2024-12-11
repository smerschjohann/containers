FROM docker.io/library/traefik:v3.2.2@sha256:990bbdb0a9174b0d441317a63188e41c63795380db42b36ed920543e27ce04c9 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
