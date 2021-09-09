import numpy as np
import matplotlib.pyplot as plt

N = 3
ind = np.arange(N)  # the x locations for the groups
width = 0.27       # the width of the bars

fig = plt.figure()
ax = fig.add_subplot(111)


'''
# all servers s3, slower but cheaper 
#[et, cost, avg queuing delay]
s1 = [18.73, 466.64/10, 23.18]

# all servers s1, faster but expansive
s2 = [12.79 , 596.83/10, 22.57]

# all s2, medium speed and medium cost 
s3 = [15.75, 484/10, 22.87]
'''
#[loss prob, cost, avg queuing delay]
# all servers s1, faster but expansive
s1 =np.array( [0.000286, 0.0315,  0.0793])*(100)

# all s2, medium speed and medium cost 
s2 = [4218.76/100, 1996.90/100, 1467.25/100]


# all servers s3, slower but cheaper 
s3 = [30.86,  36.77, 40.12]


rects1 = ax.bar(ind, s1, width, color='r')
rects2 = ax.bar(ind+width, s2, width, color='g')
rects3 = ax.bar(ind+width*2, s3, width, color='b')

ax.set_ylabel('Scores')
ax.set_xticks(ind+width)
ax.set_xticklabels( ('s1', 's2', 's3') )
ax.legend( (rects1[0], rects2[0], rects3[0]), ('loss prob', 'cost', 'avg queuing') )

def autolabel(rects):
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*h, '%d'%int(h),
                ha='center', va='bottom')

autolabel(rects1)
autolabel(rects2)
autolabel(rects3)

plt.show()




#####################################################################################
#[loss prob, cost, avg queuing delay]
# scenario 1:  1-2-3-1-2
# scenario 2. 1-3-3-3-3
# scenario 3: 2-3-1-2-3

N = 3
ind = np.arange(N)  # the x locations for the groups
width = 0.27       # the width of the bars

fig = plt.figure()
ax = fig.add_subplot(111)

# all servers s1, faster but expansive
s1 =np.array( [ 0.0048,  0.0226,  0.0158])*(100)

# all s2, medium speed and medium cost 
s2 = [3250.99/100, 2635.38/100, 2595.57/100]


# all servers s3, slower but cheaper 
s3 = [33.311,  36.77,35.21]


rects1 = ax.bar(ind, s1, width, color='r')
rects2 = ax.bar(ind+width, s2, width, color='g')
rects3 = ax.bar(ind+width*2, s3, width, color='b')

ax.set_ylabel('Scores')
ax.set_xticks(ind+width)
ax.set_xticklabels( ('s4', 's5', 's6') )
ax.legend( (rects1[0], rects2[0], rects3[0]), ('loss prob', 'cost', 'avg queuing') )

def autolabel(rects):
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*h, '%d'%int(h),
                ha='center', va='bottom')

autolabel(rects1)
autolabel(rects2)
autolabel(rects3)
plt.axhline(y=35)
plt.show()


#####################################################################################
#[loss prob, cost, avg queuing delay]
# scenario 1:  2-1-3
# scenario 2. 1-1-3
# scenario 3: 2-2-2

N = 3
ind = np.arange(N)  # the x locations for the groups
width = 0.27       # the width of the bars

fig = plt.figure()
ax = fig.add_subplot(111)

# all servers s1, faster but expansive
s1 =np.array( [  0.0857,  0.0342,   0.1823])*(100)

# all s2, medium speed and medium cost 
s2 = [2813.61/100, 3676.394/100, 1741.94/100]


# all servers s3, slower but cheaper 
s3 = [ 36.5612, 33.503,  41.0533]


rects1 = ax.bar(ind, s1, width, color='r')
rects2 = ax.bar(ind+width, s2, width, color='g')
rects3 = ax.bar(ind+width*2, s3, width, color='b')

ax.set_ylabel('Scores')
ax.set_xticks(ind+width)
ax.set_xticklabels( ('s4', 's5', 's6') )
ax.legend( (rects1[0], rects2[0], rects3[0]), ('loss prob', 'cost', 'avg queuing') )

def autolabel(rects):
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*h, '%d'%int(h),
                ha='center', va='bottom')

autolabel(rects1)
autolabel(rects2)
autolabel(rects3)
plt.axhline(y=35)
plt.show()



