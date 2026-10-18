# -*- coding: utf-8 -*-
"""
Unit tests for the MPD Alexa Skill.
Tests authentication, audio file serving, MPD search helpers, queue management,
and Alexa Intent / AudioPlayer handlers.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Ensure test environment paths
sys.path.insert(0, os.path.dirname(__file__))

import lambda_function as skill
from alexa import util
from ask_sdk_model import (
    RequestEnvelope, Request, IntentRequest, Intent, Slot,
    Context, Device, SupportedInterfaces
)
from ask_sdk_model.interfaces.audioplayer import (
    AudioPlayerState, PlayerActivity, PlayDirective, PlayBehavior, StopDirective
)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.response_helper import ResponseFactory


def create_handler_input(request_type="IntentRequest", intent_name=None, slots=None, token=None, offset=0):
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
    elif request_type.startswith("AudioPlayer."):
        # AudioPlayer request
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

    device = Device(
        supported_interfaces=SupportedInterfaces(audio_player=audio_player)
    )

    context = Context(
        system=MagicMock(device=device),
        audio_player=audio_player
    )

    envelope = RequestEnvelope(request=req, context=context)
    return HandlerInput(request_envelope=envelope)


class TestMpdSkillConfigAndAuth(unittest.TestCase):
    """Tests for authentication and URL generation."""

    def test_get_song_url_with_auth_token(self):
        with patch.object(skill, 'BASE_URL', 'https://jukebox.example.com'), \
             patch.object(skill, 'AUTH_TOKEN', 'secret123'):
            song = {'id': '42', 'file': 'Queen/Bohemian Rhapsody.mp3'}
            url = skill.get_song_url(song)
            self.assertEqual(
                url,
                'https://jukebox.example.com/song/42/Bohemian%20Rhapsody.mp3?token=secret123'
            )

    def test_get_song_url_without_auth_token(self):
        with patch.object(skill, 'BASE_URL', 'https://jukebox.example.com'), \
             patch.object(skill, 'AUTH_TOKEN', None):
            song = {'id': '42', 'file': 'Queen/Bohemian Rhapsody.flac'}
            url = skill.get_song_url(song)
            self.assertEqual(
                url,
                'https://jukebox.example.com/song/42/Bohemian%20Rhapsody.flac'
            )

    def test_check_auth_query_token(self):
        with patch.object(skill, 'AUTH_TOKEN', 'mytoken'):
            skill.request.bind({'QUERY_STRING': 'token=mytoken'})
            self.assertTrue(skill.check_auth())

            skill.request.bind({'QUERY_STRING': 'token=wrong'})
            self.assertFalse(skill.check_auth())

            skill.request.bind({'QUERY_STRING': ''})
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

    def test_check_auth_disabled_when_token_none(self):
        with patch.object(skill, 'AUTH_TOKEN', None):
            self.assertTrue(skill.check_auth())


class TestMpdQueueHelpers(unittest.TestCase):
    """Tests for MPD navigation and search helpers."""

    def test_find_song_in_playlist(self):
        playlist = [
            {'id': '1', 'title': 'Song 1'},
            {'id': '2', 'title': 'Song 2'},
            {'id': '3', 'title': 'Song 3'}
        ]
        idx, song = skill.find_song_in_playlist(playlist, '2')
        self.assertEqual(idx, 1)
        self.assertEqual(song['title'], 'Song 2')

        idx, song = skill.find_song_in_playlist(playlist, '99')
        self.assertIsNone(idx)
        self.assertIsNone(song)

    @patch.object(skill, 'client')
    @patch.object(skill, 'connection')
    def test_get_next_song(self, mock_conn, mock_client):
        mock_conn.return_value.__enter__.return_value = None
        mock_client.playlistinfo.return_value = [
            {'id': '1', 'title': 'Song 1'},
            {'id': '2', 'title': 'Song 2'}
        ]
        next_song = skill.get_next_song('1')
        self.assertIsNotNone(next_song)
        self.assertEqual(next_song['id'], '2')

        # At end of playlist with repeat off -> None
        mock_client.status.return_value = {'repeat': '0'}
        end_song = skill.get_next_song('2')
        self.assertIsNone(end_song)

        # At end of playlist with repeat on -> returns first
        mock_client.status.return_value = {'repeat': '1'}
        loop_song = skill.get_next_song('2')
        self.assertEqual(loop_song['id'], '1')

    @patch.object(skill, 'client')
    @patch.object(skill, 'connection')
    def test_search_tracks(self, mock_conn, mock_client):
        mock_conn.return_value.__enter__.return_value = None
        mock_client.search.return_value = [{'id': '10', 'title': 'Hysteria', 'artist': 'Muse', 'file': 'Muse/Hysteria.flac'}]

        res = skill.search_tracks(title="Hysteria", artist="Muse")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['title'], 'Hysteria')


class TestAlexaHandlers(unittest.TestCase):
    """Tests for Alexa skill intent handlers."""

    def setUp(self):
        self.patch_mode = patch.object(skill, 'STREAM_MODE', 'tracks')
        self.patch_base = patch.object(skill, 'BASE_URL', 'https://jukebox.example.com')
        self.patch_auth = patch.object(skill, 'AUTH_TOKEN', 'token123')
        self.patch_conn = patch.object(skill, 'connection')
        self.patch_client = patch.object(skill, 'client')

        self.patch_mode.start()
        self.patch_base.start()
        self.patch_auth.start()
        self.mock_conn = self.patch_conn.start()
        self.mock_client = self.patch_client.start()
        self.mock_conn.return_value.__enter__.return_value = None

    def tearDown(self):
        self.patch_mode.stop()
        self.patch_base.stop()
        self.patch_auth.stop()
        self.patch_conn.stop()
        self.patch_client.stop()

    def test_launch_handler_plays_first_track(self):
        self.mock_client.currentsong.return_value = {'id': '1', 'title': 'First Song', 'artist': 'Artist A', 'file': 'A/First.mp3'}
        handler = skill.LaunchRequestOrPlayAudioHandler()
        hi = create_handler_input("LaunchRequest")

        self.assertTrue(handler.can_handle(hi))
        resp = handler.handle(hi)

        self.assertIsNotNone(resp.directives)
        self.assertIsInstance(resp.directives[0], PlayDirective)
        self.assertEqual(resp.directives[0].play_behavior, PlayBehavior.REPLACE_ALL)
        self.assertEqual(resp.directives[0].audio_item.stream.token, '1')
        self.assertIn('token=token123', resp.directives[0].audio_item.stream.url)

    def test_launch_handler_empty_queue(self):
        self.mock_client.currentsong.return_value = {}
        self.mock_client.playlistinfo.return_value = []
        handler = skill.LaunchRequestOrPlayAudioHandler()
        hi = create_handler_input("LaunchRequest")

        resp = handler.handle(hi)
        self.assertIn("Wiedergabeliste ist leer", resp.output_speech.ssml)

    def test_queue_song_intent(self):
        self.mock_client.search.return_value = [{'title': 'Starlight', 'artist': 'Muse', 'file': 'Muse/Starlight.flac'}]
        # Existing playlist has 1 song
        self.mock_client.playlistinfo.side_effect = [
            [{'id': '1', 'title': 'Song 1'}],  # before
            [{'id': '1', 'title': 'Song 1'}, {'id': '2', 'title': 'Starlight', 'file': 'Muse/Starlight.flac'}]  # after
        ]

        handler = skill.QueueSongHandler()
        hi = create_handler_input("IntentRequest", "QueueSongIntent", {"Song": "Starlight", "Artist": "Muse"})

        self.assertTrue(handler.can_handle(hi))
        resp = handler.handle(hi)

        self.mock_client.add.assert_called_with('Muse/Starlight.flac')
        self.assertIn("hinzugefügt", resp.output_speech.ssml)
        # Should NOT interrupt current playback with a play directive
        self.assertIsNone(resp.directives)

    def test_play_song_intent(self):
        self.mock_client.search.return_value = [{'title': 'Animals', 'artist': 'Pink Floyd', 'file': 'PF/Animals.mp3'}]
        self.mock_client.addid.return_value = '99'
        self.mock_client.playlistid.return_value = [{'id': '99', 'title': 'Animals', 'artist': 'Pink Floyd', 'file': 'PF/Animals.mp3'}]

        handler = skill.PlaySongHandler()
        hi = create_handler_input("IntentRequest", "PlaySongIntent", {"Song": "Animals"})

        self.assertTrue(handler.can_handle(hi))
        resp = handler.handle(hi)

        self.mock_client.addid.assert_called_with('PF/Animals.mp3')
        self.assertEqual(len(resp.directives), 1)
        self.assertEqual(resp.directives[0].audio_item.stream.token, '99')

    def test_play_album_intent(self):
        self.mock_client.search.return_value = [
            {'title': 'Track 1', 'file': 'Album/01.mp3'},
            {'title': 'Track 2', 'file': 'Album/02.mp3'}
        ]
        self.mock_client.playlistinfo.return_value = [
            {'id': '101', 'title': 'Track 1', 'file': 'Album/01.mp3'},
            {'id': '102', 'title': 'Track 2', 'file': 'Album/02.mp3'}
        ]

        handler = skill.PlayAlbumHandler()
        hi = create_handler_input("IntentRequest", "PlayAlbumIntent", {"Album": "Dark Side"})

        self.assertTrue(handler.can_handle(hi))
        resp = handler.handle(hi)

        self.mock_client.clear.assert_called_once()
        self.assertEqual(self.mock_client.add.call_count, 2)
        self.assertEqual(resp.directives[0].audio_item.stream.token, '101')

    def test_clear_queue_intent(self):
        handler = skill.ClearQueueHandler()
        hi = create_handler_input("IntentRequest", "ClearQueueIntent")

        self.assertTrue(handler.can_handle(hi))
        resp = handler.handle(hi)

        self.mock_client.clear.assert_called_once()
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

    def test_playback_nearly_finished_enqueues_next_song(self):
        self.mock_client.playlistinfo.return_value = [
            {'id': '1', 'title': 'Song 1'},
            {'id': '2', 'title': 'Song 2', 'artist': 'Artist', 'file': 'Song2.mp3'}
        ]
        self.mock_client.currentsong.return_value = {'id': '1'}

        handler = skill.PlaybackNearlyFinishedHandler()
        hi = create_handler_input("AudioPlayer.PlaybackNearlyFinished", token="1")

        self.assertTrue(handler.can_handle(hi))
        resp = handler.handle(hi)

        self.assertEqual(len(resp.directives), 1)
        self.assertEqual(resp.directives[0].play_behavior, PlayBehavior.ENQUEUE)
        self.assertEqual(resp.directives[0].audio_item.stream.token, '2')
        self.assertEqual(resp.directives[0].audio_item.stream.expected_previous_token, '1')

    def test_playback_started_syncs_mpd_seekid(self):
        handler = skill.PlaybackStartedHandler()
        hi = create_handler_input("AudioPlayer.PlaybackStarted", token="42")

        self.assertTrue(handler.can_handle(hi))
        handler.handle(hi)

        self.mock_client.seekid.assert_called_with(42, 0)

    def test_next_intent(self):
        self.mock_client.playlistinfo.return_value = [
            {'id': '1', 'title': 'Song 1'},
            {'id': '2', 'title': 'Song 2', 'artist': 'Artist', 'file': 'Song2.mp3'}
        ]

        handler = skill.NextOrPreviousIntentHandler()
        hi = create_handler_input("IntentRequest", "AMAZON.NextIntent", token="1")

        self.assertTrue(handler.can_handle(hi))
        resp = handler.handle(hi)

        self.assertEqual(resp.directives[0].audio_item.stream.token, '2')


class TestBottleAudioServing(unittest.TestCase):
    """Tests for the HTTP audio serving route in Bottle."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.music_dir = self.temp_dir.name
        self.test_file = os.path.join(self.music_dir, "test.mp3")
        with open(self.test_file, "wb") as f:
            f.write(b"AUDIO_DATA_TEST_1234567890")

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch.object(skill, 'client')
    @patch.object(skill, 'connection')
    def test_serve_song_with_auth(self, mock_conn, mock_client):
        mock_conn.return_value.__enter__.return_value = None
        mock_client.playlistid.return_value = [{'id': '10', 'file': 'test.mp3'}]

        with patch.object(skill, 'MUSIC_DIR', self.music_dir), \
             patch.object(skill, 'AUTH_TOKEN', 'secret_token'):

            # Test 1: Access without token -> 403
            skill.request.bind({'QUERY_STRING': ''})
            resp = skill.serve_song(10, 'test.mp3')
            self.assertEqual(skill.response.status_code, 403)

            # Test 2: Access with wrong token -> 403
            skill.request.bind({'QUERY_STRING': 'token=wrong'})
            resp = skill.serve_song(10, 'test.mp3')
            self.assertEqual(skill.response.status_code, 403)

            # Test 3: Access with correct token -> 200 / file response
            skill.request.bind({'QUERY_STRING': 'token=secret_token'})
            resp = skill.serve_song(10, 'test.mp3')
            # Bottle static_file returns a HTTPResponse
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.content_type, 'audio/mpeg')


if __name__ == '__main__':
    unittest.main()
