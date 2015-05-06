#TODO : find the right multiplication factor - have increased it from 1.4 to 1.5 for now 

import math
import cProfile
import hashlib

#from iblt_old import IBLT_OLD
from iblt_xor import IBLT
from time import time

# Returning list after subtraction and not the time taken
def make_iblt(len1, len2):

	pairs1 = [( hashlib.md5("key%d" % i).hexdigest(), hashlib.sha1("value%d" % i).hexdigest() ) for i in range(len1)]
	pairs2 = [( hashlib.md5("key%d" % i).hexdigest(), hashlib.sha1("value%d" % i).hexdigest() ) for i in range(len2)]
	start = time()
	size_iblt = abs(len1-len2)*1.5
	if size_iblt == 0:
		size_iblt =1
		t1 = IBLT(int(math.ceil(size_iblt)), 1)
		t2 = IBLT(int(math.ceil(size_iblt)), 1)
	elif size_iblt < 4:
		t1 = IBLT(int(math.ceil(size_iblt)),int(math.ceil(size_iblt)))
		t2 = IBLT(int(math.ceil(size_iblt)),int(math.ceil(size_iblt)))
	else :

		t1 = IBLT(int(math.ceil(size_iblt)), 4)
		t2 = IBLT(int(math.ceil(size_iblt)), 4)

	for key, value in pairs1:
	   	t1.insert( t1.T, key, value )

	for key, value in pairs2:
        	t2.insert( t2.T, key, value )

	t1.subtract(t1.T,t2.T)
	entries = t1.list_entries()
	end = time()
	return entries 

"""
def make_iblt_old(len1, len2):

        size_iblt = abs(len1-len2)*1.4
        if size_iblt < 6:
                size_iblt =6
        t1 = IBLT(int(math.ceil(size_iblt)), 4, 10, 10)
        t2 = IBLT(int(math.ceil(size_iblt)), 4, 10, 10)

        start = time()
        pairs1 = [( "key%d" % i, "value%d" % i ) for i in range(len1)]
        for key, value in pairs1:
                t1.insert( key, value )
        pairs2 = [( "key%d" % i, "value%d" % i ) for i in range(len2)]
        for key, value in pairs2:
                t2.insert( key, value )

        t1.subtract(t1.T,t2.T)
        end = time()
        #print t1.list_entries()
        return end-start

	pairs1 = [( hashlib.md5("key%d" % i).hexdigest(), hashlib.sha1("value%d" % i).hexdigest() ) for i in range(len1)]
	pairs2 = [( hashlib.md5("key%d" % i).hexdigest(), hashlib.sha1("value%d" % i).hexdigest() ) for i in range(len2)]
	start = time()
	size_iblt = abs(len1-len2)*1.4
	if size_iblt == 0:
		size_iblt =1
		t1 = IBLT_OLD(int(math.ceil(size_iblt)), 1)
		t2 = IBLT_OLD(int(math.ceil(size_iblt)), 1)
	elif size_iblt < 4:
		t1 = IBLT_OLD(int(math.ceil(size_iblt)),int(math.ceil(size_iblt)))
		t2 = IBLT_OLD(int(math.ceil(size_iblt)),int(math.ceil(size_iblt)))
	else :

		t1 = IBLT_OLD(int(math.ceil(size_iblt)), 4)
		t2 = IBLT_OLD(int(math.ceil(size_iblt)), 4)

	for key, value in pairs1:
	   	t1.insert( t1.T, key, value )

	for key, value in pairs2:
        	t2.insert( t2.T, key, value )
	
	t1.subtract(t1.T,t2.T)
	t1.list_entries()
	end = time()
	
	#return end - start
"""

# Returns the absolute value of the argument passed
def abs(num):
	if num < 0 :
		return num*-1
	else :
		return num

# Calculates the set difference by sending full database instead of IBLT
# Assuming that the dbs given to us are not in the form of dictionaries, we create 2 dictionaries
# insert values and then find out the difference between them 
def full_db(len1, len2):

	pairs1 = [( hashlib.md5("key%d" % i).hexdigest(), hashlib.sha1("value%d" % i).hexdigest() ) for i in range(len1)]
	pairs2 = [( hashlib.md5("key%d" % i).hexdigest(), hashlib.sha1("value%d" % i).hexdigest() ) for i in range(len2)]
	start = time()
	dict_a = {}

	for key, value in pairs1:
	     	dict_a.update({key: value })

	dict_b = {}
	for key, value in pairs2:
        	dict_b.update({key: value })

	dict_a_minus_b = {}
	dict_b_minus_a = {}
	for key in dict_a :
		if not(dict_b.has_key(key)):
			dict_a_minus_b.update({key:dict_a[key]})	
	for key in dict_b :
		if not(dict_a.has_key(key)):
			dict_b_minus_a.update({key:dict_b[key]}) 
	end = time()
	#return end-start
	#return dict_a_minus_b
	return dict_b_minus_a

result1 = full_db(10, 11)
print result1
result = make_iblt(10,11)
assert result[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE
