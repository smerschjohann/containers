ARG TAGORDIGEST=:latest@sha256:77726ef6b57ddf65bb551896826ec38bc3e53f75cdde31354fbffb4f25238ebd
FROM docker.io/alpine${TAGORDIGEST} AS mpd

RUN apk add --no-cache mpd mpc lame alsa-utils alsaconf

RUN mkdir -p /mpd/playlists /music && chown -R 100:18 /music /mpd
ADD mpd.conf /etc/mpd.conf

CMD ["mpd",  "--stderr", "--no-daemon"]

USER 100
