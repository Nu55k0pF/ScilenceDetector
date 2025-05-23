#TODO: Programm so anpassen, dass man es über die Konsole mit argparser starten kann um testnachrichten zu senden

from pythonosc.udp_client import SimpleUDPClient

ip = "10.10.0.83"
port = 11001

client = SimpleUDPClient(ip, port)  # Create client

client.send_message("/play", (1, 1))    # Send float message
# client.send_message("/some/address", [1, 2., "hello"])  # Send message with int, float and string