import psutil
import netifaces
import socket
import re


def is_interface_up(interface):
    addr = netifaces.ifaddresses(interface)
    return netifaces.AF_INET in addr
    #interface_addrs = psutil.net_if_addrs().get(interface) or []
    #return socket.AF_INET in [snicaddr.family for snicaddr in interface_addrs]


def is_mininet_interface(string):
  # Compile the regex pattern
  pattern = re.compile(r"^s\d-eth\d$")

  # Use the `search` method to check if the string matches the pattern
  match = pattern.search(string)

  # Return a boolean indicating whether the string matches the pattern
  return bool(match)



addrs = psutil.net_if_addrs()
net_stats = psutil.net_if_stats()

for stat in net_stats.items():
    if is_mininet_interface(stat[0]):
        print(stat[0]+" "+str(stat[1].isup))







#At every step:
# -check interfaces up
# -compute energy consumed based on the number of interfaces used
# -execute pending commands for optimization
