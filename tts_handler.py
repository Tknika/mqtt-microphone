#!/usr/bin/python

import json
import logging
import base64
import uuid
import audio_handler
import mqtt_handler

logger = logging.getLogger(__name__)

GET_AUDIO_TOPIC = "mayordomo/tts/get_audio"
LANGUAGE = "es-ES"
GENDER = "female"
VOLUME = 100

def speak(text="Hi", volume=100):
    payload = json.dumps( { "text": text, "volume": volume})
    __speak(payload)

def __speak(info):
    global VOLUME
    try:
        info_dict = json.loads(info)
        text = info_dict["text"]
        VOLUME = info_dict["volume"]
    except ValueError as e:
        logger.error("Error decoding __speak information: {}".format(e))
        return
    logger.debug("Let's say: '{}' with volume: {}".format(text, VOLUME))
    __get_audio(text)

def __get_audio(text=""):
    tmp_topic = "{}/{}".format(GET_AUDIO_TOPIC, str(uuid.uuid4()))
    payload = json.dumps({"topic": tmp_topic,
                          "audio_info": {"text": text, "language": LANGUAGE, "gender": GENDER}})
    mqtt_handler.subscribe(tmp_topic, __get_audio_response)
    mqtt_handler.publish(GET_AUDIO_TOPIC, payload, 1)

def __get_audio_response(_, __, msg):
    payload = json.loads(msg.payload.decode("UTF-8"))

    status = payload["status"]
    if status == 200:
        data = base64.b64decode(payload["data"])
        logger.debug("Audio message correctly received, let's play it")
        audio_handler.play_audio(data, VOLUME)
    mqtt_handler.unsubscribe(msg.topic)