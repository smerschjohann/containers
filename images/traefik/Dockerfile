FROM docker.io/library/traefik:v3.2.3@sha256:efb87236c8c92599bcd3a67a7a8a55e0f255665f4719722bf398935aa9b92270 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
