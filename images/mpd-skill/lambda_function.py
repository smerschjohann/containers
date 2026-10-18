# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import logging
import random
from urllib.parse import quote
from contextlib import contextmanager
from mpd import MPDClient

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_model.interfaces.audioplayer import (
    PlayDirective, PlayBehavior, AudioItem, Stream,
    StopDirective, ClearQueueDirective, ClearBehavior)
from ask_sdk_webservice_support.webservice_handler import WebserviceSkillHandler

from alexa import util
import heos

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ######################### CONFIGURATION #########################

client = MPDClient()

MPD_HOST = os.getenv("MPD_HOST", "localhost")
MPD_PORT = int(os.getenv("MPD_PORT", "6600"))

RADIO_URL = os.getenv("RADIO_URL")
MPD_RADIO_URL = os.getenv("MPD_RADIO_URL")

# Optional authentication token to secure the /radio and /silence endpoints
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

# Auto-queueing: automatically append random album or tracks when playlist reaches end
AUTO_QUEUE_RANDOM = os.getenv("AUTO_QUEUE_RANDOM", "true").lower() in ("true", "1", "yes")
AUTO_QUEUE_MODE = os.getenv("AUTO_QUEUE_MODE", "album").lower()  # "album" or "tracks"

STREAM_MODE = "radio"

# Denon / HEOS Integration
HEOS_HOST = os.getenv("HEOS_HOST")
HEOS_PORT = int(os.getenv("HEOS_PORT", "1255"))
HEOS_PID = int(os.getenv("HEOS_PID")) if os.getenv("HEOS_PID") else None
HEOS_STREAM_URL = os.getenv("HEOS_STREAM_URL")
HEOS_ENABLED = os.getenv("HEOS_ENABLED", "false").lower() in ("true", "1", "yes")
HEOS_DEVICE_IDS = [d.strip() for d in os.getenv("HEOS_DEVICE_IDS", "").split(",") if d.strip()]

SILENCE_FILE = os.path.join(os.path.dirname(__file__), "silence.mp3")

heos_config = {
    "enabled": HEOS_ENABLED,
    "host": HEOS_HOST,
    "port": HEOS_PORT,
    "pid": HEOS_PID,
    "stream_url": HEOS_STREAM_URL,
    "devices": set(HEOS_DEVICE_IDS)
}

logger.info("Configured MPD Skill (Radio/Stream Mode): mpd=%s:%s, radio_url=%s, auth=%s, auto_queue=%s (%s), heos_enabled=%s (host=%s)",
            MPD_HOST, MPD_PORT, RADIO_URL, bool(AUTH_TOKEN), AUTO_QUEUE_RANDOM, AUTO_QUEUE_MODE,
            heos_config["enabled"], heos_config["host"])


@contextmanager
def connection():
    try:
        client.connect(MPD_HOST, MPD_PORT)
        yield
    finally:
        try:
            client.close()
            client.disconnect()
        except Exception:
            pass


# ######################### HELPERS #########################

def get_radio_url():
    """Return radio URL with token query parameter if AUTH_TOKEN is set."""
    if not RADIO_URL:
        return None
    if AUTH_TOKEN and 'token=' not in RADIO_URL:
        sep = '&' if '?' in RADIO_URL else '?'
        return f"{RADIO_URL}{sep}token={quote(AUTH_TOKEN)}"
    return RADIO_URL


def get_device_id(handler_input):
    """Safely extract device ID from request context."""
    try:
        return handler_input.request_envelope.context.system.device.device_id
    except Exception:
        return None


def is_heos_mode_active(handler_input=None):
    """Check if HEOS AVR mode is enabled and applies to this Alexa device."""
    if not heos_config.get("enabled"):
        return False
    if not heos_config.get("host"):
        return False
    target_devices = heos_config.get("devices")
    if not target_devices:
        return True
    if handler_input is None:
        return True
    dev_id = get_device_id(handler_input)
    return bool(dev_id and dev_id in target_devices)


def get_silence_url():
    """Return silence audio URL with token query parameter if AUTH_TOKEN is set."""
    if RADIO_URL:
        base = RADIO_URL.split("/radio")[0]
        silence_url = f"{base}/silence.mp3"
    else:
        silence_url = "/silence.mp3"
    if AUTH_TOKEN and 'token=' not in silence_url:
        sep = '&' if '?' in silence_url else '?'
        silence_url = f"{silence_url}{sep}token={quote(AUTH_TOKEN)}"
    return silence_url


