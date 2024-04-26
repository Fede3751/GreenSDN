import sys
import socket
import time

# Get the IP address and port number from the command line arguments

print(sys.argv)

ip_address = sys.argv[1]
port = int(sys.argv[2])
size = int(sys.argv[3])

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Sender side
# Send data

message = b'\x00' * size

while True:
    sock.sendto(message, (ip_address, port))
    time.sleep(1)
