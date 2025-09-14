FROM docker.io/library/traefik:v3.5.2@sha256:f0abbbd11ced29754d4d188c29e9320b613481ec162b6ea5d3a8b6bdd8e5fa54 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
