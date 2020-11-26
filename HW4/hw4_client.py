import sys  # For arg parsing
import socket  # For sockets
import select

#TODO: add in logic for handling messages from Control Server

#corresponds with QUIT command
def quit(server):
    server.close()

def run_client():
    if len(sys.argv) != 7:
        print(f"Proper usage is {sys.argv[0]} [control address] [control port] [sensor id] [sensor range] [initial x] [initial y]")
        sys.exit(0)

    # Create the TCP socket, connect to the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((sys.argv[1], int(sys.argv[2])))
    server_socket.sendall(str(sys.argv).encode('utf-8'))
    while True:
        reads, writes, excepts = select.select([sys.stdin, server_socket],[],[])
        for item in reads:
            if item is server_socket:           #Receive message from Control Server
                message = server_socket.recv(1024)
                if message:
                    message = str(message.decode('utf-8')).split()
                    print("From Server:", message)
                    if len(message) == 2 and message[0].upper() == "DATAMESSAGE":
                        pass
                    else:
                        print("Invalid arguments from server")
            elif item == sys.stdin:             #Sensor Client STDIN commands
                stdin = sys.stdin.readline().strip()
                message = stdin.split()
                print("STDIN:", message)
                if len(message) == 3 and message[0].upper() == "MOVE":
                    #send UPDATEPOSITION to control server
                    pass
                elif len(message) == 2 and message[0].upper() == "SENDDATA":
                    pass
                elif len(message) == 2 and message[0].upper() == "WHERE":
                    #server_socket.sendall(str(stdin).encode('utf-8'))
                    pass
                elif len(message) == 1 and message[0].upper() == "QUIT":
                    quit(server_socket)
                    return
                else:
                    print("Invalid arguments")



if __name__ == '__main__':
    run_client()
