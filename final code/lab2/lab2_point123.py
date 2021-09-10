import random
import simpy
import matplotlib.pyplot as plt 
import numpy as np
import scipy.stats as st
import math 

class Measure:
    def __init__(self,Narr,Ndep, NAveraegUser,OldTimeEvent,AverageDelay,SentToCloud, busy):
        self.arr = Narr
        self.dep = Ndep
        self.ut = NAveraegUser
        self.oldT = OldTimeEvent
        self.delay = AverageDelay
        self.pCloud = SentToCloud # in the cloud system this is the number of loss packets 
        self.busy = busy
        
class Measure_node:
    def __init__(self, Narr, busy, cost):
        self.arr = Narr
        self.busy = 0
        self.cost = cost
        
# ******************************************************************************
# Client
# ******************************************************************************       
class Client:
    def __init__(self,Type,ArrivalT):
        self.type = Type
        self.Tarr = ArrivalT
        self.preproc = 0 # when it is zero it means the packet hasn't done the preprocessing yet
        self.totWaitingDelay = 0  # tot time that the client waits until it is served 
        self.queuingTime = 0
        

# ******************************************************************************
# Constants
# ******************************************************************************
LOAD=0.85
SERVICE_PREPROC = 3.8 # av service time
ARRIVAL = SERVICE_PREPROC/LOAD # av inter-arrival time
TYPE1 = 'A'
TYPE2 = 'B' 
SERVICE_CLOUD_POSTPROC = 10.0
SERVICE_CLOUD_PREPROC = 2.0
# from fog to cloud time is closer respect to fog/cloud to actuators 
prop_time = 10 # time needed to move a packet from fog node to cloud datacenter
prop_cloud_act = 13 # time needed to move a packet from cloud to actuators 
prop_fog_act = 15 # time needed to move a packet from fog to actuators 
T_q = 55.00 #max queueing time
f = 0.6# fraction of packet b among all packets 

#500000
SIM_TIME = 500000 
maxBufferMD = 5
maxBufferCD = 8
arrivals=0
users=0
users_cloud = 0 
BusyServerMD=False # True: server is currently busy; False: server is currently idle
BusyServerCD=False
MM1=[]
MM1_cloud=[] 
entrance_user = []
served_user = []
actuators_user = []         
k = 0
all_delayCloud = []
avg_delayCloud = [] 
queuingTot = [] 
test = [] 

# ******************************************************************************
# generator yield events to the simulator
# ******************************************************************************

# SIMULATOR MICRODATA CENTER 

# arrivals *********************************************************************
def arrival_process(environment,queue):
    global users
    global BusyServerMD
    
    while True:
        #print("Arrival no. ",data.arr+1," at time ",environment.now," with ",users," users" )
        # cumulate statistics 
        data.arr += 1   
        data.ut += users*(environment.now-data.oldT)
        data.oldT = environment.now
        
        # sample the time until the next event
        inter_arrival = random.expovariate(1.0/ARRIVAL)
        # generate packet of type A or of type B depending on the value of x
        # if x is greater than f, generate pack A, in the other case generate pack B 
        x = random.uniform(0,1)
        if x >= f: 
            cl=Client(TYPE1,environment.now)
        else:
            cl=Client(TYPE2, environment.now)
        if users<maxBufferMD+1: # 1 server  
            users += 1
            queue.append(cl)
            if users == 1: 
                BusyServerMD = True
                service_time = random.expovariate(1.0/SERVICE_PREPROC)
                data.busy += service_time
                env.process(departure_process(environment, service_time,queue))
        elif users>=maxBufferMD+1:
            data.pCloud += 1
            # packet is sent to the cloud, so it is add the prop time
            arrival_cloud_process(env, MM1_cloud, cl)
            # send to the cloud, call function 
         # yield an event to the simulator
        yield environment.timeout(inter_arrival)
        
# ******************************************************************************

# departures *******************************************************************
def departure_process(environment, service_time, queue):
    global users
    global BusyServerMD
    global k 
    
    yield environment.timeout(service_time)
    #print("Departure no. ",data.dep+1," at time ",environment.now," with ",users," users" )
    # cumulate statistics    
    data.dep += 1
    data.ut += users*(environment.now-data.oldT)
    data.oldT = environment.now
    user=queue.pop(0)
    #update state variable and extract the client in the queue
    users -= 1 
    data.delay += (environment.now-user.Tarr)
    
    if user.type == TYPE2:
        k = k+1
        user.preproc = 1
        arrival_cloud_process(environment, MM1_cloud,user)
    if user.type == TYPE1: 
        user.queuingTime = (environment.now-user.Tarr) + prop_fog_act 
        queuingTot.append(user.queuingTime)
    if users==0: 
        BusyServerMD = False
    else:
        service_time = random.expovariate(1.0/SERVICE_PREPROC)
        data.busy += service_time
        env.process(departure_process(environment, service_time,queue))
        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"


