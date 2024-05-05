FROM docker.io/library/traefik:v3.0.0@sha256:7996bdae8aaa70eaacf2978b6c949de5b68c0a24ddc3e40c06344ecc88cfaea3 AS traefik

# allow rootless listening on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
