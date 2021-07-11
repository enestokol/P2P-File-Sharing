import datetime
import os
import socket
import json
import socketserver

file_list = dict()
peer_list = dict()


def get_peer_list(request, ipaddr):
    if ipaddr not in peer_list:
        peer_list[ipaddr] = request["username"]
    else:
        if peer_list[ipaddr] != request["username"]:
            print("{0} name changed to {1} ".format(peer_list[ipaddr], request["username"]))
            peer_list[ipaddr] = request["username"]
    print('\n'.join(['{0} {1} is online'.format(k, v.capitalize()) for k, v in peer_list.items()]))


def chunk_list(request, ipaddr):
    new = False

    print("{0} files:".format(peer_list.get(ipaddr)),end='')
    for chunk in request["files"]:
        if chunk not in file_list:
            file_list[chunk] = []
            file_list[chunk].append(ipaddr)
            new = True
            print("\n{0} Added By {1}-{2}".format(chunk, peer_list.get(ipaddr), ipaddr))
        else:
            if ipaddr not in file_list[chunk]:
                file_list[chunk].append(ipaddr)
                new = True

        def write_served_file(new):
            if new:
                with open("served.json", "w") as served:
                    json.dump(file_list, served)

        if new == False:
            print("{0}".format(chunk), end=' ', flush=True)

        write_served_file(new)
    print()
    # return new


class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0]
        ipaddr = self.client_address[0]
        json_data = json.loads(data.decode())

        get_peer_list(json_data, ipaddr)
        chunk_list(json_data, ipaddr)


def run_udp_server(port):
    print("<SERVER>: UDP Server started")
    try:
        server = socketserver.UDPServer(('', port), UDPHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("<SERVER>: UDP Server Closed")


if __name__ == "__main__":
    port = 5000
    buffer = 1024
    run_udp_server(port)
