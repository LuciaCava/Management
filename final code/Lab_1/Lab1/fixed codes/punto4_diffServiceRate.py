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
ARRIVAL   = SERVICE/LOAD # av inter-arrival time
TYPE1 = 1 
maxBuffer = 0 
SIM_TIME = 500000
arrivals=0
users = 0

BusyServer = [False, False, False, False]
busy_time = [0,0,0,0]
server_cost = [0.5, 1.5, 1.2, 2]
#service_rate = [5, 10, 7, 15]
service_rate = [15, 10, 7, 5]
overall_cost = 0 
queue =[] 
MM2=[]
infiniteBuff = False
server = 0  #it can be either 0 or 1. base on its value, the new packet will be assigned to server1 or 2 first
entrance_user = []
served_user = []
assign = 1
a=0

#oper_cost = 

# ******************************************************************************
# User input
# ******************************************************************************

infiniteBuff = True

assign = int(input("How do you want to assign a new packet to a server? \n1:Round Robin\n2:Random\n3:Least costly:\n"))
print(assign)
# assign : RR (Round robin), Random, LC (least costly)



def arrival_process(environment,queue, serv, arrival):
    global users
    global BusyServer, a,server, busy_time, overall_cost 

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
            s1=0
            if assign == 1:
                while s1<4:
                    server = (server+1)%4
                    if BusyServer[server]==False:
                        BusyServer[server]=True
                        overall_cost = overall_cost + server_cost[server]
                        service_time = random.expovariate(1.0/service_rate[server])
                        busy_time[server] = busy_time[server] + service_time
                        env.process(departure_process(env, service_time,queue,service_rate[server],server))
                        s1=4
                    s1=s1+1
            elif assign == 2:
                server_list = [0,1,2,3]
                random.shuffle(server_list)
                while s1<4:
                    server = server_list.pop() 
                    if BusyServer[server]==False:
                        BusyServer[server]=True
                        overall_cost = overall_cost + server_cost[server]
                        service_time = random.expovariate(1.0/service_rate[server])
                        busy_time[server] = busy_time[server] + service_time
                        env.process(departure_process(env, service_time,queue,service_rate[server],server))
                        s1=4
                    s1 = s1+1
                a = a+server
            elif assign == 3:
                lis = sorted(range(len(server_cost)), key=lambda k: server_cost[k])
                while s1<4:
                    server = lis.pop(0)
                    
                    if BusyServer[server]==False:
                        overall_cost = overall_cost + server_cost[server]
                        BusyServer[server]=True
                        service_time = random.expovariate(1.0/service_rate[server])
                        busy_time[server] = busy_time[server] + service_time
                        env.process(departure_process(env, service_time,queue,service_rate[server],server))
                        s1=4
                    s1 = s1+1
            
        yield environment.timeout(inter_arrival)
        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"

# ******************************************************************************

# departures *******************************************************************
def departure_process(environment, service_time,queue, serv,i):
    global users
    global BusyServer, overall_cost
    
    
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
    if len(queue)<=4: 
        BusyServer[i] = False
    else:
        service_time = random.expovariate(1.0/serv)
        overall_cost = overall_cost + server_cost[i]
        data1.busy += service_time
        env.process(departure_process(env, service_time,queue,serv,i))

        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"
       
    

# ******************************************************************************

# ******************************************************************************
# the main body of the simulation
# ******************************************************************************


# create the environment

random.seed(13)

dataSys = Measure_system(0,0,0,0,0,0)
data1 = Measure_node(0,0,0.5)
data2 = Measure_node(0,0,0.3)

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

print("\nThe first server processed packets: ")
print(f"and was busy the {(busy_time[0]/env.now)*100} % of the time")

print("\nThe second server ", )
print(f"was busy the {(busy_time[1]/env.now)*100} % of the time")

print("\nThe third server ")
print(f" was busy the {(busy_time[2]/env.now)*100} % of the time")

print("\nThe fourth server")
print(f"was busy the {(busy_time[3]/env.now)*100} % of the time")

print('-----------------------------------------------------')
print('the overall cost is:', overall_cost)
print('and the avg time in the waiting line is:', dataSys.delay/dataSys.dep)

if len(MM2)>0:
    print("Arrival time of the last element in the queue:",MM2[len(MM2)-1].Tarr)


infiniteBuff = True    
assign = 0
loads=np.arange(0.05, 1.05, 0.05)
s = len(loads)
busy_serv1 = np.zeros((3,s))
busy_serv2 = np.zeros((3,s))
busy_serv3 = np.zeros((3,s))
busy_serv4 = np.zeros((3,s))


while (assign <=2):
    assign = assign + 1
    j = 0
    for load in loads: 
        if load == 0:
            pass
        else:
            MM2 = [] 
            arrivals=0
            users=0
            BusyServer = [False, False, False, False]
            busy_time =  [0,0,0,0]
            arrival = SERVICE/load
            dataSys = Measure_system(0,0,0,0,0,0)
            data1 = Measure_node(0,0,0.5)
            data2 = Measure_node(0,0,0.3)
            
            env = simpy.Environment()
            # start the arrival processes
            env.process(arrival_process(env,MM2, SERVICE, ARRIVAL))  
            # simulate until SIM_TIME
            env.run(until=SIM_TIME)
            
            i = assign - 1
            busy_serv1[i,j] = (busy_time[0]/env.now)*100
            busy_serv2[i,j] = (busy_time[1]/env.now)*100
            busy_serv3[i,j] = (busy_time[2]/env.now)*100
            busy_serv4[i,j] = (busy_time[3]/env.now)*100
            j=j+1
    
plt.plot(loads, busy_serv1[0,:], 'r', label='serv1')
plt.plot(loads, busy_serv2[0,:], 'b',label='serv2')    
plt.plot(loads, busy_serv3[0,:], 'g', label='serv3') 
plt.plot(loads, busy_serv4[0,:], 'y', label='serv4') 
 
plt.xlabel('Loads')
plt.ylabel('% busy time')
plt.title('% busy time using Round Robin')
plt.legend()
plt.show()

plt.plot(loads, busy_serv1[1,:], 'r', label='serv1')
plt.plot(loads, busy_serv2[1,:], 'b',label='serv2')    
plt.plot(loads, busy_serv3[1,:], 'g', label='serv3') 
plt.plot(loads, busy_serv4[1,:], 'y', label='serv4') 
 
plt.xlabel('Loads')
plt.ylabel('% busy time')
plt.title('% busy time using Random assignment')
plt.legend()
plt.show()

plt.plot(loads, busy_serv1[2,:], 'r', label='serv1')
plt.plot(loads, busy_serv2[2,:], 'b',label='serv2')    
plt.plot(loads, busy_serv3[2,:], 'g', label='serv3') 
plt.plot(loads, busy_serv4[2,:], 'y', label='serv4') 
 
plt.xlabel('Loads')
plt.ylabel('% busy time')
plt.title('% busy time using least coslty')
plt.legend()
plt.show()

