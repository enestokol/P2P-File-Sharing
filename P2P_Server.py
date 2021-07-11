import datetime
import json
import logging
import os
import socket
import socketserver
import threading
import time
from os.path import exists
from sys import stdout

from helper import split, size_format

now = datetime.datetime.now()
timestamp = datetime.datetime.timestamp(now)
logging.basicConfig(filename="server.log", level=logging.INFO)





class TCPHandler(socketserver.BaseRequestHandler):
    def setup(self):
        self.connection = self.request
        self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)

    def handle(self):
        transferred_data = 0
        print("<SERVER>: Connected to [%s]" % self.client_address[0])
        request = self.request.recv(1024)
        request = json.loads(request)
        chunk = request["filename"]
        cur_thread = threading.current_thread()

        # If the file doesn't exists, return from the handle function
        if not exists("uploads/temp/" + chunk):
            self.request.send(str("0").encode())
            self.request.close()
        else:
            self.request.send(str("1").encode())
            time.sleep(1)
            self.request.send(str(os.path.getsize("uploads/temp/" + chunk)).encode())
            time.sleep(1)
            print("<SERVER>: Start transferring file {0}:{1}".format(chunk, self.client_address[0]))
            with open("uploads/temp/" + chunk, 'rb') as f:
                try:
                    data = f.read(1024)
                    while data:
                        transferred_data += self.request.send(data)
                        stdout.write("\rFile sending {1}: {0:.0f}%".format(
                            transferred_data / int(os.path.getsize("uploads/temp/" + chunk)) * 100, cur_thread.name))
                        stdout.flush()
                        data = f.read(1024)
                except Exception as e:
                    print(e)
            print("\n<SERVER>: Completed transfer file {0}, transferred data {1} {2}".format(chunk, size_format(
                transferred_data), self.client_address[0]))
            logging.info("{0}, {1}, {2}".format(timestamp, chunk, self.client_address[0]))
            logging.shutdown()


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def run_tcp_server(port):
    print("<SERVER>: TCP Server Started")
    try:
        # server = socketserver.TCPServer(('', port), TCPHandler)
        server = ThreadedTCPServer(('', port), TCPHandler)
        with server:
            server_thread = threading.Thread(target=server.serve_forever())
            server_thread.daemon = True
            server_thread.start()
    except KeyboardInterrupt:
        print("<SERVER>: TCP Server Closed")


if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())

    port = 5001
    buffer = 2048

    menu = int(input("Do you want to host any files?\nYes: 1 - No: 0 :"))

    if menu == 1:
        path = os.path.dirname(__file__) + "/uploads"
        directory = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

        user_file = dict(zip(range(len(directory)), directory))
        print("Your files under the {} ".format(path))
        print(user_file)

        choose = input("Which files do you want to host? Please write the index numbers, leaving a space: ")
        splited_list = choose.split()

        hosted_files = [value for key, value in user_file.items() if key in map(int, splited_list)]
        split(hosted_files)

        print("stating it is ready to host these files")
        print(hosted_files)
        print("Server is launching")
    else:
        print("Server is launching")

    run_tcp_server(port)
