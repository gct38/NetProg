import sys  # For arg parsing
import socket  # For sockets
import select
from math import sqrt


#includes all nodes (sensors and base stations)
class Sensor:
    def __init__(self, id, range, x, y):
        self.id = str(id)
        self._range = int(range)    #"private" variable
        self.x = int(x)
        self.y = int(y)
        self.num_links = 0
        self.connections = {}

    def distance_to(self, other):
        return sqrt((self.x-other.x)**2 + (self.y-other.y)**2)

    def in_range(self, other):
        return self.distance_to(other) <= self._range

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

    def distance_to(self, other):
        return sqrt((self.x-other.x)**2 + (self.y-other.y)**2)

    def __str__(self):
        return "Base Station id: {}, x: {}, y: {}, connected to: {}".format(self.id, self.x, self.y, str(self.connections))

    def __eq__(self, other):
        return self.id==other.id

    def __ne__(self, other):
        return not self.__eq__(other)

#initializes all distances to -1 (used to initialize all the Sensor neighbors and their distances to -1)
def populate_connections(links):
    connections = {}
    for item in links:
        connections[item] = -1
    return connections


#updates neighbors of all nodes
def update_neighbors(nodes):
    for id1 in nodes:
        if type(nodes[id1]) == Sensor:
            for id2 in nodes:
                if nodes[id1] != nodes[id2] and nodes[id1].in_range(nodes[id2]):
                    nodes[id1].connections[id2] = nodes[id1].distance_to(nodes[id2])
                    nodes[id2].connections[id1] = nodes[id2].distance_to(nodes[id1])

#updates distances of all nodes
def update_distance(nodes):
    for id in nodes:
        for connected_node in nodes[id].connections:
            nodes[id].connections[connected_node] = nodes[id].distance_to(nodes[connected_node])

#parse the base station txt file and returns dict of BaseStation objects (key = id of BaseStation)
def parse_bases(file):
    bases = {}
    for line in open(file):
        base = line.strip().split()
        bases[str(base[0])] = BaseStation(base[0],base[1],base[2],base[3], base[4:])
    return bases


def send_data():
    pass

def quit(client_socket):
    # Close the connection
    client_socket.close()
    print('clientsocket should be closed by now')


def run_control():
    if len(sys.argv) != 3:
        print(f"Proper usage is {sys.argv[0]} [port number] [base station file]")
        sys.exit(0)

    port = int(sys.argv[1])
    file = str(sys.argv[2])
    nodes = parse_bases(file)   #dict of all clients/base stations
    update_distance(nodes)

    for id in nodes:
        print(nodes[id])
    print()

    # Create a TCP socket
    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listening_socket.bind(('', port))
    listening_socket.listen(5)

    # Server loop
    while True:
        (client_socket, address) = listening_socket.accept()

        #Control Server STDIN commands
        '''
        inp = input().split()
        if inp[0].upper() == "SENDDATA" and len(inp) == 3:
            pass
        elif inp[0].upper() == "QUIT" and len(inp) == 1:
            quit(client_socket)
            return
        else:
            print("Invalid arguments")
        '''

        while True:
            #read_ready, _, _ = select.select([client_socket],[],[])
            message = client_socket.recv(1024)
            if message:
                message = str(message.decode('utf-8'))
                print(message)
                if message.find('hw4_client.py'):
                    message = message.replace('[','').replace(']','').replace('\'','').split(',')
                    nodes[str(message[3]).strip()] = Sensor(message[3].strip(), message[4].strip(), message[5].strip(), message[6].strip())
                    update_neighbors(nodes)
                    update_distance(nodes)

                    print("\nUpdated neighbors and distance")
                    for id in nodes:
                        print(nodes[id])
                    print()
                else:
                    #Commands received from Sensor client
                    message = message.split()
                    if message[0].upper() == "WHERE":
                        pass
                    elif message[0].upper() == "UPDATEPOSITION":
                        #update positions of clients and update their distances and repopulate neighbors
                        update_neighbors(nodes)
                        update_distance(nodes)
                    else:
                        print("Invalid arguments from client")
            else:
                break


if __name__ == '__main__':
    run_control()
