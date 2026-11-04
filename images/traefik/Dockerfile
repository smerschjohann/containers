FROM docker.io/library/traefik:v3.7.17@sha256:68ae5fe5b64ca166704b746a9e8afcd385e36b3f569a5691401bf652d57b3748 AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

