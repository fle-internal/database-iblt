import hashlib, math, struct
import sys 
import re
import cProfile
import json

from copy import deepcopy
from time import time 

SIZE_KEY = 32
SIZE_VAL = 40

def fnv_1a ( octet ) :
	result = 2166136261
	for num in octet :
		result ^= num
		result *= 16777619
	return result

def format (str, size) :
	"""
	returns formatted string by removing 0x,L from ends and filling 0's if string smaller than size
	"""
	return hex(str)[2:-1].zfill(size)

def md5 (str) :
	"""
	Returns the hex representation of a string's md5 encryption
	"""
	return hashlib.md5(str).hexdigest()

def sha1 (str) :
	"""
	Returns the hex representation of a string's sha1 encryption
	"""	
	return hashlib.sha1(str).hexdigest()

def hex_string_to_ascii (hex_string) :
	"""
	Returns ASCII representation of the hex value, assuming lengh supplied is even
	"""	
	list_char = []
	for i in range(0, len(hex_string),2) :
		list_char.append(chr(hex_string[i:i+2]))	
	return ''.join(list_char)


def deserialize ( file_name ) :
	"""
	Retrieve IBLT and its metadata from received json file
	"""
	with open(file_name) as json_file:
    		json_data = json.load(json_file)
		new_iblt = IBLT(json_data["Metadata"][0], json_data["Metadata"][1], json_data["IBLT"])

class IBLT:
	# m is amount of cells in underlying lookup tables
	m = None
	# k is amount of hash functions
	k = None

	RESULT_GET_NO_MATCH = "no_match"
	RESULT_GET_MATCH = "match"
	RESULT_GET_DELETED_MATCH = "deleted_match"
	RESULT_GET_INCONCLUSIVE = "inconclusive"
	RESULT_LIST_ENTRIES_COMPLETE = "complete"
	RESULT_LIST_ENTRIES_INCOMPLETE = "incomplete"

	def __init__( self, m, k,T=None):
		self.m = m	
		self.k = k
		if T == None:	
			self.T = [[0,0,0,0] for i in range( m )]
		else :
			self.T = deepcopy( T )
	
	def __int_of_fracStr(self, tup, low, high) :
		octet = []
		for i in range(1,5):	
			octet.append(int(tup[0][low:low+i*2], 16)^int(tup[1][low:low+i*2], 16))
		return fnv_1a(octet)%self.m

	def __hash(self, i, tup) :
		"""
		hash( i, tuple) where i is index of hash function, tuple is key-value pair to be hashed
		Assuming there are no more than 4 hash functions, according to the paper
		"""
		if i == 0 :
			return self.__int_of_fracStr(tup, 0, 8)
		elif i == 1 :
			return self.__int_of_fracStr(tup, 8, 16)
		elif i == 2 :
			return self.__int_of_fracStr(tup, 16, 24)
		else :
			return self.__int_of_fracStr(tup, 24, 32)

	def _xor_tuple(self, tuple, operation):
		"""
		helper function for insert and delete functions	
		"""
		indices = set( [self.__hash( i, tuple ) for i in range( self.k ) ] )
		T = self.T
		#if operation == "insert":
		#	print indices
		for index in indices:
			if operation == "insert" : 
				# Increase count
				T[index][0] += 1
	 		elif operation == "delete" :
				# Decrease count
				T[index][0] -= 1
		      	T[index][1] = T[index][1]^int(tuple[0], 16)
                        T[index][2] = T[index][2]^int(tuple[1], 16)
			T[index][3] = T[index][3]^int(md5(tuple[0]), 16)
		
	def insert( self, tuple ):
		"""
		Insert the tuple into IBLT	
		"""
		self._xor_tuple(tuple, "insert")

	def delete( self, tuple ):
		"""
		Delete the tuple from IBLT	
		"""
		self._xor_tuple(tuple, "delete")

	def subtract_inplace (self, other_iblt):
		for i in range(0, len(self.T)):
			self.T[i][0] = self.T[i][0] - other_iblt[i][0]
			self.T[i][1] = self.T[i][1] ^ other_iblt[i][1]	
			self.T[i][2] = self.T[i][2] ^ other_iblt[i][2]
			self.T[i][3] = self.T[i][3] ^ other_iblt[i][3]
	        return self.T	
	
	def list_entries( self ):
		"""
		Tries to list all entries in the table.
		Returns ( <Result>, [<Normal entries>], [<Deleted entries>] )
		where <Result> is either IBLT.RESULT_LIST_ENTRIES_COMPLETE to indicate that the list is complete,
		or IBLT.RESULT_LIST_ENTRIES_INCOMPLETE to indicate that some entries couldn't be recovered
		"""
		dummy = IBLT(self.m, self.k, self.T)
		entries = []
		deleted_entries = []
		while True:	
			for i in range( len( dummy.T ) ):
				entry = dummy.T[i]
				if entry[0] == 1 or entry[0] == -1:
					retrieved_tup = (format(entry[1], SIZE_KEY), format(entry[2], SIZE_VAL))
					hashed_key = int(md5(retrieved_tup[0]), 16)  
					if entry[0] == 1 and entry[3] == hashed_key: 
						entries.append(retrieved_tup)
						dummy.delete(retrieved_tup)
						break 
					elif entry[0] == -1 and entry[3] == hashed_key:
						deleted_entries.append(retrieved_tup)
						dummy.insert(retrieved_tup)
						break
			else :
				break
		if not dummy.is_empty() :
			return ( IBLT.RESULT_LIST_ENTRIES_INCOMPLETE, entries, deleted_entries )
		return ( IBLT.RESULT_LIST_ENTRIES_COMPLETE, entries, deleted_entries )

	def is_empty( self ):
		"""
		Returns true if the table is completely empty, i.e. no contains no entries,
		inserted or deleted
		"""
		return all( map( lambda e: e[0] == 0 and e[1]== 0, self.T ) )

	def serialize( self ):
		"""
		Create json object for sending, include the magic bytes and the name of the json file?	
		"""
		dummy_dict = {}	
		dummy_dict["Metadata"] = [self.m, self.k]
		dummy_dict["IBLT"] = self.T
		dummy_dict = json.dumps(dummy_dict)
		f = open('iblt.json','w')
		f.write(dummy_dict)
		f.close()
		#print dummy_dict


