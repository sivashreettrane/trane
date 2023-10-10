from deviceCommunicator import DeviceCommunicator
import json
import time
from mqtt_application import PubSub

current_milli_time = lambda: round(time.time() * 1000)


class EvoxEquipmentBuilder():

    def __init__(self):
        self.device_communicator = DeviceCommunicator()
        self.equipment_json = dict()
        pass

    def get_equipment_list(self):
        return self.equipment_json

    def build_equipments(self):
        try:
            with open("device_map.json", 'r') as read_map_file:
                self.equipment_directory = json.load(read_map_file)
        except:
            start_time = current_milli_time()
            self.equipment_response = self.device_communicator.requestDevice("equipment")
            self.equipment_directory = dict()
            for response_equipment_type in self.equipment_response["obj"]["ref"]:
                response_equipment_type_list = self.device_communicator.requestDevice(   "equipment/" + response_equipment_type["@href"])
                if response_equipment_type["@name"] == 'userKeys':
                    self.equipment_directory[response_equipment_type["@name"]] = dict()
                    self.equipment_directory[response_equipment_type["@name"]]["hpath"] = response_equipment_type["@href"]
                    for each_key_map in response_equipment_type_list["list"]["obj"]:
                        for each_str_key in each_key_map["str"]:
                            if each_str_key["@name"] == "keyName":
                                keyName = each_str_key["@val"]
                            elif each_str_key["@name"] == "displayName":
                                displayName = each_str_key["@val"]
                        self.equipment_directory[response_equipment_type["@name"]][keyName] = displayName
                elif response_equipment_type["@name"] == 'unmapped':
                    pass
                elif response_equipment_type["@name"] == 'installed':
                    pass
                elif response_equipment_type["@name"] == 'keys':
                    self.equipment_directory[response_equipment_type["@name"]] = dict()
                    self.equipment_directory[response_equipment_type["@name"]]["hpath"] = response_equipment_type[
                        "@href"]
                    for each_key_map in response_equipment_type_list["list"]["obj"]:
                        for each_str_key in each_key_map["str"]:
                            if each_str_key["@name"] == "keyName":
                                keyName = each_str_key["@val"]
                            elif each_str_key["@name"] == "displayName":
                                displayName = each_str_key["@val"]
                        self.equipment_directory[response_equipment_type["@name"]][keyName] = displayName
                elif "list" in response_equipment_type_list and "ref" in response_equipment_type_list[
                    "list"] and isinstance(response_equipment_type_list["list"]["ref"], list):
                    self.equipment_directory[response_equipment_type["@name"]] = dict()
                    self.equipment_directory[response_equipment_type["@name"]]["hpath"] = response_equipment_type[
                        "@href"]
                    for response_equipment_in_type in response_equipment_type_list["list"]["ref"]:
                        self.equipment_directory[response_equipment_type["@name"]][
                            response_equipment_in_type["@href"]] = dict()
                        response_equipment_details = self.device_communicator.requestRootDevice(
                            response_equipment_in_type["@href"] + "/keymap")
                        for each_key_of_equipment in response_equipment_details["list"]["obj"]:
                            self.equipment_directory[response_equipment_type["@name"]][
                                response_equipment_in_type["@href"]][each_key_of_equipment["str"]["@val"]] = dict()
                            self.equipment_directory[response_equipment_type["@name"]][
                                response_equipment_in_type["@href"]][each_key_of_equipment["str"]["@val"]]["hpath"] = \
                                each_key_of_equipment["ref"]["@href"]
            print("Time to build equipment table frm evox read :", (current_milli_time() - start_time) / 1000)
            with open("device_map.json", 'w', encoding='utf-8') as map_file:
                json.dump(self.equipment_directory, map_file, ensure_ascii=False, indent=4)

        for each_equipment_type in self.equipment_directory:
            if each_equipment_type not in ["keys", "userKeys"]:
                if each_equipment_type not in self.equipment_json:
                    self.equipment_json[each_equipment_type] = list()
                for each_equipment in self.equipment_directory[each_equipment_type]:
                    if each_equipment != "hpath":
                        self.equipment_json[each_equipment_type].append(each_equipment)

        print("Done")
