#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import json
import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

logger = logging.getLogger(__name__)

class VoiceCommandHandler(object):
    def __init__(self, device_name="", hostname="localhost", port=1883, username="test", password="test", keepalive=60):
        self.device_name = device_name
        self.device_location = self.device_name.split("_")[1]
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.keepalive = keepalive
        self.client = mqtt.Client()
        self.client.username_pw_set(self.username, self.password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.hostname, self.port, self.keepalive)
        self.client.loop_start()

    def on_message(self, client, userdata, msg):
        if "notification" in msg.topic:
            self.process_notification(str(msg.payload))
        elif "question" in msg.topic:
            self.process_question(str(msg.payload))

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe([("{}/notification".format(self.device_name), 2), 
                                ("{}/question".format(self.device_name), 2)])

    def process_voice_command(self, topic="voice/command", command=""):
        self.client.publish(topic, command)

    def process_notification(self, notification_json):
        text = json.loads(notification_json)["text"]
        self.squeeze_speak(text)

    def process_question(self, question_json):
        text = json.loads(question_json)["text"]
        self.squeeze_speak(text)
        time.sleep(5)

    def complete_silence(self, state):
        topic = "reproductores/silencio"
        if state != "ON" and state != "OFF": return
        publish.single(topic, state, hostname=self.hostname, auth={'username': self.username, 'password': self.password})

    def squeeze_speak(self, text):
        payload = json.dumps({"location": self.device_location, "text": text}, ensure_ascii=False, encoding="utf-8")
        topic = "squeeze/speak"
        publish.single(topic, payload, hostname=self.hostname, auth={'username': self.username, 'password':self.password})