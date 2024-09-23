FROM docker.io/library/traefik:v3.1.4@sha256:6215528042906b25f23fcf51cc5bdda29e078c6e84c237d4f59c00370cb68440 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
