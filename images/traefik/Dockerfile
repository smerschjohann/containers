FROM docker.io/library/traefik:v3.6.5@sha256:67622638cd88dbfcfba40159bc652ecf0aea0e032f8a3c7e3134ae7c037b9910 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

