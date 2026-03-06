FROM docker.io/library/traefik:v3.6.10@sha256:c549d482c55d7a797398562064f35428cc53e748d84d7190997930e7b31bcc32 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

