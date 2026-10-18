# Alexa Skill (MPD Player)

This is an Alexa Skill that integrates with an MPD (Music Player Daemon) server to play music on Amazon Echo / Alexa devices.

It supports two modes of playback:
1. **Track-by-track mode (`STREAM_MODE=tracks`, default when `MUSIC_DIR` is set)**: Directly streams individual music files (MP3, FLAC, M4A, etc.) with HTTP Range request support. Alexa displays title, artist, album, and track progress, and advances seamlessly through the MPD playlist queue. MPD's active song pointer stays synchronized with Alexa, so web and mobile clients (such as ympd or MALP) show what's currently playing.
2. **Radio stream mode (`STREAM_MODE=radio`)**: Streams the continuous live HTTP/Icecast stream provided by MPD's `httpd` output.

## Configuration Values

| Variable | Description | Default |
|---|---|---|
| `STREAM_MODE` | Playback mode: `tracks` (individual files) or `radio` (continuous MPD stream) | `tracks` if `MUSIC_DIR` is set, else `radio` |
| `MUSIC_DIR` | Path to the local music directory mounted in the container (e.g. `/music`) | None |
| `AUTH_TOKEN` | Secret token to secure `/song` (and `/radio`) endpoints. Alexa URLs will include `?token=...`. | None (public) |
| `BASE_URL` | Public HTTPS URL Alexa uses to access audio streams (e.g. `https://jukebox.example.com`) | Derived from `RADIO_URL` |
| `MPD_HOST` | Hostname or IP of the MPD server | `localhost` |
| `MPD_PORT` | Port of the MPD server | `6600` |
| `RADIO_URL` | External HTTPS URL for the radio stream endpoint (legacy radio mode) | None |
| `MPD_RADIO_URL` | Internal URL pointing to MPD's HTTP stream output (legacy radio mode) | None |
| `LISTEN_HOST` | Host to bind the internal web server to | `0.0.0.0` |
| `LISTEN_PORT` | Port the internal web server listens on | `8844` (or `$PORT`) |

## How to Configure

1. Deploy the container and make the service accessible over HTTPS (e.g. via Traefik or Caddy).
2. Configure a custom Alexa skill in the [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask):
   - **Service Endpoint**: Point HTTPS endpoint to `https://<domain>/alexa`.
   - **Interfaces**: Enable the **Audio Player** interface.