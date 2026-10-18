# -*- coding: utf-8 -*-
import os
import sys
import time
import requests
import logging
import json
import mimetypes
from urllib.parse import quote
from contextlib import contextmanager

from mpd import MPDClient
from bottle import route, run, template, request, response, redirect, static_file, abort

from ask_sdk_webservice_support.webservice_handler import WebserviceSkillHandler
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from alexa import util

# Ensure common audio mimetypes are registered
mimetypes.add_type('audio/flac', '.flac')
mimetypes.add_type('audio/mpeg', '.mp3')
mimetypes.add_type('audio/mp4', '.m4a')
mimetypes.add_type('audio/ogg', '.ogg')

sb = SkillBuilder()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

client = MPDClient()

# Configuration via environment variables (kept fully generic)
MPD_HOST = os.getenv("MPD_HOST", "localhost")
MPD_PORT = int(os.getenv("MPD_PORT", "6600"))

# Base URL that Alexa uses to access streams on this service (e.g. https://jukebox.example.com)
BASE_URL = os.getenv("BASE_URL")
RADIO_URL = os.getenv("RADIO_URL")
MPD_RADIO_URL = os.getenv("MPD_RADIO_URL")

# Music directory (mounted into container for direct file streaming, e.g. /music)
MUSIC_DIR = os.getenv("MUSIC_DIR")

# Optional authentication token to secure the /song endpoints from public access
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

# Operating mode: "tracks" (direct song-by-song streaming) or "radio" (continuous MPD HTTP stream)
# Defaults to "tracks" if MUSIC_DIR is set, otherwise falls back to "radio"
STREAM_MODE = os.getenv("STREAM_MODE", "tracks" if MUSIC_DIR else "radio").lower()

if not BASE_URL and RADIO_URL:
    BASE_URL = RADIO_URL.rsplit('/', 1)[0]

# Ensure RADIO_URL ends with .mp3 for Alexa compatibility in radio mode
if RADIO_URL and not RADIO_URL.endswith('.mp3'):
    RADIO_URL_MP3 = RADIO_URL + '.mp3'
else:
    RADIO_URL_MP3 = RADIO_URL

logger.info("Configured MPD Skill: mode=%s, mpd=%s:%s, music_dir=%s, base_url=%s, auth=%s",
            STREAM_MODE, MPD_HOST, MPD_PORT, MUSIC_DIR, BASE_URL, bool(AUTH_TOKEN))


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


# ######################### SONG & QUEUE HELPERS #########################

def get_song_url(song):
    """Generate the streaming URL for a song, including auth token if configured."""
    song_id = song.get('id')
    file_path = song.get('file', '')
    safe_name = quote(os.path.basename(file_path))
    query_str = f"?token={quote(AUTH_TOKEN)}" if AUTH_TOKEN else ""
    if BASE_URL:
        base = BASE_URL.rstrip('/')
        return f"{base}/song/{song_id}/{safe_name}{query_str}"
    return f"/song/{song_id}/{safe_name}{query_str}"


def get_song_metadata(song):
    """Return dictionary of metadata for Alexa AudioItem display."""
    title = song.get('title') or os.path.splitext(os.path.basename(song.get('file', '')))[0]
    artist = song.get('artist', '')
    album = song.get('album', '')
    if artist and album:
        subtitle = f"{artist} - {album}"
    else:
        subtitle = artist or album
    return {
        "title": title,
        "subtitle": subtitle,
        "art_url": None
    }


def get_song_speech(song):
    """Format speech description for a song."""
    title = song.get('title')
    artist = song.get('artist')
    if title and artist:
        return f"Spiele das Lied {title} von {artist}"
    elif title:
        return f"Spiele das Lied {title}"
    return "Spiele nächsten Titel"


def find_song_in_playlist(playlist, song_id):
    """Find a song by its id in the playlist and return (index, song)."""
    if not playlist or song_id is None:
        return None, None
    for idx, s in enumerate(playlist):
        if str(s.get('id')) == str(song_id):
            return idx, s
    return None, None


