from pythonping import ping
import requests
import xmltodict
from pythonping import ping
import unittest
import os
import json
import time


class Equipment(object):
    """docstring for Equipment"""

    def __init__(self, url):
        self.url = url

    def check_ip(self):
        get_ip = self.url[7:19]
        result = ping(get_ip, count=5)
        if result.success():
            return "online"
        else:
            return "offline"

    def check_url(self):
        url = self.url
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return 30
            else:
                return 404

        except Exception as e:
            print(f"An error occured: {str(e)}")

    def get_equipment_count(self):
        url = self.url + "equipment/installed/count"
        try:
            response = requests.get(url)
            response_text = response.text
            xml_todict = xmltodict.parse(response_text)
            # count_equipment_data = json.dumps(xml_todict, indent=4)
            count_equip = xml_todict["int"]["@val"]
            print(count_equip)
            return count_equip
        except Exception as e:
            print(f"An error occured: {str(e)}")

    def get_equipment_data(self):
        equipment_list = []
        url = self.url + "equipment/installed"
        try:
            response = requests.get(url)
            response_data = xmltodict.parse(response.text)
            for i in response_data['list']['ref']:
                equipment_list.append(i['@href'])
            print(equipment_list)
            return equipment_list
        except Exception as e:
            print(f"An error occured: {str(e)}")

    def check_attributes_present_get_data(self, response_data_url_dict):
        create_data = []
        if 'str' in response_data_url_dict['obj']:
            for i in response_data_url_dict['obj']['str']:
                if '@href' and '@val' in i:
                    create_data.append(i)
        if 'list' in response_data_url_dict['obj']:
            for i in response_data_url_dict['obj']['list']:
                if '@href' and '@val' in i:
                    create_data.append(i)
        if 'ref' in response_data_url_dict['obj']:
            for i in response_data_url_dict['obj']['ref']:
                if '@href' and '@val' in i:
                    create_data.append(i)
        if 'uri' in response_data_url_dict['obj']:
            for i in response_data_url_dict['obj']['uri']:
                if '@href' and '@val' in i:
                    create_data.append(i)

        if 'int' in response_data_url_dict['obj']:
            for i in response_data_url_dict['obj']['int']:
                if '@href' and '@val' in i:
                    create_data.append(i)

        if 'op' in response_data_url_dict['obj']:
            for i in response_data_url_dict['obj']['op']:
                if '@href' and '@val' in i:
                    create_data.append(i)

        if 'obj' in response_data_url_dict['obj']:
            for i in response_data_url_dict['obj']['obj']:
                if '@href' and '@val' in i:
                    create_data.append(i)

        if 'bool' in response_data_url_dict['obj']:
            for i in response_data_url_dict['obj']['bool']:
                if '@href' and '@val' in i:
                    create_data.append(i)

        if 'abstime' in response_data_url_dict['obj']:
            for i in response_data_url_dict['obj']['abstime']:
                if '@href' and '@val' in i:
                    create_data.append(i)

        else:
            print("no match")
        return create_data

    def get_specific_equipment_data(self, equipment_data):
        get_equipment_url = []
        data = []
        for i in equipment_data:
            get_equipment_url.append(self.url + i[6:])
        print(get_equipment_url)
        print("Getting equipment Data...")
        time.sleep(1)
        for i in get_equipment_url:
            get_equipment_response = requests.get(str(i))
            response_data_url_dict = xmltodict.parse(get_equipment_response.text)
            device_data = self.check_attributes_present_get_data(response_data_url_dict)
            device_data.pop()
            for j in device_data:
                if '@href' and '@val' in j:
                    j["equipment_name"] = str(i[35:])
                    data.append(j)
        return data
