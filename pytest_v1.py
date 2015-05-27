import pytest
import math
import cProfile
import hashlib
import sys 

from time import time
from iblt_xor import *

MUL_FACTOR = 1.4
MAX_HASH = 4
IBLT_FRAC = 0.3

def make_lists(key, value, seed, limit) :
	"""
	Generate list of tuples till the limit	
	"""
	return [( md5(seed+key+"%d" % i), sha1(seed+value+"%d" % i)) for i in range(limit)]

def generate_lists_SameKey (size_db1, size_db2, percentage_intersection, sameKey, seed=None):
	"""
	Returns list of tuples for database1 and database2, according to the 
	percentage intersection(of smaller database) and sameKey are the number of entries
	having same keys but different values in both the databases
	""" 
	if seed == None:
		seed = ""
	lists = generate_db_lists (size_db1, size_db2, percentage_intersection, seed)
	sameKey_db1 = make_lists("samekey", "db1_value", seed, sameKey)
	sameKey_db2 = make_lists("samekey", "db2_value", seed, sameKey)
	lists[0].extend(sameKey_db1)
	lists[1].extend(sameKey_db2)
	#print lists[0]
	#print lists[1]
	return (lists[0], lists[1], lists[2])


def generate_db_lists (size_db1, size_db2, percentage_intersection, seed=None):
	"""
	Returns list of tuples for database1 and database2, according to the 
	percentage intersection(of smaller database)
	"""
	if seed == None:
		seed = ""
	if percentage_intersection > 100 or percentage_intersection < 0:
		raise NameError('Percentage should lie between 0 and 100 ')		
	intersection = int(percentage_intersection * min(size_db1, size_db2) * .01)
	total = size_db1 + size_db2 - intersection
	dataset = make_lists("key", "value", seed, total)
	if size_db1 >= size_db2 :
		pairs1 = dataset[0:size_db1]
		pairs2 = dataset[size_db1-intersection:total]
	else :
		pairs2 = dataset[0:size_db2]
		pairs1 = dataset[size_db2-intersection:total]
	#print "pairs1", pairs1
	#print "pairs2", pairs2
	return (pairs1, pairs2, intersection)

def make_iblt(pairs1, pairs2,intersection):
	"""
 	Returning list of database entries after subtraction
 	Third argument is the number of entries that are common in both databases
	"""
	start = time()
	size_iblt = int(math.ceil((len(pairs1)+len(pairs2)- 2*intersection)*MUL_FACTOR))
	if size_iblt == 0:
		t1 = IBLT(1, 1)
		t2 = IBLT(1, 1)
	elif size_iblt < MAX_HASH :
		t1 = IBLT(size_iblt, size_iblt)
		t2 = IBLT(size_iblt, size_iblt)
	else :
		t1 = IBLT(size_iblt, MAX_HASH)
		t2 = IBLT(size_iblt, MAX_HASH)

	for tup in pairs1:
	   	t1.insert(tup)

	for tup in pairs2:
        	t2.insert(tup)

	#print t1.T
	#print t2.T
	t1.subtract_inplace(t2.T)
	end = time()
	#print t1.serialize()
	#print t1.unserialize()
	return t1.list_entries()

def full_db(pairs1, pairs2, intersection):

	"""
	Calculates database difference by sending full database instead of IBLT
	Assuming that the dbs given to us are not in the form of dictionaries, we create 2 dictionaries
	insert values and then find out the difference between them 
	"""
	start = time()
	dict_a = dict(pairs1)
	dict_b = dict(pairs2)
	dict_a_minus_b = {}
	dict_b_minus_a = {}

	for key in dict_a :
		if not(dict_b.has_key(key) and dict_b[key] == dict_a[key]):
			dict_a_minus_b.update({key:dict_a[key]})	
	for key in dict_b :
		if not(dict_a.has_key(key) and dict_b[key] == dict_a[key]):
			dict_b_minus_a.update({key:dict_b[key]}) 
	end = time()
	# Converting dictionary to lists
	entries = dict_a_minus_b.items()
	deleted_entries = dict_b_minus_a.items()
	#return end-start
	return (entries, deleted_entries)


