FROM docker.io/library/traefik:v3.6.7@sha256:a9890c898f379c1905ee5b28342f6b408dc863f08db2dab20e46c267d1ff463a AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

