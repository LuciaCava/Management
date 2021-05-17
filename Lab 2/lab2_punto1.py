import random
import simpy
import matplotlib.pyplot as plt 
import numpy as np

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
        self.waitingDelayCloud = 0  # tot time that the client waits in the cloud
        

# ******************************************************************************
# Constants
# ******************************************************************************
LOAD=0.85
SERVICE_PREPROC = 5.0 # av service time
ARRIVAL = SERVICE_PREPROC/LOAD # av inter-arrival time
TYPE1 = 'A'
TYPE2 = 'B' 
SERVICE_CLOUD_POSTPROC = 10.0
SERVICE_CLOUD_PREPROC = 2.0
T_q = 30.00 #max queueing time
f = 0.6# fraction of packet b among all packets 


SIM_TIME = 500000
maxBufferMD = 5  #if we set equal to 1 it is like other case, 1 service and no buffer 
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
avg_delay = []
avg_delay2 = []

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
       
        loss_probab.append(cloud.pCloud/data.arr)
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
        if users<maxBufferMD: 
            users += 1
            queue.append(cl)
            cl.totWaitingDelay = environment.now
            if users == 1: 
                BusyServerMD = True
                service_time = random.expovariate(1.0/SERVICE_PREPROC)
                data.busy += service_time
                env.process(departure_process(environment, service_time,queue))
        elif users>=maxBufferMD:
            data.pCloud += 1
            
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

    
    user=queue.pop(0)
    user.totWaitingDelay = environment.now - user.Tarr
    yield environment.timeout(service_time)
    #print("Departure no. ",data.dep+1," at time ",environment.now," with ",users," users" )
    # cumulate statistics    
    data.dep += 1
    data.ut += users*(environment.now-data.oldT)
    data.oldT = environment.now
    
    #update state variable and extract the client in the queue
    users -= 1 
    
    data.delay += (environment.now-user.Tarr)
    
    if user.type == TYPE2:
        k = k+1
        user.preproc = 1
        arrival_cloud_process(environment, MM1_cloud,user)
   
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
        client.waitingDelayCloud = environment.now
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
    elif users_cloud>=maxBufferCD:
        cloud.pCloud += 1
        # send to the cloud, call function 
        
   
# departures *******************************************************************
def departure_cloud(environment, service_time, queue):
    global users_cloud
    global BusyServerCD

    user=queue.pop(0)
    user.waitingDelayCloud = environment.now - user.waitingDelayCloud
    user.totWaitingDelay = user.totWaitingDelay + user.waitingDelayCloud
    yield environment.timeout(service_time) 
    #print("Departure no. ",data.dep+1," at time ",environment.now," with ",users," users" )
    
    # cumulate statistics    
    cloud.dep += 1
    cloud.ut += users*(environment.now-cloud.oldT)
    cloud.oldT = environment.now

    #update state variable and extract the client in the queue
    users_cloud -= 1

    #cloud.delay += (env.now-user.Tarr)
    
    avg_delay.append(user.waitingDelayCloud)
    avg_delay2.append(user.totWaitingDelay)
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

random.seed(42)
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


print("Loss probability: ", cloud.pCloud/data.arr)

print('-----------------')

print(len(avg_delay))

# ******************************************************************************
# REMOVE WARM UP TRANSIENT ******************************************************

j=0 
x = np.average(avg_delay)
x_k = []
r_k = []
n = len(avg_delay)

for j in range(len(avg_delay)):
    new_x = avg_delay[j+1:]
    x_k1 = np.average(new_x)
    #x_k1= (1/(n-j))*sum(new_x)
    x_k.append(x_k1)
    #print(x_k1)
    r_k1 = (x_k1-x)/x
    r_k.append(r_k1)
    

plt.plot(r_k, 'r')
plt.xlabel('f')
plt.ylabel('Loss probability')
plt.title('Loss probability with different rates of B packets')
plt.show()


'''

# ******************************************************************************
# PLOTS *******************************************************************


# DROP PROBABILITY UNDER DIFFERENT VALUES OF f 
# add system meauserments
B_rate = np.arange(0, 1.05, 0.05)
loss_prob = []
for f in B_rate:
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
    env.process(arrival_process(env, MM1, SERVICE, ARRIVAL))
    # simulate until SIM_TIME
    env.run(until=SIM_TIME)
    loss_prob.append(cloud.pCloud/data.arr)

    
plt.plot(B_rate, loss_prob, 'r')
plt.xlabel('f')
plt.ylabel('Loss probability')
plt.title('Loss probability with different rates of B packets')
plt.show()
f=0.4  # set fixed value


# SIZE OF BUFFER OF MICRO DATA CENTER IMPACT
buffSize = np.arange(5, 60, 5)
loss_prob1 = []
for size in buffSize:
    maxBufferMD = size
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
    env.process(arrival_process(env, MM1, SERVICE, ARRIVAL))
    # simulate until SIM_TIME
    env.run(until=SIM_TIME)
    loss_prob1.append(cloud.pCloud/data.arr)
    
plt.plot(buffSize, loss_prob1, 'r')
plt.xlabel('Buffer of Micro Datacenter')
plt.ylabel('Loss probability')
plt.title('Loss probability with different buffer of micro datacenter')
plt.show()
maxBufferMD = 7 # set fixed value

# SIZE OF BUFFER OF CLOUD DATA CENTER IMPACT
buffSize = np.arange(5, 60, 5)
loss_prob2 = []
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
    env.process(arrival_process(env, MM1, SERVICE, ARRIVAL))
    # simulate until SIM_TIME
    env.run(until=SIM_TIME)
    loss_prob2.append(cloud.pCloud/data.arr)
    
plt.plot(buffSize, loss_prob2, 'r')
plt.xlabel('Buffer of Cloud Datacenter')
plt.ylabel('Loss probability')
plt.title('Loss probability with different buffer size of cloud datacenter')
plt.show()
maxBufferCD = 7 # set fixed value

'''
'''
INCREASING THE BUFFER SIZE OF BOTH MICRODATACENTER AND CLOUD REDUCE THE LOSS PROBABILITY
BUT IN CASE OF CLOUD THE PROB DROP TO 0 WITH A BUFF GREATER THAN 20
WHILE FOR MICRODATACENTER THE PROBABILITY IS REDUCED BUT NOT TO 0 


'''
