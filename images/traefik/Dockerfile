FROM docker.io/library/traefik:v3.5.3@sha256:d6be8725d21b45bdd84b93ea01438256e0e3c94aa8fa51834fe87f37cd5d4af8 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
