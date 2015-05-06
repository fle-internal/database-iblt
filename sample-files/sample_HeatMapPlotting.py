import numpy
file = open("heat_10.txt", "r")
data = numpy.random.rand(9,9)

line_num =0
while line_num < 10:
    line=file.readline()
    if not line:
        break
    str=line.split()
    for i in range (9):
    	data[line_num]=str[i]

    line_num = line_num + 1


from matplotlib import pyplot as plt 
#cbar = plt.colorbar(data, ticks=[-1, 0, 1], orientation='horizontal')
heatmap = plt.pcolor(data)
plt.show()




