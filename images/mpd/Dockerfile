ARG TAGORDIGEST=:latest@sha256:c5b1261d6d3e43071626931fc004f70149baeba2c8ec672bd4f27761f8e1ad6b
FROM docker.io/alpine${TAGORDIGEST} AS mpd

RUN apk add --no-cache mpd mpc lame alsa-utils alsaconf

RUN mkdir -p /mpd/playlists /music && chown -R 100:18 /music /mpd
ADD mpd.conf /etc/mpd.conf

CMD ["mpd",  "--stderr", "--no-daemon"]

USER 100
