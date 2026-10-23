FROM alpine:3.24.3@sha256:be2656061b536c1883c4034790e21d0a09c5aaaf51968b89368a3c0371ea2c9a as tor

RUN apk add tor

VOLUME /var/lib/tor
WORKDIR /var/lib/tor

USER tor