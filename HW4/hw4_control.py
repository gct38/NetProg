import sys  # For arg parsing
import socket  # For sockets
import select
from math import sqrt


class Sensor:
    def __init__(self, id, range, x, y):
        self.id = str(id)
        self._range = int(range)    #"private" variable
        self.x = int(x)
        self.y = int(y)
        self.num_links = 0
        self.connections = {}

    def in_range(self, other):
        return distance_to(self,other) <= self._range

    def __str__(self):
        return "Sensor id: {}, x: {}, y: {}, connected to:{}".format(self.id, self.x, self.y, self.connections)

    def __eq__(self, other):
        return self.id==other.id

    def __ne__(self, other):
        return not self.__eq__(other)

class BaseStation:
    def __init__(self, id, x, y, num_links, list_of_links):
        self.id = str(id)
        self.x = int(x)
        self.y = int(y)
        self.num_links = int(num_links)
        self.connections = populate_connections(list_of_links)    #dict of anything the base is connected to (bases/clients)

    def __str__(self):
        return "Base Station id: {}, x: {}, y: {}, connected to: {}".format(self.id, self.x, self.y, str(self.connections))

    def __eq__(self, other):
        return self.id==other.id

    def __ne__(self, other):
        return not self.__eq__(other)

#helper function to calculate distance between two objects (Sensor/BaseStation)
def distance_to(obj, other):
    return sqrt((obj.x-other.x)**2 + (obj.y-other.y)**2)

#initializes all distances to -1 (used to initialize all the Sensor neighbors and their distances to -1)
def populate_connections(links):
    connections = {}
    for item in links:
        connections[item] = -1
    return connections

#clean up disconnected clients as connections
def remove_disconnected(nodes):
    for id in nodes:
        temp = nodes[id].connections.copy()
        for conn_id in temp:
            if conn_id not in nodes:
                del nodes[id].connections[conn_id]

#updates neighbors of all nodes
def update_neighbors(nodes):
    for id1 in nodes:
        if type(nodes[id1]) == Sensor:
            for id2 in nodes:
                if nodes[id1] != nodes[id2] and nodes[id1].in_range(nodes[id2]):
                    nodes[id1].connections[id2] = distance_to(nodes[id1], nodes[id2])
                    nodes[id2].connections[id1] = distance_to(nodes[id2], nodes[id1])
                if not nodes[id1].in_range(nodes[id2]) and nodes[id1] != nodes[id2] and id1 in nodes[id2].connections and id2 in nodes[id1].connections:
                    del nodes[id1].connections[id2]
                    del nodes[id2].connections[id1]

#updates distances of all nodes
def update_distance(nodes):
    for id in nodes:
        for connected_node in nodes[id].connections:
            nodes[id].connections[connected_node] = distance_to(nodes[id], nodes[connected_node])

#parse the base station txt file and returns dict of BaseStation objects (key = id of BaseStation)
def parse_bases(file):
    bases = {}
    for line in open(file):
        base = line.strip().split()
        bases[str(base[0])] = BaseStation(base[0],base[1],base[2],base[3], base[4:])
    return bases

#TODO:
def senddata(origin, destination):
    #create DATAMESSAGE
    pass


#corresponds to quit command, closes server
def quit(inputs):
    for socket in inputs:
        #print('socket {} should be closed by now'.format(socket))
        socket.close()

#Finds (x,y) coordinates of given NodeID
def where(nodes, id):
    return "THERE {} {} {}".format(id, nodes[id].x, nodes[id].y)

#updates the sensor client's location and every node's connections
def updateposition(nodes, id, range, x, y):
    remove_disconnected(nodes)
    nodes[id].x = x
    nodes[id].y = y
    nodes[id].range = range
    update_distance(nodes)
    update_neighbors(nodes)

    print("printing nodes after updating id {} with range {} to ({},{})".format(id, range, x, y))
    for id in nodes:
        print(nodes[id])
    print()

    reached = []
    reachable = ""
    for id1 in nodes:
        if id1 == id:
            for conn_id in nodes[id1].connections:
                reached.append(nodes[conn_id])
    reached = sorted(reached, key=lambda x: (distance_to(x,nodes[id]), x.id))
    for node in reached:
        reachable += " {} {} {}".format(node.id, node.x, node.y)
    return "REACHABLE {}{}".format(len(reached), reachable)

#TODO:
def datamessage():
    pass

def run_control():
    if len(sys.argv) != 3:
        print(f"Proper usage is {sys.argv[0]} [port number] [base station file]")
        sys.exit(0)

    inputs = [sys.stdin]
    clients = {}                #stores all of our Sensor Clients
    node_addresses = {}         #stores client address as key and node id as value
                                #node id can be used as a key in nodes
    port = int(sys.argv[1])
    file = str(sys.argv[2])
    nodes = parse_bases(file)   #dict of all clients/base stations
    update_distance(nodes)

    '''
    for id in nodes:
        print(nodes[id])
    print()
    '''

    # Create a TCP socket
    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listening_socket.bind(('', port))
    listening_socket.listen(5)
    inputs.append(listening_socket)

    # Server loop
    while True:
        reads, writes, excepts = select.select(inputs,[],[])
        for client in reads:
            if client is listening_socket:      #Accepting new Sensor Client connections
                (client_socket, address) = listening_socket.accept()
                inputs.append(client_socket)
            elif client == sys.stdin:           #Control Server STDIN commands
                message = sys.stdin.readline().strip().split()
                print("std in message: {}".format(message))
                if len(message) == 3 and message[0].upper() == "SENDDATA":
                    senddata(str(message[1]), str(message[2]))
                elif len(message) == 1 and message[0].upper() == "QUIT":
                    quit(inputs)
                    return
                else:
                    print("Invalid arguments")
            else:                               #Receive message from Sensor Client
                message = client.recv(1024)
                if message:
                    message = str(message.decode('utf-8'))
                    print("From Client:", message)
                    if message.find('hw4_client.py') != -1:
                        message = message.replace('[','').replace(']','').replace('\'','').split(',')
                        nodes[str(message[3]).strip()] = Sensor(message[3].strip(), message[4].strip(), message[5].strip(), message[6].strip())
                        node_addresses[client] = str(message[3]).strip()
                        update_neighbors(nodes)
                        update_distance(nodes)

                        print("\nUpdated neighbors and distance")
                        for id in nodes:
                            print(nodes[id])
                        print()
                    else:
                        #Commands received from Sensor client
                        message = message.split()
                        if len(message) == 2 and message[0].upper() == "WHERE":
                            there = where(nodes, str(message[1]))
                            client.sendall(there.encode('utf-8'))
                        elif len(message) == 5 and message[0].upper() == "UPDATEPOSITION":
                            reachable = updateposition(nodes, str(message[1]), int(message[2]), int(message[3]), int(message[4]))
                            print("Reachable to send to client:", reachable)
                            client.sendall(reachable.encode('utf-8'))
                        elif len(message) == 6 and message[0].upper() == "DATAMESSAGE":
                            pass
                        else:
                            print("Invalid arguments from client")
                else:
                    if node_addresses[client] in nodes:
                        del nodes[node_addresses[client]]
                    inputs.remove(client)
                    remove_disconnected(nodes)
                    update_neighbors(nodes)
                    update_distance(nodes)
                    client.close()

                    print("Client {} has disconnected".format(node_addresses[client]))
                    print("Updated neighbors and distance")
                    for id in nodes:
                        print(nodes[id])
                    print()
                    continue







if __name__ == '__main__':
    run_control()
