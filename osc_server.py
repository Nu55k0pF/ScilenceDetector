# Referemce https://python-osc.readthedocs.io/en/latest/server.html#blocking-server
# This is not written by me and is only used for testing while developing the scilence detector

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc import udp_client
import pyaudio
import audioop

# Make all your configurations here
CHUNK: int = 3200 # Sets buffe size
BIT_DEPTH: int = pyaudio.paInt16
CHANNELS: int = 1 # Mono or Stereo 1/2
SAMPLING_RATE: int = 44100
OSC_SERVER_IP: str = "127.0.0.1" # IP Adress of OSC server to send messages to
OSC_SERVER_PORT: int = 8000
OSC_ADRESS: str = "t/stop" # Enter OSC Adress to send message to
OSC_VALUE: str =  "1" # Enter the desired value for your osc action
HOST_IP: str = "127.0.0.1"
HOST_PORT: int = 9000

def send_osc_message() -> None:
    """Use this to configure the action to take when detecitng scilence"""
    osc_client = udp_client.SimpleUDPClient(address=OSC_SERVER_IP, port=OSC_SERVER_PORT) 
    print("Sending {} '{}' to {}:{}".format(OSC_ADRESS, OSC_VALUE, OSC_SERVER_IP, OSC_SERVER_PORT))
    osc_client.send_message(OSC_ADRESS, value=OSC_VALUE) #Send a OSC Message to some other hardware or module

def detect_scilence(stream) -> None:
    # Initialize an arry to store data in
    frames: list = [] 
    # stors the last x rms values
    last_rms: list = [] 
    threshold: int = 50
    # at 44.1 kHz and 3200 samples in the buffer you have about 14 chunks per second, so if you want a detection time of 2 seconds 30 is about the right value here. 3 sek ~ 42
    time: int = 40 

    listen: bool = True
    while listen:
        data = stream.read(CHUNK)
        frames.append(data)
        rms: int = audioop.rms(data, 2)
        
        if len(last_rms) < time:
            last_rms.append(rms)
            print(rms)
        else:
            last_rms.pop(0)
            last_rms.append(rms)
            
            avarage: float = sum(last_rms)/len(last_rms)
            if avarage > threshold:
                print(rms)
                continue
            else:
                send_osc_message()
                listen = False

def handler(address: str, *args: list[str]):
    """This is an example function. 
    It detects the Reaper OSC message for toggle play and starts listening. 
    This needs to be adapted for other aplications
    """
    print("Recived {} {}".format(address, args))
    p = pyaudio.PyAudio()
    stream = p.open(
        format=BIT_DEPTH,
        channels=CHANNELS,
        rate=SAMPLING_RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=3 # here you have to set the input device to monitor use p.get_device_info_by_index() to list all available
    )
    if args [-1] == 1:
        detect_scilence(stream)
    else:
        return

dispatcher = Dispatcher()
# dispatcher.map("/something/*", print_handler)
dispatcher.map("/play", handler)
# dispatcher.set_default_handler(reaper_handler)

server = BlockingOSCUDPServer( (HOST_IP, HOST_PORT), dispatcher)
server.serve_forever()  # Blocks forever