#!/usr/bin/env python3

from csci4220_hw3_pb2_grpc import KadImplServicer
from concurrent import futures
import sys  # For sys.argv, sys.exit()
import socket  # for gethostbyname()

import grpc

import csci4220_hw3_pb2
import csci4220_hw3_pb2_grpc

#Finds distance using XOR between 2 IDs
def distance(id1, id2):
	return id1 ^ id2

def print_k_buckets(k_buckets):
	for i in range(len(k_buckets)):
		print("%d: " % i)
		for j in range(len(k_buckets[i])):
			current = k_buckets[i]
			print("%d : %d" % (current[j].id, current[j].port))
			if (j == len(i)-1):
				print()
			else:
				print(" ")
			

#Server Implementation
class KadImplServicer(csci4220_hw3_pb2_grpc.KadImplServicer):

	def __init__(self):
		self.hashtable = dict()

	#return NodeList of k closest nodes to given ID
	def FindNode(self, IDKey, context):
		idkey = IDKey.idkey
		distances = dict() #key=id, value=distance
		responder = None
		'''
		for id in self.bucket:
			if id==idkey:
				responder = self.nodes[id]
				continue
			distance = self.__distance(id, idkey)
			if len(distances) > self.k:
				distances[id] = distances 
				continue

			highest = max(distances.values())
			if distance < highest: #you have a closer node
				to_remove = None
				#remove furthest node from distances dict
				for key, value in distances:
					if value == highest:  
						to_remove = key 
						break
				del distances[to_remove]
		'''
		#Creating NodeList from distances dict
		#TODO: implement NodeList, don't think nodes parameter is right
		return csci4220_hw3_pb2.NodeList(responding_node=responder, nodes=list(distances.values()))
		
		
	#returns KV_Node_Wrapper
	def FindValue(self, request, context):
		pass

	#Stores KeyValue at current node and returns IDKey
	def Store(self, KeyValue, context):
		if KeyValue.key not in self.hashtable: 		
			self.hashtable[KeyValue.key] = KeyValue
			print("Storing key {:} at value {:}".format(KeyValue.key, KeyValue.value))
		return csci4220_hw3_pb2.IDKey(node=csci4220_hw3_pb2.Node(id=self.id, 
																 port=self.port, 
																 address=self.address), 
									  idkey=KeyValue.key)

	#Quit current node, removes all nodes from current node's kbucket
	def Quit(self, request, context):
		pass

	#updating kbuckets so that requester's id is most recent 
	def __update_kbuckets(self, id):
		found = False
		for i in range(len(self.bucket)):
			for j in range(len(self.bucket[i])):
				if self.bucket[i][j].value == id:
					found = True 
					break
				if found:
					if j+1 != len(self.bucket[i])-1:
						self.bucket[i] = self.bucket[i][:j] + self.bucket[i][j+1:] + [self.bucket[i][j]] 
					else:
						self.bucket[i] = self.bucket[i][:j] + [self.bucket[i][j]]


#Client Implementation
def bootstrap(hostname, port, local_node):
	with grpc.insecure_channel('localhost:' + port) as channel:
		stub = csci4220_hw3_pb2_grpc.KadImplStub(channel)
		stub.FindNode(csci4220_hw3_pb2.IDKey(node=local_node,idkey=local_node.id))
		

def find_node(stub, IDKey):
	print('Serving FindNode(<targetID>) request for <requesterID>')
	print('Before FIND_NODE command, k-buckets are:')
	#PRINT K BUCKETS
	#implement pseudocode from PDF
	print('After FIND_NODE command, k-buckets are:')
	#PRINT K BUCKETS

def find_value(stub, key):
	pass

#store key:value as KeyValue
#	finds and stores to closest node id by key
def store(stub, key, value):
	#Determine where to store key-value pair

	#Print record of storage at location
	print('Storing key {:} at node {:}'.format(key, value))
	#If the key is same as this node Store here
	#Else send key-value pair to appropriate Node
	pass

#quit current node, removes all nodes from current node's kbucket
def Quit(stub):
	pass

def run():
	if len(sys.argv) != 4:
		print("Error, correct usage is {} [my id] [my port] [k]".format(sys.argv[0]))
		sys.exit(-1)

	local_id = int(sys.argv[1])
	my_port = str(int(sys.argv[2])) # add_insecure_port() will want a string
	k = int(sys.argv[3])
	my_hostname = socket.gethostname() # Gets my host name
	my_address = socket.gethostbyname(my_hostname) # Gets my IP address from my hostname
   
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
	csci4220_hw3_pb2_grpc.add_KadImplServicer_to_server(
		KadImplServicer(), server)
	server.add_insecure_port('[::]:' + my_port)
	server.start()

	kbuckets = [[]] * 4

	local_node = csci4220_hw3_pb2.Node(id=local_id,port=my_port,address=my_address)

	while(1):
		inp = input().lower().split()
		print(inp)		
		if (inp[0] == "quit"):
			print("Exited")
			sys.exit(0)
		elif (inp[0] == "boostrap"):
			buckets = bootstrap(inp[1], inp[2], local_node)	
		elif (inp[0] == "find_node"):
			print("Before FIND_NODE command, k-buckets are:")
			print(kbuckets)


	''' Use the following code to convert a hostname to an IP and start a channel
	Note that every stub needs a channel attached to it
	When you are done with a channel you should call .close() on the channel.
	Submitty may kill your program if you have too many file descriptors open
	at the same time. '''
	
	#remote_addr = socket.gethostbyname(remote_addr_string)
	#remote_port = int(remote_port_string)
	#channel = grpc.insecure_channel(remote_addr + ':' + str(remote_port))

if __name__ == '__main__':
	run()
		