import socket
SERVER_ADDRESS = ("192.168.1.120", 9000)
BUFFER_SIZE = 4096

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(SERVER_ADDRESS)
    while True:
        string = input("command:\n1 = foward\n2 = backward\n3 = left\n4 = right\n->")
        value = input("value->")
        s.sendall(f"{string}|{value}".encode())
        message = s.recv(BUFFER_SIZE)#bloccante
        print(f"{message.decode()}")
    s.close()

if __name__ == '__main__':
    main()