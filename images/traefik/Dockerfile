FROM docker.io/library/traefik:v3.7.0@sha256:eb328e2c806c53aafbbace6c451fa54d268961261a85452fcf0fb752a30c17be AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

