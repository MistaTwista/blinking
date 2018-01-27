# OSC Client

import argparse
import random
import time

from pythonosc import osc_message_builder
from pythonosc import udp_client


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1", help="OSC server IP")
    parser.add_argument("--port", type=int, default=5005, help="OSC server port")
    args = parser.parse_args()

    client = udp_client.SimpleUDPClient(args.ip, args.port)

    # for x in range(100):
    #     client.send_message("/filter", random.random())
    #     time.sleep(1)
    # 
    while True:
        client.send_message("/filter", random.random())
        time.sleep(1)