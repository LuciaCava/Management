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
        self.waitingTime = []
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

# ******************************************************************************
# Constants
# ******************************************************************************
LOAD=0.85
SERVICE = 10.0 # av service time
ARRIVAL = SERVICE/LOAD # av inter-arrival time
TYPE1 = 'A'
TYPE2 = 'B' 
SERVICE_CLOUD = 15.0
ARRIVAL_CLOUD = SERVICE_CLOUD/LOAD
f = 0.8# fraction of packet b among all packets 

SIM_TIME = 500000
maxBufferMD = 10 #if we set equal to 1 it is like other case, 1 service and no buffer 
maxBufferCD = 10
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

pack_delay = [] 

# ******************************************************************************
# generator yield events to the simulator
# ******************************************************************************

# SIMULATOR MICRODATA CENTER 

# arrivals *********************************************************************
def arrival_process(environment,queue, service, arrival):
    global users
    global BusyServerMD
   
    
    while True:
        #print("Arrival no. ",data.arr+1," at time ",environment.now," with ",users," users" )
        # cumulate statistics 
        data.arr += 1   
        data.ut += users*(environment.now-data.oldT)
        data.oldT = environment.now
        # sample the time until the next event
        inter_arrival = random.expovariate(1.0/arrival)
        cl=Client(TYPE1,env.now)
        # generate packet of type A or of type B depending on the value of x
        # if x is greater than f, generate pack A, in the other case generate pack B 
        x = random.uniform(0,1)
        if x >= f: 
            cl=Client(TYPE1,env.now)
        else:
            cl=Client(TYPE2, env.now)
            
        if users<maxBufferMD: 
            users += 1
            queue.append(cl)
            entrance_user.append(env.now)
            if users == 1: 
                BusyServerMD = True
                service_time = random.expovariate(1.0/service)
                data.busy += service_time
                env.process(departure_process(env, service_time,queue, service))
        elif users>=maxBufferMD:
            data.pCloud += 1
            arrival_cloud_process(env, MM1_cloud, SERVICE_CLOUD, ARRIVAL_CLOUD,cl)
            # send to the cloud, call function 
         # yield an event to the simulator
        yield environment.timeout(inter_arrival)
        
# ******************************************************************************

# departures *******************************************************************
def departure_process(environment, service_time, queue, service):
    global users
    global BusyServerMD
    global k 

    served_user.append(env.now)
    yield environment.timeout(service_time)
    #print("Departure no. ",data.dep+1," at time ",environment.now," with ",users," users" )
    # cumulate statistics    
    data.dep += 1
    data.ut += users*(environment.now-data.oldT)
    data.oldT = environment.now
    #update state variable and extract the client in the queue
    users -= 1
    user=queue.pop(0)
   
    if user.type == TYPE2:
        k = k+1
        arrival_cloud_process(env, MM1_cloud, SERVICE_CLOUD, ARRIVAL_CLOUD,user)
    data.delay += (env.now-user.Tarr)
    if users==0: 
        BusyServerMD = False
    else:
        service_time = random.expovariate(1.0/service)
        data.busy += service_time
        env.process(departure_process(env, service_time,queue, service))
        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"


# ******************************************************************************
# SIMULATION CLOUD SERVER *******************************************************************
    
# arrivals *********************************************************************
def arrival_cloud_process(environment,queue1, service, arrival, client):
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
            service_time = random.expovariate(1.0/service)
            cloud.busy += service_time
            env.process(departure_cloud(env, service_time,queue1, service))
    elif users_cloud>=maxBufferCD:
        cloud.pCloud += 1
        # send to the cloud, call function 
        
   
    
# departures *******************************************************************
def departure_cloud(environment, service_time, queue, service):
    global users_cloud
    global BusyServerCD

    yield environment.timeout(service_time)
    #print("Departure no. ",data.dep+1," at time ",environment.now," with ",users," users" )
    
    # cumulate statistics    
    cloud.dep += 1
    cloud.ut += users*(environment.now-cloud.oldT)
    cloud.oldT = environment.now

    #update state variable and extract the client in the queue
    users_cloud -= 1

    user=queue.pop(0)
            
    cloud.delay += (env.now-user.Tarr)
    
    if users_cloud==0: 
        BusyServerCD = False
    else:
        service_time = random.expovariate(1.0/service)
        cloud.busy += service_time
        env.process(departure_cloud(env, service_time,queue, service))
        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"
       
# ******************************************************************************






random.seed(42)
data = Measure(0,0,0,0,0,0,0)
cloud = Measure(0,0,0,0,0,0,0) 
env = simpy.Environment()

# start the arrival processes
env.process(arrival_process(env, MM1, SERVICE, ARRIVAL))

# simulate until SIM_TIME
env.run(until=SIM_TIME)


# print output data
print("MEASUREMENTS \n")
print("No. of arrivals =", data.arr)
print("No. of departures =",data.dep)
print("No. of packets sent to the cloud =", data.pCloud+k)
print("Actual queue size: ",len(MM1))

print("\nLoad = ",SERVICE/ARRIVAL)
print("Service rate =", 1/SERVICE)

print("Arrival rate = ",data.arr/env.now,"\nDeparture rate = ",data.dep/env.now)
print("Sent to the cloud rate = ", data.pCloud/env.now)

print("\nAverage number of users (E[N]) = ",data.ut/env.now)
print("Average delay (E[T]) =  ",data.delay/data.dep)
#print("Average time in the waiting line (E[T_w]) =  ", np.mean(data.waitingTime))
#print("Average time in the waiting line only considering delayed packets (E[T_w]) =  ", np.mean(delayed_waiting))

if len(MM1)>0:
    print("Arrival time of the last element in the queue:",MM1[len(MM1)-1].Tarr)




# print output data
print("MEASUREMENTS of CLOUD SERVER\n")
print("No. of arrivals =", cloud.arr)
print("No. of departures =",cloud.dep)
print("No. of packets dropped =", cloud.pCloud)
print("Actual queue size: ",len(MM1_cloud))




# ******************************************************************************
# PLOTS *******************************************************************


# DROP PROBABILITY UNDER DIFFERENT VALUES OF f 
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
f=0.4


# SIZE OF BUFFER OF MICRO DATA CENTER IMPACT





