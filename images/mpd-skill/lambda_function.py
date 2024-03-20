# -*- coding: utf-8 -*-
import os, sys
import time

import logging

import json

from ask_sdk_webservice_support.webservice_handler import WebserviceSkillHandler
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from alexa import util

sb = SkillBuilder()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

from contextlib import contextmanager
from mpd import MPDClient

client = MPDClient()

RADIO_URL = os.getenv("RADIO_URL")
MPD_RADIO_URL = os.getenv("MPD_RADIO_URL")
MPD_HOST = os.getenv("MPD_HOST")
MPD_PORT = int(os.getenv("MPD_PORT"))


@contextmanager
def connection():
    try:
        client.connect(MPD_HOST, MPD_PORT)
        yield
    finally:
        client.close()
        client.disconnect()

# ######################### INTENT HANDLERS #########################
# This section contains handlers for the built-in intents and generic
# request handlers like launch, session end, skill events etc.

class CheckAudioInterfaceHandler(AbstractRequestHandler):
    """Check if device supports audio play.

    This can be used as the first handler to be checked, before invoking
    other handlers, thus making the skill respond to unsupported devices
    without doing much processing.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        if handler_input.request_envelope.context.system.device:
            # Since skill events won't have device information
            return handler_input.request_envelope.context.system.device.supported_interfaces.audio_player is None
        else:
            return False

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CheckAudioInterfaceHandler")
        handler_input.response_builder.speak("Sorry, this skill is not supported on this device").set_should_end_session(True)
        return handler_input.response_builder.response


class SkillEventHandler(AbstractRequestHandler):
    """Close session for skill events or when session ends.

    Handler to handle session end or skill events (SkillEnabled,
    SkillDisabled etc.)
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (handler_input.request_envelope.request.object_type.startswith(
            "AlexaSkillEvent") or
                is_request_type("SessionEndedRequest")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SkillEventHandler")
        return handler_input.response_builder.response


class LaunchRequestOrPlayAudioHandler(AbstractRequestHandler):
    """Launch radio for skill launch or PlayAudio intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_request_type("LaunchRequest")(handler_input) or
                is_intent_name("PlayAudio")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LaunchRequestOrPlayAudioHandler")

        song = None
        with connection():    
            client.play()
            time.sleep(1)

            song = client.currentsong()
        
        if not song:
           handler_input.response_builder.speak("Die Wiedergabeliste ist leer.").set_should_end_session(True)
           return handler_input.response_builder.response
        else:
            speech = f"Spiele das Lied {song['title']} von {song['artist']}"
            logger.info("speak: %s", speech)

            return util.play(url=RADIO_URL,
                            offset=0,
                            text="ok",
                            card_data=None,
                            response_builder=handler_input.response_builder)


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for providing help information to user."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")

        speech = "Dies ist ein MPD Player"
        try:
            with connection():
                song = client.currentsong()
                speech = f"Spiele das Lied {song['title']} von {song['artist']}"
                logger.info("speak: %s", speech)
        except Exception:
            pass

        handler_input.response_builder.speak(speech).set_should_end_session(False)
        return handler_input.response_builder.response


class UnhandledIntentHandler(AbstractRequestHandler):
    """Handler for fallback intent, for unmatched utterances.

    2018-July-12: AMAZON.FallbackIntent is currently available in all
    English locales. This handler will not be triggered except in that
    locale, so it can be safely deployed for any locale. More info
    on the fallback intent can be found here:
    https://developer.amazon.com/docs/custom-skills/standard-built-in-intents.html#fallback
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In UnhandledIntentHandler")
        handler_input.response_builder.speak("Entschuldigung das habe ich nicht verstanden").set_should_end_session(True)
        return handler_input.response_builder.response


class NextOrPreviousIntentHandler(AbstractRequestHandler):
    """Handler for next or previous intents."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.NextIntent")(handler_input) or
                is_intent_name("AMAZON.PreviousIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In NextOrPreviousIntentHandler")

        with connection():
            try:
                if is_intent_name("AMAZON.NextIntent")(handler_input):
                    client.next()
                else:
                    client.previous()
            except Exception as e:
                logger.error("error executing", e)
                client.play()
        
            time.sleep(0.1)

            song = client.currentsong()
            speech = f"Spiele das Lied {song['title']} von {song['artist']}"
            logger.info("speak: %s", speech)

            handler_input.response_builder.speak(speech=speech).set_should_end_session(True)
        
        return handler_input.response_builder.response

        #return util.play(
        #    url=RADIO_URL, offset=0,
        #    text=speech, card_data=None,
        #    response_builder=handler_input.response_builder)


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Handler for cancel, stop or pause intents."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input) or
                is_intent_name("AMAZON.PauseIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CancelOrStopIntentHandler")

        with connection():
            try:
                client.stop()
            except Exception:
                pass
        
        return util.stop("Auf Wiedersehen!", handler_input.response_builder)


class ResumeIntentHandler(AbstractRequestHandler):
    """Handler for resume intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.ResumeIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ResumeIntentHandler")

        with connection():
            song = client.currentsong()
            speech = f"Spiele das Lied {song['title']} von {song['artist']}"
            logger.info("speak: %s", speech)
        return util.play(
            url=RADIO_URL, offset=0,
            text=speech, card_data=None,
            response_builder=handler_input.response_builder)


class StartOverIntentHandler(AbstractRequestHandler):
    """Handler for start over, loop on/off, shuffle on/off intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.StartOverIntent")(handler_input) or
                is_intent_name("AMAZON.LoopOnIntent")(handler_input) or
                is_intent_name("AMAZON.LoopOffIntent")(handler_input) or
                is_intent_name("AMAZON.ShuffleOnIntent")(handler_input) or
                is_intent_name("AMAZON.ShuffleOffIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In StartOverIntentHandler")

        speech = "This is radio, you can not do that.  You can ask me to stop or pause to stop listening."
        return handler_input.response_builder.speak(speech).response

# ###################################################################

# ########## AUDIOPLAYER INTERFACE HANDLERS #########################
# This section contains handlers related to Audioplayer interface

class PlaybackStartedHandler(AbstractRequestHandler):
    """AudioPlayer.PlaybackStarted Directive received.

    Confirming that the requested audio file began playing.
    Do not send any specific response.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("AudioPlayer.PlaybackStarted")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PlaybackStartedHandler")
        logger.info("Playback started")
        return handler_input.response_builder.response

class PlaybackFinishedHandler(AbstractRequestHandler):
    """AudioPlayer.PlaybackFinished Directive received.

    Confirming that the requested audio file completed playing.
    Do not send any specific response.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("AudioPlayer.PlaybackFinished")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PlaybackFinishedHandler")
        logger.info("Playback finished")
        return handler_input.response_builder.response


class PlaybackStoppedHandler(AbstractRequestHandler):
    """AudioPlayer.PlaybackStopped Directive received.

    Confirming that the requested audio file stopped playing.
    Do not send any specific response.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("AudioPlayer.PlaybackStopped")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PlaybackStoppedHandler")
        logger.info("Playback stopped")
        return handler_input.response_builder.response


class PlaybackNearlyFinishedHandler(AbstractRequestHandler):
    """AudioPlayer.PlaybackNearlyFinished Directive received.

    Replacing queue with the URL again. This should not happen on live streams.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("AudioPlayer.PlaybackNearlyFinished")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PlaybackNearlyFinishedHandler")
        logger.info("Playback nearly finished")
        request = handler_input.request_envelope.request
        return util.play_later(
            url=RADIO_URL,
            card_data=util.audio_data(request)["card"],
            response_builder=handler_input.response_builder)


class PlaybackFailedHandler(AbstractRequestHandler):
    """AudioPlayer.PlaybackFailed Directive received.

    Logging the error and restarting playing with no output speech and card.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("AudioPlayer.PlaybackFailed")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PlaybackFailedHandler")
        request = handler_input.request_envelope.request
        logger.info("Playback failed: {}".format(request.error))
        return util.play(
            url=RADIO_URL, offset=0, text=None,
            card_data=None,
            response_builder=handler_input.response_builder)


class ExceptionEncounteredHandler(AbstractRequestHandler):
    """Handler to handle exceptions from responses sent by AudioPlayer
    request.
    """
    def can_handle(self, handler_input):
        # type; (HandlerInput) -> bool
        return is_request_type("System.ExceptionEncountered")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("\n**************** EXCEPTION *******************")
        logger.info(handler_input.request_envelope)
        return handler_input.response_builder.response

# ###################################################################

# ########## PLAYBACK CONTROLLER INTERFACE HANDLERS #################
# This section contains handlers related to Playback Controller interface
# https://developer.amazon.com/docs/custom-skills/playback-controller-interface-reference.html#requests

class PlayCommandHandler(AbstractRequestHandler):
    """Handler for Play command from hardware buttons or touch control.

    This handler handles the play command sent through hardware buttons such
    as remote control or the play control from Alexa-devices with a screen.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type(
            "PlaybackController.PlayCommandIssued")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PlayCommandHandler")

        return util.play(url=RADIO_URL,
                         offset=0,
                         text="ok",
                         card_data=None,
                         response_builder=handler_input.response_builder)


class NextOrPreviousCommandHandler(AbstractRequestHandler):
    """Handler for Next or Previous command from hardware buttons or touch
    control.

    This handler handles the next/previous command sent through hardware
    buttons such as remote control or the next/previous control from
    Alexa-devices with a screen.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_request_type(
            "PlaybackController.NextCommandIssued")(handler_input) or
                is_request_type(
                    "PlaybackController.PreviousCommandIssued")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In NextOrPreviousCommandHandler")
        return handler_input.response_builder.response


class PauseCommandHandler(AbstractRequestHandler):
    """Handler for Pause command from hardware buttons or touch control.

    This handler handles the pause command sent through hardware
    buttons such as remote control or the pause control from
    Alexa-devices with a screen.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("PlaybackController.PauseCommandIssued")(
            handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PauseCommandHandler")
        return util.stop(text=None,
                         response_builder=handler_input.response_builder)

# ###################################################################

# ###################################################################

# ############# REQUEST / RESPONSE INTERCEPTORS #####################
class RequestLogger(AbstractRequestInterceptor):
    """Log the alexa requests."""
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the alexa responses."""
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.debug("Alexa Response: {}".format(response))

# ###################################################################


# ############# REGISTER HANDLERS #####################
# Request Handlers
sb.add_request_handler(CheckAudioInterfaceHandler())
sb.add_request_handler(SkillEventHandler())
sb.add_request_handler(LaunchRequestOrPlayAudioHandler())
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

# Exception handlers
#sb.add_exception_handler(CatchAllExceptionHandler())

# Interceptors
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

# AWS Lambda handler
webservice_handler = WebserviceSkillHandler(skill=sb.create())

#####################################################################
#####################################################################
# Webserver
#####################################################################
from bottle import route, run, template, request, response, redirect

def pretty_print_json(json_data):
    logger.debug(json.dumps(json.loads(json_data), indent=2))

@route('/radio', method=["GET"])
def radio():
    return redirect(MPD_RADIO_URL, 302)

@route('/alexa', method=['POST'])
def index():
    body = request.body.read().decode()
    headers = request.headers
    logger.info(headers)
    pretty_print_json(body)
    return webservice_handler.verify_request_and_dispatch(headers, body)

run(host='0.0.0.0', port=8844)