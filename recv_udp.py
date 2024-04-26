import sys
import socket
import time

# Get the IP address and port number from the command line arguments
#ip_address = sys.argv[1]
port = int(sys.argv[1])
#size = int(sys.argv[3])


# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Receiver side
# Bind the socket to an address and port
sock.bind(("", port))

# Receive data
while True:
    data, addr = sock.recvfrom(1024)
    print(data)
    time.sleep(1)
