import paho.mqtt.client as paho
import os
import socket
import ssl
from time import sleep
from random import uniform
import json
import logging

logging.basicConfig(level=logging.INFO)


class PubSub(object):

    def __init__(self, listener=True, topic="default"):
        self.connect = False
        self.listener = listener
        self.topic = topic
        self.logger = logging.getLogger(repr(self))
        self.subscribe_list = dict()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PubSub, cls).__new__(cls)
        return cls.instance

    def __on_connect(self, client, userdata, flags, rc):
        self.connect = True

        if self.listener:
            self.mqttc.subscribe(self.topic)

        self.logger.debug("{0}".format(rc))

    def __on_message(self, client, userdata, msg):
        self.logger.info("{0}, {1} - {2}".format(userdata, msg.topic, msg.payload))
        if msg.topic in self.subscribe_list:
            for each_subscription_client in self.subscribe_list[msg.topic]:
                each_subscription_client(msg.payload)

    def __on_log(self, client, userdata, level, buf):
        self.logger.debug("{0}, {1}, {2}, {3}".format(client, userdata, level, buf))

    def bootstrap_mqtt(self):

        self.mqttc = paho.Client()
        self.mqttc.on_connect = self.__on_connect
        self.mqttc.on_message = self.__on_message
        self.mqttc.on_log = self.__on_log

        awshost = "a2mkrgk5t6xnn8-ats.iot.us-east-1.amazonaws.com"
        awsport = 8883

        caPath = "AmazonRootCA1.pem"  # Root certificate authority, comes from AWS with a long, long name
        certPath = "e61a8e1a632ae1ab0022ecf9c08640cd828aa0c0a6b028ddb0dc09a200c4f87e-certificate.pem.crt"
        keyPath = "e61a8e1a632ae1ab0022ecf9c08640cd828aa0c0a6b028ddb0dc09a200c4f87e-private.pem.key"

        self.mqttc.tls_set(caPath,
                           certfile=certPath,
                           keyfile=keyPath,
                           cert_reqs=ssl.CERT_REQUIRED,
                           tls_version=ssl.PROTOCOL_TLSv1_2,
                           ciphers=None)

        result_of_connection = self.mqttc.connect(awshost, awsport, keepalive=1200)

        if result_of_connection == 0:
            self.connect = True

        return self

    def start(self):
        self.mqttc.loop_start()

        while True:
            sleep(2)
            if self.connect == True:
                self.logger.debug("Connected to connect.")
                return self
            else:
                self.logger.debug("Attempting to connect.")

    def subscribe_msg(self, topic, callback):
        if self.connect == True:
            if self.listener:
                self.mqttc.subscribe(topic)
                if topic not in self.subscribe_list:
                    self.subscribe_list[topic] = list()
                if callback not in self.subscribe_list[topic]:
                    self.subscribe_list[topic].append(callback)
        else:
            self.logger.debug("Attempting to connect.")

    def publish_msg(self, topic, payload):
        if self.connect == True:
            self.mqttc.publish(topic, json.dumps({"message": (payload)}), qos=1)
        else:
            self.logger.debug("Attempting to connect.")

    def isConnect(self):
        return self.connect


if __name__ == '__main__':
    PubSub(listener=True, topic="chat-evets").bootstrap_mqtt().start()