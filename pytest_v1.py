#TODO : find the right multiplication factor - have increased it from 1.4 to 1.5 for now 

import pytest
import math
import cProfile
import hashlib
import sys 

from iblt_xor import IBLT
from time import time

xfail = pytest.mark.xfail
# Returning list after subtraction and not the time taken
# Third argument is the percentage of smaller set which intersects which the larger one
def make_iblt(len1, len2,percentage_intersection):

	if percentage_intersection > 100 or percentage_intersection < 0:
		raise NameError('Percentage should lie between 0 and 100 ')		
	if len1 >= len2 :
		pairs1 = [( hashlib.md5("key%d" % i).hexdigest(), hashlib.sha1("value%d" % i).hexdigest() ) for i in range(len1)]
		intersection = int(percentage_intersection*len2*.01)
		pairs2 = [( hashlib.md5("key%d" % i).hexdigest(), hashlib.sha1("value%d" % i).hexdigest() ) for i in range(intersection)]
		for x in range(len1, len1+len2-int(intersection)):
			pairs2.append(( hashlib.md5("key%d" % x).hexdigest(), hashlib.sha1("value%d" % x).hexdigest() ))
	else :
		pairs2 = [( hashlib.md5("key%d" % i).hexdigest(), hashlib.sha1("value%d" % i).hexdigest() ) for i in range(len2)]
		intersection = int(percentage_intersection*len1)
		pairs1 = [( hashlib.md5("key%d" % i).hexdigest(), hashlib.sha1("value%d" % i).hexdigest() ) for i in range(intersection)]
		for x in range(len2, len2+len1-intersection):
			pairs1.append(( hashlib.md5("key%d" % x).hexdigest(), hashlib.sha1("value%d" % x).hexdigest() ))

	start = time()
	size_iblt = (len1+len2- 2*intersection)*1.4
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

	#print t1.T
	#print t2.T
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

#@xfail(reason="unknown")
def test(): 
	for percent in range(0, 100, 10):
		for db1 in range(10, 100, 10):
			for db2 in range(10, 100, 10):
				# If the difference between databses is lesser than 30% of the larger database then go with the IBLT approach
				intersection = int(min(db1,db2)*percent*.01)	
				if (int(max(db1, db2)*.3) >= db1+db2-2*intersection):
					print "IBLT db1 db2 percent intersection ", db1, db2, percent ,intersection
					assert make_iblt(db1, db2, percent)[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE
				else:
					print "full DB", db1, db2, percent, intersection
					result = full_db(db1, db2)
test()
if (sys.argv[0] == "pytest_v1.py") and (len(sys.argv) > 2) :
	assert make_iblt(int(sys.argv[1]), int(sys.argv[2]))[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE




