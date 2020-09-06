import subprocess
import struct
import socket
import fcntl

def cpu_load():
    return __call_command("top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'")

def ram_usage():
    return __call_command("free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'")

def disk_usage():
    return __call_command("df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'")

def cpu_temperature():
    tempI = int(open('/sys/class/thermal/thermal_zone0/temp').read())
    if tempI>1000:
        tempI = tempI/1000
    return "CPU TEMP: %sC" % str(tempI)

def ip_address(interface_name):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', interface_name[:15])
        )[20:24])
    except:
        return ip_address()

def ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# Private functions
def __call_command(cmd):
    try:
        return subprocess.check_output(cmd, shell = True)
    except Exception as ex:
        print(ex)
        return 'N/A'
