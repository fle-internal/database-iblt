#!/usr/bin/python

f = open('test_new_result.txt','r')
sum = 0
for i in f:
        sum += float(i)
print sum/200

