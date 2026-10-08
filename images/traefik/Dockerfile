FROM docker.io/library/traefik:v3.7.14@sha256:575fa15b135078fe5e50aa847987d96dbddd7b093c172429618404df73f3fa7c AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

