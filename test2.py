import math
from iblt import IBLT
from time import time

def make_iblt(len1, len2):
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

def abs(num):
	if num < 0 :
		return num*-1
	else :
		return num

def full_db(len1, len2):
	start = time()
	dict1 = {}
	dict2 = {}

	pairs1 = [( "key%d" % i, "value%d" % i ) for i in range(len1 )]
	for key, value in pairs1:
        	dict1.update({key: value })

	pairs2 = [( "key%d" % i, "value%d" % i ) for i in range(len2)]
	for key, value in pairs2:
        	dict2.update({key: value })

	a=1
	dict3 = {}
	for key in dict1 :
		if dict2.has_key(key):
		# How to not do anything 	
			a=2
		else:
			dict3.update({key:dict1[key]})	
	for key in dict2 :
		if dict1.has_key(key):
			a =2 
		else:
			dict3.update({key:dict2[key]}) 
	end = time()
	return end-start
	#print dict3

file = open("heat.txt", "w")
for db1 in range(10, 1000, 10):
	#file.write(str(db1))
	for db2 in range(10, 1000, 10):
		if (int(max(db1, db2)*.3) >= abs(db1 - db2)): 
			file.write(str(make_iblt(db1, db2)))	
		 	file.write(" ")
		else:
			file.write(str(full_db(db1, db2)))
			file.write(" ")
	file.write("\n")
file.close()

