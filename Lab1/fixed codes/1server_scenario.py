import random
import simpy
import matplotlib.pyplot as plt 
import numpy as np

# ******************************************************************************
# To take the measurements
# ******************************************************************************
class Measure:
    def __init__(self,Narr,Ndep,NAveraegUser,OldTimeEvent,AverageDelay, SentToCloud, busy):
        self.arr = Narr
        self.dep = Ndep
        self.ut = NAveraegUser
        self.oldT = OldTimeEvent
        self.delay = AverageDelay
        self.pCloud = SentToCloud
        self.waitingTime = []
        self.busy = busy 
 
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
TYPE1 = 1 

SIM_TIME = 500000
maxBuffer = 0 #if we set equal to 1 it is like other case, 1 service and no buffer 
arrivals=0
users=0
BusyServer=False # True: server is currently busy; False: server is currently idle
MM1=[]
infiniteBuff = False
entrance_user = []
served_user = []


# ******************************************************************************
# User input
# ******************************************************************************
fin = input("Do you want to simulate a finite or infinite buffer? Press f for finite or i for infinite: \n")
if fin=='i':
    infiniteBuff = True
elif fin == 'f':
    print(1)
    maxBuffer = int(input("Insert the buffer size:\nf"))
    maxBuffer = maxBuffer + 1 
    print("Max number of packets in the systems is = ", maxBuffer)
    


# ******************************************************************************
# generator yield events to the simulator
# ******************************************************************************

# arrivals *********************************************************************
def arrival_process(environment,queue, service, arrival):
    global users
    global BusyServer
    while True:
        #print("Arrival no. ",data.arr+1," at time ",environment.now," with ",users," users" )
        # cumulate statistics 
        data.arr += 1   
        data.ut += users*(environment.now-data.oldT)
        data.oldT = environment.now
        # sample the time until the next event
        inter_arrival = random.expovariate(1.0/arrival)
        
        # check if the user wants to simulate a finite or infinite buffer 
        if infiniteBuff == True: 
            #update state variable and put the client in the queue
            users += 1
            cl=Client(TYPE1,env.now)
            queue.append(cl)
            entrance_user.append(env.now)
            if users == 1: 
                BusyServer = True
                service_time = random.expovariate(1.0/service)
                data.busy += service_time
                env.process(departure_process(env, service_time,queue, service))
        else: 
            #update state variable and put the client in the queue
            # check size of the queue, if it hasn't reach the max capacity yet then we can add the new client in the queue
            # otherwise, send the packets directly to the cloud
            if users<maxBuffer: 
                users += 1
                cl=Client(TYPE1,env.now)
                queue.append(cl)
                entrance_user.append(env.now)
                if users == 1: 
                    BusyServer = True
                    service_time = random.expovariate(1.0/service)
                    data.busy += service_time
                    env.process(departure_process(env, service_time,queue, service))
            elif users>=maxBuffer:
                data.pCloud += 1
        
        # yield an event to the simulator
        yield environment.timeout(inter_arrival)

        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"

# ******************************************************************************

# departures *******************************************************************
def departure_process(environment, service_time, queue, service):
    global users
    global BusyServer

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
    data.delay += (env.now-user.Tarr)
    
    if users==0: 
        BusyServer = False
    else:
        service_time = random.expovariate(1.0/service)
        data.busy += service_time
        env.process(departure_process(env, service_time,queue, service))
        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"
       
# ******************************************************************************


# ******************************************************************************
# the main body of the simulation
# ******************************************************************************

# create the environment

random.seed(42)

data = Measure(0,0,0,0,0,0,0)

env = simpy.Environment()

# start the arrival processes
env.process(arrival_process(env, MM1, SERVICE, ARRIVAL))


# simulate until SIM_TIME
env.run(until=SIM_TIME)

# compute time in waiting line for each user
for i in range(len(served_user)-1):
    data.waitingTime.append(served_user[i] - entrance_user[i])
    
# erase values equal to zero 
delayed_waiting = [w for w in data.waitingTime if w!=0]


# print output data
print("MEASUREMENTS \n")
print("No. of arrivals =", data.arr)
print("No. of departures =",data.dep)
print("No. of packets sent to the cloud =", data.pCloud)
print("Actual queue size: ",len(MM1))

print("\nLoad = ",SERVICE/ARRIVAL)
print("Service rate =", 1/SERVICE)

