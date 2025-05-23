# Referemce https://python-osc.readthedocs.io/en/latest/server.html#blocking-server

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc import udp_client
import os
import numpy as np
import queue
import sys
import time

# Set environment variable before importing sounddevice. Value is not important.
os.environ["SD_ENABLE_ASIO"] = "1"

import sounddevice as sd

""" Start of config block
The followoing part of code is to be configured as required
Don't mess with anything after the config section if you are just using this.
If you are not shure what device ID your audio hardware has or what sampling rate to use
set DEFAULT = True
"""

# Audio device config
DEFAULT = False
DEVICE = 2 # 3 for Focusrite
CHUNK: int = 3200
CHANNELS = [1, 2] # Focusrite 18i8 loopback Channels [11, 12]
SAMPEL_RATE: int = 44100

# Network and OSC config
REMOTE_OSC_IP: str = "10.10.0.110" # IP Adress of OSC server to send messages to
REMOTE_OSC_PORT: int = 11000
LOCAL_OSC_IP: str = "10.10.0.83"
LOCAL_OSC_PORT: int = 11001

# Scilence detection config
SCILENCE_DETECT_LEVEL: float = -50
SECONDS: int = 3 # This number reperesents the time in seconds
SCILENCE_DETECT_TIME: int = round(SAMPEL_RATE/CHUNK * SECONDS)
THRESHOLD: float = -50 # In DBFS

# Failover OSC acction config
OSC_ADRESS: str = "t/stop" # Enter OSC Adress to send message to
OSC_VALUE: str =  "1" # Enter the desired value for your osc action

""" End of config block
Don't mess with anything after the config section if you just want to use the program 'as is'.
"""

#TODO Build a nice function to set everythting to default for the sounddevice config
# if DEFAULT:
#     DEVICE = sd.default.device
#     SAMPEL_RATE = sd.query_devices(DEVICE, 'input')['default_samplerate']
#     CHANNELS = sd.default.channels

q = queue.Queue()

def send_osc_message() -> None:
    """Use this to configure the action to take when detecitng scilence"""
    osc_client = udp_client.SimpleUDPClient(address=REMOTE_OSC_IP, port=REMOTE_OSC_PORT) 
    print("Sending {} '{}' to {}:{}".format(OSC_ADRESS, OSC_VALUE, REMOTE_OSC_IP, REMOTE_OSC_PORT))
    osc_client.send_message(OSC_ADRESS, value=OSC_VALUE) # Send a OSC Message to some other hardware or module


def calculate_dbfs(data) -> float:
    rms = np.sqrt(np.mean(data ** 2))
    loudness_db = 20 * np.log10(rms)
    return loudness_db


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    # Put indata in the cue to be used in the detect_scilence function
    q.put(indata.copy())


def detect_scilence(args: list[str]) -> None:
    # Stors the last x dbfs values
    last_messurment: list = [] 
    threshold = THRESHOLD
    time = SCILENCE_DETECT_TIME 
    listen = True
    #TODO: add functionality to dect when playback is stopped manually
    while listen:
        frame = q.get()
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
                print(avarage, threshold)
                send_osc_message()
                listen = False


def handler(address: str, *args: list[str]):
    """This is an example function. 
    It detects the Reaper OSC message for toggle play and starts listening. 
    This needs to be adapted for other aplications
    map the OSC adress for the dispatcher according to your DAW or other OSC device.
    By default this script assumes, that it gets '/play 1' as its OSC start signal 

    addres: OSC adress like /play
    *args: OSC values 1 or 0
    """
    print("Recived {} {}".format(address, args))
    if args [-1] == 1:
        stream = sd.InputStream(samplerate=SAMPEL_RATE, channels=CHANNELS,
            blocksize=CHUNK, device=DEVICE, callback=callback)
        with stream:
            detect_scilence(args)
    else:
        return

dispatcher = Dispatcher()
dispatcher.map("/play", handler)

server = BlockingOSCUDPServer((LOCAL_OSC_IP, LOCAL_OSC_PORT), dispatcher)
server.serve_forever()  # Blocks forever