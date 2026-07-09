FROM docker.io/library/traefik:v3.7.7@sha256:1cb3845d7a05e1473c9086351426597e911db49db382b6e4769f9b0744962ac8 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

