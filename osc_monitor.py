# This is a little utility. Start the server to test if you recive messages.
# All recived messages will be printed to the console.

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer


def print_handler(address, *args):
    print(f"{address}: {args}")


def default_handler(address, *args):
    print(f"DEFAULT {address}: {args}")


dispatcher = Dispatcher()
dispatcher.map("/something/*", print_handler)
dispatcher.set_default_handler(default_handler)

ip = "10.10.0.83"
port = 11001

server = BlockingOSCUDPServer((ip, port), dispatcher)
server.serve_forever()  # Blocks forever