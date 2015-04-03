import sys
from iblt import IBLT 

#t = IBLT( 30, 4, 10, 10 )
t = IBLT(2,10,10,10)

#print(t.T);
t.insert( "testkey", "testvalue" )
print(t.T);

#c = 0;
#print("c",sys.getsizeof(c));

#d=[0];
#print("d",sys.getsizeof(d));

#b =[0, 0, 0, 0, 0, 0, 0, 0, 0]; 
#print("b",sys.getsizeof(b));
#a = [[0, [0], [0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0]]];
#print("a",sys.getsizeof(a));
#print("\n");

