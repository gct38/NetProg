import sys  # For arg parsing
import socket  # For sockets
import select

#TODO: add in logic for handling messages from Control Server

def run_client():
    if len(sys.argv) != 7:
        print(f"Proper usage is {sys.argv[0]} [control address] [control port] [sensor id] [sensor range] [initial x] [initial y]")
        sys.exit(0)

    # Create the TCP socket, connect to the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((sys.argv[1], int(sys.argv[2])))
    server_socket.sendall(str(sys.argv).encode('utf-8'))
    while True:
        #Sensor Client STDIN commands
        inp = input().split()
        if inp[0].upper() == "MOVE" and len(inp) == 3:
            #send UPDATEPOSITION to control server
            pass
        elif inp[0].upper() == "SENDDATA" and len(inp) == 2:
            pass
        elif inp[0].upper() == "WHERE" and len(inp) == 2:
            pass
        elif inp[0].upper() == "UPDATEPOSITION" and len(inp) == 5:
            pass
        elif inp[0].upper() == "QUIT" and len(inp) == 1:
            break
        else:
            print("Invalid arguments")


    # Disconnect from the server
    server_socket.close()

if __name__ == '__main__':
    run_client()