def get_current_or_first_song():
    """Get the currently selected or first song in the playlist."""
    with connection():
        curr = client.currentsong()
        if curr and 'id' in curr:
            return curr
        playlist = client.playlistinfo()
        if playlist:
            return playlist[0]
        return None


def get_next_song(current_song_id=None):
    """Find the next song in the MPD queue after current_song_id."""
    with connection():
        playlist = client.playlistinfo()
        if not playlist:
            return None

        if current_song_id is None:
            curr = client.currentsong()
            current_song_id = curr.get('id') if curr else None

        if current_song_id is not None:
            idx, _ = find_song_in_playlist(playlist, current_song_id)
            if idx is not None and idx + 1 < len(playlist):
                return playlist[idx + 1]
            try:
                status = client.status()
                if status.get('repeat') == '1':
                    return playlist[0]
            except Exception:
                pass
            return None
        return playlist[0]


def get_previous_song(current_song_id=None):
    """Find the previous song in the MPD queue before current_song_id."""
    with connection():
        playlist = client.playlistinfo()
        if not playlist:
            return None

        if current_song_id is None:
            curr = client.currentsong()
            current_song_id = curr.get('id') if curr else None

        if current_song_id is not None:
            idx, _ = find_song_in_playlist(playlist, current_song_id)
            if idx is not None and idx > 0:
                return playlist[idx - 1]
            return playlist[0]
        return playlist[0]


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
        return results


def search_album_tracks(album, artist=None):
    """Search MPD library for tracks belonging to an album."""
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
        return results


# ######################### INTENT HANDLERS #########################

class CheckAudioInterfaceHandler(AbstractRequestHandler):
    """Check if device supports audio play."""
    def can_handle(self, handler_input):
        if handler_input.request_envelope.context.system.device:
            return handler_input.request_envelope.context.system.device.supported_interfaces.audio_player is None
        return False

    def handle(self, handler_input):
        logger.info("In CheckAudioInterfaceHandler")
        handler_input.response_builder.speak("Sorry, this skill is not supported on this device").set_should_end_session(True)
        return handler_input.response_builder.response


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
        logger.info("In LaunchRequestOrPlayAudioHandler (mode: %s)", STREAM_MODE)

        if STREAM_MODE == "tracks":
            song = get_current_or_first_song()
            if not song:
                handler_input.response_builder.speak("Die Wiedergabeliste ist leer.").set_should_end_session(True)
                return handler_input.response_builder.response

            speech = get_song_speech(song)
            logger.info("speak: %s", speech)
            song_url = get_song_url(song)
            token = str(song['id'])
            metadata = get_song_metadata(song)
            return util.play(url=song_url,
                             offset=0,
                             text="ok",
                             card_data=None,
                             response_builder=handler_input.response_builder,
                             token=token,
                             metadata=metadata)
        else:
            song = None
            with connection():
                client.play()
                time.sleep(1)
                song = client.currentsong()

            if not song:
                handler_input.response_builder.speak("Die Wiedergabeliste ist leer.").set_should_end_session(True)
                return handler_input.response_builder.response
            else:
                try:
                    speech = f"Spiele das Lied {song['title']} von {song['artist']}"
                    logger.info("speak: %s", speech)
                except Exception:
                    pass
                return util.play(url=RADIO_URL_MP3,
                                offset=0,
                                text="ok",
                                card_data=None,
                                response_builder=handler_input.response_builder)


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
            playlist_before = client.playlistinfo()
            was_empty = len(playlist_before) == 0
            client.add(file_path)
            playlist_after = client.playlistinfo()
            new_song = playlist_after[-1] if playlist_after else None

        title = match.get('title') or song_title
        art = match.get('artist', '')
        speech_text = f"Ich habe {title}" + (f" von {art}" if art else "") + " zur Wiedergabeliste hinzugefügt."

        # If queue was empty, start playback immediately
        if STREAM_MODE == "tracks" and was_empty and new_song:
            song_url = get_song_url(new_song)
            token = str(new_song['id'])
            metadata = get_song_metadata(new_song)
            return util.play(url=song_url,
                             offset=0,
                             text=speech_text,
                             card_data=None,
                             response_builder=handler_input.response_builder,
                             token=token,
                             metadata=metadata)

        handler_input.response_builder.speak(speech_text).set_should_end_session(True)
        return handler_input.response_builder.response


