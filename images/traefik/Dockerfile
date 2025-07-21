FROM docker.io/library/traefik:v3.4.4@sha256:9b0e9d788816d722703eae57ebf8b4d52ad98e02b76f0362d5a040ef46902ef7 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
