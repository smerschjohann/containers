# -*- coding: utf-8 -*-
"""
Unit tests for the MPD Alexa Skill (Continuous Radio / FLAC Stream mode).
Tests authentication, stream redirection, MPD search helpers, queue management,
auto-queueing, and Alexa Intent / AudioPlayer / PlaybackController handlers.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure test environment paths
sys.path.insert(0, os.path.dirname(__file__))

import lambda_function as skill
from ask_sdk_model import (
    RequestEnvelope, Request, IntentRequest, Intent, Slot,
    Context, Device, SupportedInterfaces
)
from ask_sdk_model.interfaces.audioplayer import (
    AudioPlayerState, PlayerActivity, PlayDirective, PlayBehavior, StopDirective
)
from ask_sdk_core.handler_input import HandlerInput


def create_handler_input(request_type="IntentRequest", intent_name=None, slots=None, token="radio_stream", offset=0, supported_interfaces=True):
    """Helper to create a typed HandlerInput for testing."""
    if request_type == "IntentRequest":
        slot_objs = {}
        if slots:
            for k, v in slots.items():
                slot_objs[k] = Slot(name=k, value=v)
        req = IntentRequest(
            request_id="req-test-1",
            timestamp="2026-10-18T12:00:00Z",
            intent=Intent(name=intent_name, slots=slot_objs)
        )
    elif request_type == "LaunchRequest":
        req = Request(
            object_type="LaunchRequest",
            request_id="req-test-launch",
            timestamp="2026-10-18T12:00:00Z"
        )
    elif request_type.startswith("AudioPlayer.") or request_type.startswith("PlaybackController."):
        req = Request(
            object_type=request_type,
            request_id="req-test-audio",
            timestamp="2026-10-18T12:00:00Z"
        )
        setattr(req, "token", token)
        setattr(req, "offset_in_milliseconds", offset)
    else:
        req = Request(
            object_type=request_type,
            request_id="req-test-generic",
            timestamp="2026-10-18T12:00:00Z"
        )

    audio_player = AudioPlayerState(
        token=token,
        offset_in_milliseconds=offset,
        player_activity=PlayerActivity.PLAYING
    )

    if supported_interfaces:
        device = Device(supported_interfaces=SupportedInterfaces(audio_player=audio_player))
    else:
        device = Device(supported_interfaces=SupportedInterfaces(audio_player=None))

    context = Context(
        system=MagicMock(device=device),
        audio_player=audio_player
    )

    envelope = RequestEnvelope(request=req, context=context)
    return HandlerInput(request_envelope=envelope)


class TestMpdSkillConfigAndAuth(unittest.TestCase):
    """Tests for authentication and radio URL generation."""

    def test_get_radio_url_with_auth_token(self):
        with patch.object(skill, 'RADIO_URL', 'https://jukebox.example.com/radio'), \
             patch.object(skill, 'AUTH_TOKEN', 'secret123'):
            url = skill.get_radio_url()
            self.assertEqual(url, 'https://jukebox.example.com/radio?token=secret123')

    def test_get_radio_url_with_existing_query_string(self):
        with patch.object(skill, 'RADIO_URL', 'https://jukebox.example.com/radio?fmt=flac'), \
             patch.object(skill, 'AUTH_TOKEN', 'secret123'):
            url = skill.get_radio_url()
            self.assertEqual(url, 'https://jukebox.example.com/radio?fmt=flac&token=secret123')

    def test_get_radio_url_already_has_token(self):
        with patch.object(skill, 'RADIO_URL', 'https://jukebox.example.com/radio?token=preexisting'), \
             patch.object(skill, 'AUTH_TOKEN', 'secret123'):
            url = skill.get_radio_url()
            self.assertEqual(url, 'https://jukebox.example.com/radio?token=preexisting')

    def test_get_radio_url_without_auth_token(self):
        with patch.object(skill, 'RADIO_URL', 'https://jukebox.example.com/radio'), \
             patch.object(skill, 'AUTH_TOKEN', None):
            url = skill.get_radio_url()
            self.assertEqual(url, 'https://jukebox.example.com/radio')

    def test_get_radio_url_none(self):
        with patch.object(skill, 'RADIO_URL', None):
            self.assertIsNone(skill.get_radio_url())

    def test_check_auth_query_token(self):
        with patch.object(skill, 'AUTH_TOKEN', 'mytoken'):
            skill.request.bind({'QUERY_STRING': 'token=mytoken'})
            self.assertTrue(skill.check_auth())

            skill.request.bind({'QUERY_STRING': 'token=wrong'})
            self.assertFalse(skill.check_auth())

            skill.request.bind({'QUERY_STRING': ''})
            self.assertFalse(skill.check_auth())

    def test_check_auth_header_x_auth_token(self):
        with patch.object(skill, 'AUTH_TOKEN', 'mytoken'):
            skill.request.bind({'HTTP_X_AUTH_TOKEN': 'mytoken', 'QUERY_STRING': ''})
            self.assertTrue(skill.check_auth())

            skill.request.bind({'HTTP_X_AUTH_TOKEN': 'wrong', 'QUERY_STRING': ''})
            self.assertFalse(skill.check_auth())

    def test_check_auth_basic_auth(self):
        import base64
        with patch.object(skill, 'AUTH_TOKEN', 'mytoken'):
            auth_header = 'Basic ' + base64.b64encode(b'alexa:mytoken').decode('ascii')
            skill.request.bind({'HTTP_AUTHORIZATION': auth_header, 'QUERY_STRING': ''})
            self.assertTrue(skill.check_auth())

            bad_header = 'Basic ' + base64.b64encode(b'alexa:wrongpass').decode('ascii')
            skill.request.bind({'HTTP_AUTHORIZATION': bad_header, 'QUERY_STRING': ''})
            self.assertFalse(skill.check_auth())

    def test_check_auth_bearer_token(self):
        with patch.object(skill, 'AUTH_TOKEN', 'mytoken'):
            skill.request.bind({'HTTP_AUTHORIZATION': 'Bearer mytoken', 'QUERY_STRING': ''})
            self.assertTrue(skill.check_auth())

            skill.request.bind({'HTTP_AUTHORIZATION': 'Bearer wrong', 'QUERY_STRING': ''})
            self.assertFalse(skill.check_auth())

    def test_check_auth_disabled_when_token_none(self):
        with patch.object(skill, 'AUTH_TOKEN', None):
            self.assertTrue(skill.check_auth())


class TestMpdHelpersAndQueue(unittest.TestCase):
    """Tests for MPD search and auto-queue helpers."""

    @patch.object(skill, 'client')
    @patch.object(skill, 'connection')
    def test_search_tracks(self, mock_conn, mock_client):
        mock_conn.return_value.__enter__.return_value = None
        mock_client.search.return_value = [{'id': '10', 'title': 'Hysteria', 'artist': 'Muse', 'file': 'Muse/Hysteria.flac'}]

        res = skill.search_tracks(title="Hysteria", artist="Muse")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['title'], 'Hysteria')

    @patch.object(skill, 'client')
    @patch.object(skill, 'connection')
    def test_search_album_tracks(self, mock_conn, mock_client):
        mock_conn.return_value.__enter__.return_value = None
        mock_client.search.return_value = [
            {'title': 'Track 1', 'file': 'Album/01.flac'},
            {'title': 'Track 2', 'file': 'Album/02.flac'}
        ]

        res = skill.search_album_tracks(album="Origin of Symmetry", artist="Muse")
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]['title'], 'Track 1')

    @patch.object(skill, 'client')
    @patch.object(skill, 'connection')
    def test_add_random_music_to_queue_album_mode(self, mock_conn, mock_client):
        mock_conn.return_value.__enter__.return_value = None
        mock_client.list.return_value = [{'album': 'Discovery'}, {'album': 'Random Access Memories'}]

        with patch.object(skill, 'AUTO_QUEUE_MODE', 'album'):
            result = skill.add_random_music_to_queue()
            self.assertTrue(result)
            mock_client.findadd.assert_called_once()
            args = mock_client.findadd.call_args[0]
            self.assertEqual(args[0], 'album')
            self.assertIn(args[1], ['Discovery', 'Random Access Memories'])

    @patch.object(skill, 'client')
    @patch.object(skill, 'connection')
    def test_add_random_music_to_queue_tracks_mode(self, mock_conn, mock_client):
        mock_conn.return_value.__enter__.return_value = None
        mock_client.list.return_value = [{'file': 'track1.flac'}, {'file': 'track2.flac'}]

        with patch.object(skill, 'AUTO_QUEUE_MODE', 'tracks'):
            result = skill.add_random_music_to_queue()
            self.assertTrue(result)
            self.assertGreaterEqual(mock_client.add.call_count, 1)

    @patch.object(skill, 'client')
    @patch.object(skill, 'connection')
    def test_restore_last_music_or_album_playlist(self, mock_conn, mock_client):
        mock_conn.return_value.__enter__.return_value = None
        mock_client.listplaylists.return_value = [
            {'playlist': 'OlderList', 'last-modified': '2026-01-01T00:00:00Z'},
            {'playlist': 'NewestList', 'last-modified': '2026-10-18T10:00:00Z'}
        ]

        success, what = skill.restore_last_music_or_album()
        self.assertTrue(success)
        self.assertEqual(what, "Wiedergabeliste NewestList")
        mock_client.load.assert_called_with("NewestList")

    @patch.object(skill, 'client')
    @patch.object(skill, 'connection')
    def test_restore_last_music_or_album_directory(self, mock_conn, mock_client):
        mock_conn.return_value.__enter__.return_value = None
        mock_client.listplaylists.return_value = []
        mock_client.lsinfo.side_effect = [
            [{'directory': 'OlderArtist', 'last-modified': '2025-01-01T00:00:00Z'},
             {'directory': 'NewArtist', 'last-modified': '2026-10-18T12:00:00Z'}],
            [{'directory': 'NewArtist/GreatestHits', 'last-modified': '2026-10-18T12:00:00Z'}]
        ]

        success, what = skill.restore_last_music_or_album()
        self.assertTrue(success)
        self.assertEqual(what, "Album GreatestHits")
        mock_client.add.assert_called_with("NewArtist/GreatestHits")

    @patch.object(skill, 'client')
    @patch.object(skill, 'connection')
    def test_restore_last_music_or_album_fallback_random(self, mock_conn, mock_client):
        mock_conn.return_value.__enter__.return_value = None
        mock_client.listplaylists.return_value = []
        mock_client.lsinfo.return_value = []
        mock_client.list.return_value = [{'album': 'RandomAlbum'}]

        success, what = skill.restore_last_music_or_album()
        self.assertTrue(success)
        self.assertEqual(what, "Album RandomAlbum")
        mock_client.findadd.assert_called_with('album', 'RandomAlbum')


class TestAlexaHandlers(unittest.TestCase):
    """Tests for Alexa skill intent and controller handlers in Radio Stream mode."""

    def setUp(self):
        self.patch_radio_url = patch.object(skill, 'RADIO_URL', 'https://jukebox.example.com/radio')
        self.patch_auth = patch.object(skill, 'AUTH_TOKEN', 'token123')
        self.patch_conn = patch.object(skill, 'connection')
        self.patch_client = patch.object(skill, 'client')

        self.patch_radio_url.start()
        self.patch_auth.start()
        self.mock_conn = self.patch_conn.start()
        self.mock_client = self.patch_client.start()
        self.mock_conn.return_value.__enter__.return_value = None

    def tearDown(self):
        self.patch_radio_url.stop()
        self.patch_auth.stop()
        self.patch_conn.stop()
        self.patch_client.stop()

    def test_check_audio_interface_unsupported(self):
        handler = skill.CheckAudioInterfaceHandler()
        hi = create_handler_input("LaunchRequest", supported_interfaces=False)

        self.assertTrue(handler.can_handle(hi))
        resp = handler.handle(hi)
        self.assertIn("unterstützt keine Audiowiedergabe", resp.output_speech.ssml)

    def test_launch_handler_plays_radio_stream(self):
        self.mock_client.playlistinfo.return_value = [{'id': '1', 'title': 'First Song'}]
        self.mock_client.currentsong.return_value = {'id': '1', 'title': 'First Song', 'artist': 'Band'}

        handler = skill.LaunchRequestOrPlayAudioHandler()
        hi = create_handler_input("LaunchRequest")

        self.assertTrue(handler.can_handle(hi))
        resp = handler.handle(hi)

        self.mock_client.play.assert_called_once()
        self.assertIsNotNone(resp.directives)
        self.assertIsInstance(resp.directives[0], PlayDirective)
        self.assertEqual(resp.directives[0].play_behavior, PlayBehavior.REPLACE_ALL)
        self.assertEqual(resp.directives[0].audio_item.stream.token, 'radio_stream')
        self.assertIn('token=token123', resp.directives[0].audio_item.stream.url)
        self.assertIn('First Song', resp.output_speech.ssml)

    def test_launch_handler_auto_queues_if_empty(self):
        self.mock_client.playlistinfo.return_value = []
        self.mock_client.currentsong.return_value = {}

        with patch.object(skill, 'restore_last_music_or_album') as mock_restore:
            mock_restore.return_value = (True, "Album Discovery")
            handler = skill.LaunchRequestOrPlayAudioHandler()
            hi = create_handler_input("LaunchRequest")

            resp = handler.handle(hi)
            mock_restore.assert_called_once()
            self.mock_client.play.assert_called_once()
            self.assertEqual(resp.directives[0].audio_item.stream.token, 'radio_stream')
            self.assertIn('Album Discovery', resp.output_speech.ssml)

    def test_queue_song_intent(self):
        self.mock_client.search.return_value = [{'title': 'Starlight', 'artist': 'Muse', 'file': 'Muse/Starlight.flac'}]

        handler = skill.QueueSongHandler()
        hi = create_handler_input("IntentRequest", "QueueSongIntent", {"Song": "Starlight", "Artist": "Muse"})

        self.assertTrue(handler.can_handle(hi))
        resp = handler.handle(hi)

        self.mock_client.add.assert_called_with('Muse/Starlight.flac')
        self.assertIn("hinzugefügt", resp.output_speech.ssml)
        # Should NOT interrupt current radio stream with a play directive
        self.assertIsNone(resp.directives)

    def test_play_song_intent(self):
        self.mock_client.search.return_value = [{'title': 'Animals', 'artist': 'Pink Floyd', 'file': 'PF/Animals.flac'}]
        self.mock_client.addid.return_value = '99'

        handler = skill.PlaySongHandler()
        hi = create_handler_input("IntentRequest", "PlaySongIntent", {"Song": "Animals"})

        self.assertTrue(handler.can_handle(hi))
        resp = handler.handle(hi)

        self.mock_client.addid.assert_called_with('PF/Animals.flac')
        self.mock_client.playid.assert_called_with('99')
        self.assertEqual(len(resp.directives), 1)
        self.assertEqual(resp.directives[0].audio_item.stream.token, 'radio_stream')
        self.assertIn("Spiele Animals", resp.output_speech.ssml)

    def test_play_album_intent(self):
        self.mock_client.search.return_value = [
            {'title': 'Track 1', 'file': 'Album/01.flac'},
            {'title': 'Track 2', 'file': 'Album/02.flac'}
        ]

        handler = skill.PlayAlbumHandler()
        hi = create_handler_input("IntentRequest", "PlayAlbumIntent", {"Album": "Dark Side", "Artist": "Pink Floyd"})

        self.assertTrue(handler.can_handle(hi))
        resp = handler.handle(hi)

        self.mock_client.clear.assert_called_once()
        self.assertEqual(self.mock_client.add.call_count, 2)
        self.mock_client.play.assert_called_once()
        self.assertEqual(resp.directives[0].audio_item.stream.token, 'radio_stream')
        self.assertIn("Dark Side", resp.output_speech.ssml)

    def test_play_artist_intent(self):
        self.mock_client.search.return_value = [
            {'title': 'Song 1', 'file': 'Artist/01.flac'},
            {'title': 'Song 2', 'file': 'Artist/02.flac'}
        ]

        handler = skill.PlayArtistHandler()
        hi = create_handler_input("IntentRequest", "PlayArtistIntent", {"Artist": "Radiohead"})

        self.assertTrue(handler.can_handle(hi))
        resp = handler.handle(hi)

        self.mock_client.clear.assert_called_once()
        self.assertEqual(self.mock_client.add.call_count, 2)
        self.mock_client.play.assert_called_once()
        self.assertEqual(resp.directives[0].audio_item.stream.token, 'radio_stream')
        self.assertIn("Radiohead", resp.output_speech.ssml)

    def test_clear_queue_intent(self):
        handler = skill.ClearQueueHandler()
        hi = create_handler_input("IntentRequest", "ClearQueueIntent")

        self.assertTrue(handler.can_handle(hi))
        resp = handler.handle(hi)

        self.mock_client.clear.assert_called_once()
        self.mock_client.stop.assert_called_once()
        self.assertIsInstance(resp.directives[0], StopDirective)
        self.assertIn("geleert", resp.output_speech.ssml)

    def test_queue_status_intent(self):
        self.mock_client.playlistinfo.return_value = [
            {'id': '1', 'title': 'Song 1'},
            {'id': '2', 'title': 'Song 2'}
        ]
        self.mock_client.currentsong.return_value = {'title': 'Song 1', 'artist': 'Band'}

        handler = skill.QueueStatusHandler()
        hi = create_handler_input("IntentRequest", "QueueStatusIntent")

        self.assertTrue(handler.can_handle(hi))
        resp = handler.handle(hi)

        self.assertIn("2 Lieder", resp.output_speech.ssml)
        self.assertIn("Song 1", resp.output_speech.ssml)

    def test_queue_status_intent_when_empty_restores_and_plays(self):
        self.mock_client.playlistinfo.return_value = []
        self.mock_client.currentsong.return_value = {'title': 'Song A', 'artist': 'Artist B'}

        with patch.object(skill, 'restore_last_music_or_album') as mock_restore:
            mock_restore.return_value = (True, "Album Greatest Hits")
            handler = skill.QueueStatusHandler()
            hi = create_handler_input("IntentRequest", "QueueStatusIntent")

            self.assertTrue(handler.can_handle(hi))
            resp = handler.handle(hi)

            mock_restore.assert_called_once()
            self.mock_client.play.assert_called_once()
            self.assertEqual(resp.directives[0].audio_item.stream.token, 'radio_stream')
            self.assertIn("Die Wiedergabeliste war leer", resp.output_speech.ssml)
            self.assertIn("Album Greatest Hits", resp.output_speech.ssml)

    def test_next_intent(self):
        self.mock_client.status.return_value = {'song': '0', 'playlistlength': '5'}

        handler = skill.NextOrPreviousIntentHandler()
        hi = create_handler_input("IntentRequest", "AMAZON.NextIntent")

        self.assertTrue(handler.can_handle(hi))
        resp = handler.handle(hi)

        self.mock_client.next.assert_called_once()
        self.assertEqual(resp.directives[0].audio_item.stream.token, 'radio_stream')

    def test_next_intent_auto_queues_at_end(self):
        self.mock_client.status.return_value = {'song': '4', 'playlistlength': '5'}

        with patch.object(skill, 'AUTO_QUEUE_RANDOM', True), \
             patch.object(skill, 'add_random_music_to_queue') as mock_add_random:
            handler = skill.NextOrPreviousIntentHandler()
            hi = create_handler_input("IntentRequest", "AMAZON.NextIntent")

            resp = handler.handle(hi)
            mock_add_random.assert_called_once()
            self.mock_client.next.assert_called_once()
            self.assertEqual(resp.directives[0].audio_item.stream.token, 'radio_stream')

    def test_previous_intent(self):
        handler = skill.NextOrPreviousIntentHandler()
        hi = create_handler_input("IntentRequest", "AMAZON.PreviousIntent")

        self.assertTrue(handler.can_handle(hi))
        resp = handler.handle(hi)

        self.mock_client.previous.assert_called_once()
        self.assertEqual(resp.directives[0].audio_item.stream.token, 'radio_stream')

    def test_next_command_issued(self):
        self.mock_client.status.return_value = {'song': '1', 'playlistlength': '5'}

        handler = skill.NextOrPreviousCommandHandler()
        hi = create_handler_input("PlaybackController.NextCommandIssued")

        self.assertTrue(handler.can_handle(hi))
        resp = handler.handle(hi)

        self.mock_client.next.assert_called_once()
        self.assertEqual(resp.directives[0].audio_item.stream.token, 'radio_stream')

    def test_cancel_or_stop_intent(self):
        for intent_name in ["AMAZON.StopIntent", "AMAZON.CancelIntent", "AMAZON.PauseIntent", "AMAZON.NavigateHomeIntent"]:
            self.mock_client.stop.reset_mock()
            handler = skill.CancelOrStopIntentHandler()
            hi = create_handler_input("IntentRequest", intent_name)

            self.assertTrue(handler.can_handle(hi))
            resp = handler.handle(hi)

            self.mock_client.stop.assert_called_once()
            self.assertIsInstance(resp.directives[0], StopDirective)

    def test_pause_command_issued(self):
        handler = skill.PauseCommandHandler()
        hi = create_handler_input("PlaybackController.PauseCommandIssued")

        self.assertTrue(handler.can_handle(hi))
        resp = handler.handle(hi)

        self.mock_client.pause.assert_called_with(1)
        self.assertIsInstance(resp.directives[0], StopDirective)

    def test_resume_intent(self):
        handler = skill.ResumeIntentHandler()
        hi = create_handler_input("IntentRequest", "AMAZON.ResumeIntent")

        self.assertTrue(handler.can_handle(hi))
        resp = handler.handle(hi)

        self.mock_client.play.assert_called_once()
        self.assertEqual(resp.directives[0].audio_item.stream.token, 'radio_stream')

    def test_start_over_intent(self):
        handler = skill.StartOverIntentHandler()
        hi = create_handler_input("IntentRequest", "AMAZON.StartOverIntent")

        self.assertTrue(handler.can_handle(hi))
        resp = handler.handle(hi)

        self.mock_client.seekcur.assert_called_with(0)
        self.assertEqual(resp.directives[0].audio_item.stream.token, 'radio_stream')

    def test_playback_nearly_finished(self):
        handler = skill.PlaybackNearlyFinishedHandler()
        hi = create_handler_input("AudioPlayer.PlaybackNearlyFinished")

        self.assertTrue(handler.can_handle(hi))
        resp = handler.handle(hi)
        self.assertIsNone(resp.directives)


class TestBottleRadioRoutes(unittest.TestCase):
    """Tests for the HTTP /radio streaming redirection route in Bottle."""

    def test_radio_unauthorized(self):
        with patch.object(skill, 'AUTH_TOKEN', 'secret_token'), \
             patch.object(skill, 'MPD_RADIO_URL', 'http://mpd:8000/'):

            skill.request.bind({'QUERY_STRING': ''})
            resp = skill.radio()
            self.assertEqual(skill.response.status_code, 403)

    def test_radio_authorized_redirect(self):
        with patch.object(skill, 'AUTH_TOKEN', 'secret_token'), \
             patch.object(skill, 'MPD_RADIO_URL', 'http://mpd:8000/'):

            skill.request.bind({'QUERY_STRING': 'token=secret_token'})
            try:
                resp = skill.radio()
            except Exception as e:
                # Bottle's redirect() raises HTTPResponse
                resp = e
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.headers.get('Location'), 'http://mpd:8000/')

    def test_radio_unconfigured_mpd_radio_url(self):
        with patch.object(skill, 'AUTH_TOKEN', None), \
             patch.object(skill, 'MPD_RADIO_URL', None):

            skill.request.bind({'QUERY_STRING': ''})
            resp = skill.radio()
            self.assertEqual(skill.response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
