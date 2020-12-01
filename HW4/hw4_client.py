import sys  # For arg parsing
import socket  # For sockets
import select
from math import sqrt

#helper function to calculate Euclidean distance between two nodes
def distance_to(x1, y1, x2, y2):
    return sqrt((x1-x2)**2 + (y1-y2)**2)

#returns a reachable node that is closest to the destination
def closest_to_dest(reachable, there):
    x, y = there.split()[2:]
    x = int(x)
    y = int(y)
    node = ""
    shortest = 100000
    reachable_nodes = reachable.split()[2:]
    for i in range(0,len(reachable_nodes),3):
        if distance_to(x, y, int(reachable_nodes[i+1]), int(reachable_nodes[i+2])) < shortest:
            shortest = distance_to(x, y, int(reachable_nodes[i+1]), int(reachable_nodes[i+2]))
            node = reachable_nodes[i]
    return node

#Sends UPDATEPOSTITION command to server and returns new (x,y) coordinates
def move(server, id, new_x, new_y, ranges):
    reachable = updateposition(server, id, ranges, new_x, new_y)
    print(reachable)
    return new_x, new_y

#TODO:
def senddata(server, destination, source, ranges, x, y):
    reachable = updateposition(server, source, ranges, x, y)
    print(reachable)
    reachable_nodes = reachable.split()[2::3]

    if destination == source:
        print("Sent a message directly to {}".format(source))
    elif destination in reachable_nodes:
        print("Sent a message directly to {}".format(destination))
        server.sendall("DATAMESSAGE {} {} {} {} {}".format(source, destination, destination, 1, destination).encode('utf-8'))
    else:
        there = where(server, "WHERE {}".format(destination))
        #print(there)
        closest = closest_to_dest(reachable, there)
        #print(closest)
        print("Sent a message bound for {}".format(destination))
        server.sendall("DATAMESSAGE {} {} {} {} {}".format(source, closest, destination, 1, closest).encode('utf-8'))
        print("DATAMESSAGE {} {} {} {} {}".format(source, closest, destination, 1, closest))

#sends UPDATEPOSITION command to server and waits until it replies with a REACHABLE message
def updateposition(server, id, ranges, x, y):
    server.sendall("UPDATEPOSITION {} {} {} {}".format(id, ranges, x, y).encode('utf-8'))
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
    ranges = int(sys.argv[4])
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
                    x,y = move(server_socket, id, int(message[1]), int(message[2]), ranges)
                elif len(message) == 2 and message[0].upper() == "SENDDATA":
                    #TODO
                    senddata(server_socket, str(message[1]), id, ranges, x, y)
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
