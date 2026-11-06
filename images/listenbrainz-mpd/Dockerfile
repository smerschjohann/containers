ARG RUST_TAG=docker.io/rust:1-alpine@sha256:44819b27be4c97b0e4d7203bd2e02c4820f97700211b6a37fb4c246a2de59383
ARG ALPINE_TAGORDIGEST=:latest@sha256:3f4d6b32e26703c6082839234f43769d5046b3ac7c910033911d1e71d8cd630a

FROM ${RUST_TAG} AS build

RUN apk add --no-cache musl-dev pkgconfig openssl-dev openssl-libs-static sqlite-static git
RUN git clone --depth 1 --branch v2.6.0 https://codeberg.org/elomatreb/listenbrainz-mpd /src

WORKDIR /src
# patch: required listen time 1 minute instead of 4 minutes
# (DLNA streams have no known duration, short tracks would never scrobble)
RUN sed -i 's/from_secs(4 \* 60)/from_secs(60)/' src/main.rs
RUN cargo build --release && strip target/release/listenbrainz-mpd

FROM docker.io/alpine${ALPINE_TAGORDIGEST} AS app

RUN apk add --no-cache ca-certificates libssl3
COPY --from=build /src/target/release/listenbrainz-mpd /usr/local/bin/listenbrainz-mpd

USER 100
ENTRYPOINT ["listenbrainz-mpd"]