print("Arrival rate = ",data.arr/env.now,"\nDeparture rate = ",data.dep/env.now)
print("Sent to the cloud rate = ", data.pCloud/env.now)

print("\nAverage number of users (E[N]) = ",data.ut/env.now)
print("Average delay (E[T]) =  ",data.delay/data.dep)
print("Average time in the waiting line (E[T_w]) =  ", np.mean(data.waitingTime))
print("Average time in the waiting line only considering delayed packets (E[T_w]) =  ", np.mean(delayed_waiting))


if len(MM1)>0:
    print("Arrival time of the last element in the queue:",MM1[len(MM1)-1].Tarr)

 
  
# ******************************************************************************
# PLOTS MEASUREMENTS UNDER DIFFERENT SERVICE RATES 
# ******************************************************************************

# performance analysis for infinite or no buffer scenario
if infiniteBuff==True or maxBuffer==1: 
    #service_rate =np.arange(8, 15, 0.5)  # av service time
    loads=np.arange(0.05, 1.05, 0.05)
    ser_rate = []
    e_n = [] 
    e_t = []
    cloud = [] 
    # simulate the system 
    #for serv in service_rate: 
    for load in loads: 
        if load == 0:
            pass
        else:
            MM1 = [] 
            arrivals=0
            users=0
            BusyServer=False
            random.seed(42)
            arrival = SERVICE/load
            
            data = Measure(0,0,0,0,0,0, 0)
            #ser_rate.append(1/serv)
            env = simpy.Environment()
            
            # start the arrival processes
            env.process(arrival_process(env, MM1, SERVICE, arrival))
            # simulate until SIM_TIME
            env.run(until=SIM_TIME)
            e_n.append(data.ut/env.now)
            e_t.append(data.delay/data.dep)
            if infiniteBuff==False:
                cloud.append(data.pCloud/data.arr)
    
    # plot the avg number of packets 
    plt.plot(loads, e_n, 'r')
    plt.xlabel('Loads')
    plt.ylabel('E[N]')
    plt.title('Average Number of Users')
    plt.show()
    
    # plot the avg delay
    plt.plot(loads, e_t, 'r')
    plt.xlabel('Loads')
    plt.ylabel('E[T]')
    plt.title('Average delay')
    plt.show()
    
    if infiniteBuff==False: 
        plt.plot(loads, cloud, 'r')
        plt.xlabel('Loads')
        plt.ylabel('Cloud rate')
        plt.title('Rate of packets sent to the cloud')
        plt.show()
    


# for finite buffer scenario: plot measurement with diff buffer size 
if maxBuffer >1 : 
    loads=np.arange(0.05, 1.05, 0.05)
    s = len(loads)
    buffSize = [8,16,32,64]
    b = len(buffSize)
    e_n = np.zeros((b,s))
    e_t = np.zeros((b,s))
    cloud = np.zeros((b,s))
    i=0
    
    for buff in buffSize:
        j=0
        maxBuffer = buff
        for load in loads: 
            if load == 0:
                pass
            else:
                MM1 = [] 
                arrivals=0
                users=0
                BusyServer=False
                random.seed(42)
                arrival = SERVICE/load
                
                data = Measure(0,0,0,0,0,0,0)
                env = simpy.Environment()
                # start the arrival processes
                env.process(arrival_process(env, MM1, SERVICE, arrival))
                # simulate until SIM_TIME
                env.run(until=SIM_TIME)
                
                e_n[i,j]= data.ut/env.now
                e_t[i,j] = data.delay/data.dep
                cloud[i,j] = data.pCloud/data.arr
               
            j = j+1
            
        i = i +1

    plt.plot(loads, e_n[0,:], 'r', label='B=8')
    plt.plot(loads, e_n[1,:], 'b',label='B=16')    
    plt.plot(loads, e_n[2,:], 'g', label='B=32') 
    plt.plot(loads, e_n[3,:], 'y', label='B=64')
    plt.plot('Loads')
    plt.ylabel('E[N]')
    plt.title('Average Number of Users')
    plt.legend()
    plt.show()
    
    plt.plot(loads, e_t[0,:], 'r', label='B=8')
    plt.plot(loads, e_t[1,:], 'b',label='B=16')    
    plt.plot(loads, e_t[2,:], 'g', label='B=32') 
    plt.plot(loads, e_t[3,:], 'y', label='B=64')
    plt.xlabel('Loads')
    plt.ylabel('E[T]')
    plt.legend()
    plt.title('Average delay')
    plt.show()
    
    plt.plot(loads, cloud[0,:], 'r', label='B=8')
    plt.plot(loads, cloud[1,:], 'b',label='B=16')    
    plt.plot(loads, cloud[2,:], 'g', label='B=32') 
    plt.plot(loads, cloud[3,:], 'y', label='B=64')
    plt.xlabel('loads')
    plt.ylabel('Cloud rate')
    plt.title('Rate of packets sent to the cloud')
    plt.legend()
    plt.show()
    
            
            
