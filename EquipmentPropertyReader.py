from deviceCommunicator import DeviceCommunicator
import json
import time

def handle_string_list(ipJson, opJson):
    if isinstance(ipJson, dict):
        updated_json = list()
        updated_json.append(ipJson)
    else:
        updated_json = ipJson

    for eachStr in updated_json:
        if "@name" in eachStr.keys():
            opJson[eachStr["@name"]] = eachStr["@val"]
        else:
            opJson["modelName"] = eachStr["@val"]

def handle_real_list(ipJson, opJson):
    if isinstance(ipJson, dict):
        updated_json = list()
        updated_json.append(ipJson)
    else:
        updated_json = ipJson
    for eachStr in updated_json:
        if isinstance(eachStr, dict):
            if "@name" in eachStr.keys():
                opJson[eachStr["@name"]] = float(eachStr["@val"])
        else:
            print("unknown type")


def handle_int_list(ipJson, opJson):
    if isinstance(ipJson, dict):
        updated_json = list()
        updated_json.append(ipJson)
    else:
        updated_json = ipJson
    for eachStr in updated_json:
        if isinstance(eachStr, dict):
            if "@name" in eachStr.keys():
                opJson[eachStr["@name"]] = int(eachStr["@val"])
        else:
            print("unknown type")

def update_config(data):
    print("received property update msg")
    try:
        json_data = json.loads(data.decode().replace("'", '"'))
        print(json_data)
        with open("adaptive_config.json", 'r') as read_config_file:
            logging_config = json.load(read_config_file)
            for each_mapping in json_data["message"]["mapping"]:
                if "enum" in each_mapping:
                    logging_config[json_data["message"]["equipment_type"]][json_data["message"]["equipment"]][each_mapping["targetKey"]]["enum"] = each_mapping["enum"]

            with open("adaptive_config.json", 'w', encoding='utf-8') as map_file:
                json.dump(logging_config, map_file, ensure_ascii=False, indent=4)
    except  Exception as x:
        print(x)
    pass

class PropertyReader():
    def __init__(self, mqtt_client):
        with open("device_map.json", 'r') as read_map_file:
            self.equipment_directory = json.load(read_map_file)
        self.device_communicator = DeviceCommunicator()
        self.mqtt_client = mqtt_client
        self.mqtt_client.subscribe_msg("/equipment/property/update", update_config)

    def property_value_parser(self,property_value, response_value):
        updated_value = dict()
        if "obj" not in property_value:
            updated_value["obj"] = property_value.copy()
        else:
            updated_value = property_value.copy()

        for each_key in updated_value["obj"]:
            if "str" == each_key:
                handle_string_list(updated_value["obj"][each_key], response_value)
            if "real" == each_key:
                handle_real_list(updated_value["obj"][each_key], response_value)
            if "int" == each_key:
                handle_int_list(updated_value["obj"][each_key], response_value)
        if "value" in response_value and response_value["value"] != 0:
            if '|' in response_value["name"]:
                equipment = response_value["name"].split('|')[1]
                property = response_value["name"].split('|')[0]
            else:
                equipment = "None"
                equipment = response_value["name"]
            # print(equipment, property, response_value["value"])

    def property_reader(self):
        with open("adaptive_config.json", 'r') as read_config_file:
            self.logging_config = json.load(read_config_file)
        for each_equipment_type in self.logging_config:
            if isinstance(self.logging_config[each_equipment_type], dict):
                for each_equipment in self.logging_config[each_equipment_type]:
                    packet_payload = dict()
                    for each_property in self.logging_config[each_equipment_type][each_equipment]:
                        sourceKey = self.logging_config[each_equipment_type][each_equipment][each_property]["sourceKey"]
                        if sourceKey in self.equipment_directory[each_equipment_type][each_equipment]:
                            property_value = self.device_communicator.requestRootDevice(self.equipment_directory[each_equipment_type][each_equipment][sourceKey]["hpath"])
                            response_value = dict()
                            if property_value:
                                self.property_value_parser(property_value, response_value)

                                if each_property not in packet_payload:
                                    packet_payload[each_property] = dict()

                                if "value" in response_value:
                                    if "enum" in self.logging_config[each_equipment_type][each_equipment][each_property]:
                                        packet_payload[each_property]["value"] = self.logging_config[each_equipment_type][each_equipment][each_property]["enum"][str(response_value.get("value", "NA"))]
                                    else:
                                        packet_payload[each_property]["value"] = response_value.get("value", "NA")

                                if "minimumValue" in response_value:
                                    packet_payload[each_property]["min"] = response_value.get("minimumValue", "NA")

                                if "maximumValue" in response_value:
                                    packet_payload[each_property]["max"] = response_value.get("maximumValue", "NA")

                    curr_clock = time.strftime("%H:%M:%S", time.localtime())
                    packet_payload["time"] = curr_clock
                    self.mqtt_client.publish_msg(each_equipment,packet_payload)


