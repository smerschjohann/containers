FROM docker.io/library/traefik:v3.7.14@sha256:e849695bc5c317da0cec22bfee4794fd9e15871fe554f864d31b625983e883ff AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

