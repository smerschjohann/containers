FROM docker.io/library/traefik:v3.3.2@sha256:b280164afb554d6b7d4a0b86cac31f46e99f8386b7b74bb15e89d173b44c7824 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
