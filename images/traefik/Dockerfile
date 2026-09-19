FROM docker.io/library/traefik:v3.7.13@sha256:1c32e7c368204fd72812152ebdd2ac0425993df6fd982317deb02e48f2d5423c AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

