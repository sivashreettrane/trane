


import xmltodict

class EvoxReadPath():

    def __init__(self):
        pass

    def readPath(self, path):
        # for each_ai_ref in ai_list["obj"]["list"]["ref"]:
        #     point_url = url + "/" + each_ai_ref['@href']
        #     point_response = requests.request("GET", point_url, headers=headers, data=payload)
        #     ai_point_value = xmltodict.parse(point_response.text)
        #     ai_values[each_ai_ref['@href']] = dict()
        #     for each_key in ai_point_value["obj"]:
        #         if "str" == each_key:
        #             __handle_string_list(ai_point_value["obj"][each_key], ai_values[each_ai_ref['@href']])
        #         if "real" == each_key:
        #             __handle_real_list(ai_point_value["obj"][each_key], ai_values[each_ai_ref['@href']])
        #         if "int" == each_key:
        #             __handle_int_list(ai_point_value["obj"][each_key], ai_values[each_ai_ref['@href']])
        #     if ai_values[each_ai_ref['@href']]["value"] != 0:
        #         if '|' in ai_values[each_ai_ref['@href']]["name"]:
        #             equipment = ai_values[each_ai_ref['@href']]["name"].split('|')[1]
        #             property = ai_values[each_ai_ref['@href']]["name"].split('|')[0]
        #         else:
        #             equipment = "None"
        #             equipment = ai_values[each_ai_ref['@href']]["name"]
        #         print(equipment, property, ai_values[each_ai_ref['@href']]["value"])
        pass