# credit for level calculations: 
# https://github.com/Sreeleena3s/Loudness-calculation/blob/main/loudness.py

import os
import numpy as np
import queue
import sys

# Set environment variable before importing sounddevice. Value is not important.
os.environ["SD_ENABLE_ASIO"] = "1"

import sounddevice as sd

CHUNK = 3200
CHANNELS = [11,12] # Focusrite 18i8 loopback Channels 11/12
q = queue.Queue()

def calculate_dbfs(data) -> float:
    rms = np.sqrt(np.mean(data ** 2))
    loudness_db = 20 * np.log10(rms)
    return loudness_db

# Define the callback function for real-time audio processing
def audio_callback(indata, frames, time, status):
    loudness_db = calculate_dbfs(indata)
    # Print the loudness in decibels
    print("Loudness (dB):", loudness_db)

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
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


# print(sd.query_hostapis())
# print(sd.query_devices(20))

stream = sd.InputStream(samplerate=44100, channels=CHANNELS,
    blocksize=CHUNK, device=20, callback=callback)

with stream:
    while True:
        detect_scilence()

# stream.start()

# while True:
#     # detect_scilence(stream.read(CHUNK))
#     pass

# stream.stop()
# stream.close()