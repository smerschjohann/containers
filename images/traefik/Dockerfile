FROM docker.io/library/traefik:v3.2.1@sha256:1a3e33f976d10f45efd613aa64814867068bf51c782599a70ef370447686291b AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
