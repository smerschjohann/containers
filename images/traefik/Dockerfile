FROM docker.io/library/traefik:v3.1.0@sha256:c612189cbcee82f2301ac337d38e581f806719db6fd5049e3352dae148313b18 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