class PlaySongHandler(AbstractRequestHandler):
    """Handler for immediately playing a specific song."""
    def can_handle(self, handler_input):
        return is_intent_name("PlaySongIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In PlaySongHandler")
        song_title = get_slot_value(handler_input, "Song")
        artist = get_slot_value(handler_input, "Artist")

        if not song_title:
            handler_input.response_builder.speak("Welches Lied soll ich spielen?").set_should_end_session(False)
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
            song_id = client.addid(file_path)
            songs = client.playlistid(song_id)
            song = songs[0] if songs else match
            song['id'] = song_id

        title = match.get('title') or song_title
        art = match.get('artist', '')
        speech = f"Spiele {title}" + (f" von {art}" if art else "")

        if STREAM_MODE == "tracks":
            song_url = get_song_url(song)
            token = str(song_id)
            metadata = get_song_metadata(song)
            return util.play(url=song_url,
                             offset=0,
                             text=speech,
                             card_data=None,
                             response_builder=handler_input.response_builder,
                             token=token,
                             metadata=metadata)
        else:
            with connection():
                client.playid(song_id)
            return util.play(url=RADIO_URL_MP3,
                             offset=0,
                             text=speech,
                             card_data=None,
                             response_builder=handler_input.response_builder)


class PlayAlbumHandler(AbstractRequestHandler):
    """Handler for playing an album."""
    def can_handle(self, handler_input):
        return is_intent_name("PlayAlbumIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In PlayAlbumHandler")
        album = get_slot_value(handler_input, "Album")
        artist = get_slot_value(handler_input, "Artist")

        if not album:
            handler_input.response_builder.speak("Welches Album möchtest du hören?").set_should_end_session(False)
            return handler_input.response_builder.response

        tracks = search_album_tracks(album, artist=artist)
        if not tracks:
            handler_input.response_builder.speak(f"Ich konnte das Album {album} nicht finden.").set_should_end_session(True)
            return handler_input.response_builder.response

        with connection():
            client.clear()
            for t in tracks:
                client.add(t['file'])
            playlist = client.playlistinfo()
            first_song = playlist[0] if playlist else None

        speech = f"Spiele Album {album}" + (f" von {artist}" if artist else "")
        if STREAM_MODE == "tracks" and first_song:
            song_url = get_song_url(first_song)
            token = str(first_song['id'])
            metadata = get_song_metadata(first_song)
            return util.play(url=song_url,
                             offset=0,
                             text=speech,
                             card_data=None,
                             response_builder=handler_input.response_builder,
                             token=token,
                             metadata=metadata)
        else:
            with connection():
                client.play(0)
            return util.play(url=RADIO_URL_MP3,
                             offset=0,
                             text=speech,
                             card_data=None,
                             response_builder=handler_input.response_builder)


class PlayArtistHandler(AbstractRequestHandler):
    """Handler for playing music by an artist."""
    def can_handle(self, handler_input):
        return is_intent_name("PlayArtistIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In PlayArtistHandler")
        artist = get_slot_value(handler_input, "Artist")

        if not artist:
            handler_input.response_builder.speak("Welchen Künstler möchtest du hören?").set_should_end_session(False)
            return handler_input.response_builder.response

        tracks = search_tracks(artist=artist)
        if not tracks:
            handler_input.response_builder.speak(f"Ich konnte keine Musik von {artist} finden.").set_should_end_session(True)
            return handler_input.response_builder.response

        with connection():
            client.clear()
            for t in tracks[:100]:
                client.add(t['file'])
            playlist = client.playlistinfo()
            first_song = playlist[0] if playlist else None

        speech = f"Spiele Musik von {artist}"
        if STREAM_MODE == "tracks" and first_song:
            song_url = get_song_url(first_song)
            token = str(first_song['id'])
            metadata = get_song_metadata(first_song)
            return util.play(url=song_url,
                             offset=0,
                             text=speech,
                             card_data=None,
                             response_builder=handler_input.response_builder,
                             token=token,
                             metadata=metadata)
        else:
            with connection():
                client.play(0)
            return util.play(url=RADIO_URL_MP3,
                             offset=0,
                             text=speech,
                             card_data=None,
                             response_builder=handler_input.response_builder)