def trigger_heos_stream():
    """Direct Denon HEOS to play the MPD stream."""
    host = heos_config.get("host")
    if not host:
        return False
    stream_url = heos_config.get("stream_url") or MPD_RADIO_URL or RADIO_URL
    if not stream_url:
        logger.error("No stream URL available for HEOS")
        return False
    return heos.play_stream(host, stream_url, pid=heos_config.get("pid"), port=heos_config.get("port", 1255))


def trigger_heos_stop():
    """Direct Denon HEOS to stop playback."""
    host = heos_config.get("host")
    if host:
        return heos.stop(host, pid=heos_config.get("pid"), port=heos_config.get("port", 1255))
    return False


def get_playback_url_and_token(handler_input, trigger_stream=True):
    """Return appropriate audio stream URL and token for the current device and mode."""
    if is_heos_mode_active(handler_input):
        if trigger_stream:
            trigger_heos_stream()
        return get_silence_url(), "heos_silence"
    return get_radio_url(), "radio_stream"


def add_random_music_to_queue(count=1):
    """Pick a random album or random tracks from MPD library and append to queue."""
    with connection():
        try:
            if AUTO_QUEUE_MODE == "album":
                raw_albums = client.list('album')
                clean_albums = []
                for a in raw_albums:
                    val = a.get('album') if isinstance(a, dict) else str(a)
                    if val and val.strip():
                        clean_albums.append(val.strip())
                if clean_albums:
                    chosen = random.choice(clean_albums)
                    logger.info("Auto-queueing random album: %s", chosen)
                    client.findadd('album', chosen)
                    return True

            # Fallback or "tracks" mode: pick random files
            raw_files = client.list('file')
            clean_files = []
            for f in raw_files:
                val = f.get('file') if isinstance(f, dict) else str(f)
                if val and val.strip():
                    clean_files.append(val.strip())
            if clean_files:
                sample = random.sample(clean_files, min(count * 5, len(clean_files)))
                logger.info("Auto-queueing %d random tracks", len(sample))
                for f in sample:
                    client.add(f)
                return True
        except Exception as e:
            logger.error("Failed to auto-queue random music: %s", e)
    return False


def restore_last_music_or_album():
    """
    When the MPD queue is empty, restore playback by:
    1. Loading the most recently modified stored playlist in MPD.
    2. Or adding the most recently modified/added album directory from the music library.
    3. Falling back to a random album or tracks from the library.
    Returns (success: bool, description: str).
    """
    with connection():
        # 1. Try stored playlists (most recently modified)
        try:
            stored_playlists = client.listplaylists()
            if stored_playlists:
                sorted_playlists = sorted(
                    stored_playlists,
                    key=lambda p: p.get('last-modified', '') if isinstance(p, dict) else '',
                    reverse=True
                )
                if sorted_playlists and isinstance(sorted_playlists[0], dict):
                    chosen_pl = sorted_playlists[0].get('playlist')
                    if chosen_pl:
                        logger.info("Empty queue: loading last modified playlist: %s", chosen_pl)
                        client.load(chosen_pl)
                        return True, f"Wiedergabeliste {chosen_pl}"
        except Exception as e:
            logger.warning("Failed to check stored playlists: %s", e)

        # 2. Try most recently added/modified directory in music library
        try:
            entries = client.lsinfo()
            dirs = [e for e in entries if isinstance(e, dict) and 'directory' in e]
            if dirs:
                sorted_dirs = sorted(
                    dirs,
                    key=lambda d: d.get('last-modified', ''),
                    reverse=True
                )
                if sorted_dirs and isinstance(sorted_dirs[0], dict):
                    top_dir = sorted_dirs[0].get('directory')
                    if top_dir:
                        try:
                            sub_entries = client.lsinfo(top_dir)
                            sub_dirs = [s for s in sub_entries if isinstance(s, dict) and 'directory' in s]
                            if sub_dirs:
                                sorted_subs = sorted(
                                    sub_dirs,
                                    key=lambda s: s.get('last-modified', ''),
                                    reverse=True
                                )
                                if sorted_subs and isinstance(sorted_subs[0], dict):
                                    target_dir = sorted_subs[0].get('directory')
                                else:
                                    target_dir = top_dir
                            else:
                                target_dir = top_dir
                        except Exception:
                            target_dir = top_dir

                        logger.info("Empty queue: adding latest modified album directory: %s", target_dir)
                        client.add(target_dir)
                        album_name = os.path.basename(target_dir)
                        return True, f"Album {album_name}"
        except Exception as e:
            logger.warning("Failed to check newest directory: %s", e)

        # 3. Fallback: random album from library
        try:
            raw_albums = client.list('album')
            clean_albums = []
            for a in raw_albums:
                val = a.get('album') if isinstance(a, dict) else str(a)
                if val and val.strip():
                    clean_albums.append(val.strip())
            if clean_albums:
                chosen = random.choice(clean_albums)
                logger.info("Empty queue: fallback adding random album: %s", chosen)
                client.findadd('album', chosen)
                return True, f"Album {chosen}"
        except Exception as e:
            logger.error("Failed to add fallback random album: %s", e)

    return False, ""


