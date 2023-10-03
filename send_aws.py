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


mqttc = mqtt.Client("iotconsole-fd413880-f440-4de6-ae44-e812364d7b91", protocol=mqtt.MQTTv5)
logger = logging.getLogger(__name__)
mqttc.enable_logger(logger)

#mqttc.on_message = on_message
#mqttc.on_subscribe = on_subscribe
mqttc.on_connect = on_connect

mqttc.tls_set(certs["cafile"],
              certfile=certs["certfile"],
              keyfile=certs["keyfile"],
              cert_reqs=ssl.CERT_REQUIRED,
              tls_version=ssl.PROTOCOL_TLSv1_2,
              ciphers=None)

def enter_ip(ip="http://10.28.249.11/evox/equipment"):
    return ip
def get_response(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            json_data = response.text
        else:
            print("Data not correct")

    except Exception as e:
        print(f"An error occured: {str(e)}")
    return json_data

def check_device_online(ip):
    ip="10.28.249.77"
    result = ping(ip,count=5)
    if result.success():
        print("Device is Online and Connected to VPN")
        print('\n')
    else:
        print("Device is Offline and Not Connected to VPN")
        print('\n')
        time.sleep(1)
        print("Please enter correct url")
        print('\n')
        #the code for entering url data

def check_installed_equipment():
    url = "http://10.28.249.77/evox/equipment/installed/count"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            count_equipment = response.text
            xml_todict = xmltodict.parse(count_equipment)
            count_equipment_data = json.dumps(xml_todict, indent=4)
            print(count_equipment_data)
            print('\n')
            count_equip = xml_todict["int"]["@val"]
            return count_equip
        else:
            print("Data not correct")
    except Exception as e:
        print(f"An error occured: {str(e)}")

def get_equipment_data():
    xml_dict = xmltodict.parse(get_response())
    data_dump = json.dumps(xml_dict, indent=4)
    time.sleep(1)
    return data_dump


enter_ip("http://10.28.249.77/evox/equipment")
print("Checking IP")
check_device_online("10.28.249.77")
time.sleep(1)
print('\n')
print("Checking device responding or not")
if get_response("http://10.28.249.77/evox/") == "":
    print("Data not found")
else:
    count_equipment = check_installed_equipment()
    if int(count_equipment) == 0:
        print("No device installed or found")
    else:
        print("{} equipment found/installed".format(count_equipment))
        pub_topic = "http/data"
        properties = Properties(PacketTypes.PUBLISH)

        command_parameters = {
            "user_profile_id": 10
            ,
            "request_id": "eb1bd30a-c7e6-42a4-9e00-d5baee89f65c"
        }
        properties.CorrelationData = json.dumps(command_parameters).encode('utf-8')
        properties.ResponseTopic = "http/status"
        mqttc.publish(pub_topic, get_equipment_data(), qos=0, properties=properties)
        mqttc.connect(args.endpoint, 8883)


mqttc.connect(args.endpoint, 8883)
mqttc.loop_forever()
