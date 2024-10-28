FROM docker.io/library/traefik:v3.2.0@sha256:66e37237b371f2b25ce5f247cc371976929dcb18c041e05685f1de1df6422b72 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