def get_slot_value(handler_input, slot_name):
    """Safely extract slot value from intent request."""
    try:
        intent = handler_input.request_envelope.request.intent
        if intent and intent.slots and slot_name in intent.slots:
            slot = intent.slots[slot_name]
            if slot and slot.value:
                return slot.value
    except Exception:
        pass
    return None


def search_tracks(title=None, artist=None):
    """Search MPD library for tracks matching title and/or artist."""
    with connection():
        results = []
        if title and artist:
            try:
                results = client.search('artist', artist, 'title', title)
            except Exception:
                pass
            if not results:
                try:
                    results = client.search('any', f"{artist} {title}")
                except Exception:
                    pass
        elif title:
            try:
                results = client.search('title', title)
            except Exception:
                pass
            if not results:
                try:
                    results = client.search('any', title)
                except Exception:
                    pass
        elif artist:
            try:
                results = client.search('artist', artist)
            except Exception:
                pass
            if not results:
                try:
                    results = client.search('any', artist)
                except Exception:
                    pass
        return results or []


def search_album_tracks(album, artist=None):
    """Search MPD library for all tracks of an album."""
    with connection():
        results = []
        if artist:
            try:
                results = client.search('artist', artist, 'album', album)
            except Exception:
                pass
        if not results:
            try:
                results = client.search('album', album)
            except Exception:
                pass
        return results or []


# ######################### ALEXA SKILL BUILDER #########################

sb = SkillBuilder()


class CheckAudioInterfaceHandler(AbstractRequestHandler):
    """Check if device supports AudioPlayer interface."""
    def can_handle(self, handler_input):
        return (is_request_type("LaunchRequest")(handler_input) and
                handler_input.request_envelope.context.system.device.supported_interfaces.audio_player is None)

    def handle(self, handler_input):
        return handler_input.response_builder.speak(
            "Entschuldigung, dieses Gerät unterstützt keine Audiowiedergabe."
        ).set_should_end_session(True).response


class SkillEventHandler(AbstractRequestHandler):
    """Close session for skill events or when session ends."""
    def can_handle(self, handler_input):
        return (handler_input.request_envelope.request.object_type.startswith("AlexaSkillEvent") or
                is_request_type("SessionEndedRequest")(handler_input))

    def handle(self, handler_input):
        logger.info("In SkillEventHandler")
        return handler_input.response_builder.response


class LaunchRequestOrPlayAudioHandler(AbstractRequestHandler):
    """Launch playback for skill launch or PlayAudio intent."""
    def can_handle(self, handler_input):
        return (is_request_type("LaunchRequest")(handler_input) or
                is_intent_name("PlayAudio")(handler_input))

    def handle(self, handler_input):
        logger.info("In LaunchRequestOrPlayAudioHandler")
        url = get_radio_url()
        if not url:
            handler_input.response_builder.speak("RADIO_URL ist nicht konfiguriert.").set_should_end_session(True)
            return handler_input.response_builder.response

        speech = "ok"
        with connection():
            playlist = client.playlistinfo()
            restored_what = None
            if not playlist:
                success, what = restore_last_music_or_album()
                if success:
                    restored_what = what

            try:
                client.play()
            except Exception:
                pass

            song = client.currentsong()
            if song and song.get('title'):
                title = song.get('title')
                artist = song.get('artist', '')
                by = f" von {artist}" if artist else ""
                if restored_what:
                    speech = f"Spiele {restored_what}. {title}{by}"
                else:
                    speech = f"Spiele das Lied {title}{by}"
            elif restored_what:
                speech = f"Spiele {restored_what}"

        stream_url, stream_token = get_playback_url_and_token(handler_input, trigger_stream=True)
        return util.play(url=stream_url,
                         offset=0,
                         text=speech,
                         card_data=None,
                         response_builder=handler_input.response_builder,
                         token=stream_token)


