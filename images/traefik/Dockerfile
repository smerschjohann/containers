FROM docker.io/library/traefik:v3.6.0@sha256:18112aed2bfe3dfb8534f1045622390c3316596cff0cefab64f44e43d23e1640 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

