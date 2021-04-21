#!/usr/bin/python3
import random
import simpy
import matplotlib.pyplot as plt 
import numpy as np

# ******************************************************************************
# To take the measurements
# ******************************************************************************
class Measure_system:
    def __init__(self,Narr,Ndep, NAveraegUser,OldTimeEvent,AverageDelay,SentToCloud):
        self.arr = Narr
        self.dep = Ndep
        self.ut = NAveraegUser
        self.oldT = OldTimeEvent
        self.delay = AverageDelay
        self.pCloud = SentToCloud
        self.waitingTime = []
        
      
class Measure_queue:
    def __init__(self, Narr, busy):
        self.arr = Narr
        self.busy = 0
        
       
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
ARRIVAL   = SERVICE/LOAD # av inter-arrival time
TYPE1 = 1 
maxBuffer = 0 
SIM_TIME = 500000

arrivals=0
users = 0
BusyServer1=False # True: server is currently busy; False: server is currently idle

BusyServer2=False # True: server is currently busy; False: server is currently idle
queue =[] 
MM2=[]
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
    maxBuffer = int(input("Insert the buffer size:\nf"))
    maxBuffer = maxBuffer + 2
    print("Max number of packets in the systems is = ", maxBuffer)



# ******************************************************************************
# generator yield events to the simulator
# ******************************************************************************

# arrivals *********************************************************************
def arrival_process(environment,queue, serv, arrival):
    global users
    global BusyServer1, BusyServer2
    
    while True:
        #print("Arrival no. ",data.arr+1," at time ",environment.now," with ",users," users" )
        
        # total number of packets arrived in the system
        dataSys.arr += 1 
        dataSys.ut += users*(environment.now-dataSys.oldT)
        dataSys.oldT = environment.now
            
        # sample the time until the next event
        inter_arrival = random.expovariate(1.0/arrival)
        
        if infiniteBuff==True:
            users += 1
            cl=Client(TYPE1,env.now)
            queue.append(cl)
            entrance_user.append(env.now)
            if BusyServer1 == False: 
                BusyServer1 = True
                service_time1 = random.expovariate(1.0/serv)
                data1.busy += service_time1
                env.process(departure_process1(env, service_time1,queue,serv))
            elif BusyServer2 == False:
                BusyServer2 = True
                service_time2 = random.expovariate(1.0/serv)
                data2.busy += service_time2
                env.process(departure_process2(env, service_time2,queue,serv))
            
        else: 
            if users<maxBuffer:
                users += 1
                cl=Client(TYPE1,env.now)
                queue.append(cl)
                entrance_user.append(env.now)
                # distinguish the two queues
                if BusyServer1 == False: 
                    BusyServer1 = True
                    service_time1 = random.expovariate(1.0/serv)
                    data1.busy += service_time1
                    env.process(departure_process1(env, service_time1,queue, serv))
                elif BusyServer2 == False:
                    BusyServer2 = True
                    service_time2 = random.expovariate(1.0/serv)
                    data2.busy += service_time2
                    env.process(departure_process2(env, service_time2,queue, serv))
            elif users>=maxBuffer:
                dataSys.pCloud+=1
            
        yield environment.timeout(inter_arrival)
        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"

# ******************************************************************************

# departures *******************************************************************
def departure_process1(environment, service_time,queue, serv):
    global users
    global BusyServer1, BusyServer2
    
    served_user.append(env.now)
    yield environment.timeout(service_time)
    #print("Departure no. ",data.dep+1," at time ",environment.now," with ",users," users" )
    data1.arr +=1 
    # cumulate statistics    
    dataSys.dep += 1
    dataSys.ut += users*(environment.now-dataSys.oldT)
    dataSys.oldT = environment.now
    user=queue.pop(0) 
    dataSys.delay += (env.now-user.Tarr)
    #update state variable and extract the client in the queue
    users -= 1
    if len(queue)==1 or len(queue)==0: 
        BusyServer1 = False
    else:
        service_time = random.expovariate(1.0/serv)
        data1.busy += service_time
        env.process(departure_process1(env, service_time,queue,serv))

        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"
       
     
def departure_process2(environment, service_time,queue, serv):
    global users
    global BusyServer1, BusyServer2

    served_user.append(env.now)
    yield environment.timeout(service_time)
    
    #print("Departure no. ",data.dep+1," at time ",environment.now," with ",users," users" )
    
    # cumulate statistics    
    dataSys.dep += 1
    dataSys.ut += users*(environment.now-dataSys.oldT)
    dataSys.oldT = environment.now
    data2.arr += 1
    #update state variable and extract the client in the queue
    users -= 1
    user=queue.pop(0)
    dataSys.delay += (env.now-user.Tarr)
    
    if len(queue)==1 or len(queue)==0: 
        BusyServer2 = False
    else:
        service_time = random.expovariate(1.0/serv)
        data2.busy += service_time
        env.process(departure_process2(env, service_time,queue,serv))

        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"

# ******************************************************************************


# ******************************************************************************
# the main body of the simulation
# ******************************************************************************


# create the environment

random.seed(42)

dataSys = Measure_system(0,0,0,0,0,0)
data1 = Measure_queue(0,0)
data2 = Measure_queue(0,0)

env = simpy.Environment()

# start the arrival processes
env.process(arrival_process(env,MM2, SERVICE, ARRIVAL))


# simulate until SIM_TIME
env.run(until=SIM_TIME)

# compute time in waiting line for each user
for i in range(len(served_user)-1):
    dataSys.waitingTime.append(served_user[i] - entrance_user[i])

# erase values equal to zero 
delayed_waiting = [w for w in dataSys.waitingTime if w!=0]

