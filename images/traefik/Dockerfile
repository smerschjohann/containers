FROM docker.io/library/traefik:v3.6.11@sha256:acfc80650104f0194a15f73dc1648f517561bc1645391a15705332a064cfc33c AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap

