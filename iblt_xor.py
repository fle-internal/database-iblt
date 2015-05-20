import hashlib, math, struct
import sys 
import re
from copy import deepcopy
from time import time 
import cProfile

SIZE_KEY = 32
SIZE_VAL = 40

#Returns formatted string by removing 0x,L from ends and filling 0's if string smaller than size
def format (str, size) :
	return hex(str)[2:-1].zfill(size)

#Return the hex representation of a string's md5 encryption
def md5 (str) :
	return hashlib.md5(str).hexdigest()

#Return the hex representation of a string's sha1 encryption
def sha1 (str) :
	return hashlib.sha1(str).hexdigest()

#Assuming that the string supplied has an even length
def hex_string_to_ascii (hex_string) :
	list_char = []
	for i in range(0, len(hex_string),2) :
		list_char.append(chr(hex_string[i:i+2]))	
	return ''.join(list_char)


class IBLT:
	# m is amount of cells in underlying lookup tables
	m = None
	# k is amount of hash functions
	k = None
	# hash is function( i, tuple) where i is index of hash function
	# and tuple is key-value pair to be hashed
	hash = None

	RESULT_GET_NO_MATCH = "no_match"
	RESULT_GET_MATCH = "match"
	RESULT_GET_DELETED_MATCH = "deleted_match"
	RESULT_GET_INCONCLUSIVE = "inconclusive"
	RESULT_LIST_ENTRIES_COMPLETE = "complete"
	RESULT_LIST_ENTRIES_INCOMPLETE = "incomplete"

	def __init__( self, m, k,T=None, hash=None):
		self.m = m	
		self.k = k
		self.hash = self.__hash
		if T == None:	
			self.T = [[0,0,0,0] for i in range( m )]
		else :
			self.T = deepcopy( T )
		
	def _xor_tuple(self, tuple, operation):
		indices = set( [self.hash( i, tuple ) for i in range( self.k ) ] )
		T = self.T
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
		self._xor_tuple(tuple, "insert")

	def delete( self, tuple ):
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
						#raise NameError('The hashed key does not match the hash(key)')
						entries.append(retrieved_tup)
						dummy.delete(retrieved_tup)
						break 
					elif entry[0] == -1 and entry[3] == hashed_key:
						#raise NameError('The hashed key does not match the hash(key)')
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
		Serialize the IBLT for storage or transfer.
		Data format:
			[ Magic bytes ][  Header ][ Data ]
		    	4 bytes      6 bytes    
		Magic bytes: 
			0x49 0x42 0x4C 0x54 (ASCII for IBLT)
		Header:
			[ Cell count (m) ]
			  	32-bit uint
			[ Key sum length ][ Value sum length ]
			  	32-bit uint			32-bit uint
			[ HashKeySum length ][ ValueKeySum length ]
				32-bit uint				32-bit uint
			[ # hash funcs (k) ]
				32-bit uint
		Data:
			For each of the m cells:
				[ 	Count 	 ][ keySum ][ valueSum ][ hashKeySum ][ valueKeySum ]
				  32-bit int
		"""
		magic = struct.pack( ">I", 0x49424C54 )
		header = struct.pack( ">IIIIII", self.m, self.key_size, self.value_size, 
										 self.hash_key_sum_size, 0, self.k )
		data = ""
		for cell in self.T:
			# Count (32-bit signed int)
			data += struct.pack( ">i", cell[0] )
			# keySum
			data += "".join( map( lambda n: struct.pack( ">B", n ), cell[1] ) )
			# valueSum
			data += "".join( map( lambda n: struct.pack( ">B", n ), cell[2] ) )
			# hashKeySum
			data += "".join( map( lambda n: struct.pack( ">B", n ), cell[3] ) )

		return magic + header + data

	@staticmethod
	def unserialize( data ):
		header = struct.unpack( ">IIIIIII", data[:(4*7)] )
		magic = header[0]
		if magic != 0x49424C54:
			raise Exception( "Invalid magic value" )

		m, key_size, value_size, hash_key_sum_size, hash_value_sum_size, k = header[1:7]
		t = IBLT( m, k, key_size, value_size, hash_key_sum_size )

		expected_data_length = m * ( 4 + key_size + value_size + hash_key_sum_size + hash_value_sum_size )
		if len( data ) - 28 != expected_data_length:
			raise Exception( "Invalid data size: Expected %d, was %d" % ( expected_data_length, len( data ) - 28 ) )

		# 4 x 7 bytes offset from magic value and header
		offset = 28
		for i in range( m ):
			t.T[i][0] = struct.unpack( ">i", data[offset:offset+4])[0]
			offset += 4
			t.T[i][1] = map( lambda c: struct.unpack( ">B", c )[0], data[offset:offset+key_size] )
			offset += key_size
			t.T[i][2] = map( lambda c: struct.unpack( ">B", c )[0], data[offset:offset+value_size] )
			offset += value_size
			t.T[i][3] = map( lambda c: struct.unpack( ">B", c )[0], data[offset:offset+hash_key_sum_size] )
			offset += hash_key_sum_size

		return t

	def get_serialized_size( self ):
		# Magic bytes
		result = 4
		# Header
		result += 6 * 4
		# Cells
		result += self.m * ( 4 + self.key_size + self.value_size + self.hash_key_sum_size )
		return result

	def __int_of_fracStr(self, tup, low, high) :
		return (int(tup[0][low:high], 16)^int(tup[1][low:high], 16))% self.m

	# Assuming there are no more than 4 hash functions, according to the paper
	def __hash(self, i, tup) :
		if i == 0 :
			return self.__int_of_fracStr(tup, 0, 8)
		elif i == 1 :
			return self.__int_of_fracStr(tup, 8, 16)
		elif i == 2 :
			return self.__int_of_fracStr(tup, 16, 24)
		else :
			return self.__int_of_fracStr(tup, 24, 32)

