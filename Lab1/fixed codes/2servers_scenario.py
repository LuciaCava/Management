#!/usr/bin/python3
import random
import simpy


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
        
      
class Measure_queue:
    def __init__(self, Narr):
        self.arr = Narr
        
       
# ******************************************************************************
# Client
# ******************************************************************************       
class Client:
    def __init__(self,Type,ArrivalT):
        self.type = Type
        self.Tarr = ArrivalT
    def print(self):
        return self.type
        

# ******************************************************************************
# Constants
# ******************************************************************************
LOAD=0.85
SERVICE = 10.0 # av service time
ARRIVAL   = SERVICE/LOAD # av inter-arrival time
TYPE1 = 1 
maxBuffer = 4 
SIM_TIME = 500000

arrivals=0
users = 0
BusyServer1=False # True: server is currently busy; False: server is currently idle

BusyServer2=False # True: server is currently busy; False: server is currently idle
queue =[] 
MM2=[]
infiniteBuff = False



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
def arrival_process(environment,queue):
    global users
    global BusyServer1, BusyServer2
    
    while True:
        #print("Arrival no. ",data.arr+1," at time ",environment.now," with ",users," users" )
        
        # total number of packets arrived in the system
        dataSys.arr += 1 
        dataSys.ut += users*(environment.now-dataSys.oldT)
        dataSys.oldT = environment.now
            
        # sample the time until the next event
        inter_arrival = random.expovariate(1.0/ARRIVAL)
        
        if infiniteBuff==True:
            users += 1
            cl=Client(TYPE1,env.now)
            queue.append(cl)
            if BusyServer1 == False: 
                BusyServer1 = True
                service_time1 = random.expovariate(1.0/SERVICE)
                env.process(departure_process1(env, service_time1,queue))
            elif BusyServer2 == False:
                BusyServer2 = True
                service_time2 = random.expovariate(1.0/SERVICE)
                env.process(departure_process2(env, service_time2,queue))
            
        else: 
            if users<maxBuffer:
                users += 1
                cl=Client(TYPE1,env.now)
                queue.append(cl)
                
                # distinguish the two queues
                if BusyServer1 == False: 
                    BusyServer1 = True
                    service_time1 = random.expovariate(1.0/SERVICE)
                    env.process(departure_process1(env, service_time1,queue))
                elif BusyServer2 == False:
                    BusyServer2 = True
                    service_time2 = random.expovariate(1.0/SERVICE)
                    env.process(departure_process2(env, service_time2,queue))
            elif users>=maxBuffer:
                dataSys.pCloud+=1
            
        yield environment.timeout(inter_arrival)
        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"

# ******************************************************************************

# departures *******************************************************************
def departure_process1(environment, service_time,queue):
    global users
    global BusyServer1, BusyServer2
    
    
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
        service_time = random.expovariate(1.0/SERVICE)
        env.process(departure_process1(env, service_time,queue))

        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"
       
     
def departure_process2(environment, service_time,queue):
    global users
    global BusyServer1, BusyServer2

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
        service_time = random.expovariate(1.0/SERVICE)
        env.process(departure_process2(env, service_time,queue))

        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"

# ******************************************************************************


# ******************************************************************************
# the main body of the simulation
# ******************************************************************************


# create the environment

random.seed(42)

dataSys = Measure_system(0,0,0,0,0,0)
data1 = Measure_queue(0)
data2 = Measure_queue(0)

env = simpy.Environment()

# start the arrival processes
env.process(arrival_process(env,MM2))


# simulate until SIM_TIME
env.run(until=SIM_TIME)


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



if len(MM2)>0:
    print("Arrival time of the last element in the queue:",MM2[len(MM2)-1].Tarr)
    

