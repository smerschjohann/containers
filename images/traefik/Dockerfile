FROM docker.io/library/traefik:v3.1.0@sha256:24773b7a8cf711c695957a076d550b5988bad343bf6e274ade55921ad8601841 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
