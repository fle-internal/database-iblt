#TODO : find the right multiplication factor - have increased it from 1.4 to 1.5 for now 

import pytest
import math
import cProfile
import hashlib
import sys 

from iblt_xor import IBLT
from time import time
from iblt_xor import *

MUL_FACTOR = 2
MAX_HASH = 4
IBLT_FRAC = 0.3

# Third argument is the percentage of smaller set which intersects with the larger one
def generate_lists (size_db1, size_db2, percentage_intersection):
	if size_db1 >= size_db2 :
		pairs1 = [( md5("key%d" % i), sha1("value%d" % i)) for i in range(size_db1)]
		intersection = int(percentage_intersection*size_db2*.01)
		pairs2 = [( md5("key%d" % i), sha1("value%d" % i)) for i in range(intersection)]
		for x in range(size_db1, size_db1+size_db2 - intersection):
			pairs2.append(( md5("key%d" % x), sha1("value%d" % x)))
	else :
		pairs2 = [(md5("key%d" % i), sha1("value%d" % i)) for i in range(size_db2)]
		intersection = int(percentage_intersection*size_db1*.01)
		pairs1 = [(md5("key%d" % i), sha1("value%d" % i)) for i in range(intersection)]
		for x in range(size_db2, size_db2 + size_db1-intersection):
			pairs1.append((md5("key%d" % x), sha1("value%d" % x)))

	print "pairs1", pairs1
	print "pairs2", pairs2
	return (pairs1, pairs2, intersection)

xfail = pytest.mark.xfail
# Returning list after subtraction and not the time taken
# Third argument is the percentage of smaller set which intersects which the larger one
def make_iblt(len1, len2,percentage_intersection):

	if percentage_intersection > 100 or percentage_intersection < 0:
		raise NameError('Percentage should lie between 0 and 100 ')		
	db_input = generate_lists( len1, len2, percentage_intersection) 
	pairs1 = db_input[0]
	pairs2 = db_input[1]
	intersection = db_input[2]
	start = time()
	size_iblt = (len1+len2- 2*intersection)*MUL_FACTOR
	#print "size of IBLT", size_iblt
	if size_iblt == 0:
		size_iblt =1
		t1 = IBLT(int(math.ceil(size_iblt)), 1)
		t2 = IBLT(int(math.ceil(size_iblt)), 1)
	elif size_iblt < MAX_HASH :
		t1 = IBLT(int(math.ceil(size_iblt)),int(math.ceil(size_iblt)))
		t2 = IBLT(int(math.ceil(size_iblt)),int(math.ceil(size_iblt)))
	else :
		t1 = IBLT(int(math.ceil(size_iblt)), MAX_HASH)
		t2 = IBLT(int(math.ceil(size_iblt)), MAX_HASH)

	for key, value in pairs1:
	   	t1.insert( t1.T, key, value )

	for key, value in pairs2:
        	t2.insert( t2.T, key, value )

	print t1.T
	print t2.T
	print t1.subtract(t1.T,t2.T)
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
# Third argument is the percentage of smaller set which intersects which the larger one
def full_db(len1, len2, percentage_intersection):

	if percentage_intersection > 100 or percentage_intersection < 0:
		raise NameError('Percentage should lie between 0 and 100 ')		
	db_input = generate_lists( len1, len2, percentage_intersection) 
	pairs1 = db_input[0]
	pairs2 = db_input[1]
	intersection = db_input[2]
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


