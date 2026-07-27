FROM docker.io/library/traefik:v3.7.9@sha256:652929a140a32d7cafafb13c6cdfab5376cfeff800f51397b87b524501ed02a8 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