class QueueSongHandler(AbstractRequestHandler):
    """Handler for adding a song to the MPD queue without interrupting playback."""
    def can_handle(self, handler_input):
        return is_intent_name("QueueSongIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In QueueSongHandler")
        song_title = get_slot_value(handler_input, "Song")
        artist = get_slot_value(handler_input, "Artist")

        if not song_title:
            handler_input.response_builder.speak("Welches Lied möchtest du zur Wiedergabeliste hinzufügen?").set_should_end_session(False)
            return handler_input.response_builder.response

        tracks = search_tracks(title=song_title, artist=artist)
        if not tracks:
            msg = f"Ich konnte das Lied {song_title} nicht in der MPD-Bibliothek finden."
            if artist:
                msg = f"Ich konnte das Lied {song_title} von {artist} nicht finden."
            handler_input.response_builder.speak(msg).set_should_end_session(True)
            return handler_input.response_builder.response

        match = tracks[0]
        file_path = match['file']
        with connection():
            client.add(file_path)

        title = match.get('title') or song_title
        art = match.get('artist', '')
        speech_text = f"Ich habe {title}" + (f" von {art}" if art else "") + " zur Wiedergabeliste hinzugefügt."
        handler_input.response_builder.speak(speech_text).set_should_end_session(True)
        return handler_input.response_builder.response


class PlaySongHandler(AbstractRequestHandler):
    """Handler for immediately playing a specific song in MPD."""
    def can_handle(self, handler_input):
        return is_intent_name("PlaySongIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In PlaySongHandler")
        song_title = get_slot_value(handler_input, "Song")
        artist = get_slot_value(handler_input, "Artist")

        if not song_title:
            handler_input.response_builder.speak("Welches Lied möchtest du hören?").set_should_end_session(False)
            return handler_input.response_builder.response

        tracks = search_tracks(title=song_title, artist=artist)
        if not tracks:
            msg = f"Ich konnte das Lied {song_title} nicht finden."
            if artist:
                msg = f"Ich konnte das Lied {song_title} von {artist} nicht finden."
            handler_input.response_builder.speak(msg).set_should_end_session(True)
            return handler_input.response_builder.response

        match = tracks[0]
        file_path = match['file']
        with connection():
            song_id = client.addid(file_path)
            client.playid(song_id)

        title = match.get('title') or song_title
        art = match.get('artist', '')
        speech_text = f"Spiele {title}" + (f" von {art}" if art else "")
        stream_url, stream_token = get_playback_url_and_token(handler_input, trigger_stream=True)
        return util.play(url=stream_url,
                         offset=0,
                         text=speech_text,
                         card_data=None,
                         response_builder=handler_input.response_builder,
                         token=stream_token)


class PlayAlbumHandler(AbstractRequestHandler):
    """Handler for immediately playing a specific album in MPD."""
    def can_handle(self, handler_input):
        return is_intent_name("PlayAlbumIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In PlayAlbumHandler")
        album = get_slot_value(handler_input, "Album")
        artist = get_slot_value(handler_input, "Artist")

        if not album:
            handler_input.response_builder.speak("Welches Album möchtest du hören?").set_should_end_session(False)
            return handler_input.response_builder.response

        tracks = search_album_tracks(album=album, artist=artist)
        if not tracks:
            msg = f"Ich konnte das Album {album} nicht finden."
            handler_input.response_builder.speak(msg).set_should_end_session(True)
            return handler_input.response_builder.response

        with connection():
            client.clear()
            for t in tracks:
                client.add(t['file'])
            client.play()

        speech_text = f"Spiele Album {album}" + (f" von {artist}" if artist else "")
        stream_url, stream_token = get_playback_url_and_token(handler_input, trigger_stream=True)
        return util.play(url=stream_url,
                         offset=0,
                         text=speech_text,
                         card_data=None,
                         response_builder=handler_input.response_builder,
                         token=stream_token)


class PlayArtistHandler(AbstractRequestHandler):
    """Handler for playing songs by an artist in MPD."""
    def can_handle(self, handler_input):
        return is_intent_name("PlayArtistIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In PlayArtistHandler")
        artist = get_slot_value(handler_input, "Artist")

        if not artist:
            handler_input.response_builder.speak("Von welchem Künstler möchtest du Musik hören?").set_should_end_session(False)
            return handler_input.response_builder.response

        tracks = search_tracks(artist=artist)
        if not tracks:
            handler_input.response_builder.speak(f"Ich konnte keine Musik von {artist} finden.").set_should_end_session(True)
            return handler_input.response_builder.response

        with connection():
            client.clear()
            for t in tracks[:50]:
                client.add(t['file'])
            client.play()

        speech_text = f"Spiele Musik von {artist}"
        stream_url, stream_token = get_playback_url_and_token(handler_input, trigger_stream=True)
        return util.play(url=stream_url,
                         offset=0,
                         text=speech_text,
                         card_data=None,
                         response_builder=handler_input.response_builder,
                         token=stream_token)


