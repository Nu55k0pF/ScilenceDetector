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


"""The followoing part of code is to be configured as required
Don't mess with anything after the config section if you are just using this.
If you are not shure what device ID your audio hardware has or what sampling rate to use
set DEFAULT = True
"""
# Audio device config
DEFAULT = False
CHUNK: int = 3200
CHANNELS = 1 # Focusrite 18i8 loopback Channels 11/12
SAMPEL_RATE: int = 44100
DEVICE = 3 # Enter 'None' here if you just want to use your default audio device 

if DEFAULT:
    DEVICE = sd.default.device
    SAMPEL_RATE = sd.query_devices(DEVICE, 'input')['default_samplerate']

# Network and OSC config
REMOTE_OSC_IP: str = "127.0.0.1" # IP Adress of OSC server to send messages to
REMOTE_OSC_PORT: int = 8000
LOCAL_OSC_IP: str = "127.0.0.1"
LOCAL_OSC_PORT: int = 9000

# Scilence detection config
SCILENCE_DETECT_LEVEL: float = -50
SECONDS: int = 3 # This number reperesents the time in seconds
SCILENCE_DETECT_TIME: int = round(SAMPEL_RATE/CHUNK * SECONDS)

# Failover OSC acction config
OSC_ADRESS: str = "t/stop" # Enter OSC Adress to send message to
OSC_VALUE: str =  "1" # Enter the desired value for your osc action

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


def detect_scilence():
    # Stors the last x dbfs values
    last_messurment = [] 
    threshold = -80
    # at 44.1 kHz and 3200 samples in the buffer you have about 14 chunks per second, so if you want a detection time of 2 seconds 30 is about the right value here. 3 sek ~ 42
    time = SCILENCE_DETECT_TIME 
    listen = True
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
                send_osc_message()
                listen = False


def handler(address: str, *args: list[str]):
    """This is an example function. 
    It detects the Reaper OSC message for toggle play and starts listening. 
    This needs to be adapted for other aplications
    map the OSC adress for the dispatcher according to your DAW or other OSC device

    addres: OSC adress like /play
    *args: OSC values 1 or 0
    """
    print("Recived {} {}".format(address, args))
    if args [-1] == 1:
        stream = sd.InputStream(samplerate=SAMPEL_RATE, channels=CHANNELS,
            blocksize=CHUNK, device=20, callback=callback)
        with stream:
            detect_scilence()
    else:
        return

print(SAMPEL_RATE, DEVICE)
dispatcher = Dispatcher()
dispatcher.map("/play", handler)

server = BlockingOSCUDPServer((LOCAL_OSC_IP, LOCAL_OSC_PORT), dispatcher)
server.serve_forever()  # Blocks forever