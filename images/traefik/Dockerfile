FROM docker.io/library/traefik:v3.6.12@sha256:171c9c3565b29f6c133f1c1b43c5d4e5853415198e9e1078c001f8702ff66aec AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

