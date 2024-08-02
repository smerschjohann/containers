FROM docker.io/library/traefik:v3.1.1@sha256:9f68c02f50786068f6687128ae8e8632b0bc24bc806705c9ff9fcbe9e38d19ae AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