# ******************************************************************************
# ANALYZE CASE NO BUFFER WITH DIFFERENCE SERVICE RATES
# ******************************************************************************
if infiniteBuff==False and maxBuffer==1:
    print("DIFFERENT SERVICE RATE")
    service = [5,7,10,15]
    b = len(service)
    loads=np.arange(0.05, 1.05, 0.05)
    s = len(loads)
    e_n = np.zeros((b,s))
    e_t = np.zeros((b,s))
    cloud = np.zeros((b,s))
    i=0
    for serv in service:
        j=0
        for load in loads: 
            if load == 0:
                pass
            else:
                MM1 = [] 
                arrivals=0
                users=0
                BusyServer=False
                random.seed(42)
                arrival = serv/load
                
                data = Measure(0,0,0,0,0,0,0)
                env = simpy.Environment()
                # start the arrival processes
                env.process(arrival_process(env, MM1, SERVICE, arrival))
                # simulate until SIM_TIME
                env.run(until=SIM_TIME)
                
                e_n[i,j]= data.ut/env.now
                e_t[i,j] = data.delay/data.dep
                cloud[i,j] = data.pCloud/data.arr
            j = j+1
        i = i +1

    plt.plot(loads, e_n[0,:], 'r', label='serv=5')
    plt.plot(loads, e_n[1,:], 'b',label='serv=7')    
    plt.plot(loads, e_n[2,:], 'g', label='serv=10') 
    plt.plot(loads, e_n[3,:], 'y', label='serv=15')
    plt.xlabel('Loads')
    plt.ylabel('E[N]')
    plt.title('Average Number of Users')
    plt.legend()
    plt.show()
    
    plt.plot(loads, e_t[0,:], 'r', label='serv=5')
    plt.plot(loads, e_t[1,:], 'b',label='serv=7')    
    plt.plot(loads, e_t[2,:], 'g', label='serv=10') 
    plt.plot(loads, e_t[3,:], 'y', label='serv=15')
    plt.xlabel('Loads')
    plt.ylabel('E[T]')
    plt.legend()
    plt.title('Average delay')
    plt.show()
    
    plt.plot(loads, cloud[0,:], 'r', label='serv=5')
    plt.plot(loads, cloud[1,:], 'b',label='serv=7')    
    plt.plot(loads, cloud[2,:], 'g', label='serv=10') 
    plt.plot(loads, cloud[3,:], 'y', label='serv=15')
    plt.xlabel('Loads')
    plt.ylabel('Cloud rate')
    plt.title('Rate of packets sent to the cloud')
    plt.legend()
    plt.show()
    
   
            
# ******************************************************************************
# EVALUATE BUSY RATE UNDER DIFFERENT BUFFER SIZE AT FIXED LOAD=0.85
# ******************************************************************************     
            
if maxBuffer>1:
    buffSize = np.arange(5, 60, 5)
    LOAD = 0.85
    busy_time=[]
    for buff in buffSize:
        MM1 = [] 
        arrivals=0
        users=0
        BusyServer=False
        random.seed(42)
        serv = 10
        arrival = serv/load
        maxBuffer = buff
        data = Measure(0,0,0,0,0,0,0)
        env = simpy.Environment()
        # start the arrival processes
        env.process(arrival_process(env, MM1, SERVICE, arrival))
        # simulate until SIM_TIME
        env.run(until=SIM_TIME)
        busy_time.append(data.busy/env.now)
        
    plt.plot(buffSize, busy_time, 'r', label='serv1')
    plt.xlabel('Buffer size')
    plt.ylabel('Busy time')
    plt.title('Busy time vs buffer size')
    plt.show()
    

