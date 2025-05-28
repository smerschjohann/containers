FROM docker.io/library/traefik:v3.4.1@sha256:cd40ab7bc1f047731d5b22595203812343efcb6538014c4e93221cfc3a77217a AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
