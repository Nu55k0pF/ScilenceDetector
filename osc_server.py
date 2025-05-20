# Referemce https://python-osc.readthedocs.io/en/latest/server.html#blocking-server
# This is not written by me and is only used for testing while developing the scilence detector

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer


def print_handler(address, *args):
    print(f"{address}: {args}")


def default_handler(address, *args):
    print(f"DEFAULT {address}: {args}")

def reaper_handler(address, *args):
    print("now playing")


dispatcher = Dispatcher()
# dispatcher.map("/something/*", print_handler)
dispatcher.map("/play", reaper_handler)
# dispatcher.set_default_handler(reaper_handler)

ip = "127.0.0.1"
port = 9000

server = BlockingOSCUDPServer((ip, port), dispatcher)
server.serve_forever()  # Blocks forever