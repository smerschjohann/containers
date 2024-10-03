FROM docker.io/library/traefik:v3.1.5@sha256:7b927f0ab22c85a636cde667aa6a3c90f1967bb5079899ce960ec51454fc96e9 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
