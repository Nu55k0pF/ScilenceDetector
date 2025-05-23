# Referemce https://python-osc.readthedocs.io/en/latest/server.html#blocking-server

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc import udp_client
import os
import numpy as np
import queue
import sys
import threading
import time

# Set environment variable before importing sounddevice. Value is not important.
# This is needed to enable ASIO support
os.environ["SD_ENABLE_ASIO"] = "1"

import sounddevice as sd

""" Start of config block
The followoing part of code is to be configured as required
Don't mess with anything after the config section if you are just using this.
If you are not shure what device ID your audio hardware has or what sampling rate to use
set DEFAULT = True
"""

# Audio device config
DEFAULT: bool = True
DEVICE: int = 3 # 3 for Focusrite
CHUNK: int = 3200
CHANNELS = [11, 12] # Focusrite 18i8 loopback Channels [11, 12]
SAMPEL_RATE: int = 44100

# Network and OSC config
REMOTE_OSC_IP: str = "10.10.0.83" # IP Adress of OSC server to send messages to
REMOTE_OSC_PORT: int = 11000
LOCAL_OSC_IP: str = "10.10.0.83"
LOCAL_OSC_PORT: int = 11001

# Scilence detection config
SECONDS: int = 3 # This number reperesents the time in seconds
SCILENCE_DETECT_TIME: int = round(SAMPEL_RATE/CHUNK * SECONDS)
THRESHOLD: float = -40 # In DBFS

# Failover OSC acction config
OSC_ADRESS: str = "/track/1/mute/toggle" # Enter OSC Adress to send message to
OSC_VALUE: str =  "1" # Enter the desired value for your osc action

""" End of config block
Don't mess with anything after the config section if you just want to use the program 'as is'.
"""

# Set the default audio device and samplerate if DEFAULT is True
def set_audio_defaults():
    """Sets some default values for audio device configuration."""
    global DEVICE, SAMPEL_RATE, CHANNELS

    default_input = sd.default.device[0]
    if default_input is None or default_input < 0:
        default_input = sd.query_devices(kind='input')['index']

    DEVICE = default_input
    SAMPEL_RATE = int(sd.query_devices(DEVICE, 'input')['default_samplerate'])
    CHANNELS = sd.query_devices(DEVICE, 'input')['max_input_channels']

if DEFAULT:
    set_audio_defaults()

# Start of the function defenitions
q = queue.Queue()
stop_event = threading.Event()
detection_thread = None  # Globaler Thread-Handle


def send_osc_message() -> None:
    """Creats a udp client and sends a OSC message and prints it to console."""
    osc_client = udp_client.SimpleUDPClient(address=REMOTE_OSC_IP, port=REMOTE_OSC_PORT) 
    print("Sending {} '{}' to {}:{}".format(OSC_ADRESS, OSC_VALUE, REMOTE_OSC_IP, REMOTE_OSC_PORT))
    osc_client.send_message(OSC_ADRESS, value=OSC_VALUE) # Send a OSC Message to some other hardware or module


def calculate_dbfs(data) -> float:
    rms = np.sqrt(np.mean(data ** 2))
    loudness_db = 20 * np.log10(rms)
    return loudness_db


def callback(indata, frames, time, status) -> None:
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    # Put indata in the cue to be used in the detect_scilence function
    q.put(indata.copy())


def detect_scilence() -> None:
    """gets audio frame data from que and calculates dbfs audio level.
    If level is under the configured threshold, call send_osc_message"""
    last_messurment: list = [] 
    threshold = THRESHOLD
    time: float = SCILENCE_DETECT_TIME 
    stop_event.clear()
    while not stop_event.is_set():
        frame = q.get()
        dbfs: float = calculate_dbfs(frame)
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
                break


def handler(address: str, *args: list[str]) -> None:
    """ Handles incoming OSC messages. 
    This function is called when an OSC message is received.
    It checks the address and arguments of the message and takes appropriate action.

    address: OSC address like /play
    *args: OSC values 1 or 0
    """
    print("Recived {} {}".format(address, args))
    if args and args[-1] == 0:
        stop_event.set()
        return
    if args and args[-1] == 1:
        start_detection()


def start_detection() -> None:
    """Starts the silence detection thread if it is not already running.

    This function checks if the global detection_thread is either None or not alive.
    If so, it clears the stop_event and starts a new daemon thread that runs the
    silence detection logic. This ensures that only one detection thread runs at a time.
    """
    global detection_thread
    if detection_thread is None or not detection_thread.is_alive():
        stop_event.clear()
        detection_thread = threading.Thread(target=scilence_detection_thread, daemon=True)
        detection_thread.start()


def scilence_detection_thread() -> None:
    with sd.InputStream(samplerate=SAMPEL_RATE, channels=CHANNELS,
                        blocksize=CHUNK, device=DEVICE, callback=callback):
        detect_scilence()


def osc_server_thread() -> None:
    dispatcher = Dispatcher()
    dispatcher.map("/play", handler)
    # Optional: dispatcher.map("/stop", handler)
    server = BlockingOSCUDPServer((LOCAL_OSC_IP, LOCAL_OSC_PORT), dispatcher)
    server.serve_forever()


if __name__ == "__main__":
    t = threading.Thread(target=osc_server_thread, daemon=True)
    t.start()
    print("OSC Server läuft. Warte auf /play ...")
    while True:
        time.sleep(1)