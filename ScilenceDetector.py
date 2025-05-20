# Reference: https://kevinponce.com/blog/python/record-audio-on-detection/
# audioop is deprecated in 3.13 use auidoop-lts instead
# audioop width 
# 8 bit     = 1
# 16 bit    = 2
# 24 bit    = 3
# 32 bit    = 4
#TODO: Build PortAudio with ASIO Support and make it install with requirements

import pyaudio
import struct
import audioop

def get_audio_device_by_name():
    for i in range(0, p.get_device_count()):    
        print(i, p.get_device_info_by_index(i)['name'])

# Make all your configurations here
CHUNK = 3200 # Sets buffe size
BIT_DEPTH = pyaudio.paInt16
CHANNELS = 1 # Mono or Stereo 1/2
SAMPLING_RATE = 44100

p = pyaudio.PyAudio() # Create an Interface to PortAudio

get_audio_device_by_name()
print("Select input device by index:\n")

device_index = int(input())

stream = p.open(
    format=BIT_DEPTH,
    channels=CHANNELS,
    rate=SAMPLING_RATE,
    input=True,
    frames_per_buffer=CHUNK,
    input_device_index=device_index # here you have to set the input device to monitor use p.get_device_info_by_index() to list all available
)

frames = [] # Initialize an arry to store data in
seconds = 6 # how long to record
last_rms = [] # stors the last x rms values
threshold = 100
time = 40 # at 44.1 kHz and 3200 samples in the buffer you have about 14 chunks per second, so if you want a detection time of 2 seconds 30 is about the right value here. 3 sek ~ 42
listen = True

# for i in range(0, int(SAMPLING_RATE/CHUNK * seconds)):
while listen:
    data = stream.read(CHUNK)
    frames.append(data)
    rms = audioop.rms(data, 2)
    
    if len(last_rms) < time:
        last_rms.append(rms)
        print(rms)
    else:
        last_rms.pop(0)
        last_rms.append(rms)
        
        avarage = sum(last_rms)/len(last_rms)
        if avarage > threshold:
            print(rms)
            continue
        else:
            print("Scilence Detected!!!!")
            listen = False

# Stop and Close the audiostream
stream.start_stream()
stream.close()
# Terminate PortAudio interface
p.terminate()