class ClearQueueHandler(AbstractRequestHandler):
    """Handler for clearing the MPD queue."""
    def can_handle(self, handler_input):
        return is_intent_name("ClearQueueIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In ClearQueueHandler")
        with connection():
            try:
                client.clear()
            except Exception:
                pass
        return util.stop("Die Wiedergabeliste wurde geleert.", handler_input.response_builder)


class QueueStatusHandler(AbstractRequestHandler):
    """Handler for reporting queue status."""
    def can_handle(self, handler_input):
        return is_intent_name("QueueStatusIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In QueueStatusHandler")
        with connection():
            playlist = client.playlistinfo()
            curr = client.currentsong()
        count = len(playlist)
        if count == 0:
            speech = "Die Wiedergabeliste ist aktuell leer."
        else:
            curr_title = curr.get('title') if curr else None
            curr_artist = curr.get('artist') if curr else None
            if curr_title and curr_artist:
                speech = f"In der Wiedergabeliste sind {count} Lieder. Aktuell läuft {curr_title} von {curr_artist}."
            elif curr_title:
                speech = f"In der Wiedergabeliste sind {count} Lieder. Aktuell läuft {curr_title}."
            else:
                speech = f"In der Wiedergabeliste sind {count} Lieder."
        handler_input.response_builder.speak(speech).set_should_end_session(False)
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for providing help information to user."""
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In HelpIntentHandler")
        speech = "Dies ist ein MPD Player. Wähle Lieder in deiner MPD-App aus und steuere die Wiedergabe per Sprache."
        try:
            with connection():
                song = client.currentsong()
                if song and 'title' in song:
                    speech = f"In der Playlist ausgewählt ist {song['title']} von {song.get('artist', 'Unbekannt')}"
        except Exception:
            pass

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
        logger.info("In NextOrPreviousIntentHandler (mode: %s)", STREAM_MODE)
        is_next = is_intent_name("AMAZON.NextIntent")(handler_input)

        if STREAM_MODE == "tracks":
            current_token = None
            try:
                current_token = handler_input.request_envelope.context.audio_player.token
            except Exception:
                pass

            if is_next:
                song = get_next_song(current_token)
            else:
                song = get_previous_song(current_token)

            if not song:
                speech = "Das Ende der Wiedergabeliste ist erreicht." if is_next else "Der Anfang der Wiedergabeliste ist erreicht."
                handler_input.response_builder.speak(speech=speech).set_should_end_session(True)
                return handler_input.response_builder.response

            song_url = get_song_url(song)
            token = str(song['id'])
            metadata = get_song_metadata(song)
            speech = get_song_speech(song)
            logger.info("speak: %s", speech)

            return util.play(url=song_url,
                             offset=0,
                             text=None,
                             card_data=None,
                             response_builder=handler_input.response_builder,
                             token=token,
                             metadata=metadata)
        else:
            with connection():
                try:
                    if is_next:
                        client.next()
                    else:
                        client.previous()
                except Exception as e:
                    logger.error("error executing: %s", e)
                    client.play()

                time.sleep(0.1)
                song = client.currentsong()
                speech = "ok"
                try:
                    speech = f"Spiele das Lied {song['title']} von {song['artist']}"
                    logger.info("speak: %s", speech)
                except Exception:
                    pass

                handler_input.response_builder.speak(speech=speech).set_should_end_session(True)
            return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Handler for cancel, stop or pause intents."""
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input) or
                is_intent_name("AMAZON.PauseIntent")(handler_input))

    def handle(self, handler_input):
        logger.info("In CancelOrStopIntentHandler")
        if STREAM_MODE != "tracks":
            with connection():
                try:
                    client.stop()
                except Exception:
                    pass
        return util.stop("Auf Wiedersehen!", handler_input.response_builder)