class ClearQueueHandler(AbstractRequestHandler):
    """Handler for clearing the MPD queue and stopping playback."""
    def can_handle(self, handler_input):
        return is_intent_name("ClearQueueIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In ClearQueueHandler")
        if is_heos_mode_active(handler_input):
            trigger_heos_stop()
        with connection():
            client.clear()
            client.stop()
        return util.stop("Die Wiedergabeliste wurde geleert.", handler_input.response_builder)


class QueueStatusHandler(AbstractRequestHandler):
    """Handler for speaking the current song and queue status."""
    def can_handle(self, handler_input):
        return is_intent_name("QueueStatusIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In QueueStatusHandler")
        with connection():
            song = client.currentsong()
            playlist = client.playlistinfo()

        count = len(playlist)
        if not count:
            with connection():
                success, what = restore_last_music_or_album()
                if success:
                    try:
                        client.play()
                    except Exception:
                        pass
                    song = client.currentsong()
                    title = song.get('title') if song else ""
                    artist = song.get('artist', '') if song else ""
                    by = f" von {artist}" if artist else ""
                    if title:
                        msg = f"Die Wiedergabeliste war leer. Spiele {what}: {title}{by}."
                    else:
                        msg = f"Die Wiedergabeliste war leer. Spiele {what}."
                    stream_url, stream_token = get_playback_url_and_token(handler_input, trigger_stream=True)
                    return util.play(url=stream_url,
                                     offset=0,
                                     text=msg,
                                     card_data=None,
                                     response_builder=handler_input.response_builder,
                                     token=stream_token)
                else:
                    msg = "Die Wiedergabeliste ist leer und es konnte keine Musik in der Bibliothek gefunden werden."
        elif song and song.get('title'):
            title = song.get('title')
            artist = song.get('artist', '')
            by = f" von {artist}" if artist else ""
            msg = f"Es sind {count} Lieder in der Wiedergabeliste. Gerade läuft {title}{by}."
        else:
            msg = f"Es sind {count} Lieder in der Wiedergabeliste."

        handler_input.response_builder.speak(msg).set_should_end_session(True)
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for help intent."""
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In HelpIntentHandler")
        speech = ("Du kannst sagen: spiele Musik, nächstes Lied, vorheriges Lied, "
                  "füge ein Lied hinzu, oder frage was gerade läuft.")
        handler_input.response_builder.speak(speech).set_should_end_session(False)
        return handler_input.response_builder.response


class UnhandledIntentHandler(AbstractRequestHandler):
    """Handler for fallback intent."""
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In UnhandledIntentHandler")
        handler_input.response_builder.speak("Entschuldigung, das habe ich nicht verstanden.").set_should_end_session(True)
        return handler_input.response_builder.response


class NextOrPreviousIntentHandler(AbstractRequestHandler):
    """Handler for next or previous intents."""
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.NextIntent")(handler_input) or
                is_intent_name("AMAZON.PreviousIntent")(handler_input))

    def handle(self, handler_input):
        logger.info("In NextOrPreviousIntentHandler")
        is_next = is_intent_name("AMAZON.NextIntent")(handler_input)
        with connection():
            try:
                if is_next:
                    status = client.status()
                    song_pos = int(status.get('song', 0))
                    playlist_len = int(status.get('playlistlength', 0))
                    if song_pos + 1 >= playlist_len and AUTO_QUEUE_RANDOM:
                        add_random_music_to_queue()
                    client.next()
                else:
                    client.previous()
            except Exception as e:
                logger.error("error executing next/prev: %s", e)
                try:
                    client.play()
                except Exception:
                    pass

        stream_url, stream_token = get_playback_url_and_token(handler_input, trigger_stream=False)
        return util.play(url=stream_url,
                         offset=0,
                         text=None,
                         card_data=None,
                         response_builder=handler_input.response_builder,
                         token=stream_token)


class NextOrPreviousCommandHandler(AbstractRequestHandler):
    """Handler for Next or Previous command from hardware buttons."""
    def can_handle(self, handler_input):
        return (is_request_type("PlaybackController.NextCommandIssued")(handler_input) or
                is_request_type("PlaybackController.PreviousCommandIssued")(handler_input))

    def handle(self, handler_input):
        logger.info("In NextOrPreviousCommandHandler")
        is_next = is_request_type("PlaybackController.NextCommandIssued")(handler_input)
        with connection():
            try:
                if is_next:
                    status = client.status()
                    song_pos = int(status.get('song', 0))
                    playlist_len = int(status.get('playlistlength', 0))
                    if song_pos + 1 >= playlist_len and AUTO_QUEUE_RANDOM:
                        add_random_music_to_queue()
                    client.next()
                else:
                    client.previous()
            except Exception as e:
                logger.error("error executing next/prev command: %s", e)

        stream_url, stream_token = get_playback_url_and_token(handler_input, trigger_stream=False)
        return util.play(url=stream_url,
                         offset=0,
                         text=None,
                         card_data=None,
                         response_builder=handler_input.response_builder,
                         token=stream_token)


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Handler for cancel, stop or pause intents."""
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input) or
                is_intent_name("AMAZON.PauseIntent")(handler_input) or
                is_intent_name("AMAZON.NavigateHomeIntent")(handler_input))

    def handle(self, handler_input):
        logger.info("In CancelOrStopIntentHandler")
        if is_heos_mode_active(handler_input):
            trigger_heos_stop()
        with connection():
            try:
                client.stop()
            except Exception:
                pass
        return util.stop(text=None, response_builder=handler_input.response_builder)


