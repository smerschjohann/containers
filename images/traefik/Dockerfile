FROM docker.io/library/traefik:v3.7.1@sha256:09d3ef496d61fd830905fce5035c8a9505c2d3849632cffe13e5a43b34526f90 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

