import sys  # For arg parsing
import socket  # For sockets
import select

#TODO
def move(server, id, old_x, old_y, new_x, new_y, range):
    old_x = new_x
    old_y = new_y
    server.sendall("UPDATEPOSITION {} {} {} {}".format(id, range, new_x, new_y).encode('utf-8'))

#TODO:
def senddata(server, destination, id, range, x, y):
    server.sendall("UPDATEPOSITION {} {} {} {} {} {}".format(id, range, x, y).encode('utf-8'))
    datamessage = "DATAMESSAGE {} {} {} {} {} {}".format(id, id, destination, 0, [])

#corresponds with QUIT command
def quit(server):
    server.close()

#TODO:
def where(server, message):
    server.sendall(message.encode('utf-8'))
    there = ""
    while True:
        there = server.recv(1024)
        if there:
            break
    there = there.decode('utf-8')
    return there


def run_client():
    if len(sys.argv) != 7:
        print(f"Proper usage is {sys.argv[0]} [control address] [control port] [sensor id] [sensor range] [initial x] [initial y]")
        sys.exit(0)

    id = str(sys.argv[3])
    range = int(sys.argv[4])
    x = int(sys.argv[5])
    y = int(sys.argv[6])

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
                    elif message[0].upper() == "REACHABLE":
                        #TODO: figure out what you want to do when receiving a REACHABLE reply from server
                        print("x: {} y: {} num_reachable: {}".format(x, y, message[1]))
                    else:
                        print("Invalid arguments from server")
            elif item == sys.stdin:             #Sensor Client STDIN commands
                stdin = sys.stdin.readline().strip()
                message = stdin.split()
                print("STDIN:", message)
                if len(message) == 3 and message[0].upper() == "MOVE":
                    move(server_socket, id, x, y, int(message[1]), int(message[2]), range)
                elif len(message) == 2 and message[0].upper() == "SENDDATA":
                    pass
                    '''
                elif len(message) == 2 and message[0].upper() == "WHERE":
                    there = where(server, stdin)
                    '''
                elif len(message) == 1 and message[0].upper() == "QUIT":
                    quit(server_socket)
                    return
                else:
                    print("Invalid arguments")



if __name__ == '__main__':
    run_client()
