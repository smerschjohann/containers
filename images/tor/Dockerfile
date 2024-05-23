FROM alpine:3.20.0@sha256:77726ef6b57ddf65bb551896826ec38bc3e53f75cdde31354fbffb4f25238ebd as tor

RUN apk add tor

VOLUME /var/lib/tor
WORKDIR /var/lib/tor

USER tor