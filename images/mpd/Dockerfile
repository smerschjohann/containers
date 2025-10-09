ARG TAGORDIGEST=:latest@sha256:4b7ce07002c69e8f3d704a9c5d6fd3053be500b7f1c69fc0d80990c2ad8dd412
FROM docker.io/alpine${TAGORDIGEST} AS mpd

RUN apk add --no-cache mpd mpc lame alsa-utils alsaconf

RUN mkdir -p /mpd/playlists /music && chown -R 100:18 /music /mpd
ADD mpd.conf /etc/mpd.conf

CMD ["mpd",  "--stderr", "--no-daemon"]

USER 100