def verify_iblt_results(db1, db2, percentage_intersection) :
	results_iblt = make_iblt(db1, db2, percentage_intersection)
	results_full_db = full_db(db1, db2, percentage_intersection)
	if results_iblt[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE: 
		results_iblt[1].sort(key=lambda tup: tup[0]) 
		results_iblt[2].sort(key=lambda tup: tup[0]) 
		results_full_db[0].sort(key=lambda tup: tup[0]) 
		results_full_db[1].sort(key=lambda tup: tup[0]) 
		if results_iblt[1] == results_full_db[0] and results_iblt[2] == results_full_db[1]:
			return 1
		else : 
			return 0

def testing_iblt_func():

	pairs = [( hashlib.md5("key%d" % i).hexdigest(), hashlib.sha1("value%d" % i).hexdigest() ) for i in range(1)]
	t1 = IBLT(2, 2)
	# IBLT created should be empty
	assert t1.is_empty() 

	for key, value in pairs:
	   	t1.insert( t1.T, key, value )
	# Check if the entry is inserted
	assert not t1.is_empty() 

	# Check if we are able to list the entries
	assert t1.list_entries()[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE

	for key, value in pairs:
	   	t1.delete( t1.T, key, value )
	# Check if the entry is deleted
	assert t1.is_empty() 

	# Check if the status is complete on retrieving entries from an empty IBLT 
	assert t1.list_entries()[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE

	# Insert entries in t1 again
	for key, value in pairs:
	   	t1.insert( t1.T, key, value )
	# Create a new empty IBLT
	t2 = IBLT(2,2)
	# Subtraction : t1-t2 (results in entries with positive count)
	t1.subtract(t1.T, t2.T)
	# Check if we are able to get entries from the result of subtraction
	assert t1.list_entries()[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE 

	#delete the entries from the result of previous subtraction
	for key, value in pairs:
	   	t1.delete( t1.T, key, value )
	# Check if the entry is deleted
	assert t1.is_empty() 

	#Insert the entries again in first IBLT	
	for key, value in pairs:
	   	t1.insert( t1.T, key, value )
	# Subtraction : t2-t1 (results in entries with negative count)
	t1.subtract(t2.T, t1.T)
	# Check if we are able to get entries from the result of subtraction
	assert t2.list_entries()[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE 

	# Add entries back to t2	
	for key, value in pairs:
	   	t2.add( t2.T, key, value )
	assert t2.is_empty() 

@xfail(reason="unknown")
#If db1 and db2 have some intersection
def test(): 
	for percent in range(0, 110, 10):
		for db1 in range(10, 100, 10):
			for db2 in range(10, 100, 10):
				# If the difference between databses is lesser than 30% of the larger database then go with the IBLT approach
				intersection = int(min(db1,db2)*percent*.01)	
				if (int(max(db1, db2)* IBLT_FRAC) >= db1+db2-2*intersection):
					#print "IBLT db1 db2 percent intersection ", db1, db2, percent ,intersection
					#result = make_iblt(db1,db2,percent)
					#if result[0] != IBLT.RESULT_LIST_ENTRIES_COMPLETE:
					#	print db1, db2, percent 
					#assert make_iblt(db1, db2, percent)[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE
					assert verify_iblt_results(db1, db2, percent) == 1
				else:
					#print "full DB", db1, db2, percent, intersection
					result = full_db(db1, db2, percent)


@xfail(reason="unknown")
#If db2 is a subset of db1, db2=db1 not handled in this testcase
def db2_subsetOf_db1():
	for db1 in range(10, 100, 1):
		for db2 in range(10, db1, 1):
			intersection = db2
			if (int(db1* IBLT_FRAC) >= db1-db2):
				assert verify_iblt_results(db1, db2, 100) == 1
				#assert make_iblt(db1, db2, 100)[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE
			else:
				result = full_db(db1, db2,100)


@xfail(reason="unknown")
#If db1 is a subset of db2, db2=db1 not handled in this testcase
def db1_subsetOf_db2():
	for db2 in range(10, 100, 1):
		for db1 in range(10, db2, 1):
			intersection = db1
			if (int(db2*IBLT_FRAC) >= db2-db1):
				assert verify_iblt_results(db1, db2, 100) == 1	
				#assert make_iblt(db1, db2, 100)[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE
			else:
				result = full_db(db1, db2,100)


#Check if the big databases work well
def test_bigDb(): 
	db1 = 10000
	db2 = 10000
	for percent in range(990, 1000, 1):
		# If the difference between databses is lesser than 30% of the larger database then go with the IBLT approach
		percent = percent * .1
		intersection = int(min(db1,db2)*percent*.01)	
		if (int(max(db1, db2)* IBLT_FRAC) >= db1+db2-2*intersection):
			print "IBLT db1 db2 percent intersection ", db1, db2, percent ,intersection
			#result = make_iblt(db1,db2,percent)
			#if result[0] != IBLT.RESULT_LIST_ENTRIES_COMPLETE:
			#	print db1, db2, percent 
			#assert make_iblt(db1, db2, percent)[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE
			assert verify_iblt_results(db1, db2, percent) == 1
		else:
			print "full DB", db1, db2, percent, intersection
			result = full_db(db1, db2, percent)


#print full_db(1,1,0)
print make_iblt(1,0,0)
#print verify_iblt_results(20,20,90)
#print full_db(10, 10, 0)
#test_bigDb()
#testing_iblt_func()
#db2_subsetOf_db1()
#print make_iblt(60,60,90)
#test()


if (sys.argv[0] == "pytest_v1.py") and (len(sys.argv) > 2) :
	#assert make_iblt(int(sys.argv[1]), int(sys.argv[2]))[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE
	assert verify_iblt_results(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])) == 1



