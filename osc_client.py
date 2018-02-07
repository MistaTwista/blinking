# OSC Client
from pythonosc import osc_message_builder
from pythonosc import udp_client

class OSCClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self._client = self.__client(ip, port)
    
    def __client(self, ip, port):
        return udp_client.SimpleUDPClient(ip, port)
    
    def send(self, channel, value):
        print("Send OSC to", channel, "with", value)
        return self._client.send_message(channel, value)