# ******************************************************************************
# SIMULATION CLOUD SERVER *******************************************************************
    
# arrivals *********************************************************************
def arrival_cloud_process(environment,queue1, client):
    global users_cloud
    global BusyServerCD
    
    #print("Arrival no. ",data.arr+1," at time ",environment.now," with ",users," users" )
    # cumulate statistics 
    cloud.arr += 1   
    
    cloud.ut += users_cloud*(environment.now-cloud.oldT)
    cloud.oldT = environment.now
    
    # sample the time until the next event
    if users_cloud<maxBufferCD: 
        users_cloud += 1
        queue1.append(client)
        if users_cloud == 1: 
            BusyServerCD = True 
            if client.type == TYPE1:
                # packet of type A only requires preprocessing in the cloud
                service_time = random.expovariate(1.0/SERVICE_CLOUD_PREPROC)
            elif client.type == TYPE2:
                if client.preproc == 1: 
                    # packet of type B that has already done preproc only needs post processing in the cloud
                    service_time = random.expovariate(1.0/SERVICE_CLOUD_POSTPROC)
                else:
                    # packet of type B that hasn't done preproc needs pre and post processing in the cloud
                    service_time = random.expovariate(1.0/(SERVICE_CLOUD_POSTPROC+SERVICE_CLOUD_PREPROC))
            cloud.busy += service_time
            env.process(departure_cloud(environment, service_time,queue1))
    #elif users_cloud>=maxBufferCD:
    else:
        cloud.pCloud += 1
        # send to the cloud, call function 
        
   
# departures *******************************************************************
def departure_cloud(environment, service_time, queue):
    global users_cloud
    global BusyServerCD

    user=queue.pop(0)
    # estimate time in which packet waits to be served in cloud datacenter
    # from the moment it enters the system until is served in the cloud
    user.totWaitingDelay = environment.now - user.Tarr
    # add the propagation time needed to go from fog to cloud
    user.totWaitingDelay = user.totWaitingDelay + prop_time
    all_delayCloud.append(user.totWaitingDelay)
    
    yield environment.timeout(service_time) 
    #print("Departure no. ",data.dep+1," at time ",environment.now," with ",users," users" )
    
    # cumulate statistics    
    cloud.dep += 1
    cloud.ut += users_cloud*(environment.now-cloud.oldT)
    cloud.oldT = environment.now
    
    user.queuingTime = (environment.now-user.Tarr) + prop_time + prop_cloud_act 
    queuingTot.append(user.queuingTime) 
    
    #update state variable and extract the client in the queue
    users_cloud = users_cloud - 1
    cloud.delay += (env.now-user.Tarr)   
    if users_cloud==0: 
        BusyServerCD = False
    else:
        if user.type == TYPE1:
            # packet of type A only requires preprocessing in the cloud
            service_time = random.expovariate(1.0/SERVICE_CLOUD_PREPROC)
        elif user.type == TYPE2:
            if user.preproc == 1: 
                # packet of type B that has already done preproc only needs post processing in the cloud
                service_time = random.expovariate(1.0/SERVICE_CLOUD_POSTPROC)
            else:
                # packet of type B that hasn't done preproc needs pre and post processing in the cloud
                service_time = random.expovariate(1.0/(SERVICE_CLOUD_POSTPROC+SERVICE_CLOUD_PREPROC))
        service_time = random.expovariate(1.0/SERVICE_CLOUD_POSTPROC)
        cloud.busy += service_time
        env.process(departure_cloud(environment, service_time,queue))
        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"
       
# ******************************************************************************
# START SIMULATION

random.seed(4)
loss_probab = []
data = Measure(0,0,0,0,0,0,0)
cloud = Measure(0,0,0,0,0,0,0) 
env = simpy.Environment()

# start the arrival processes
env.process(arrival_process(env, MM1))

# simulate until SIM_TIME
env.run(until=SIM_TIME)


