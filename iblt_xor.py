import hashlib, math, struct
import sys 
import re
from copy import deepcopy
from time import time 
import cProfile

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
	# hash is function( i, value ), where i is index of hash function
	# and value is value to be hashed
	hash = None

	empty_key_array = None
	empty_hash_sum_array = None

	RESULT_GET_NO_MATCH = "no_match"
	RESULT_GET_MATCH = "match"
	RESULT_GET_DELETED_MATCH = "deleted_match"
	RESULT_GET_INCONCLUSIVE = "inconclusive"
	RESULT_LIST_ENTRIES_COMPLETE = "complete"
	RESULT_LIST_ENTRIES_INCOMPLETE = "incomplete"

	def __init__( self, m, k,hash=None ):
		"""
		m is the amount of cells in underlying lookup table
		k is the amount of hash functions
		key_size is maximum size for keys
		value_size is maximum size for values
		hash_key_sum_size is amount of bytes used for the hashkeySum field
		hash is function( i, value ), where i is index of hash function
		    and value is value to be hashed (or None for default hash functions)
	 	"""	
		self.m = m	
		self.k = k
		self.hash = hash if hash is not None else self.__hash

		self.T = [[0,0,0,0] for i in range( m )]
       		self.empty_key_array = 0 
		self.empty_hash_sum_array = 0 

		
	def insert( self, T, key, value ):
		indices = set( [self.hash( i, key ) for i in range( self.k ) ] )
		for index in indices:
			# Increase count
			T[index][0] += 1
			# Add key to keySum
	        	T[index][1] = T[index][1]^int(key, 16)
                        # Add value to valueSum
                        T[index][2] = T[index][2]^int(value, 16)
                        # Add key hash to hashkeySum
			hashed_key = hashlib.md5(key).hexdigest()
			T[index][3] =  T[index][3]^int(hashed_key, 16)


	def delete( self, T, key, value ):
		indices = set( [self.hash( i, key ) for i in range( self.k ) ] )
		for index in indices:
			# Decrease count
                        T[index][0] -= 1
                        # Subtract key from keySum
                        T[index][1] = T[index][1]^int(key, 16)
                        # Subtract value from valueSum
                        T[index][2] = T[index][2]^int(value, 16)
			# Subtract key hash from hashkeySum
			hashed_key = hashlib.md5(key).hexdigest()
			T[index][3] =  T[index][3]^int(hashed_key, 16)

	def add( self, T, key, value ):
		indices = set( [self.hash( i, key ) for i in range( self.k ) ] )
		for index in indices:
			#increase count
                        T[index][0] += 1
                        # Subtract key from keySum
                        T[index][1] = T[index][1]^int(key, 16)
                        # Subtract value from valueSum
                        T[index][2] = T[index][2]^int(value, 16)
			# Subtract key hash from hashkeySum
			hashed_key = hashlib.md5(key).hexdigest()
			T[index][3] =  T[index][3]^int(hashed_key, 16)

	def subtract (self, arr1, arr2):
		for i in range(0, len(arr1)):
			arr1[i][0] = arr1[i][0] - arr2[i][0]
			arr1[i][1] = arr1[i][1] ^ arr2[i][1]	
			arr1[i][2] = arr1[i][2] ^ arr2[i][2]
			arr1[i][3] = arr1[i][3] ^ arr2[i][3]
	        return arr1	

	def get( self, key ):
		"""
		Try to get a value from the table with the given key.
		This function can return four different responses:
		( IBLT.RESULT_GET_NO_MATCH, None ): The key was definitively not in the table
		( IBLT.RESULT_GET_MATCH, <Value> ): The key was in the table and the value is returned
		( IBLT.RESULT_GET_DELETED_MATCH, <Value> ): The key was deleted without being inserted
		( IBLT.RESULT_GET_INCONCLUSIVE, None ): It couldn't be determined if the key was in the table or not
		"""
		indices = set( [self.hash( i, key ) for i in range( self.k ) ] )
		for index in indices:
			if self.T[index][0] == 0 and self.T[index][1] == 0 and self.T[index][3] == 0:  
				return ( IBLT.RESULT_GET_NO_MATCH, None )
			elif self.T[index][0] == 1 and self.T[index][1] == key and \
					self.T[index][3] == hashlib.md5(key).hexdigest():
				return ( IBLT.RESULT_GET_MATCH, self.T[index][2] )
			elif self.T[index][0] == -1 and self.T[index][1] == key and \
                			self.T[index][3] == hashlib.md5(key).hexdigest(): 
				return ( IBLT.RESULT_GET_DELETED_MATCH, self.T[index][2] )
		return ( IBLT.RESULT_GET_INCONCLUSIVE, None )

	def list_entries( self ):
		"""
		Tries to list all entries in the table.
		Returns ( <Result>, [<Normal entries>], [<Deleted entries>] )
		where <Result> is either IBLT.RESULT_LIST_ENTRIES_COMPLETE to indicate that the list is complete,
		or IBLT.RESULT_LIST_ENTRIES_INCOMPLETE to indicate that some entries couldn't be recovered
		"""
		T = deepcopy( self.T )
		entries = []
		deleted_entries = []
		check = 1 
		while check > 0 :	
			check = 0	
			for i in range( len( T ) ):
				entry = T[i]
				if entry[0] == 1 or entry[0] == -1:
					check = 1	
					if entry[0] == 1 : 
						if entry[3] == int(hashlib.md5(hex(entry[1])[2:-1].zfill(32)).hexdigest(),16) :
							#raise NameError('The hashed key does not match the hash(key)')
							#print "The hashed key does not match the hash(key)"
						#else :
						        #Should be this because this is the key and value being passed 
							#entries.append(str(hex(entry[1])[2:-1].zfill(32), hex(entry[2])[2:-1].zfill(32)))
							#The way in which entries are stored in the IBLT			
							entries.append((str(entry[1]), str(entry[2])))
							self.delete(T, hex(entry[1])[2:-1].zfill(32), hex(entry[2])[2:-1].zfill(32))

					elif entry[0] == -1 :
						# make same changes as above in entries.append
						if entry[3] == int(hashlib.md5(hex(entry[1])[2:-1].zfill(32)).hexdigest(),16): 
							#raise NameError('The hashed key does not match the hash(key)')
							#print "The hashed key does not match the hash(key)"
						#else :
							deleted_entries.append((str(entry[1]), str(entry[2])))
							self.add(T, hex(entry[1])[2:-1].zfill(32), hex(entry[2])[2:-1].zfill(32))

		if any( filter( lambda e: e[0] != 0, T ) ):
			return ( IBLT.RESULT_LIST_ENTRIES_INCOMPLETE, entries, deleted_entries )
		return ( IBLT.RESULT_LIST_ENTRIES_COMPLETE, entries, deleted_entries )

	def is_empty( self ):
		"""
		Returns true if the table is completely empty, i.e. no contains no entries,
		inserted or deleted
		"""
		return all( map( lambda e: e[0] == 0, self.T ) )

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


	# Assuming there are no more than 4 hash functions, according to the paper
	def __hash(self, i, value) :
		if i == 0 :
			return int(value[0:8], 16)%self.m
		elif i == 1 :
			return int(value[8:16], 16)%self.m
		elif i == 2 :
			return int(value[16:24], 16)%self.m
		else :
			return int(value[24:32], 16)%self.m

