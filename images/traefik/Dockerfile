FROM docker.io/library/traefik:v3.0.3@sha256:a00ced69e41bf2eb475fd0cc70c1be785e4a5f45d693f26360b688c48816717f AS traefik

# allows rootless traefik to listen on ports < 1024 if NET_BIND_SERVICE is set
RUN apk add --no-cache libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/traefik && \
    apk del libcap
