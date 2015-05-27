#!/usr/bin/python
f = open('full_db_size','r')
sum = 0
for i in f:
        sum += int(i)
print sum

