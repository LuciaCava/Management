#!/usr/bin/python3


import random
import simpy
import numpy as np
import matplotlib.pyplot as plt


# ******************************************************************************
# To take the measurements
# ******************************************************************************
class Measure:
    def __init__(self,Narr,Ndep,NAveraegUser,OldTimeEvent,AverageDelay, packetsCloud):
        self.arr = Narr
        self.dep = Ndep
        self.ut = NAveraegUser
        self.oldT = OldTimeEvent
        self.delay = AverageDelay
        self.pCloud = packetsCloud
 
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
SERVICE =np.arange(3, 19, 0.5)  # av service time
#ARRIVAL   = SERVICE/LOAD # av inter-arrival time
TYPE1 = 1 

SIM_TIME = 500000

arrivals=0
users=0
pacCloud = 0 
BusyServer=False # True: server is currently busy; False: server is currently idle

MM1=[]

# ******************************************************************************
# generator yield events to the simulator
# ******************************************************************************

# arrivals *********************************************************************
def arrival_process(environment,queue,load, service):
    global users
    global BusyServer
    while True:
        #print("Arrival no. ",data.arr+1," at time ",environment.now," with ",users," users" )
        arrival = service /load
        # cumulate statistics 
        data.arr += 1
        data.ut += users*(environment.now-data.oldT)
        data.oldT = environment.now
        
        # sample the time until the next event
        inter_arrival = random.expovariate(1.0/arrival)
        
        if users == 0: 
            users = 1 
            service_time = random.expovariate(1.0/service)
            env.process(departure_process(env, service_time))
        elif users == 1: 
            data.pCloud += 1
        
        yield environment.timeout(inter_arrival)

        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"

# ******************************************************************************

# departures *******************************************************************
def departure_process(environment, service_time):
    global users
    global BusyServer

    
    yield environment.timeout(service_time)
    #print("Departure no. ",data.dep+1," at time ",environment.now," with ",users," users" )
    users = 0 
    # cumulate statistics    
    data.dep += 1
    data.ut += (environment.now-data.oldT)
    data.oldT = environment.now

    #update state variable and extract the client in the queue
    
    
   
       

# ******************************************************************************


# ******************************************************************************
# the main body of the simulation
# ******************************************************************************

#plt.close('all')
# create the environment
ratio = []
stat_dep = []
stat_cloud = []
ratio1=[]
stat_load= [] 
arrival_rate = []
stat_arr = []
departure_rate = [] 
stat_cloud_rate = []
for serv in SERVICE: 
    random.seed(42)
    arrival = serv/LOAD
    data = Measure(0,0,0,0,0,0)
    env = simpy.Environment()

    # start the arrival processes
    env.process(arrival_process(env, MM1, LOAD, serv))
    # simulate until SIM_TIME
    env.run(until=SIM_TIME)
    ratio.append(data.dep/data.arr)
    ratio1.append(data.pCloud/data.arr)
    stat_dep.append(data.dep)
    stat_arr.append(data.arr)
    stat_cloud.append(data.pCloud)
    stat_cloud_rate.append(data.pCloud/env.now)
    arrival_rate.append(data.arr/env.now)
    departure_rate.append(data.dep/env.now)
    users=0
    arrivals=0 
    MM1 = []
    
    '''
    # print output data
    print("MEASUREMENTS \n\nNo. of users in the queue:",users,"\nNo. of arrivals =",
          data.arr,"- No. of departures =",data.dep)
    
    print("Load: ",serv /arrival)
    print("\nArrival rate: ",data.arr/env.now,"\n - Departure rate: ",data.dep/env.now)
    
    print("\nAverage number of users: ",data.ut/env.now)
    
    #print("Average delay: ",data.delay/data.dep)
    print("Actual queue size: ",len(MM1))
    
    print('num Packets forwarded to cloud: ', data.pCloud)
    
    if len(MM1)>0:
        print("Arrival time of the last element in the queue:",MM1[len(MM1)-1].Tarr)
     '''

plt.figure()
plt.plot(SERVICE, stat_dep,'.b')
plt.plot(SERVICE, stat_cloud,'r')
plt.plot(SERVICE, stat_arr,'y')
plt.grid()
plt.xlabel('service rate')
plt.ylabel('departures and send to the cloud')
plt.title('Departures')

plt.figure()
plt.plot(SERVICE, arrival_rate,'y')
plt.plot(SERVICE, departure_rate,'b')
plt.plot(SERVICE, stat_cloud_rate,'r')
plt.grid()
plt.xlabel('service rate')
plt.ylabel('arrival and dep rate')
plt.title('Rates')


plt.figure()
plt.plot(SERVICE, ratio,'r')
plt.plot(SERVICE, ratio1,'b')
plt.grid()
plt.xlabel('service rate')
plt.ylabel('cloud and dep ')
plt.title('ratio')



