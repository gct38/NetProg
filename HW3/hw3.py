#!/usr/bin/env python3

from csci4220_hw3_pb2_grpc import KadImplServicer
from concurrent import futures
import sys  # For sys.argv, sys.exit()
import socket  # for gethostbyname()

import grpc

import csci4220_hw3_pb2
import csci4220_hw3_pb2_grpc

#TODO: implement container for k-buckets

#Server Implementation
class KadImplServicer(csci4220_hw3_pb2_grpc.KadImplServicer):
	def __init__(self, local_id, port, k):
		self.id = local_id
		self.port = port
		self.k = k
		self.nodes = dict() #dict of all nodes key=id, val=Node

	#return NodeList of k closest nodes to given ID
	def FindNode(self, IDKey, context):
		idkey = IDKey.idkey
		distances = dict() #key=id, value=distance
		responder = None
		for id in self.nodes:
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

		#creating NodeList from distances dict
		#TODO: implement NodeList, don't think nodes parameter is right
		return csci4220_hw3_pb2.NodeList(responding_node=responder, nodes=list(distances.values()))
		
		
	#returns KV_Node_Wrapper
	def FindValue(self, request, context):
		pass

	#Stores KeyValue at node w/ ID closest to Key
	def Store(self, KeyValue, context):
		difference = float('inf')
		insert = None
		for node in self.nodes:
			if abs(node - KeyValue.key) < difference:
				difference = abs(node - KeyValue.key)
				insert = node 
		#TODO: code to insert KeyValue into kbucket

		

	#quit current node, removes all nodes from current node's kbucket
	def Quit(self, request, context):
		pass



	#finds distance using XOR between 2 IDs
	def __distance(self, id1, id2=self.id):
		return id1 ^ id2


	


#Client Implementation
def bootstrap(stub, host, port):
	pass

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
#	stores to closest node id by key
def store(stub, key, value):
	pass

#quit current node, removes all nodes from current node's kbucket
def quit(stub):
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
	server.wait_for_termination()

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
		