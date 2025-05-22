from pythonosc.udp_client import SimpleUDPClient

ip = "192.168.1.4"
port = 1337

client = SimpleUDPClient(ip, port)  # Create client

client.send_message("/live/song/get/tempo", 1)   # Send float message
# client.send_message("/some/address", [1, 2., "hello"])  # Send message with int, float and string