class PauseCommandHandler(AbstractRequestHandler):
    """Handler for Pause command from hardware buttons."""
    def can_handle(self, handler_input):
        return is_request_type("PlaybackController.PauseCommandIssued")(handler_input)

    def handle(self, handler_input):
        logger.info("In PauseCommandHandler")
        if is_heos_mode_active(handler_input):
            trigger_heos_stop()
        with connection():
            try:
                client.pause(1)
            except Exception:
                pass
        return util.stop(text=None, response_builder=handler_input.response_builder)


class ResumeIntentHandler(AbstractRequestHandler):
    """Handler for resume intent."""
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.ResumeIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In ResumeIntentHandler")
        speech = None
        with connection():
            playlist = client.playlistinfo()
            if not playlist:
                success, what = restore_last_music_or_album()
                if success:
                    speech = f"Spiele {what}"
            try:
                client.play()
            except Exception:
                pass
        stream_url, stream_token = get_playback_url_and_token(handler_input, trigger_stream=True)
        return util.play(url=stream_url,
                         offset=0,
                         text=speech,
                         card_data=None,
                         response_builder=handler_input.response_builder,
                         token=stream_token)


class StartOverIntentHandler(AbstractRequestHandler):
    """Handler for start over intent."""
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.StartOverIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In StartOverIntentHandler")
        with connection():
            try:
                client.seekcur(0)
            except Exception:
                pass
        stream_url, stream_token = get_playback_url_and_token(handler_input, trigger_stream=False)
        return util.play(url=stream_url,
                         offset=0,
                         text=None,
                         card_data=None,
                         response_builder=handler_input.response_builder,
                         token=stream_token)


class PlayCommandHandler(AbstractRequestHandler):
    """Handler for hardware Play command."""
    def can_handle(self, handler_input):
        return is_request_type("PlaybackController.PlayCommandIssued")(handler_input)

    def handle(self, handler_input):
        logger.info("In PlayCommandHandler")
        with connection():
            playlist = client.playlistinfo()
            if not playlist:
                restore_last_music_or_album()
            try:
                client.play()
            except Exception:
                pass
        stream_url, stream_token = get_playback_url_and_token(handler_input, trigger_stream=True)
        return util.play(url=stream_url,
                         offset=0,
                         text=None,
                         card_data=None,
                         response_builder=handler_input.response_builder,
                         token=stream_token)


class PlaybackStartedHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("AudioPlayer.PlaybackStarted")(handler_input)

    def handle(self, handler_input):
        logger.info("Playback started")
        return handler_input.response_builder.response


class PlaybackFinishedHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("AudioPlayer.PlaybackFinished")(handler_input)

    def handle(self, handler_input):
        logger.info("Playback finished")
        return handler_input.response_builder.response


class PlaybackStoppedHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("AudioPlayer.PlaybackStopped")(handler_input)

    def handle(self, handler_input):
        logger.info("Playback stopped")
        return handler_input.response_builder.response


class PlaybackNearlyFinishedHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("AudioPlayer.PlaybackNearlyFinished")(handler_input)

    def handle(self, handler_input):
        try:
            token = handler_input.request_envelope.request.token
        except Exception:
            token = None
        if token == "heos_silence":
            url = get_silence_url()
            return util.play_later(url=url, card_data=None, response_builder=handler_input.response_builder,
                                   token="heos_silence", expected_previous_token="heos_silence")
        return handler_input.response_builder.response


class PlaybackFailedHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("AudioPlayer.PlaybackFailed")(handler_input)

    def handle(self, handler_input):
        logger.warning("Playback failed: %s", handler_input.request_envelope.request)
        return handler_input.response_builder.response


class ExceptionEncounteredHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("System.ExceptionEncountered")(handler_input)

    def handle(self, handler_input):
        logger.error("Exception encountered: %s", handler_input.request_envelope.request)
        return handler_input.response_builder.response


# ######################### INTERCEPTORS #########################

class RequestLogger(AbstractRequestInterceptor):
    def process(self, handler_input):
        req = handler_input.request_envelope.request
        dev_id = get_device_id(handler_input)
        logger.info("Alexa Request: type=%s, device_id=%s", getattr(req, "object_type", req), dev_id)


class ResponseLogger(AbstractResponseInterceptor):
    def process(self, handler_input, response):
        logger.debug("Alexa Response: %s", response)


# ######################### REGISTER HANDLERS #########################

