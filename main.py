#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os
import audio_handler
import tts_handler
import mqtt_handler
import google_stt_handler as stt_handler
from snowboy import snowboydecoder
from voice_command_handler import VoiceCommandHandler

# DEVICE_NAME: <name>_<location>
DEVICE_NAME = ""
MODEL_NAMES = []
MQTT_HOST = "localhost"
MQTT_USER = "test"
MQTT_PASSWORD = "test"

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


def speech_recognition():
    audio_handler.play_async_audio_file(os.path.join(current_dir, "audio_files/on.wav"))
    text = stt_handler.start()
    if text:
        payload = text
        logger.debug("Sending '{}' (MQTT)".format(payload))
        vch.process_voice_command(command=payload)
        audio_handler.play_async_audio_file(os.path.join(current_dir, "audio_files/ok.wav"))
    else:
        audio_handler.play_async_audio_file(os.path.join(current_dir, "audio_files/error.wav"))


if __name__ == "__main__":
    try:
        logger.info("Starting microphone service...")

        current_dir = os.path.dirname(os.path.abspath(__file__))

        models_path = [os.path.join(current_dir, "voice_models/{}".format(model_name)) for model_name in MODEL_NAMES]

        mqtt_handler.initialize(host=MQTT_HOST, username=MQTT_USER, password=MQTT_PASSWORD)

        vch = VoiceCommandHandler(device_name=DEVICE_NAME)

        detector = snowboydecoder.HotwordDetector(models_path, sensitivity=0.4)
        stt_handler.initialize()

        audio_handler.play_audio_file(os.path.join(current_dir, "audio_files/on.wav"))

        mqtt_handler.start()

        callbacks = [lambda: speech_recognition(),
                     lambda: speech_recognition()]        

        detector.start(detected_callback=speech_recognition, sleep_time=0.03)
        detector.terminate()
    except Exception as e:
        audio_handler.play_audio_file(os.path.join(current_dir, "audio_files/error.wav"))
        logger.exception("Unhandled exception: {0}".format(e))
