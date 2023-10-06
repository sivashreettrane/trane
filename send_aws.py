# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from paho.mqtt.packettypes import PacketTypes
import ssl
import time
from paho.mqtt.properties import Properties
import paho.mqtt.client as mqtt
import logging
import json
import argparse
import requests
import xmltodict
from pythonping import ping
import unittest
import os
import databuilder

logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument('--endpoint', dest='endpoint', type=str, required=True, help='Obtain your Device data endpoint for your AWS Account')
parser.add_argument('--certificates-path', dest='certificates_path', default='certificates',
                    type=str, required=False, help='Modify the cert folder path if your certificates are in another folder')

args = parser.parse_args()

certs = {
    "cafile": args.certificates_path+"/AmazonRootCA1.pem",
    "certfile": args.certificates_path+"/client-cert.pem",
    "keyfile": args.certificates_path+"/private-key.pem",
}

def on_connect(mqttc, userdata, flags, reasonCode, properties=None):
    mqttc.subscribe('home07/main_door/#', qos=0)
get_data=[]
trane_device=databuilder.Equipment("http://10.28.249.77/evox/")
n=1
while n>0:
    try:
        if trane_device.check_ip() == "online":
            if trane_device.check_url() == 30:
                if int(trane_device.get_equipment_count())>0:
                    get_data=trane_device.get_specific_equipment_data(trane_device.get_equipment_data())
                    n=0
                else:
                    print("NO equipment attached to device")
            else:
                print("Device throwing url error cannot access http web")
        else:
            print("device offline")

    except Exception as e:
        raise e

mqttc = mqtt.Client("iotconsole-fd413880-f440-4de6-ae44-e812364d7b91", protocol=mqtt.MQTTv5)
logger = logging.getLogger(__name__)
mqttc.enable_logger(logger)

mqttc.on_connect = on_connect

mqttc.tls_set(certs["cafile"],
              certfile=certs["certfile"],
              keyfile=certs["keyfile"],
              cert_reqs=ssl.CERT_REQUIRED,
              tls_version=ssl.PROTOCOL_TLSv1_2,
              ciphers=None)
mqttc.connect(args.endpoint, 8883)


pub_topic = "http/data"
properties = Properties(PacketTypes.PUBLISH)
command_parameters = {
    "user_profile_id": 5
    ,
    "request_id": "eb1bd30a-c7e6-42a4-9e00-d5baee89f65c"
}
properties.CorrelationData = json.dumps(command_parameters).encode('utf-8')
properties.ResponseTopic = "http/status"

for i in get_data:
    payload=json.dumps(i,indent=4)
    mqttc.publish(pub_topic, payload, qos=0, properties=properties)
    time.sleep(1)
time.sleep(1)
mqttc.loop_forever()
