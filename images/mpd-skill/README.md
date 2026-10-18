# Alexa Skill (MPD Player)

This is an Alexa Skill that integrates with an MPD (Music Player Daemon) server to play music on Amazon Echo / Alexa devices via continuous streaming (lossless FLAC or MP3).

## Features
- **Continuous lossless streaming**: Streams MPD's `httpd` output (e.g. 16-bit 44.1kHz FLAC).
- **100% Mobile & ympd Synchronization**: In continuous stream mode, MPD is the active audio engine. Any song change, pause, or queue reorder done via mobile apps (`ympd`, `MALP`, `MAFW`) takes effect immediately in the stream without lag.
- **Denon / HEOS AVR Mode (Silence Proxy)**:
  - Play the true lossless FLAC stream directly on a Denon/Marantz AVR receiver (via HEOS CLI on port 1255).
  - Stream looped silence to the designated Alexa device so that Echo hardware buttons and voice commands (Next, Previous, Pause, Stop, Queue status) continue to control MPD smoothly.
  - Device-specific: selectively applies only to designated Alexa devices (e.g. Living Room Echo) while other Echo devices play normal audio.
  - Dynamically toggleable via REST API (`/api/heos/...`).
- **Voice Control Intended Suite**:
  - `QueueSongIntent`: Add a song to the current MPD queue without interrupting playback.
  - `PlaySongIntent`: Immediately play a specific song.
  - `PlayAlbumIntent`: Play an entire album.
  - `PlayArtistIntent`: Play tracks from an artist.
  - `ClearQueueIntent`: Clear the MPD queue and stop playback.
  - `QueueStatusIntent`: Check current playing track and queue size.
  - Standard playback commands: Next, Previous, Pause, Resume, Stop, Start Over.
- **Auto-Queueing & Recovery**: Automatically restores the last modified playlist or newest album when starting with an empty queue, and appends random music when the playlist ends.
- **Multi-threaded Webserver**: Runs with `waitress` (8 threads) to ensure responsive request handling even during audio streaming.
- **Token Authentication**: Secure the streaming endpoints (`/radio`, `/radio.flac`, `/radio.mp3`, `/silence.mp3`) and HEOS management API (`/api/heos/...`) with an optional `AUTH_TOKEN`.

## Configuration Values

| Variable | Description | Default |
|---|---|---|
| `MPD_HOST` | Hostname or IP of the MPD server | `localhost` |
| `MPD_PORT` | Port of the MPD server | `6600` |
| `RADIO_URL` | External HTTPS URL for the radio stream endpoint (e.g. `https://audio.example.com/radio.flac`) | None |
| `MPD_RADIO_URL` | Internal URL pointing to MPD's HTTP stream output (e.g. `http://mpd:8000/alexa.flac`) | None |
| `AUTH_TOKEN` | Optional secret token to secure `/radio`, `/silence`, and `/api/heos/*` endpoints. | None (public) |
| `AUTO_QUEUE_RANDOM` | Automatically append random music when playlist ends | `true` |
| `AUTO_QUEUE_MODE` | Type of random music to queue: `album` or `tracks` | `album` |
| `HEOS_HOST` | IP or hostname of Denon/Marantz AVR (e.g. `192.168.0.141`) | None |
| `HEOS_PORT` | HEOS CLI control port | `1255` |
| `HEOS_PID` | Specific HEOS player ID (auto-discovered if omitted) | None |
| `HEOS_STREAM_URL` | Stream URL sent to HEOS (defaults to `MPD_RADIO_URL` or `RADIO_URL`) | None |
| `HEOS_ENABLED` | Enable HEOS receiver mode on startup | `false` |
| `HEOS_DEVICE_IDS` | Comma-separated Alexa device IDs for HEOS mode (empty = all when enabled) | None |
| `LISTEN_HOST` | Host to bind the internal web server to | `0.0.0.0` |
| `LISTEN_PORT` | Port the internal web server listens on | `8844` (or `$PORT`) |

## Denon / HEOS REST API

Manage HEOS mode dynamically at runtime (requires `AUTH_TOKEN` via `?token=...`, `X-Auth-Token: ...`, or `Authorization: Bearer ...` if configured):

- `GET /api/heos/status`: View current HEOS mode status, receiver IP, and configured Alexa devices.
- `POST /api/heos/enable`: Enable HEOS mode. (Optional params: `?device_id=...&host=...`).
- `POST /api/heos/disable`: Disable HEOS mode.
- `POST /api/heos/toggle`: Toggle HEOS mode on/off.
- `POST /api/heos/device?device_id=<id>&action=add`: Add an Echo device ID to the HEOS target list.
- `POST /api/heos/device?device_id=<id>&action=remove`: Remove an Echo device ID.

## Finding your Alexa Device ID

When talking to the skill, the `device_id` is logged at `INFO` level:
```text
INFO:lambda_function:Alexa Request: type=LaunchRequest, device_id=amzn1.ask.device.ABC123XYZ...
```
You can register this device ID via the API or `HEOS_DEVICE_IDS`.

## Setup & Deployment

1. Deploy MPD with an `httpd` output (e.g., `encoder "flac"` on port 8000).
2. Deploy `mpd-skill` with `RADIO_URL`, `MPD_RADIO_URL`, and optionally `HEOS_HOST`.
3. In the [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask):
   - **Service Endpoint**: Point HTTPS endpoint to `https://<domain>/alexa`.
   - **Interfaces**: Enable the **Audio Player** interface.
   - **Interaction Model**: Import `alexa/interaction_model_de.json`.