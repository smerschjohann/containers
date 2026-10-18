# Alexa Skill (MPD Player)

This is an Alexa Skill that integrates with an MPD (Music Player Daemon) server to play music on Amazon Echo / Alexa devices via continuous streaming (lossless FLAC or MP3).

## Features
- **Continuous lossless streaming**: Streams MPD's `httpd` output (e.g. 16-bit 44.1kHz FLAC).
- **100% Mobile & ympd Synchronization**: In continuous stream mode, MPD is the active audio engine. Any song change, pause, or queue reorder done via mobile apps (`ympd`, `MALP`, `MAFW`) takes effect immediately in the stream without lag.
- **Voice Control Intended Suite**:
  - `QueueSongIntent`: Add a song to the current MPD queue without interrupting playback.
  - `PlaySongIntent`: Immediately play a specific song.
  - `PlayAlbumIntent`: Play an entire album.
  - `PlayArtistIntent`: Play tracks from an artist.
  - `ClearQueueIntent`: Clear the MPD queue and stop playback.
  - `QueueStatusIntent`: Check current playing track and queue size.
  - Standard playback commands: Next, Previous, Pause, Resume, Stop, Start Over.
- **Auto-Queueing**: Automatically appends a random album (or random tracks) when the playlist reaches the end, so playback never stops unexpectedly.
- **Multi-threaded Webserver**: Runs with `waitress` (8 threads) to ensure responsive request handling even during audio streaming.
- **Token Authentication**: Secure the streaming endpoint (`/radio`, `/radio.flac`, `/radio.mp3`) with an optional `AUTH_TOKEN`.

## Configuration Values

| Variable | Description | Default |
|---|---|---|
| `MPD_HOST` | Hostname or IP of the MPD server | `localhost` |
| `MPD_PORT` | Port of the MPD server | `6600` |
| `RADIO_URL` | External HTTPS URL for the radio stream endpoint (e.g. `https://audio.example.com/radio`) | None |
| `MPD_RADIO_URL` | Internal URL pointing to MPD's HTTP stream output (e.g. `http://mpd:8000/`) | None |
| `AUTH_TOKEN` | Optional secret token to secure `/radio` endpoints. Alexa URLs will include `?token=...`. | None (public) |
| `AUTO_QUEUE_RANDOM` | Automatically append random music when playlist ends | `true` |
| `AUTO_QUEUE_MODE` | Type of random music to queue: `album` or `tracks` | `album` |
| `LISTEN_HOST` | Host to bind the internal web server to | `0.0.0.0` |
| `LISTEN_PORT` | Port the internal web server listens on | `8844` (or `$PORT`) |

## Setup & Deployment

1. Deploy MPD with an `httpd` output (e.g., `encoder "flac"` on port 8000).
2. Deploy `mpd-skill` with `RADIO_URL` and `MPD_RADIO_URL`.
3. In the [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask):
   - **Service Endpoint**: Point HTTPS endpoint to `https://<domain>/alexa`.
   - **Interfaces**: Enable the **Audio Player** interface.
   - **Interaction Model**: Import `alexa/interaction_model_de.json`.