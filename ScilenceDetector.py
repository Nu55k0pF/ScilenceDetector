# Reference Pyaudio: https://kevinponce.com/blog/python/record-audio-on-detection/
# Reference pythonosc docs: https://python-osc.readthedocs.io/en/latest/client.html
# audioop is deprecated in 3.13 use auidoop-lts instead
# audioop width 
# 8 bit     = 1
# 16 bit    = 2
# 24 bit    = 3
# 32 bit    = 4
#TODO: Build PortAudio with ASIO Support and make it install with requirements

import pyaudio
import audioop
from pythonosc import udp_client

def get_audio_device_by_name():
    for i in range(0, p.get_device_count()):    
        print(i, p.get_device_info_by_index(i)['name'])

# Make all your configurations here
CHUNK = 3200 # Sets buffe size
BIT_DEPTH = pyaudio.paInt16
CHANNELS = 1 # Mono or Stereo 1/2
SAMPLING_RATE = 44100
OSC_SERVER_IP = "127.0.0.1" # IP Adress of OSC server to send messages to
OSC_SERVER_PORT = 8000
OSC_ADRESS = "t/play" # Enter OSC Adress to send message to
OSC_VALUE = 1 # Enter the desired value for your osc action

# Initialize the osc_clienat
osc_client = udp_client.SimpleUDPClient(address=OSC_SERVER_IP, port=OSC_SERVER_PORT) 
# Create an Interface to PortAudio
p = pyaudio.PyAudio() 

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

# Initialize an arry to store data in
frames = [] 
# how long to record
seconds = 6 
# stors the last x rms values
last_rms = [] 
threshold = 100
# at 44.1 kHz and 3200 samples in the buffer you have about 14 chunks per second, so if you want a detection time of 2 seconds 30 is about the right value here. 3 sek ~ 42
time = 40 
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
            print("Sending {} to {}:{}{}".format(OSC_VALUE, OSC_SERVER_IP, OSC_SERVER_PORT, OSC_ADRESS))
            osc_client.send_message(OSC_ADRESS, value=OSC_VALUE) #Send a OSC Message to some other hardware or module
            listen = False

# Stop and Close the audiostream
stream.start_stream()
stream.close()
# Terminate PortAudio interface
p.terminate()