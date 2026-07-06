FROM docker.io/library/traefik:v3.7.6@sha256:21a3d83696379bac6434bb32e1dde0aff0e84ef2abd053ed3db87d3f45e749b2 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

