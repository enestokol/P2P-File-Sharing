import datetime
import logging
import os
import socket
import json
import time
from os.path import exists
from sys import stdout
from helper import combine, size_format

now = datetime.datetime.now()
timestamp = datetime.datetime.timestamp(now)
logging.basicConfig(filename="download.log", level=logging.INFO)


def content_name(file):
    content = os.path.splitext(os.path.basename(file))[0][:-2]
    extension = os.path.splitext(os.path.basename(file))[1]

    return str(content + extension)


def get_served_list():
    with open("served.json", "r") as served:
        data = json.load(served)
    return data


def get_user_info():
    with open("User.json", "r") as info:
        data = json.load(info)
    return data


def get_available_files(served_list):
    available_files = set()
    available_files = list(
        set([content_name(key) for key in list(served_list.keys()) if content_name(key) not in available_files]))
    return available_files


def get_file_name(available_file_list):
    print(dict((zip(range(len(available_file_list)), available_file_list))))
    index = int(input("Which files do you want to download? Please write their index: "))
    return available_file_list[index]


def get_file_list(file_name):
    content = os.path.splitext(os.path.basename(file_name))[0]
    extension = os.path.splitext(os.path.basename(file_name))[1]

    file_list = dict((key, value) for key, value in served_list.items() if
                     key in [content + "_" + str(i) + extension for i in range(1, 6)])

    def get_exact_list(file_list):
        for key, value in file_list.copy().items():
            if not exists("downloads/temp/" + key):
                pass
            else:
                ask = int(input(
                    "{} exist under the Download folder.\nDo you want to delete it from the download list?\nYes 1 No 0 :\n".format(
                        key)))
                if ask == 1:
                    print("{} is deleted from the download list".format(key))
                    del file_list[key]
                else:
                    continue
        return file_list

    return get_exact_list(file_list)




def download_chunk(chunk, transferred_data, size):
    with open("downloads/temp/" + chunk, 'wb') as f:
        print("File size: {}".format(size_format(int(size))))
        while True:
            data = s.recv(1024)
            transferred_data += len(data)
            stdout.write("\rFile receiving: {0:.0f}%".format(transferred_data / int(size) * 100))
            stdout.flush()
            # time.sleep(1)
            if not data:
                break
            f.write(data)
    f.close()
    print("\n<CLIENT>: Recieved  file {0}, transferred data {1}".format(chunk, size_format(transferred_data)))


if __name__ == "__main__":
    served_list = get_served_list()
    available_file_list = get_available_files(served_list)
    info = get_user_info()

    port = 5001
    buffer = 2048

    print("Welcome " + info["username"])
    transferred_data = 0
    while 1:
        menu = int(
            input("Welcome to Menu Please write Index \n1 download file\n2 exit"))

        if menu == 1:
            index = 0
            file_name = get_file_name(available_file_list)
            download_list = get_file_list(file_name)

            chunk_list = list(key for key, value in download_list.items())
            request_filename = {
                "filename": ""
            }

            while index < len(download_list):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                filestatus = ""
                chunk = chunk_list[index]
                request_filename["filename"] = chunk
                try:
                    s.connect((download_list[chunk_list[index]][0], port))
                    s.send(bytes(json.dumps(request_filename), 'utf-8'))
                    print(chunk + " Try to download from: " + download_list[chunk_list[index]][0])
                    filestatus = s.recv(buffer).decode('utf-8')
                    time.sleep(1)
                    size = s.recv(buffer).decode("utf-8")
                except:
                    print("Connection lost")
                    break
                if filestatus == "1":
                    # time.sleep(1)
                    download_chunk(chunk, transferred_data, size)
                    logging.info("{0}, {1},{2}".format(timestamp, chunk, download_list[chunk_list[index]][0]))
                    index += 1
                else:
                    count = len(download_list[chunk_list[index]]) - 1
                    if count >= 1:
                        new = 1
                        while count >= 1:
                            print("File didn't find try to download new peer")
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            filestatus = ""
                            try:
                                s.connect((download_list[chunk_list[index]][new], port))
                                s.send(bytes(json.dumps(request_filename), 'utf-8'))
                                print(chunk + " Try to download from: " + download_list[chunk_list[index]][new])
                                filestatus = s.recv(buffer).decode("utf-8")
                                time.sleep(1)
                                size = s.recv(buffer).decode("utf-8")
                            except:
                                print("Connection lost")
                                break
                            if filestatus == "yes":
                                count = 0
                                download_chunk(chunk, transferred_data, size)
                                logging.info(
                                    "{0}, {1}, {2}".format(timestamp, chunk, download_list[chunk_list[index]][new]))
                                logging.shutdown()
                                index += 1
                            else:
                                new += 1
                                count -= 1
                    else:
                        print("“CHUNK {0} CANNOT BE DOWNLOADED FROM ONLINE PEERS.".format(chunk))
                        print("Connection closed")
                        logging.error("{0}, {1},{2}".format(timestamp, chunk, download_list[chunk_list[index]][0]))
                        logging.shutdown()
                        break

            if index == len(download_list):
                print("{0} is combining please wait".format(file_name))
                combine(file_name)
                d_path = os.path.dirname(__file__) + "/downloads"
                print("File successfully combined\nCombined file under the {0}".format(d_path))
        else:
            break
