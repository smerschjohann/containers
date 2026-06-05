FROM docker.io/library/traefik:v3.7.4@sha256:fcdef599e6259359833dd2e1d49f9e964f66825d69bd3dd468f51102ce013d03 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

