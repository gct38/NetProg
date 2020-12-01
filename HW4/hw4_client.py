import sys  # For arg parsing
import socket  # For sockets
import select

#Sends UPDATEPOSTITION command to server and returns new (x,y) coordinates
def move(server, id, new_x, new_y, range):
    reachable = updateposition(server, id, range, new_x, new_y)
    print(reachable)
    return new_x, new_y

#TODO:
def senddata(server, destination, source, range, x, y):
    reachable = updateposition(server, source, range, x, y)
    print(reachable)
    #TODO: make an updateposition call to server for destination?
    reachable_nodes = reachable.split()[2::3]
    closest = reachable.split()[2]
    #print(reachable_nodes, closest)
    if destination == source:
        print("Sent a message directly to {}".format(source))
    elif destination in reachable_nodes:
        print("Sent a message directly to {}".format(destination))
        server.sendall("DATAMESSAGE {} {} {} {} {}".format(source, closest, destination, 1, [closest]).encode('utf-8'))
    else:
        server.sendall("DATAMESSAGE {} {} {} {} {}".format(source, closest, destination, 1, [closest]).encode('utf-8'))
        print("DATAMESSAGE {} {} {} {} {}".format(source, closest, destination, 1, [closest]))

#sends UPDATEPOSITION command to server and waits until it replies with a REACHABLE message
def updateposition(server, id, range, x, y):
    server.sendall("UPDATEPOSITION {} {} {} {}".format(id, range, x, y).encode('utf-8'))
    while True:
        reachable = server.recv(1024)
        if reachable:
            break
    return reachable.decode('utf-8')

#corresponds with QUIT command
#closes the server connection
def quit(server):
    server.close()

#Forwards WHERE command to server. Waits until receives THERE reply from server
def where(server, message):
    server.sendall(message.encode('utf-8'))
    while True:
        there = server.recv(1024)
        if there:
            break
    return there.decode('utf-8')

#main control loop for client
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
                    x,y = move(server_socket, id, int(message[1]), int(message[2]), range)
                elif len(message) == 2 and message[0].upper() == "SENDDATA":
                    #TODO
                    senddata(server_socket, str(message[1]), id, range, x, y)
                elif len(message) == 2 and message[0].upper() == "WHERE":
                    there = where(server_socket, stdin)
                    print(there)
                elif len(message) == 1 and message[0].upper() == "QUIT":
                    quit(server_socket)
                    return
                else:
                    print("Invalid arguments")



if __name__ == '__main__':
    run_client()
