import math
from iblt_xor import IBLT
#from iblt import IBLT
from time import time
import cProfile
import hashlib

t1 = IBLT(10000, 4, 10, 10)

start = time()
insertion_time_start = time()
pairs = [( "key%d" % i, "value%d" % i ) for i in range(10000)]
for key, value in pairs:
	key = hashlib.md5(key).hexdigest()
        value = hashlib.sha1(value).hexdigest()
       	t1.insert( key, value )
insertion_time_end = time()
print "Insertion time"
print insertion_time_end - insertion_time_start
