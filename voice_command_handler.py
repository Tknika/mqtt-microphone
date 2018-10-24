#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import json
import time
import threading
import mqtt_handler
import tts_handler

logger = logging.getLogger(__name__)

class VoiceCommandHandler(object):
    def __init__(self, device_name=""):
        self.device_name = device_name
        self.device_location = self.device_name.split("_")[1]
        self.answer_topic = "mayordomo/{}/+".format(self.device_name)
        mqtt_handler.subscribe(self.answer_topic, self.__on_answer)

    def __on_answer(self, client, userdata, msg):
        if "notification" in msg.topic:
            self.process_notification(msg.payload.decode("UTF-8"))
        elif "question" in msg.topic:
            self.process_question(msg.payload.decode("UTF-8"))
        elif "notify" in msg.topic:
            self.__on_notify(msg.payload.decode("UTF-8"))

    def __on_notify(self, text):
        logger.debug("'{}' message received, say it loud".format(text))
        tts_handler.speak(text)

    def process_voice_command(self, topic="voice/command", command=""):
        mqtt_handler.publish(topic, command)

    def process_notification(self, notification_json):
        text = json.loads(notification_json)["text"]
        tts_handler.speak(text)

    def process_question(self, question_json):
        text = json.loads(question_json)["text"]
        tts_handler.speak(text)
        time.sleep(5)

    # def squeeze_speak(self, text):
    #     payload = json.dumps({"location": self.device_location, "text": text}, ensure_ascii=False, encoding="utf-8")
    #     topic = "squeeze/speak"
    #     threading.Thread(target=mqtt_handler.publish, args=[topic, payload]).start()