class ResumeIntentHandler(AbstractRequestHandler):
    """Handler for resume intent."""
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.ResumeIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In ResumeIntentHandler (mode: %s)", STREAM_MODE)
        if STREAM_MODE == "tracks":
            current_token = None
            offset = 0
            try:
                audio_player = handler_input.request_envelope.context.audio_player
                current_token = audio_player.token
                offset = audio_player.offset_in_milliseconds or 0
            except Exception:
                pass

            song = None
            if current_token:
                with connection():
                    songs = client.playlistid(current_token)
                    if songs:
                        song = songs[0]
            if not song:
                song = get_current_or_first_song()

            if not song:
                handler_input.response_builder.speak("Die Wiedergabeliste ist leer.").set_should_end_session(True)
                return handler_input.response_builder.response

            song_url = get_song_url(song)
            token = str(song['id'])
            metadata = get_song_metadata(song)
            return util.play(url=song_url,
                             offset=offset,
                             text=None,
                             card_data=None,
                             response_builder=handler_input.response_builder,
                             token=token,
                             metadata=metadata)
        else:
            with connection():
                song = client.currentsong()
                speech = "ok"
                try:
                    speech = f"Spiele das Lied {song['title']} von {song['artist']}"
                    logger.info("speak: %s", speech)
                except Exception:
                    pass
            return util.play(
                url=RADIO_URL_MP3, offset=0,
                text=speech, card_data=None,
                response_builder=handler_input.response_builder)


class StartOverIntentHandler(AbstractRequestHandler):
    """Handler for start over, loop on/off, shuffle on/off intent."""
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.StartOverIntent")(handler_input) or
                is_intent_name("AMAZON.LoopOnIntent")(handler_input) or
                is_intent_name("AMAZON.LoopOffIntent")(handler_input) or
                is_intent_name("AMAZON.ShuffleOnIntent")(handler_input) or
                is_intent_name("AMAZON.ShuffleOffIntent")(handler_input))

    def handle(self, handler_input):
        logger.info("In StartOverIntentHandler")
        if is_intent_name("AMAZON.StartOverIntent")(handler_input):
            if STREAM_MODE == "tracks":
                current_token = None
                try:
                    current_token = handler_input.request_envelope.context.audio_player.token
                except Exception:
                    pass
                song = None
                if current_token:
                    with connection():
                        songs = client.playlistid(current_token)
                        if songs:
                            song = songs[0]
                if not song:
                    song = get_current_or_first_song()
                if song:
                    return util.play(url=get_song_url(song),
                                     offset=0,
                                     text=None,
                                     card_data=None,
                                     response_builder=handler_input.response_builder,
                                     token=str(song['id']),
                                     metadata=get_song_metadata(song))

        speech = "Diese Funktion wird im aktuellen Modus nicht unterstützt."
        return handler_input.response_builder.speak(speech).response


# ######################### AUDIOPLAYER INTERFACE HANDLERS #########################

class PlaybackStartedHandler(AbstractRequestHandler):
    """AudioPlayer.PlaybackStarted Directive received."""
    def can_handle(self, handler_input):
        return is_request_type("AudioPlayer.PlaybackStarted")(handler_input)

    def handle(self, handler_input):
        logger.info("In PlaybackStartedHandler")
        request = handler_input.request_envelope.request
        token = getattr(request, 'token', None)
        logger.info("Playback started for token: %s", token)

        # Synchronize MPD active song pointer with Alexa playback
        if STREAM_MODE == "tracks" and token and token.isdigit():
            try:
                with connection():
                    client.seekid(int(token), 0)
            except Exception as e:
                logger.debug("Could not seekid in MPD: %s", e)

        return handler_input.response_builder.response


