#!/usr/bin/python3

'''
Consider max size of the buffer equal to 3 
'''


import random
import simpy


# ******************************************************************************
# To take the measurements
# ******************************************************************************
class Measure:
    def __init__(self,Narr,Ndep,NAveraegUser,OldTimeEvent,AverageDelay, SentToCloud):
        self.arr = Narr
        self.dep = Ndep
        self.ut = NAveraegUser
        self.oldT = OldTimeEvent
        self.delay = AverageDelay
        self.pCloud = SentToCloud
 
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

SIM_TIME = 500000
maxBuffer = 3 #if we set equal to 1 it is like other case, 1 service and no buffer 
arrivals=0
users=0
BusyServer=False # True: server is currently busy; False: server is currently idle

MM1=[]

# ******************************************************************************
# generator yield events to the simulator
# ******************************************************************************

# arrivals *********************************************************************
def arrival_process(environment,queue):
    global users
    global BusyServer
    while True:
        #print("Arrival no. ",data.arr+1," at time ",environment.now," with ",users," users" )
        # cumulate statistics 
        data.arr += 1   
        data.ut += users*(environment.now-data.oldT)
        data.oldT = environment.now
        # sample the time until the next event
        inter_arrival = random.expovariate(1.0/ARRIVAL)
        
        #update state variable and put the client in the queue
        # check size of the queue, if it hasn't reach the max capacity yet then we can add the new client in the queue
        # otherwise, send the packets directly to the cloud
        if users<maxBuffer: 
            users += 1
            cl=Client(TYPE1,env.now)
            queue.append(cl)
            if users == 1: 
                BusyServer = True
                service_time = random.expovariate(1.0/SERVICE)
                env.process(departure_process(env, service_time,queue))
        elif users>=maxBuffer:
            data.pCloud += 1
        
        # yield an event to the simulator
        yield environment.timeout(inter_arrival)

        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"

# ******************************************************************************

# departures *******************************************************************
def departure_process(environment, service_time, queue):
    global users
    global BusyServer

    
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
        service_time = random.expovariate(1.0/SERVICE)
        env.process(departure_process(env, service_time,queue))

        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"
       

# ******************************************************************************


# ******************************************************************************
# the main body of the simulation
# ******************************************************************************


# create the environment

random.seed(42)

data = Measure(0,0,0,0,0,0)

env = simpy.Environment()

# start the arrival processes
env.process(arrival_process(env, MM1))


# simulate until SIM_TIME
env.run(until=SIM_TIME)


# print output data
print("MEASUREMENTS \n\nNo. of users in the queue:",users,"\nNo. of arrivals =",
      data.arr,"- No. of departures =",data.dep)

print("Load: ",SERVICE/ARRIVAL)
print("\nArrival rate: ",data.arr/env.now,"/n - Departure rate: ",data.dep/env.now)

print("\nAverage number of users: ",data.ut/env.now)

print("Average delay: ",data.delay/data.dep)
print("Actual queue size: ",len(MM1))

print('number of packets sent to the cloud: ', data.pCloud)

if len(MM1)>0:
    print("Arrival time of the last element in the queue:",MM1[len(MM1)-1].Tarr)
    