# print output data
print("MEASUREMENTS \n")
print("No. of arrivals =", data.arr)
print("No. of departures =",data.dep)
print("No. of packets sent to the cloud =", data.pCloud+k)
print("Actual queue size: ",len(MM1))
print("Arrival rate = ",data.arr/env.now,"\nDeparture rate = ",data.dep/env.now)
print("Sent to the cloud rate = ", data.pCloud/env.now)
print("\nAverage number of users (E[N]) = ",data.ut/env.now)
print("Average delay (E[T]) =  ",data.delay/data.dep)

if len(MM1)>0:
    print("Arrival time of the last element in the queue:",MM1[len(MM1)-1].Tarr)

# print output data
print("MEASUREMENTS of CLOUD SERVER\n")
print("No. of arrivals =", cloud.arr)
print("No. of departures =",cloud.dep)
print("No. of packets dropped =", cloud.pCloud)
print("Actual queue size: ",len(MM1_cloud))
print("\nAverage number of users (E[N]) = ",cloud.ut/env.now)
print("Average delay (E[T]) =  ",cloud.delay/cloud.dep)
print("Loss probability: ", cloud.pCloud/data.arr)
print('-----------------')
print(np.mean(queuingTot))


# ******************************************************************************
# CONFIDENCE INTERVAL  *********************************************************

n = 20 
p = 0
samples_waitingD = []
while p<n:
    p=p+1
    random.seed(42*p)
    MM1 = []
    MM1_cloud = []
    all_delayCloud = [] 
    users=0
    users_cloud = 0 
    BusyServerMD=False 
    BusyServerCD=False
    data = Measure(0,0,0,0,0,0,0)
    cloud = Measure(0,0,0,0,0,0,0) 
    env = simpy.Environment()
    # start the arrival processes
    env.process(arrival_process(env, MM1))
    # simulate until SIM_TIME
    env.run(until=SIM_TIME)
    avg = np.mean(all_delayCloud)
    samples_waitingD.append(avg)

# compute the aritmetic mean and variance of the observation 
plt.plot(samples_waitingD, 'r')
plt.xlabel('k')
plt.ylabel('r_k')
plt.title('-')
plt.show()

mean_samples = np.mean(samples_waitingD)
print(mean_samples)
print(st.t.interval(alpha=0.95, df=len(samples_waitingD)-1, loc=np.mean(samples_waitingD), scale=st.sem(samples_waitingD)))


# ******************************************************************************
# PLOTS *******************************************************************

# DROP PROBABILITY UNDER DIFFERENT VALUES OF f 
# add system meauserments
B_rate = np.arange(0, 1.05, 0.05)
loss_prob = []
for f1 in B_rate:
    f = f1
    MM1 = []
    MM1_cloud = []
    users=0
    users_cloud = 0 
    BusyServerMD=False 
    BusyServerCD=False
    data = Measure(0,0,0,0,0,0,0)
    cloud = Measure(0,0,0,0,0,0,0) 
    env = simpy.Environment()
    # start the arrival processes
    env.process(arrival_process(env, MM1))
    # simulate until SIM_TIME
    env.run(until=SIM_TIME)
    loss_prob.append(cloud.pCloud/data.arr)

    
plt.plot(B_rate, loss_prob, 'r')
plt.xlabel('f')
plt.ylabel('Loss probability')
plt.title('Loss probability with different rates of B packets')
plt.show()
f=0.6 # set fixed value


e_n = []
loss_prob1 = []
e_n_cloud = [] 
e_t = []
e_t_cloud = [] 
# SIZE OF BUFFER OF MICRO DATA CENTER IMPACT
buffSize = np.arange(5, 60, 5)
for size in buffSize:
    maxBufferMD = size
    MM1 = []
    MM1_cloud = []
    users=0
    users_cloud = 0 
    k = 0 
    test = [] 
    BusyServerMD=False 
    BusyServerCD=False
    data = Measure(0,0,0,0,0,0,0)
    cloud = Measure(0,0,0,0,0,0,0) 
    env = simpy.Environment()
    # start the arrival processes
    env.process(arrival_process(env, MM1))
    # simulate until SIM_TIME
    env.run(until=SIM_TIME)
    print(size)
    print(data.pCloud)
    print(cloud.pCloud)
    print(np.mean(test))
    print('-------')
    loss_prob1.append(cloud.pCloud/data.arr)
    e_n.append(data.ut/env.now)
    e_n_cloud.append(cloud.ut/env.now)
    e_t.append(data.delay/data.dep)
    e_t_cloud.append(cloud.delay/cloud.dep)
    
