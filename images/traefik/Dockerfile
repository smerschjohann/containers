FROM docker.io/library/traefik:v3.3.2@sha256:e8b170343bb1ab703a956049291ef0d951867bef39839c9b0d70eebda6b2ed29 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
