FROM docker.io/library/traefik:v3.3.6@sha256:83f3c843133530e4aa45e6ddc415488583a8a01c88adc5022d415c6e97ceeaae AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
