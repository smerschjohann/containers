FROM docker.io/library/traefik:v3.3.4@sha256:cc11989f418e2cfe5e60fc40c92c1813be847f58eda15eced7d5ac890255ad9e AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