def verify_iblt_results(db1, db2, intersection) :
	"""
	Generating IBLT and comparing the results with full db approach
	"""
	results_iblt = make_iblt(db1, db2, intersection)
	#print results_iblt
	results_full_db = full_db(db1, db2, intersection)
	#print results_full_db
	if results_iblt[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE: 
		results_iblt[1].sort()
		results_iblt[2].sort()
		results_full_db[0].sort()
		results_full_db[1].sort()
		if results_iblt[1] == results_full_db[0] and results_iblt[2] == results_full_db[1]:
			return True
		else :		
			return False
def test_creating_IBLT():
	"""
	Creating IBLT and checking if it is empty
	"""
	t = IBLT(2, 2)
	# IBLT created should be empty
	assert t.is_empty() 

def test_insert_IBLT():
	"""
	Checking insertion(of a tuple) in IBLT
	"""
	t = IBLT(2, 2)
	tup = (md5("key"), sha1("value"))
	t.insert(tup)
	# Check if the entry is inserted
	assert not t.is_empty() 
	return t

def test_list_entries_IBLT():
	"""
	Checking listing entries from IBLT
	"""	
	t = IBLT(2, 2)
	tup = (md5("key"), sha1("value"))
	t.insert(tup)
	# Check if we are able to list the entries
	assert t.list_entries()[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE

def test_delete_IBLT():
	"""
	Checking deletion of a tuple from IBLT
	"""
	t = IBLT(2, 2)
	tup = (md5("key"), sha1("value"))
	t.insert(tup)
	t.delete(tup)
	# Check if the entry is deleted
	assert t.is_empty() 
	# Check if the status is complete on retrieving entries from an empty IBLT 
	assert t.list_entries()[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE

def test_aMinusB_IBLT():
	"""
	Subtract an empty IBLT from an IBLT with one entry and check if we 
	are able to retrieve this entry using list_entries() after subtraction
	"""
	t1 = IBLT(2, 2)
	tup = (md5("key"), sha1("value"))
	t1.insert(tup)
	# Create a new empty IBLT
	t2 = IBLT(2,2)
	# Subtraction : t1-t2 (results in entries with positive count)
	t1.subtract_inplace(t2.T)
	# Check if we are able to get entries from the result of subtraction
	assert t1.list_entries()[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE 
	assert t1.list_entries()[1][0] == tup
	return t1

def test_delete_after_subtract_IBLT():
	"""
	Check if deletion works after subtraction aMinusB
	"""
	t = test_aMinusB_IBLT()
	tup = (md5("key"), sha1("value"))
	t.delete(tup)
	assert t.is_empty() 

def test_bMinusA_IBLT():
	"""
	Subtract an IBLT with one entry from an empty IBLT and check if we 
	are able to retrieve this entry using list_entries() after subtraction
	"""
	# Create an empty IBLT
	t1 = IBLT(2, 2)
	t2 = IBLT(2,2)
	tup = (md5("key"), sha1("value"))
	t2.insert(tup)
	# Subtraction : results in entries with negative count
	t1.subtract_inplace(t2.T)
	# Check if we are able to get entries from the result of subtraction
	assert t1.list_entries()[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE 
	assert t1.list_entries()[2][0] == tup
	return t1

def test_insert_after_subtract_IBLT():
        """
        Check if insertion works after subtraction bMinusA
        """
        t = test_bMinusA_IBLT()
        tup = (md5("key"), sha1("value"))
        t.insert(tup)
        assert t.is_empty()

def test_db1_subsetOf_db2():
	"""
	If db1 is a subset of db2, db2=db1 not handled in this testcase
	"""
        #Since db2 is a subset and is the smaller among the 2 databses
        percentage_intersection = 100
	start_range = 40
        for size_db2 in range(start_range, start_range+10, 1):
                for size_db1 in range(start_range, size_db2, 1):
                        lists=generate_db_lists (size_db1, size_db2, percentage_intersection, "db1subsetdb2")
                        assert verify_iblt_results(lists[0], lists[1], lists[2]) == True, "size_db1 %d size_db2 %d" %(size_db1, size_db2)
	
# Always fails for (18,10), (28,20), (38,30) etc
def test_db2_subsetOf_db1():
        """
        If db2 is a subset of db1, db2=db1 not handled in this testcase
        """
        #Since db2 is a subset and is the smaller among the 2 databses
        percentage_intersection = 100
	start_range = 40
        for size_db1 in range(start_range, start_range+10, 1):
                for size_db2 in range(start_range, size_db1, 1):
                        lists=generate_db_lists (size_db1, size_db2, percentage_intersection, "db2subsetdb1")
                        assert verify_iblt_results(lists[0], lists[1], lists[2]) == True, "size_db1 %d size_db2 %d" %(size_db1, size_db2)

#Fails at 99.6 for 1.4 and succeeds if IBLT is 2 times the size of difference
def test_bigDb(): 
	"""
	Check if the big databases work well
	"""		
	size_db1 = 10000
	size_db2 = 10000
	for percent_intersection in range(990, 1000, 1):
		percent_intersection = percent_intersection * .1
		lists=generate_db_lists (size_db1, size_db2, percent_intersection, "bigDb")
		assert verify_iblt_results(lists[0], lists[1], lists[2]) == True, "percent intersection %f" %(percent_intersection)


def test(): 
	"""
	db1 and db2 have some intersection
	"""
	for percent_intersection in range(0, 110, 10):
		for size_db1 in range(10, 100, 10):
			for size_db2 in range(10, 100, 10):
				lists=generate_db_lists (size_db1, size_db2, percent_intersection, "test")
				assert verify_iblt_results(lists[0], lists[1], lists[2]) == True, \
					"size_db1 %d size_db2 %d percent intersection %f" %(size_db1, size_db2, percent_intersection)

# Always fails for (18,10), (28,20), (38,30) etc
def db2_subsetOf_db1():
        percentage_intersection = 100
	size_db1 = 1
	size_db2 = 1
	lists=generate_db_lists (size_db1, size_db2, percentage_intersection, "db2subsetdb1")
	assert verify_iblt_results(lists[0], lists[1], lists[2]) == True, "size_db1 %d size_db2 %d" %(size_db1, size_db2)


db2_subsetOf_db1()				
#lists=generate_db_lists (2, 1, 0, "test")
#print make_iblt(lists[0], lists[1], lists[2])
