# Alexa Skill (MPD Player)

This is a simple Alexa Skill that can start and stop music on an MPD server.

It will stream the music that MPD offers at the stream.

## config values

- RADIO_URL: The external HTTPS url that can be used by alexa to access the stream. It will redirect to an internal URL. e.g `https://domain.tld/radio`
- MPD_RADIO_URL: the internal url that must be reachable from the Alexa (can be in the internal network) e.g. `http://192.168.0.10:8000/alexa`
- MPD_HOST: the mpd host e.g. `192.168.0.10`
- MPD_PORT: The mpd port e.g. `6600`

## How to configure?

Use as custom skill with custom endpoint. Point it at `https://domain.tld/alexa`