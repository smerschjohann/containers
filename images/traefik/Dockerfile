FROM docker.io/library/traefik:v3.6.7@sha256:2c5e029ee3638d3788b4ca7c8ef454baa8f924b91b190b3fd2742bee721ebeea AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

