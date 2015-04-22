#!/usr/bin/python

f = open('compare_unmodified.txt','r')
sum = 0
for i in f:
        sum += float(i)
print sum/25

