# -*- coding: utf-8 -*-

import datetime
from typing import Dict, Optional
from ask_sdk_model import Request, Response
from ask_sdk_model.ui import StandardCard, Image
from ask_sdk_model.interfaces.audioplayer import (
    PlayDirective, PlayBehavior, AudioItem, Stream, AudioItemMetadata,
    StopDirective, ClearQueueDirective, ClearBehavior)
from ask_sdk_model.interfaces import display
from ask_sdk_core.response_helper import ResponseFactory
from ask_sdk_core.handler_input import HandlerInput



def play(url, offset, text, card_data, response_builder):
    """Function to play audio.

    Using the function to begin playing audio when:
        - Play Audio Intent is invoked.
        - Resuming audio when stopped / paused.
        - Next / Previous commands issues.

    https://developer.amazon.com/docs/custom-skills/audioplayer-interface-reference.html#play
    REPLACE_ALL: Immediately begin playback of the specified stream,
    and replace current and enqueued streams.
    """
    # type: (str, int, str, Dict, ResponseFactory) -> Response
    if card_data:
        response_builder.set_card(
            StandardCard(
                title=card_data["title"], text=card_data["text"],
                image=Image(
                    small_image_url=card_data["small_image_url"],
                    large_image_url=card_data["large_image_url"])
            )
        )

    # Using URL as token as they are all unique
    response_builder.add_directive(
        PlayDirective(
            play_behavior=PlayBehavior.REPLACE_ALL,
            audio_item=AudioItem(
                stream=Stream(
                    token="radio_stream",  # Unique token for the stream not required
                    url=url,
                    offset_in_milliseconds=offset),
                metadata=None
            )
        )
    ).set_should_end_session(True)

    if text:
        response_builder.speak(text)

    return response_builder.response

def stop(text, response_builder):
    """Issue stop directive to stop the audio.

    Issuing AudioPlayer.Stop directive to stop the audio.
    Attributes already stored when AudioPlayer.Stopped request received.
    """
    # type: (str, ResponseFactory) -> Response
    response_builder.add_directive(StopDirective())
    if text:
        response_builder.speak(text)

    return response_builder.response

def clear(response_builder):
    """Clear the queue amd stop the player."""
    # type: (ResponseFactory) -> Response
    response_builder.add_directive(ClearQueueDirective(
        clear_behavior=ClearBehavior.CLEAR_ENQUEUED))
    return response_builder.response


def play_later(url, card_data, response_builder):
    """Function to play audio later (enqueue).
    
    Using the function to enqueue audio when:
        - PlaybackNearlyFinished request received.
    """
    # type: (str, Dict, ResponseFactory) -> Response
    if card_data:
        response_builder.set_card(
            StandardCard(
                title=card_data["title"], text=card_data["text"],
                image=Image(
                    small_image_url=card_data["small_image_url"],
                    large_image_url=card_data["large_image_url"])
            )
        )

    response_builder.add_directive(
        PlayDirective(
            play_behavior=PlayBehavior.ENQUEUE,
            audio_item=AudioItem(
                stream=Stream(
                    token=url,
                    url=url,
                    offset_in_milliseconds=0,
                    expected_previous_token=url),
                metadata=None
            )
        )
    ).set_should_end_session(True)

    return response_builder.response


def audio_data(request):
    """Extract audio data from request for card display."""
    # type: (Request) -> Dict
    return {
        "card": {
            "title": "Radio Stream",
            "text": "Streaming audio",
            "small_image_url": None,
            "large_image_url": None
        }
    }
