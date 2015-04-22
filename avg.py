#!/usr/bin/python

f = open('compare.txt','r')
sum = 0
for i in f:
        sum += float(i)
print sum/100

