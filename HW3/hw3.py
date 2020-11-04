#!/usr/bin/env python3

from socket import close
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
local_node = None
k = 0

#Prints the k_buckets in proper format
def print_k_buckets():
	for i in range(len(k_buckets)):
		print("%d: " % i, end="")
		for j in range(len(k_buckets[i])):
			current = k_buckets[i]
			print("%d:%d" % (current[j].id, current[j].port),end="")
			if (j != len(k_buckets[i])-1):			
				print(" ",end="")
		print()
				
def AddorUpdateNode(node):	

	distance = node.id ^ local_node.id
	bucket = -1
	for i in range(4):
		if (distance < 2**(i+1)) and (distance >= 2**i):
			bucket = i
			break
	
	if node in k_buckets[bucket]:
		temp = k_buckets[bucket].pop(k_buckets[bucket].index(node))
		k_buckets[bucket].append(temp)
	else:
		if len(k_buckets[bucket]) == k:
			k_buckets[bucket].pop(0)
		k_buckets[bucket].append(node)

#Server Implementation
class KadImplServicer(csci4220_hw3_pb2_grpc.KadImplServicer):

	#return NodeList of k closest nodes to given ID
	def FindNode(self, IDKey, context):
		id = IDKey.idkey		
		print("Serving FindNode(%d) request for %d" % (id, IDKey.node.id))

		closest = []
		for i in range(4):		
			closest += k_buckets[i]
		closest = sorted(closest, key=lambda x : id ^ x.id)[:k]

		AddorUpdateNode(IDKey.node)
		return csci4220_hw3_pb2.NodeList(responding_node=local_node, nodes=closest)		
		
	#returns KV_Node_Wrapper
	def FindValue(self, IDKey, context):	
		key = IDKey.idkey
		AddorUpdateNode(IDKey.node)	
		print("Serving FindKey(%d) request for %d" % (IDKey.idkey, IDKey.node.id))
		if key in hash_table.keys():
			value = csci4220_hw3_pb2.KeyValue(key=key, value=hash_table[key])
			return csci4220_hw3_pb2.KV_Node_Wrapper(responding_node=local_node, mode_kv=True, kv=value)

	#Stores KeyValue at current node and returns IDKey
	def Store(self, KeyValue, context):
		AddorUpdateNode(KeyValue.node)
		print("Storing key %d at value \"%s\"" % (KeyValue.key, KeyValue.value))
		hash_table[KeyValue.key] = KeyValue.value
		return csci4220_hw3_pb2.IDKey(node=local_node, idkey=KeyValue.key)
	#Removes the quitting node from the k_bucket
	def Quit(self, IDKey, context):
		id = IDKey.idkey
		for i in range(len(k_buckets)):
			if IDKey.node in k_buckets[i]:
				print("Evicting quitting node %d from bucket %d" % (id, i))
				k_buckets[i].remove(IDKey.node)
		return IDKey	

#Client Implementation

#Bootstraps the current Node with another desired node
def Bootstrap(hostname, port):
	remote_addr = socket.gethostbyname(hostname)
	remote_port = port
	with grpc.insecure_channel("%s:%s" % (remote_addr,remote_port)) as channel:
		stub = csci4220_hw3_pb2_grpc.KadImplStub(channel)
		ret = stub.FindNode(csci4220_hw3_pb2.IDKey(node=local_node,idkey=local_node.id))		
		for i in ret.nodes:
			AddorUpdateNode(i)
		AddorUpdateNode(ret.responding_node)		
		print("AFTER BOOTSTRAP(%d), k_buckets now look like:" % ret.responding_node.id)
		print_k_buckets()

def Find_Node(nodeID):
	if nodeID == local_node.id:
		print("Found destination id %d" % nodeID)
	else:
		for i in k_buckets:
			if i.id == nodeID:
				print("Found desination id %d" % nodeID)
				return

		for s in k_buckets:			
			for node in s:
				with grpc.insecure_channel("%s:%d" % (node.address, node.port)) as channel:
					stub = csci4220_hw3_pb2_grpc.KadImplStub(channel)
					stub.FindNode(csci4220_hw3_pb2.IDKey(node=local_node,idkey=nodeID))
	

def Find_Value(key):
	if key in hash_table.keys():
		print("Found data \"%s\" for key %d" % (hash_table[key], key))
	else:
		closest = []
		for i in k_buckets:
			closest += i
		closest = sorted(closest, key=lambda x : key ^ x.id)

		for i in closest:
			pass

#store key:value as KeyValue
#	finds and stores to closest node id by key
def Store(key, value):
	distance = local_node.id ^ key
	closest = local_node
	for i in k_buckets:
		for j in i:
			if j.id ^ key < distance:
				distance = j.id ^ key
				closest = j
	print("Storing key %d at node %d" % (key, closest.id))
	if closest == local_node:
		hash_table[key] = value		
	else:			
		with grpc.insecure_channel("%s:%d" % (closest.address, closest.port)) as channel:
			stub = csci4220_hw3_pb2_grpc.KadImplStub(channel)
			stub.Store(csci4220_hw3_pb2.KeyValue(node=local_node, key=key, value=value))

#quit current node, removes all nodes from current node's kbucket
def Quit():
	for i in k_buckets:
		for j in i:
			print("Letting %d know im quitting." % j.id)
			with grpc.insecure_channel("%s:%d" % (j.address,j.port)) as channel:
				stub = csci4220_hw3_pb2_grpc.KadImplStub(channel)
				stub.Quit(csci4220_hw3_pb2.IDKey(node=local_node, idkey=local_node.id))

def run():
	global local_node
	global k
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
		KadImplServicer(), server)
	server.add_insecure_port('[::]:' + my_port)
	server.start()

	while(1):
		inp = input().split()
		if inp[0] == "QUIT":
			Quit()
			print("Shutdown node %d" % local_id)
			sys.exit(0)
		elif inp[0] == "BOOTSTRAP":
			Bootstrap(inp[1], inp[2])
		elif inp[0] == "FIND_NODE":
			print("Before FIND_NODE command, k-buckets are:")
			print_k_buckets()
		elif inp[0] == "FIND_VALUE":
			Find_Value(int(inp[1]))
		elif inp[0] == "STORE":
			Store(int(inp[1]), inp[2])
		else:
			print("Invalid arguement!")

if __name__ == '__main__':
	run()
		