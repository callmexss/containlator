import socket
import fcntl
import struct
import subprocess
import random
  
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


dev = subprocess.check_output("ifconfig").split(b" ")[0]


with open("/fred/freenet.ini", "r") as f:
    ret = f.read()
    ret = ret.replace("replaced_ip", get_ip_address(dev))
    ret = ret.replace("OBL", str(random.randint(10000, 30000)))
    ret = ret.replace("IBL", str(random.randint(10000, 30000)))


with open("/fred/freenet.ini", "w") as f:
    f.write(ret)

