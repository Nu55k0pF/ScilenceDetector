import os
import numpy as np

# Set environment variable before importing sounddevice. Value is not important.
os.environ["SD_ENABLE_ASIO"] = "1"

import sounddevice as sd

CHUNK = 3200
CHANNELS = [11,12] # Focusrite 18i8 loopback Channels 11/12

def calculate_loudness(data):
    # Compute the RMS (root mean square) of the audio signal
    rms = np.sqrt(np.mean(data ** 2))

    # Convert RMS to decibels (dB)
    loudness_db = 20 * np.log10(rms)
    return np.abs(loudness_db)


# Define the callback function for real-time audio processing
def audio_callback(indata, frames, time, status):
    # Calculate the loudness of the audio signal
    loudness_db = calculate_loudness(indata)

    # Print the loudness in decibels
    print("Loudness (dB):", loudness_db)

def detect_scilence(stream):
    # Initialize an arry to store data in
    frames = [] 
    # how long to record
    seconds = 6 
    # stors the last x dbfs values
    last_dbfs = [] 
    threshold = 100
    # at 44.1 kHz and 3200 samples in the buffer you have about 14 chunks per second, so if you want a detection time of 2 seconds 30 is about the right value here. 3 sek ~ 42
    time = 40 
    listen = True
    while listen:
        data = stream.read(CHUNK)
        print(data)
        frames.append(data)
        dbfs = calculate_rms(data)
        
        if len(last_dbfs) < time:
            last_dbfs.append(dbfs)
            print(dbfs)
        else:
            last_dbfs.pop(0)
            last_dbfs.append(dbfs)
            
            avarage = sum(last_dbfs)/len(last_dbfs)
            if avarage > threshold:
                print(dbfs)
                continue
            else:
                print("Scilence Detected!!!!")
                listen = False


# print(sd.query_hostapis())
# print(sd.query_devices(20))

stream = sd.InputStream(
    samplerate=44100,
    channels=CHANNELS,
    blocksize=CHUNK,
    device=20,
    callback=audio_callback
)

stream.start()

while True:
    pass

stream.stop()
stream.close()