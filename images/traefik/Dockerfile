FROM docker.io/library/traefik:v3.3.3@sha256:19884a9d0b922b321c9cff54cbfe43f3169893041b8dd4ea6100677afaddce46 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
