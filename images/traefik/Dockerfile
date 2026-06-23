FROM docker.io/library/traefik:v3.7.5@sha256:e4d98158c01ad752fc1071d4e9573788747230d902cdde00a772516e692d07c9 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

