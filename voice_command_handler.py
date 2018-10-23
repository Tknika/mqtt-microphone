#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import json
import time
import threading
import paho.mqtt.publish as publish

logger = logging.getLogger(__name__)

class VoiceCommandHandler(object):
    def __init__(self, device_name="", mqtt_handler=None):
        self.device_name = device_name
        self.device_location = self.device_name.split("_")[1]
        self.mqtt_handler = mqtt_handler
        self.answer_topic = "{}/+".format(self.device_name)
        self.mqtt_handler.subscribe(self.answer_topic, self.__on_answer)

    def __on_answer(self, client, userdata, msg):
        if "notification" in msg.topic:
            self.process_notification(str(msg.payload))
        elif "question" in msg.topic:
            self.process_question(str(msg.payload))

    def process_voice_command(self, topic="voice/command", command=""):
        self.mqtt_handler.publish(topic, command)

    def process_notification(self, notification_json):
        text = json.loads(notification_json)["text"]
        self.squeeze_speak(text)

    def process_question(self, question_json):
        text = json.loads(question_json)["text"]
        self.squeeze_speak(text)
        time.sleep(5)

    def squeeze_speak(self, text):
        payload = json.dumps({"location": self.device_location, "text": text}, ensure_ascii=False, encoding="utf-8")
        topic = "squeeze/speak"
        threading.Thread(target=self.mqtt_handler.publish, args=[topic, payload]).start()