FROM docker.io/library/traefik:v3.6.13@sha256:34d5089d0b414945342848518b383f11f5b3a645504ed87b77ffeb9d683d0e48 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

