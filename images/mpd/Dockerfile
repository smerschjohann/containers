ARG TAGORDIGEST=:latest@sha256:28bd5fe8b56d1bd048e5babf5b10710ebe0bae67db86916198a6eec434943f8b
FROM docker.io/alpine${TAGORDIGEST} AS mpd

RUN apk add --no-cache mpd mpc lame alsa-utils alsaconf

RUN mkdir -p /mpd/playlists /music && chown -R 100:18 /music /mpd
ADD mpd.conf /etc/mpd.conf

CMD ["mpd",  "--stderr", "--no-daemon"]

USER 100
