import sys 
#!/usr/bin/python
f = open(str(sys.argv[1]),'r')
sum = 0
for i in f:
        sum += int(i)
print sum
