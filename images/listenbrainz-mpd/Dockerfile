ARG RUST_TAG=docker.io/rust:1-alpine@sha256:b1d5dd5a22a09404d3e798c0cf051b689077360374eb505fa5bb93c479693d87
ARG ALPINE_TAGORDIGEST=:latest@sha256:be2656061b536c1883c4034790e21d0a09c5aaaf51968b89368a3c0371ea2c9a

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
