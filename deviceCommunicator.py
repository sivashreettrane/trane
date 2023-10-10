
import xmltodict
import http.client

class DeviceCommunicator():
    ip_address = str()
    url = str()
    def __init__(self):
        self.conn = None

    def set_device_ip(self, ip_address):
        DeviceCommunicator.ip_address = ip_address
        DeviceCommunicator.url = "http://{}/evox/".format(self.ip_address)
        self.conn = http.client.HTTPConnection(ip_address)
        print(self.conn)

    def requestDevice(self, path):
        get_response = None
        if self.conn is None:
            self.conn = http.client.HTTPConnection(DeviceCommunicator.ip_address)
        payload = ''
        headers = {}
        try:
            self.conn.request("GET", DeviceCommunicator.url+path, headers=headers, body=payload)
            get_response = self.conn.getresponse().read().decode('utf-8')
        except Exception as x:
            print("http request error : ", path, x)
        return(xmltodict.parse(get_response))

    def requestRootDevice(self, path):
        get_response = None
        json_response = dict()
        if self.conn is None:
            self.conn = http.client.HTTPConnection(DeviceCommunicator.ip_address)
        payload = ''
        headers = {}
        try:
            self.conn.request("GET", path, headers=headers, body=payload)
            get_response = self.conn.getresponse().read().decode('utf-8')
            json_response = xmltodict.parse(get_response)
        except Exception as x:
            print("http request error : ", path, x)
        return (json_response)
