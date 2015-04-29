import math
from iblt import IBLT
from time import time
import cProfile
import hashlib
import sys

start = time()
t1 = IBLT(10, 4)
t2 = IBLT(10, 4)

pairs1 = [( "key%d" % i, "value%d" % i ) for i in range(0, 5)]
for key, value in pairs1:
	key = hashlib.md5(key).hexdigest()
        value = hashlib.sha1(value).hexdigest()
	print key
	print value
       	t1.insert( t1.T, key, value )

pairs2 = [( "key%d" % i, "value%d" % i ) for i in range(1, 6)]
for key, value in pairs2:
        key = hashlib.md5(key).hexdigest()
        value = hashlib.sha1(value).hexdigest()
      	print key
	print value 
	t2.insert( t2.T, key, value )

t1.subtract(t1.T, t2.T)
print t1.list_entries()
end = time()
"""
file_hash = open("test_new_result.txt","a")
file_hash.write(str(end - start))
file_hash.write("\n")
file_hash.close()
"""

