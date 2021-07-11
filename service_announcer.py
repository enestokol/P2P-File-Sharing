import socket
import json
import time
import os
from sys import stdout


class User:
    def __init__(self, username, port, files):
        self.username = username
        self.files = files
        self.port = port
        self.write_to_file()

    def get_info(self):
        info = {
            "username": self.username,
            "files": self.files,
        }
        return info

    def write_to_file(self):
        with open("User.json", "w") as file:
            json.dump(self.get_info(), file)

    def connect_to(self, broadcast, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        addr = (broadcast, port)
        while True:
            s.sendto(json.dumps(self.get_info()).encode(), addr)
            for i in range(50):
                stdout.write("\r%d" % i)
                stdout.flush()
                time.sleep(1)


def get_files_from_path(path):
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]


def _broadcast(ip):
    broadcast = str()
    first_octet = int(ip.split(".")[0])

    if first_octet in range(1, 127):
        broadcast = '.'.join(ip.split('.')[0:-3]) + ".255.255.255"
    elif first_octet in range(127, 191):
        broadcast = '.'.join(ip.split('.')[0:-2]) + ".255.255"
    elif first_octet in range(192, 223):
        broadcast = '.'.join(ip.split('.')[0:-1]) + ".255"

    return broadcast


if __name__ == "__main__":
    ip = str(input("IP Address :"))

    port = 5000  # defined in project file
    broadcast = _broadcast(ip)

    print("IP: {0} Broadcast: {1}".format(ip, broadcast))
    username = input("Username :")

    path = os.path.dirname(__file__) + "/uploads/temp"
    files = get_files_from_path(path)

    u1 = User(username, port, files)
    u1.connect_to(broadcast, port)
