import math
from iblt import IBLT
from time import time

def make_iblt(len1, len2):
	# 
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
	start = time()
	dict_a = {}
	dict_b = {}

	pairs1 = [( "key%d" % i, "value%d" % i ) for i in range(len1 )]
	for key, value in pairs1:
        	dict_a.update({key: value })

	pairs2 = [( "key%d" % i, "value%d" % i ) for i in range(len2)]
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
	#print dict_a_minus_b
	#print dict_b_minus_a	

file = open("heat.txt", "w")
for db1 in range(1, 10, 1):
	#file.write(str(db1))
	for db2 in range(1, 10, 1):
		# If the difference between databses is lesser than 30% of the larger database then go with the IBLT approach
		if (int(max(db1, db2)*.3) >= abs(db1 - db2)): 
			file.write(str(make_iblt(db1, db2)))	
		 	file.write(" ")
		else:
			file.write(str(full_db(db1, db2)))
			file.write(" ")
	file.write("\n")
file.close()

