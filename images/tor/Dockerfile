FROM alpine:3.20.0@sha256:8768f0ca8ce33ec230c116364fbaebc1e18aaabbbda1ced56658f5eb0012202b as tor

RUN apk add tor

VOLUME /var/lib/tor
WORKDIR /var/lib/tor

USER tor