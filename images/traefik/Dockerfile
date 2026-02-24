FROM docker.io/library/traefik:v3.6.9@sha256:9004e1cd1e33c5eb0b6ec02bc6cfda61fe9caca36751114b1c9c6662f01b264a AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

