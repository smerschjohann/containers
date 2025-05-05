FROM docker.io/library/traefik:v3.4.0@sha256:4cf907247939b5d20bf4eff73abd21cb413c339600dde76dbc94a874b2578a27 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
