FROM docker.io/library/traefik:v3.7.8@sha256:5cb000ad823bfcfff911e22a4c4fa09cee74c7a2d960c012a1a46a8d0a159fcf AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

