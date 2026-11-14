ARG RUST_TAG=docker.io/rust:1-alpine@sha256:2cccd8b212b37dad15a555589c1b6787da4ab913fe24d8a9b2d99d3498869409
ARG ALPINE_TAGORDIGEST=:latest@sha256:f59abe656b692d901e184be3445e084786602108599d2a51d229c0f5a48c71bf

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
