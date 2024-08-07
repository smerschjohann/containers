FROM docker.io/library/traefik:v3.1.2@sha256:ec1a82940b8e00eaeef33fb4113aa1d1573b2ebb6440e10c023743fe96f08475 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
