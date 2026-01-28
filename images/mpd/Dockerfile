ARG TAGORDIGEST=:latest@sha256:25109184c71bdad752c8312a8623239686a9a2071e8825f20acb8f2198c3f659
FROM docker.io/alpine${TAGORDIGEST} AS mpd

RUN apk add --no-cache mpd mpc lame alsa-utils alsaconf

RUN mkdir -p /mpd/playlists /music && chown -R 100:18 /music /mpd
ADD mpd.conf /etc/mpd.conf

CMD ["mpd",  "--stderr", "--no-daemon"]

USER 100
