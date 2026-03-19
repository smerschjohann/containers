FROM docker.io/library/traefik:v3.6.11@sha256:37f515ab3fe37979ca6abec9fbb2437acebee8086bb7914f1353faeec27fdb5e AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

