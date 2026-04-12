FROM docker.io/library/traefik:v3.6.13@sha256:5ae9c349154d5298a5d61a7b25e5f3a9f53314f1515e87632120b95051c7917c AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

