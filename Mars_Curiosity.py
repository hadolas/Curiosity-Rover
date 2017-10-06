#!/usr/bin/python

import threading
from threading import Lock
import random
import time
import logging

## log the problem encountered into log file. 
logging.basicConfig(filename = 'curiosity.log', level=logging.INFO,
                    format='%(asctime)s:%(message)s')


def decision():
    ## decide whether a solution works (40% chance of success).
    global solved
    probability = ["SUCCESS", "SUCCESS","FAIL","FAIL","FAIL"]
    #probability = ["SUCCESS"]
    #probability = ["FAIL"]
    solved = random.choice(probability)
    print("SOLVED =", solved)
    return solved

def vectoring(cv, problem):
    ## vector forwards if:
    ## (a)there is no problem,
    ## (b)after changing direction(rotate) to see if new direction works, or
    ## (c)after deflating wheels to see if loose sand can now be traversed over. 
    global solved
    global wheel_Lifted
    cv.acquire()
    if problem == "None":
        print("VECTORING...\n")
    if (solved=="FAIL" and problem=="Rock"):
        if (wheel_Lifted==True and rotated==False):
            print("VECTORING...\n")
        if rotated==True:
            print("VECTORING...")
            ## check if changing direction works
            decision()
            if solved == "SUCCESS":
                solution = "Reverse --> New Direction --> Vector"
    if (solved=="FAIL" and problem == "Loose Sand"):
        if deflated_Wheels == True:
            print("VECTORING...\n")
            ## check if Loose Sand problem has been overcome
            decision()
            if solved == "SUCCESS":
                solution = "Deflate Wheels --> Vector --> Inflate Wheels"
                logging.info('>> ERROR: {} \\ SOLUTION: {} \\ {}'.format(problem, solution, solved))
    cv.notifyAll()
    cv.release()

    

def lift_Wheel(cv,problem):
    ## lift a wheel of the rover
    global wheel_Lifted
    cv.acquire()
    if problem =="Rock" and solved== "FAIL": 
        print("LIFTING WHEEL\n")
        wheel_Lifted=True
    cv.notifyAll()
    cv.release()
    return wheel_Lifted

def lower_Wheel(cv,problem):
    ## lower lifted wheel
    solution = "Lift wheel --> Vector --> Lower Wheel"
    global wheel_Lifted
    cv.acquire()
    if problem =="Rock" and solved== "FAIL" and wheel_Lifted==True: 
        print("LOWERING WHEEL\n")
        wheel_Lifted=False
        ## check if Rock problem has been overcome
        decision()
        ## if overcome, log the problem and solution
        if solved == "SUCCESS":
            logging.info('>> ERROR: {} \\ SOLUTION: {} \\ {}'.format(problem, solution, solved))
    cv.notifyAll()
    cv.release()
    return wheel_Lifted

def reverse(cv, problem):
    ## reverse rover to ready it either for a new direction (Rock) or
    ## to deflate wheels (Loose Sand)
    global reverse_d
    cv.acquire()
    if (problem =="Rock" or problem=="Loose Sand")and solved== "FAIL":
        print("REVERSING 30cm (subtlely)...\n")
        reverse_d = True
    cv.notifyAll()
    cv.release()
    return reverse_d


def change_Direction(cv, problem):
    ## change direction of Rover to try to avoid the Rock
    global rotated
    cv.acquire()
    if problem =="Rock" and solved== "FAIL":
        print("Changing Direction")
        rotated = True
    cv.notifyAll()
    cv.release()
    return rotated


def requestingHelp(cv,problem):
    ## if the rover is unable to overcome the problem then request help from headquarters.
    cv.acquire()
    if (problem =="Rock" or problem=="Loose Sand" or problem=="Rough Terrain") and solved== "FAIL":
        print("Requesting help from headquarters...")
        decision()
        if solved == "SUCCESS":
            ## The help received from headquarters was successful! Log this solution. 
            solution = "Received instructions from headquarters"
            logging.info('>> ERROR: {} \\ SOLUTION: {} \\ {}'.format(problem, solution, solved))
        else:
            ## The help received wasn't enough to overcome the problem. Log mission fail.
            mission_fail = "No solution -- Mission Failure"
            logging.info('>> ERROR: {} \\ SOLUTION: {} \\ {}'.format(problem, mission_fail, solved))
    cv.notifyAll()
    cv.release()

