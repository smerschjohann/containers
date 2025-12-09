FROM docker.io/library/traefik:v3.6.4@sha256:c5bd185c41ba3dbb42cf8a1b9fbdc368bdc96f90c8e598134879935f64e7a7f1 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