sb.add_request_handler(CheckAudioInterfaceHandler())
sb.add_request_handler(SkillEventHandler())
sb.add_request_handler(LaunchRequestOrPlayAudioHandler())
sb.add_request_handler(QueueSongHandler())
sb.add_request_handler(PlaySongHandler())
sb.add_request_handler(PlayArtistHandler())
sb.add_request_handler(PlayAlbumHandler())
sb.add_request_handler(ClearQueueHandler())
sb.add_request_handler(QueueStatusHandler())
sb.add_request_handler(PlayCommandHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(ExceptionEncounteredHandler())
sb.add_request_handler(UnhandledIntentHandler())
sb.add_request_handler(NextOrPreviousIntentHandler())
sb.add_request_handler(NextOrPreviousCommandHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(PauseCommandHandler())
sb.add_request_handler(ResumeIntentHandler())
sb.add_request_handler(StartOverIntentHandler())
sb.add_request_handler(PlaybackStartedHandler())
sb.add_request_handler(PlaybackFinishedHandler())
sb.add_request_handler(PlaybackStoppedHandler())
sb.add_request_handler(PlaybackNearlyFinishedHandler())
sb.add_request_handler(PlaybackFailedHandler())

sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

webservice_handler = WebserviceSkillHandler(skill=sb.create())


# ######################### WEBSERVER #########################

from bottle import route, run, request, response, redirect


def pretty_print_json(json_data):
    try:
        logger.debug(json.dumps(json.loads(json_data), indent=2))
    except Exception:
        logger.debug(json_data)


def check_auth():
    """Verify auth token from query parameter, HTTP Basic Auth, Bearer, or X-Auth-Token."""
    if not AUTH_TOKEN:
        return True
    # 1. Query parameter ?token=...
    token = request.query.get('token')
    if token and token == AUTH_TOKEN:
        return True
    # 2. X-Auth-Token header
    header_token = request.headers.get('X-Auth-Token')
    if header_token and header_token == AUTH_TOKEN:
        return True
    # 3. HTTP Basic Auth: Authorization: Basic <base64(user:password)>
    if request.auth:
        user, pwd = request.auth
        if pwd == AUTH_TOKEN or user == AUTH_TOKEN:
            return True
    # 4. Bearer token in Authorization header
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        if auth_header[7:].strip() == AUTH_TOKEN:
            return True
    return False


@route('/radio', method=["GET", "HEAD"])
@route('/radio.flac', method=["GET", "HEAD"])
@route('/radio.mp3', method=["GET", "HEAD"])
def radio():
    """Stream endpoint redirecting to the internal MPD HTTP streaming output."""
    if not check_auth():
        response.status = 403
        return "Forbidden: Invalid or missing authentication token"
    if MPD_RADIO_URL:
        return redirect(MPD_RADIO_URL, 302)
    response.status = 404
    return "MPD_RADIO_URL not configured"


@route('/silence', method=["GET", "HEAD"])
@route('/silence.mp3', method=["GET", "HEAD"])
def serve_silence():
    """Serve silence audio file for Alexa AudioPlayer when HEOS mode is active."""
    if not check_auth():
        response.status = 403
        return "Forbidden: Invalid or missing authentication token"
    response.content_type = 'audio/mpeg'
    if os.path.exists(SILENCE_FILE):
        with open(SILENCE_FILE, 'rb') as f:
            return f.read()
    response.status = 404
    return "Silence file not found"


def _get_heos_status_json():
    return json.dumps({
        "enabled": heos_config["enabled"],
        "host": heos_config["host"],
        "port": heos_config["port"],
        "pid": heos_config["pid"],
        "stream_url": heos_config["stream_url"] or MPD_RADIO_URL or RADIO_URL,
        "devices": list(heos_config["devices"])
    }, indent=2)


@route('/api/heos/status', method=["GET"])
def heos_status():
    if not check_auth():
        response.status = 403
        response.content_type = 'application/json'
        return json.dumps({"error": "Forbidden: Invalid or missing authentication token"})
    response.status = 200
    response.content_type = 'application/json'
    return _get_heos_status_json()


@route('/api/heos/enable', method=["GET", "POST"])
def heos_enable():
    if not check_auth():
        response.status = 403
        response.content_type = 'application/json'
        return json.dumps({"error": "Forbidden: Invalid or missing authentication token"})
    heos_config["enabled"] = True
    device_id = request.query.get("device_id")
    if device_id:
        heos_config["devices"].add(device_id)
    host = request.query.get("host")
    if host:
        heos_config["host"] = host
    logger.info("HEOS mode enabled: host=%s, devices=%s", heos_config["host"], heos_config["devices"])
    response.status = 200
    response.content_type = 'application/json'
    return _get_heos_status_json()


@route('/api/heos/disable', method=["GET", "POST"])
def heos_disable():
    if not check_auth():
        response.status = 403
        response.content_type = 'application/json'
        return json.dumps({"error": "Forbidden: Invalid or missing authentication token"})
    heos_config["enabled"] = False
    logger.info("HEOS mode disabled")
    response.status = 200
    response.content_type = 'application/json'
    return _get_heos_status_json()


@route('/api/heos/toggle', method=["GET", "POST"])
def heos_toggle():
    if not check_auth():
        response.status = 403
        response.content_type = 'application/json'
        return json.dumps({"error": "Forbidden: Invalid or missing authentication token"})
    heos_config["enabled"] = not heos_config["enabled"]
    logger.info("HEOS mode toggled to: %s", heos_config["enabled"])
    response.status = 200
    response.content_type = 'application/json'
    return _get_heos_status_json()


@route('/api/heos/device', method=["GET", "POST"])
def heos_device():
    if not check_auth():
        response.status = 403
        response.content_type = 'application/json'
        return json.dumps({"error": "Forbidden: Invalid or missing authentication token"})
    device_id = request.query.get("device_id")
    action = request.query.get("action", "add")
    if not device_id:
        response.status = 400
        response.content_type = 'application/json'
        return json.dumps({"error": "device_id parameter required"})
    if action == "add":
        heos_config["devices"].add(device_id)
    elif action == "remove":
        heos_config["devices"].discard(device_id)
    response.status = 200
    response.content_type = 'application/json'
    return _get_heos_status_json()


@route('/alexa', method=['POST'])
def index():
    body = request.body.read().decode()
    headers = request.headers
    logger.info(headers)
    pretty_print_json(body)
    return webservice_handler.verify_request_and_dispatch(headers, body)


from socketserver import ThreadingMixIn
from wsgiref.simple_server import WSGIServer, make_server
from bottle import ServerAdapter


class ThreadedWSGIServer(ThreadingMixIn, WSGIServer):
    daemon_threads = True
    multithread = True


class ThreadedWSGIRefServer(ServerAdapter):
    def run(self, handler):
        server = make_server(self.host, self.port, handler, server_class=ThreadedWSGIServer)
        server.serve_forever()


LISTEN_HOST = os.getenv("LISTEN_HOST", "0.0.0.0")
LISTEN_PORT = int(os.getenv("LISTEN_PORT", os.getenv("PORT", "8844")))

if __name__ == '__main__':
    try:
        import waitress
        logger.info("Starting multi-threaded Waitress WSGI server on %s:%s (8 threads)...", LISTEN_HOST, LISTEN_PORT)
        run(host=LISTEN_HOST, port=LISTEN_PORT, server='waitress', threads=8)
    except ImportError:
        logger.info("Starting multi-threaded WSGIRefServer on %s:%s...", LISTEN_HOST, LISTEN_PORT)
        run(host=LISTEN_HOST, port=LISTEN_PORT, server=ThreadedWSGIRefServer)