class PlaybackFinishedHandler(AbstractRequestHandler):
    """AudioPlayer.PlaybackFinished Directive received."""
    def can_handle(self, handler_input):
        return is_request_type("AudioPlayer.PlaybackFinished")(handler_input)

    def handle(self, handler_input):
        logger.info("In PlaybackFinishedHandler")
        return handler_input.response_builder.response


class PlaybackStoppedHandler(AbstractRequestHandler):
    """AudioPlayer.PlaybackStopped Directive received."""
    def can_handle(self, handler_input):
        return is_request_type("AudioPlayer.PlaybackStopped")(handler_input)

    def handle(self, handler_input):
        logger.info("In PlaybackStoppedHandler")
        return handler_input.response_builder.response


class PlaybackNearlyFinishedHandler(AbstractRequestHandler):
    """AudioPlayer.PlaybackNearlyFinished Directive received."""
    def can_handle(self, handler_input):
        return is_request_type("AudioPlayer.PlaybackNearlyFinished")(handler_input)

    def handle(self, handler_input):
        logger.info("In PlaybackNearlyFinishedHandler (mode: %s)", STREAM_MODE)
        request = handler_input.request_envelope.request

        if STREAM_MODE == "tracks":
            current_token = getattr(request, 'token', None)
            next_song = get_next_song(current_token)
            if next_song:
                next_url = get_song_url(next_song)
                next_token = str(next_song['id'])
                metadata = get_song_metadata(next_song)
                logger.info("Enqueuing next track: %s (id: %s)", next_song.get('title'), next_token)
                return util.play_later(
                    url=next_url,
                    card_data=None,
                    response_builder=handler_input.response_builder,
                    token=next_token,
                    expected_previous_token=current_token,
                    metadata=metadata
                )
            else:
                logger.info("End of playlist reached, nothing more to enqueue.")
                return handler_input.response_builder.response
        else:
            return util.play_later(
                url=RADIO_URL_MP3,
                card_data=util.audio_data(request)["card"],
                response_builder=handler_input.response_builder)


class PlaybackFailedHandler(AbstractRequestHandler):
    """AudioPlayer.PlaybackFailed Directive received."""
    def can_handle(self, handler_input):
        return is_request_type("AudioPlayer.PlaybackFailed")(handler_input)

    def handle(self, handler_input):
        logger.info("In PlaybackFailedHandler")
        request = handler_input.request_envelope.request
        logger.error("Playback failed: %s, token: %s",
                     getattr(request, 'error', None), getattr(request, 'token', None))
        return util.stop(text=None, response_builder=handler_input.response_builder)


class ExceptionEncounteredHandler(AbstractRequestHandler):
    """Handler to handle exceptions from responses sent by AudioPlayer."""
    def can_handle(self, handler_input):
        return is_request_type("System.ExceptionEncountered")(handler_input)

    def handle(self, handler_input):
        logger.info("\n**************** EXCEPTION *******************")
        logger.info(handler_input.request_envelope)
        return handler_input.response_builder.response


# ######################### PLAYBACK CONTROLLER HANDLERS #########################

class PlayCommandHandler(AbstractRequestHandler):
    """Handler for Play command from hardware buttons or touch control."""
    def can_handle(self, handler_input):
        return is_request_type("PlaybackController.PlayCommandIssued")(handler_input)

    def handle(self, handler_input):
        logger.info("In PlayCommandHandler")
        if STREAM_MODE == "tracks":
            song = get_current_or_first_song()
            if song:
                song_url = get_song_url(song)
                token = str(song['id'])
                metadata = get_song_metadata(song)
                return util.play(url=song_url,
                                 offset=0,
                                 text="ok",
                                 card_data=None,
                                 response_builder=handler_input.response_builder,
                                 token=token,
                                 metadata=metadata)
            return handler_input.response_builder.response
        else:
            return util.play(url=RADIO_URL_MP3,
                             offset=0,
                             text="ok",
                             card_data=None,
                             response_builder=handler_input.response_builder)


