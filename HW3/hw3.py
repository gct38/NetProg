#!/usr/bin/env python3

from threading import local
from csci4220_hw3_pb2_grpc import KadImplServicer
from concurrent import futures
import sys  # For sys.argv, sys.exit()
import socket  # for gethostbyname()

import grpc

import csci4220_hw3_pb2
import csci4220_hw3_pb2_grpc

k_buckets = [[], [], [], []]
hash_table = dict()

#Prints the k_buckets in proper format
def print_k_buckets(k_buckets):
	for i in range(len(k_buckets)):
		print("%d: " % i, end="")
		for j in range(len(k_buckets[i])):
			current = k_buckets[i]
			print("%d : %d" % (current[j].id, current[j].port),end="")
			if (j != len(k_buckets[i])-1):			
				print(" ",end="")
		print()
				
def AddNode(node, local_node, k):
	distance = node.id ^ local_node.id
	bucket = 0
	for i in range(4):
		if (distance < 2**(i+1)) and (distance > 2**i):
			bucket = i
			break	

	if len(k_buckets[bucket]) == k:
		k_buckets[bucket].pop(0)
	k_buckets[bucket].append(node)

#Server Implementation
class KadImplServicer(csci4220_hw3_pb2_grpc.KadImplServicer):

	def __init__(self, node, k):
		self.node = node
		self.k = k

	#return NodeList of k closest nodes to given ID
	def FindNode(self, IDKey, context):
		id = IDKey.idkey
		print("Serving FindNode(%d) request for %d" % (id, IDKey.node.id))
		if id == IDKey.node.id:			
			temp = []
			for i in k_buckets:
				temp += i
			AddNode(IDKey.node, self.node, self.k)
			return csci4220_hw3_pb2.NodeList(responding_node=self.node, nodes=temp+[self.node])
		
		closest = []
		for b in range(0,3):
			closest = sorted(self.kbuckets[b], key=lambda x : id ^ x.id)[:self.k]		

		return csci4220_hw3_pb2.NodeList(responding_node=self.node, nodes=closest)		
		
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
	#Evicts the quitting node from the k_bucket
	def Quit(self, IDKey, context):
		id = IDKey.id
		found = False
		i = 0
		while not found and i < 4:
			new_bucket = []
			for j in k_buckets[i]:
				if j.id == id:
					print("Evicting node %d from bucket %d" % (id, i))
					found = True
					continue
				new_bucket.append(j)
			k_buckets[i] = new_bucket
			i += 1
		return IDKey

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

#Bootstraps the current Node with another desired node
def Bootstrap(hostname, port, local_node, k):
	remote_addr = socket.gethostbyname(hostname)
	remote_port = port
	with grpc.insecure_channel("%s:%s" % (remote_addr,remote_port)) as channel:
		stub = csci4220_hw3_pb2_grpc.KadImplStub(channel)
		ret = stub.FindNode(csci4220_hw3_pb2.IDKey(node=local_node,idkey=local_node.id))
		print("AFTER BOOTSTRAP(%d), k_buckets now look like:" % ret.responding_node.id)		
		for i in ret.nodes:
			AddNode(i, local_node, k)
		print_k_buckets(k_buckets)

def Find_Node(IDKey):
	pass

def Find_Value(stub, key):	
	pass

#store key:value as KeyValue
#	finds and stores to closest node id by key
def Store(stub, key, value):
	#TODO Determine where to store key-value pair
	#TODO Print record of storage at location
	pass	

#quit current node, removes all nodes from current node's kbucket
def Quit(node):
	for i in k_buckets:
		for j in i:
			print("Letting %d know im quitting." % j.id)
			with grpc.insecure_channel("%s:%d" % (j.address,j.port)) as channel:
				stub = csci4220_hw3_pb2_grpc.KadImplStub(channel)
				stub.Quit(csci4220_hw3_pb2.IDKey(node=node,idkey=node.id))

def run():
	if len(sys.argv) != 4:
		print("Error, correct usage is {} [my id] [my port] [k]".format(sys.argv[0]))
		sys.exit(-1)

	local_id = int(sys.argv[1])
	my_port = str(int(sys.argv[2])) # add_insecure_port() will want a string
	k = int(sys.argv[3])
	my_hostname = socket.gethostname() # Gets my host name
	my_address = socket.gethostbyname(my_hostname) # Gets my IP address from my hostname  

	local_node = csci4220_hw3_pb2.Node(id=local_id,port=int(my_port),address=my_address) 
	
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
	csci4220_hw3_pb2_grpc.add_KadImplServicer_to_server(
		KadImplServicer(local_node, k), server)
	server.add_insecure_port('[::]:' + my_port)
	server.start()

	while(1):
		inp = input().split()
		if inp[0] == "QUIT":
			Quit(local_node)
			print("Shutdown node %d" % local_id)
			sys.exit(0)
		elif inp[0] == "BOOTSTRAP":
			buckets = Bootstrap(inp[1], inp[2], local_node, k)	
		elif inp[0] == "FIND_NODE":
			print("Before FIND_NODE command, k-buckets are:")
			print_k_buckets(k_buckets)
		elif inp[0] == "FIND_VALUE":
			print("Before FIND_VALUE command, k-buckets are:")
			print_k_buckets(k_buckets)
		elif inp[0] == "STORE":
			continue

if __name__ == '__main__':
	run()
		