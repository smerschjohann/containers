FROM docker.io/library/traefik:v3.1.2@sha256:3f92eba47bd4bfda91d47b72d16fef2d7ae15db61a92b2057cf0cb389f8938f6 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
