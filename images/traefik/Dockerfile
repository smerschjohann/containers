FROM docker.io/library/traefik:v3.6.15@sha256:8cb20d16e01a53d8d7f7696ac2f1af7d200d5c9984d226ce2299731d9eab6d6c AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

