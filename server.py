import socket
import colorama

colorama.init()

LHOST = "0.0.0.0"
LPORT = 2222

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((LHOST, LPORT))
sock.listen(1)
print("Listening on port", LPORT)
client, addr = sock.accept()

while True:
    input_header = client.recv(1024)
    command = input(input_header.decode()).encode()

    if command.decode("utf-8").split(" ")[0] == "download":
        file_name = command.decode("utf-8").split(" ")[1]
        client.send(command)
        with open(file_name, "wb") as f:
            read_data = client.recv(1024)
            while read_data:
                f.write(read_data)
                read_data = client.recv(1024)
                if read_data == b"DONE":
                    break

    elif command.decode("utf-8").split(" ")[0] == 'upload':
        client.send(command)
        with open(command.decode("utf-8").split(" ")[1], "rb") as f:
            file_data = f.read(1024)
            while file_data:
                client.send(file_data)
                file_data = f.read(1024)
            client.send(b"Done")
        print("Finished uploading data")

    elif command is b"":
        print("Please enter a command")
    else:
        client.send(command)
        data = client.recv(1024).decode("utf-8")
        if data == "exit":
            print("Terminating connection", addr[0])
            break
        print(data)
client.close()
sock.close()
