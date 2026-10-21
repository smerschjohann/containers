FROM docker.io/library/traefik:v3.7.16@sha256:6d3e069ee484ab1da5adfdda555a75eb9b1545ef09096a0cc7c3043101986a20 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

