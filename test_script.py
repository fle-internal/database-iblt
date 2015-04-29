import math
from iblt import IBLT
from time import time
import cProfile
import hashlib

def make_iblt(len1, len2):

	pairs1 = [( hashlib.md5("key%d" % i).hexdigest(), hashlib.sha1("value%d" % i).hexdigest() ) for i in range(len1)]
	pairs2 = [( hashlib.md5("key%d" % i).hexdigest(), hashlib.sha1("value%d" % i).hexdigest() ) for i in range(len2)]
	start = time()
	size_iblt = abs(len1-len2)*1.4
	# Check why this script fails in the hash function
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
	t1.list_entries()
	end = time()
	return end - start

# Returns the absolute value of the argument passed
def abs(num):
	if num < 0 :
		return num*-1
	else :
		return num

# Returns the time taken to find the set differnce 
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
	return end-start
"""
file = open("heat.txt", "w")
for db1 in range(1, 10, 1):
	#file.write(str(db1))
	for db2 in range(1, 10, 1):
		# If the difference between databses is lesser than 30% of the larger database then go with the IBLT approach
		if (int((db1+db2)*.3) >= abs(db1 - db2)): 
			file.write(str(make_iblt(db1, db2)))	
		 	file.write(" ")
		else:
			file.write(str(full_db(db1, db2)))
			file.write(" ")
	file.write("\n")
file.close()
"""

file_compare = open("compare.txt","a")
file_compare.write(str(make_iblt(10000, 9997)/full_db(10000, 9997)))
file_compare.write("\n")
#cProfile.run('make_iblt(10000,10000)')
#print cProfile.run('full_db(10000, 10000)')
file_compare.close()
