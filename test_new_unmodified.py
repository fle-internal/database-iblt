import math
from iblt_xor_unmodified import IBLT
#from iblt import IBLT
from time import time
import cProfile
import hashlib

start = time()
t1 = IBLT(10, 4, 10, 10)
t2 = IBLT(10, 4, 10, 10)

pairs = [( "key%d" % i, "value%d" % i ) for i in range(100000)]
for key, value in pairs:
	key = hashlib.md5(key).hexdigest()
        value = hashlib.sha1(value).hexdigest()
       	t1.insert( key, value )

pairs2 = [( "key%d" % i, "value%d" % i ) for i in range(99999)]
for key, value in pairs:
	key = hashlib.md5(key).hexdigest()
        value = hashlib.sha1(value).hexdigest()
       	t2.insert( key, value )

t1.subtract(t1.T, t2.T)
t1.list_entries()
end = time()
print end - start