def deflate_Wheels(cv,problem):
    ## deflate wheels, readying the rover for traversing over loose sand
    global deflated_Wheels
    cv.acquire()
    if (problem=="Loose Sand") and solved== "FAIL":
        print("Slightly deflating wheels...")
        deflated_Wheels = True
    cv.release()
    return deflated_Wheels

def inflate_Wheels(cv,problem):
    ## re-inflate the wheels of the rover
    global deflated_Wheels
    cv.acquire()
    if (problem=="Loose Sand") and solved== "FAIL":
        print("Inflating wheels back to normal pressure...")
        deflated_Wheels = False
    cv.release()
    return deflated_Wheels

def Three_point_turn(cv, problem):
    ## Turn rover to face backwards. Apparently traversing backwards over rough terrain
    ## causes less damage to a vehicle!
    global facing_forward
    cv.acquire()
    if (problem=="Rough Terrain") and solved== "FAIL":
        print("Performing 3-point-turn")
        facing_forward = False
    cv.release()
    return facing_forward

def traversing_backwards(cv, problem):
    ## Traverse backwards over rough terrain
    global facing_forward
    cv.acquire()
    if (problem=="Rough Terrain") and solved== "FAIL" and facing_forward==False:
        print("Traversing backwards over rough terrain")
    cv.release()

def reorienting(cv,problem):
    ## Face forwards again after traversing over rough terrain. 
    global facing_forward
    cv.acquire()
    if (problem=="Rough Terrain") and solved== "FAIL" and facing_forward==False:
        print("Reorienting to face forwards")
        facing_forward = True
        ## Check if Rough Terrain problem has been overcome.
        decision()
        if solved == "SUCCESS":
            ## log the problem and solution 
            solution = "3-point-turn --> Traversed backwards over rough terrain --> Reoriented to face forward"
            logging.info('>> ERROR: {} \\ SOLUTION: {} \\ {}'.format(problem, solution, solved))
    cv.release()
    return facing_forward


## list of problems which the rover could encounter
problist =["Rock", "Loose Sand", "Rough Terrain", "None"]

## Pass lock to thread to enable execution of a sequence of  actions
lock = Lock()
cv = threading.Condition(lock)

probNumber=0

## The rover encounters exactly 5 problems.
while probNumber<5:
    wheel_Lifted = False
    reverse_d = False
    rotated = False
    deflated_Wheels = False
    facing_forward = True
    
    solved = "FAIL"
    problem = random.choice(problist)
    print("\nProblem encountered: ", problem)
    print(".........................")

    ## Create threads, where each thread can only carry out one action.
    t1 = threading.Thread(target = lift_Wheel, args=(cv,problem))
    t2 = threading.Thread(target = vectoring, args=(cv,problem))
    t3 = threading.Thread(target = lower_Wheel, args=(cv,problem))
    t4 = threading.Thread(target = reverse, args=(cv,problem))
    t5 = threading.Thread(target = change_Direction, args=(cv,problem))
    t6 = threading.Thread(target = deflate_Wheels, args=(cv,problem))
    t7 = threading.Thread(target = vectoring, args=(cv,problem))
    t8 = threading.Thread(target = inflate_Wheels, args=(cv,problem))
    t9 = threading.Thread(target = Three_point_turn, args=(cv,problem))
    t10 = threading.Thread(target = traversing_backwards, args=(cv,problem))
    t11 = threading.Thread(target = reorienting, args=(cv,problem))
    t12 = threading.Thread(target = requestingHelp, args=(cv,problem))

    ## start running threads 
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()
    t7.start()
    t8.start()
    t9.start()
    t10.start()
    t11.start()
    t12.start()
    
   
    time.sleep(3)
    ## only increment probNumber if a problem was encountered.
    if problem != "None":
        probNumber=probNumber+1
    

    time.sleep(3)

    print("____________________________________________")
    


