FROM docker.io/library/traefik:v3.0.2@sha256:022f4662751b720c61ca2ba4322728117a8173280c4678261a48dba07a2b9bfd AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