class NextOrPreviousCommandHandler(AbstractRequestHandler):
    """Handler for Next or Previous command from hardware buttons."""
    def can_handle(self, handler_input):
        return (is_request_type("PlaybackController.NextCommandIssued")(handler_input) or
                is_request_type("PlaybackController.PreviousCommandIssued")(handler_input))

    def handle(self, handler_input):
        logger.info("In NextOrPreviousCommandHandler")
        is_next = is_request_type("PlaybackController.NextCommandIssued")(handler_input)

        if STREAM_MODE == "tracks":
            current_token = None
            try:
                current_token = handler_input.request_envelope.context.audio_player.token
            except Exception:
                pass
            if is_next:
                song = get_next_song(current_token)
            else:
                song = get_previous_song(current_token)
            if song:
                song_url = get_song_url(song)
                token = str(song['id'])
                metadata = get_song_metadata(song)
                return util.play(url=song_url,
                                 offset=0,
                                 text=None,
                                 card_data=None,
                                 response_builder=handler_input.response_builder,
                                 token=token,
                                 metadata=metadata)
        return handler_input.response_builder.response


class PauseCommandHandler(AbstractRequestHandler):
    """Handler for Pause command from hardware buttons."""
    def can_handle(self, handler_input):
        return is_request_type("PlaybackController.PauseCommandIssued")(handler_input)

    def handle(self, handler_input):
        logger.info("In PauseCommandHandler")
        return util.stop(text=None, response_builder=handler_input.response_builder)


# ######################### INTERCEPTORS #########################

class RequestLogger(AbstractRequestInterceptor):
    def process(self, handler_input):
        logger.debug("Alexa Request: %s", handler_input.request_envelope.request)


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
    # e.g. https://alexa:<token>@domain/song/...
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


@route('/song/<song_id:int>', method=["GET", "HEAD"])
@route('/song/<song_id:int>/<filename:path>', method=["GET", "HEAD"])
def serve_song(song_id, filename=None):
    """Serve a music file directly for Alexa AudioPlayer with Range and Auth support."""
    if not check_auth():
        logger.warning("Unauthorized access to song %s from %s", song_id, request.remote_addr)
        response.status = 403
        return "Forbidden: Invalid or missing authentication token"

    if not MUSIC_DIR:
        response.status = 404
        return "MUSIC_DIR is not configured"

    try:
        with connection():
            songs = client.playlistid(song_id)
    except Exception as e:
        logger.error("MPD error retrieving song %s: %s", song_id, e)
        response.status = 500
        return "MPD connection error"

    if not songs:
        response.status = 404
        return "Song not found in playlist"

    file_rel_path = songs[0].get('file')
    if not file_rel_path:
        response.status = 404
        return "No file path for song"

    logger.info("Serving song id %s: %s", song_id, file_rel_path)
    return static_file(file_rel_path, root=MUSIC_DIR)


@route('/radio', method=["GET", "HEAD"])
def radio():
    if not check_auth():
        response.status = 403
        return "Forbidden: Invalid or missing authentication token"
    if MPD_RADIO_URL:
        return redirect(MPD_RADIO_URL, 302)
    response.status = 404
    return "MPD_RADIO_URL not configured"


@route('/radio.mp3', method=["GET", "HEAD"])
def radio_mp3():
    if not check_auth():
        response.status = 403
        return "Forbidden: Invalid or missing authentication token"
    if MPD_RADIO_URL:
        return redirect(MPD_RADIO_URL, 302)
    response.status = 404
    return "MPD_RADIO_URL not configured"


@route('/alexa', method=['POST'])
def index():
    body = request.body.read().decode()
    headers = request.headers
    logger.info(headers)
    pretty_print_json(body)
    return webservice_handler.verify_request_and_dispatch(headers, body)


LISTEN_HOST = os.getenv("LISTEN_HOST", "0.0.0.0")
LISTEN_PORT = int(os.getenv("LISTEN_PORT", os.getenv("PORT", "8844")))

if __name__ == '__main__':
    run(host=LISTEN_HOST, port=LISTEN_PORT)