# print output data
print("MEASUREMENTS \n")
print("No. of arrivals =", dataSys.arr)
print("No. of departures =",dataSys.dep)
print("No. of packets sent to the cloud =", dataSys.pCloud)
print("Actual queue size: ",len(MM2))

print("\nLoad = ",SERVICE/ARRIVAL)
print("Service rate =", 1/SERVICE)

print("Arrival rate = ",dataSys.arr/env.now,"\nDeparture rate = ",dataSys.dep/env.now)
print("Sent to the cloud rate = ", dataSys.pCloud/env.now)

print("\nAverage number of users (E[N]) = ",dataSys.ut/env.now)
print("Average delay (E[T]) =  ",dataSys.delay/dataSys.dep)
print("Average time in the waiting line (E[T_w]) =  ", np.mean(dataSys.waitingTime))
print("Average time in the waiting line only considering delayed packets (E[T_w]) =  ", np.mean(delayed_waiting))

print("\nThe first server processed packets: ", data1.arr)
print(f"and was busy the {(data1.busy/env.now)*100} % of the time")
print(data1.busy)
print("\nThe second server processed packets: ", data2.arr)
print(f"and was busy the {(data2.busy/env.now)*100} % of the time")

if len(MM2)>0:
    print("Arrival time of the last element in the queue:",MM2[len(MM2)-1].Tarr)
    
    
# ******************************************************************************
# PLOTS MEASUREMENTS UNDER DIFFERENT SERVICE RATES 
# ******************************************************************************

# performance analysis for infinite or no buffer scenario
if infiniteBuff==True or maxBuffer==2: 
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
            MM2 = [] 
            arrivals=0
            users=0
            
            BusyServer1=False # True: server is currently busy; False: server is currently idle
            BusyServer2=False
            random.seed(42)
            arrival = SERVICE/load
            
            dataSys = Measure_system(0,0,0,0,0,0)
            data1 = Measure_queue(0,0)
            data2 = Measure_queue(0,0)
            #ser_rate.append(1/serv)
            env = simpy.Environment()
            
            # start the arrival processes
            env.process(arrival_process(env, MM2, SERVICE, arrival))
            # simulate until SIM_TIME
            env.run(until=SIM_TIME)
            e_n.append(dataSys.ut/env.now)
            
            e_t.append(dataSys.delay/dataSys.dep)
            if infiniteBuff==False:
                cloud.append(dataSys.pCloud/dataSys.arr)
    
    # plot the avg number of packets 
    plt.plot(loads, e_n, 'r')
    plt.xlabel('Service rate-loads')
    plt.ylabel('E[N]')
    plt.title('Average Number of Users')
    plt.show()
    
    # plot the avg delay
    plt.plot(loads, e_t, 'r')
    plt.xlabel('Service rate-loads')
    plt.ylabel('E[T]')
    plt.title('Average delay')
    plt.show()
    
    if infiniteBuff==False: 
        plt.plot(loads, cloud, 'r')
        plt.xlabel('Service rate-loads')
        plt.ylabel('Cloud rate')
        plt.title('Rate of packets sent to the cloud')
        plt.show()
   
# for finite buffer scenario: plot measurement with diff buffer size 
if maxBuffer>2 : 
    print('boh')
    loads=np.arange(0.05, 1.05, 0.05)
    s = len(loads)
    #buffSize = [8,16,32,64] # with values used in the case of one server, no big changes 
    buffSize = [4,8,16]
    b = len(buffSize)
    e_n = np.zeros((b,s))
    e_t = np.zeros((b,s))
    cloud = np.zeros((b,s))
    i=0
    
    for buff in buffSize:
        j=0
        maxBuffer = buff
        print(buff)
        for load in loads: 
            if load == 0:
                pass
            else:
                MM2 = [] 
                arrivals=0
                users=0
                BusyServer1=False # True: server is currently busy; False: server is currently idle
                BusyServer2=False
                
                random.seed(42)
                arrival = SERVICE/load
                
                dataSys = Measure_system(0,0,0,0,0,0)
                env = simpy.Environment()
                # start the arrival processes
                env.process(arrival_process(env, MM2, SERVICE, arrival))
                # simulate until SIM_TIME
                env.run(until=SIM_TIME)
                
                e_n[i,j]= dataSys.ut/env.now
                e_t[i,j] = dataSys.delay/dataSys.dep
                cloud[i,j] = dataSys.pCloud/dataSys.arr
            j = j+1
            
        i = i +1

    plt.plot(loads, e_n[0,:], 'r', label='B=4')
    plt.plot(loads, e_n[1,:], 'b',label='B=8')    
    plt.plot(loads, e_n[2,:], 'g', label='B=16') 
     #plt.plot(loads, e_n[3,:], 'y', label='B=64')
    plt.xlabel('Service rate-loads')
    plt.ylabel('E[N]')
    plt.title('Average Number of Users')
    plt.legend()
    plt.show()
    
    plt.plot(loads, e_t[0,:], 'r', label='B=4')
    plt.plot(loads, e_t[1,:], 'b',label='B=8')    
    plt.plot(loads, e_t[2,:], 'g', label='B=16') 
    #plt.plot(loads, e_t[3,:], 'y', label='B=64')
    plt.xlabel('Service rate-loads')
    plt.ylabel('E[T]')
    plt.legend()
    plt.title('Average delay')
    plt.show()
    
    plt.plot(loads, cloud[0,:], 'r', label='B=4')
    plt.plot(loads, cloud[1,:], 'b',label='B=8')    
    plt.plot(loads, cloud[2,:], 'g', label='B=16') 
    #plt.plot(loads, cloud[3,:], 'y', label='B=64')
    plt.xlabel('Service rate-loads')
    plt.ylabel('Cloud rate')
    plt.title('Rate of packets sent to the cloud')
    plt.legend()
    plt.show()

