FROM docker.io/library/traefik:v3.6.8@sha256:90099f8948c828ecf0ababd711a4359a2443eba12261c1df2f548a3b1d815938 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

