import socket

MY_ADDRESS = ("192.168.1.120", 9000)
BUFFER_SIZE = 4096

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(MY_ADDRESS)
    s.listen()

    connection, client_address = s.accept()
    print(f"Il client {client_address} si è connesso")
    running = True

    while running:
        #dizComandi = {1: "forward", 2: "backward", 3: "left", 4: "right"}
        listaComandi = ["0", "1", "2", "3", "4"]
        message = connection.recv(BUFFER_SIZE)
        string = message.decode()
        listMessage = string.split("|")
        print(listMessage)
        try:
            eval(listMessage[1])
            if listMessage[0] in listaComandi:
                if listMessage[0] == "0":
                    connection.sendall("connessione chiusa".encode())
                    running = False
                elif listMessage[0] == "1":
                    connection.sendall(f"ok|avanti di {listMessage[1]}".encode())
                elif listMessage[0] == "2":
                    connection.sendall(f"ok|indietro di {listMessage[1]}".encode())
                elif listMessage[0] == "3":
                    connection.sendall(f"ok|sinistra di {listMessage[1]}".encode())
                elif listMessage[0] == "4":
                    connection.sendall(f"ok|destra di {listMessage[1]}".encode())
            else:
                connection.sendall("error|comando non valido".encode())
        except:
            connection.sendall("error|comando non valido".encode())
    connection.close()

if __name__ == "__main__":
    main()