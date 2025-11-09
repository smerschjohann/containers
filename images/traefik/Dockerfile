FROM docker.io/library/traefik:v3.6.0@sha256:e4153c8abbeaf88bfae33796b1860c584fb937ce31c53d0137012e9bfc3af99b AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

