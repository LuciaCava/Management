import random
import simpy
import matplotlib.pyplot as plt 
import numpy as np

'''
LAB 2 POINT 4, MULTIPLE SERVERS IN MICRO AND CLOUD DATA CENTER

'''

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
SERVICE_PREPROC = 5.0 # av service time
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
n_server = 3
n_serverCD = 4
busyMD = [False for i in range(n_server)]
busyCD= [False for i in range(n_serverCD)]
MM1=[]
MM1_cloud=[] 
entrance_user = []
served_user = []
actuators_user = []         
k = 0
queuingTot = [] 
prova = np.zeros(n_server)

# ******************************************************************************
# generator yield events to the simulator
# ******************************************************************************

# SIMULATOR MICRODATA CENTER 

# arrivals *********************************************************************
def arrival_process(environment,queue):
    global users, prova
    global BusyMD
    
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
        if users<maxBufferMD+n_server: 
            users += 1
            queue.append(cl)
            for i,item in enumerate(busyMD):
                if item == False: 
                    busyMD[i] = True 
                    #print(i)
                    prova[i] = prova[i] + 1
                    service_time = random.expovariate(1.0/SERVICE_PREPROC)
                    data.busy += service_time
                    env.process(departure_process(environment, service_time,queue, i))
                    break
        elif users>=maxBufferMD+n_server:
            data.pCloud += 1
            # packet is sent to the cloud, so it is add the prop time
            arrival_cloud_process(env, MM1_cloud, cl)
            # send to the cloud, call function 
         # yield an event to the simulator
        yield environment.timeout(inter_arrival)
        
# ******************************************************************************

# departures *******************************************************************
def departure_process(environment, service_time, queue, i):
    global users
    global BusyMD
    global k, prova
    
    #print(len(queue))
    yield environment.timeout(service_time)
    user=queue.pop(0)
    #print("Departure no. ",data.dep+1," at time ",environment.now," with ",users," users" )
    # cumulate statistics    
    data.dep += 1
    data.ut += users*(environment.now-data.oldT)
    data.oldT = environment.now
    prova[i] = prova[i]-1 
    #update state variable and extract the client in the queue
    users -= 1 
    #print(prova)
    data.delay += (environment.now-user.Tarr)
    
    if user.type == TYPE2:
        k = k+1
        user.preproc = 1
        arrival_cloud_process(environment, MM1_cloud,user)
    if user.type == TYPE1: 
        user.queuingTime = (environment.now-user.Tarr) + prop_fog_act 
        queuingTot.append(user.queuingTime)
    #if (len(queue) - sum(prova)<0): 
    if users < n_server:
        busyMD[i] = False 
    else:
        prova[i] = prova[i] + 1 
        service_time = random.expovariate(1.0/SERVICE_PREPROC)
        data.busy += service_time
        env.process(departure_process(environment, service_time,queue, i))
        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"


# ******************************************************************************
# SIMULATION CLOUD SERVER *******************************************************************
    
# arrivals *********************************************************************
def arrival_cloud_process(environment,queue1, client):
    global users_cloud
    global BusyCD
    
    #print("Arrival no. ",data.arr+1," at time ",environment.now," with ",users," users" )
    # cumulate statistics 
    cloud.arr += 1   
    
    cloud.ut += users_cloud*(environment.now-cloud.oldT)
    cloud.oldT = environment.now
    
    # sample the time until the next event
    if users_cloud<maxBufferCD+n_serverCD: 
        queue1.append(client)
        users_cloud += 1
        for j,item in enumerate(busyCD):
            if busyCD[j] == False: 
                busyCD[j] = True 
                print(busyCD)
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
                env.process(departure_cloud(environment, service_time,queue1, j))
                break
    else:
        cloud.pCloud += 1
        
   
# departures *******************************************************************
def departure_cloud(environment, service_time, queue1, i):
    global users_cloud
    global BusyCD

    yield environment.timeout(service_time) 
    user=queue1.pop(0)
    # cumulate statistics    
    cloud.dep += 1
    cloud.ut += users_cloud*(environment.now-cloud.oldT)
    cloud.oldT = environment.now
    
    user.queuingTime = (environment.now-user.Tarr) + prop_time + prop_cloud_act 
    queuingTot.append(user.queuingTime) 
    
    #update state variable and extract the client in the queue
    users_cloud = users_cloud - 1
    cloud.delay += (env.now-user.Tarr)   
    if users_cloud< n_serverCD: 
        busyCD[i] = False
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
       
        cloud.busy += service_time
        env.process(departure_cloud(environment, service_time,queue1, i))
        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"
    
# ******************************************************************************
# START SIMULATION

random.seed(43)
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
print("No. of packets sent to the cloud =", data.pCloud)  #+k)
print("Actual queue size: ",len(MM1))

print("Arrival rate = ",data.arr/env.now,"\nDeparture rate = ",data.dep/env.now)
print("Sent to the cloud rate = ", (data.pCloud+k)/env.now)

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
print(cloud.pCloud)

