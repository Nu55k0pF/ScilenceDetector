import argparse
from pythonosc.udp_client import SimpleUDPClient

parser = argparse.ArgumentParser(description="Send OSC messages to a server.")
parser.add_argument(
    "-ip", type=str, default="10.10.0.83", help="IP address of the server")
parser.add_argument(
    "-p", type=int, default=11001, help="Port of the server")
parser.add_argument(
    "-m", type=str, help="Message to send", required=True)
parser.add_argument(
    "-v", type=str, help="Value to send", required=True, nargs='+')

args = parser.parse_args()
ip = args.ip  # IP address of the server
port = args.p  # Port of the server
message = args.m  # Message to send
value = args.v  # Value to send
# Convert value to float if possible

try:
    value = [int(v) for v in value]
except ValueError:
    pass

client = SimpleUDPClient(ip, port)  # Create client
client.send_message(message, value)    # Send float message