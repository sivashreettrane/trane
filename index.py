import requests
from equipmentBuilder import EvoxEquipmentBuilder
from deviceCommunicator import DeviceCommunicator
from EquipmentPropertyReader import PropertyReader
from mqtt_application import PubSub
from time import sleep

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

#device_ip = "10.28.2.61" # production board

device_ip = "10.28.249.77" # karthi dev

mqtt_client = PubSub().bootstrap_mqtt().start()

device_communicator = DeviceCommunicator()
device_communicator.set_device_ip(device_ip)

equipment_handler = EvoxEquipmentBuilder()
equipment_handler.build_equipments()


def href_remover(data):
    if isinstance(data,dict):
        data_copy = data.copy()
        for key,value in data_copy.items():
            if key =="@href":
                del data[key]
            else:
                data[key]=href_remover(value)
    elif isinstance(data,list):
        for i in range(len(data)):
            data[i]= href_remover(data[i])
    return data



mqtt_client.publish_msg("equipments", equipment_handler.get_equipment_list())
time.sleep(2)
#-------------------------------------------------------------------------
device_communicator.conn.close()
get_data = dict()
ip ="http://10.28.249.77/evox/"
trane_device = databuilder.Equipment(ip)

n = 1
while n > 0:
    try:
        if trane_device.check_ip() == "online":
            if trane_device.check_url() == 30:
                if int(trane_device.get_equipment_count()) > 0:
                    get_data = trane_device.get_specific_equipment_data(trane_device.get_equipment_data())
                    n = 0
                else:
                    print("NO equipment attached to device")
            else:
                print("Device throwing url error cannot access http web")
        else:
            print("device offline")

    except Exception as e:
        raise e

result_dict = dict()
result_dict = href_remover(get_data)
payload=json.dumps(result_dict,indent=4)
time.sleep(2)

mqtt_client.publish_msg("equipments_prop", result_dict)
print("published")

property_handler = PropertyReader(mqtt_client)
while True:
    property_handler.property_reader()
    sleep(3)

print("Done")

