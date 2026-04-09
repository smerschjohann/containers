FROM docker.io/library/traefik:v3.6.13@sha256:abb4f51887319c9b9d9cfe1d3cdf9379a771138003bf683f10e97697e148f95f AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