plt.plot(buffSize, loss_prob1, 'r')
plt.xlabel('Buffer of Micro Datacenter')
plt.ylabel('Loss probability')
plt.title('Loss probability with different buffer of micro datacenter')
plt.show()

plt.plot(buffSize, e_n, 'r', label='fog nodes')
plt.plot(buffSize, e_n_cloud, 'b', label='cloud')
plt.xlabel('Buffer of Micro Datacenter')
plt.ylabel('avg number of user')
plt.title('E[N]avg number of user ')
plt.legend()
plt.show()

plt.plot(buffSize, e_t, 'r', label='fog nodes')
plt.plot(buffSize, e_t_cloud, 'b', label='cloud')
plt.xlabel('Buffer of micro Datacenter')
plt.ylabel('avg delay')
plt.title('avg delay ')
plt.legend()
plt.show()

maxBufferMD = 5 # set fixed value


f = 0.6
e_n = []
loss_prob2 = []
e_n_cloud = [] 
e_t = []
e_t_cloud = [] 
# SIZE OF BUFFER OF CLOUD DATA CENTER IMPACT
buffSize = np.arange(5, 60, 5)
for size in buffSize:
    maxBufferCD = size
    MM1 = []
    MM1_cloud = []
    users=0
    users_cloud = 0 
    BusyServerMD=False # True: server is currently busy; False: server is currently idle
    BusyServerCD=False
    data = Measure(0,0,0,0,0,0,0)
    cloud = Measure(0,0,0,0,0,0,0) 
    env = simpy.Environment()
    # start the arrival processes
    env.process(arrival_process(env, MM1))
    # simulate until SIM_TIME
    env.run(until=SIM_TIME)
    loss_prob2.append(cloud.pCloud/data.arr)
    e_n.append(data.ut/env.now)
    e_n_cloud.append(cloud.ut/env.now)
    e_t.append(data.delay/data.dep)
    e_t_cloud.append(cloud.delay/cloud.dep)
    
plt.plot(buffSize, loss_prob2, 'r')
plt.xlabel('Buffer of Cloud Datacenter')
plt.ylabel('Loss probability')
plt.title('Loss probability with different buffer size of cloud datacenter')
plt.show()

plt.plot(buffSize, e_n, 'r', label='fog nodes')
plt.plot(buffSize, e_n_cloud, 'b', label='cloud')
plt.xlabel('Buffer of cloud Datacenter')
plt.ylabel('avg number of user')
plt.title('avg number of user ')
plt.legend()
plt.show()

plt.plot(buffSize, e_t, 'r', label='fog nodes')
plt.plot(buffSize, e_t_cloud, 'b', label='cloud')
plt.xlabel('Buffer of cloud Datacenter')
plt.ylabel('avg delay')
plt.title('avg delay ')
plt.legend()
plt.show()
maxBufferCD = 8 # set fixed value


'''
INCREASING THE BUFFER SIZE OF BOTH MICRODATACENTER AND CLOUD REDUCE THE LOSS PROBABILITY
BUT IN CASE OF CLOUD THE PROB DROP TO 0 WITH A BUFF GREATER THAN 20
WHILE FOR MICRODATACENTER THE PROBABILITY IS REDUCED BUT NOT TO 0 
'''


fog_servTime = np.arange(2, 7, 0.5)
avg_queuing = [] 
np.x = T_q 
for serv in fog_servTime: 
    SERVICE_PREPROC = serv
    MM1 = []
    queuingTot = [] 
    MM1_cloud = []
    users=0
    users_cloud = 0 
    BusyServerMD=False # True: server is currently busy; False: server is currently idle
    BusyServerCD=False
    data = Measure(0,0,0,0,0,0,0)
    cloud = Measure(0,0,0,0,0,0,0) 
    env = simpy.Environment()
    # start the arrival processes
    env.process(arrival_process(env, MM1))
    # simulate until SIM_TIME
    env.run(until=SIM_TIME)
    print(SERVICE_PREPROC)
    print(np.mean(queuingTot))
    avg_queuing.append(np.mean(queuingTot))
    test.append(cloud.ut/env.now)
    
plt.plot(fog_servTime, avg_queuing, 'r')
plt.axhline(y=T_q)
plt.xlabel('Fog service Time')
plt.ylabel('avg queuing time')
plt.title('avg queuing time vs fog service rate' )
plt.show()

