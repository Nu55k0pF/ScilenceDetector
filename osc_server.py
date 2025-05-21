# Referemce https://python-osc.readthedocs.io/en/latest/server.html#blocking-server

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc import udp_client
import os
import numpy as np
import queue
import sys

# Set environment variable before importing sounddevice. Value is not important.
os.environ["SD_ENABLE_ASIO"] = "1"

import sounddevice as sd


# Make all your configurations here
CHUNK: int = 3200
CHANNELS = [11,12] # Focusrite 18i8 loopback Channels 11/12
SAMPLING_RATE: int = 44100
DEVICE = 20
OSC_SERVER_IP: str = "127.0.0.1" # IP Adress of OSC server to send messages to
OSC_SERVER_PORT: int = 8000
OSC_ADRESS: str = "t/stop" # Enter OSC Adress to send message to
OSC_VALUE: str =  "1" # Enter the desired value for your osc action
HOST_IP: str = "127.0.0.1"
HOST_PORT: int = 9000

q = queue.Queue()

def send_osc_message() -> None:
    """Use this to configure the action to take when detecitng scilence"""
    osc_client = udp_client.SimpleUDPClient(address=OSC_SERVER_IP, port=OSC_SERVER_PORT) 
    print("Sending {} '{}' to {}:{}".format(OSC_ADRESS, OSC_VALUE, OSC_SERVER_IP, OSC_SERVER_PORT))
    osc_client.send_message(OSC_ADRESS, value=OSC_VALUE) #Send a OSC Message to some other hardware or module


def calculate_dbfs(data) -> float:
    rms = np.sqrt(np.mean(data ** 2))
    loudness_db = 20 * np.log10(rms)
    return loudness_db


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    # put indata in the cue to be used in the detect_scilence function
    q.put(indata.copy())


def detect_scilence():
    # Initialize an arry to store data in
    frames = [] 
    # stors the last x dbfs values
    last_messurment = [] 
    threshold = -80
    # at 44.1 kHz and 3200 samples in the buffer you have about 14 chunks per second, so if you want a detection time of 2 seconds 30 is about the right value here. 3 sek ~ 42
    time = 40 
    listen = True
    while listen:
        frame = q.get()
        frames.append(frame)
        dbfs = calculate_dbfs(frame)

        if len(last_messurment) < time:
            last_messurment.append(dbfs)
            print(dbfs)
        else:
            last_messurment.pop(0)
            last_messurment.append(dbfs)
            
            avarage = sum(last_messurment)/len(last_messurment)
            if avarage > threshold:
                print(dbfs)
                continue
            else:
                print("Scilence Detected!!!!")
                listen = False


def handler(address: str, *args: list[str]):
    """This is an example function. 
    It detects the Reaper OSC message for toggle play and starts listening. 
    This needs to be adapted for other aplications
    """
    print("Recived {} {}".format(address, args))
    stream = sd.InputStream(samplerate=SAMPLING_RATE, channels=CHANNELS,
        blocksize=CHUNK, device=20, callback=callback)
    if args [-1] == 1:
        with stream:
            while True:
                detect_scilence()
                #TODO: Make it so it stops when detecting scilence!
    else:
        return


dispatcher = Dispatcher()
# dispatcher.map("/something/*", print_handler)
dispatcher.map("/play", handler)
# dispatcher.set_default_handler(reaper_handler)

server = BlockingOSCUDPServer( (HOST_IP, HOST_PORT), dispatcher)
server.serve_forever()  # Blocks forever