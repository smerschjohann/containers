FROM docker.io/library/traefik:v3.7.12@sha256:5447d0eaf375d832b8f224f88db0e80c0a2d44554fc973e3ba72c3a52946cfcc AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

