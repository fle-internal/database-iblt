#TODO : find the right multiplication factor - have increased it from 1.4 to 1.5 for now 

import pytest
import math
import cProfile
import hashlib

from iblt_xor import IBLT
from time import time

xfail = pytest.mark.xfail
# Returning list after subtraction and not the time taken
def make_iblt(len1, len2):

	pairs1 = [( hashlib.md5("key%d" % i).hexdigest(), hashlib.sha1("value%d" % i).hexdigest() ) for i in range(len1)]
	pairs2 = [( hashlib.md5("key%d" % i).hexdigest(), hashlib.sha1("value%d" % i).hexdigest() ) for i in range(len2)]
	start = time()
	size_iblt = abs(len1-len2)*1.5
	#print "size of IBLT", size_iblt
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
	# Converting dictionary to lists
	entries = dict_a_minus_b.items()
	deleted_entries = dict_b_minus_a.items()
	#return end-start
	return (entries, deleted_entries)


@xfail(reason="unknown")
def test() :
	for db1 in range(10, 100, 10):
		for db2 in range(10, 100, 10):
			# If the difference between databses is lesser than 30% of the larger database then go with the IBLT approach
			if (int(max(db1, db2)*.3) >= abs(db1 - db2)):
				#print "IBLT", db1, db2
				assert make_iblt(db1, db2)[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE
			else:
				#print "full DB", db1, db2
				result = full_db(db1, db2)

