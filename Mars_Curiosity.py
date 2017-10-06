#!/usr/bin/python

import threading
from threading import Lock
import random
import time
import logging

logging.basicConfig(filename = 'curiosity.log', level=logging.INFO,
                    format='%(asctime)s:%(message)s')


def decision():
    global solved
    probability = ["SUCCESS", "SUCCESS","FAIL","FAIL","FAIL"]
    #probability = ["SUCCESS"]
    #probability = ["FAIL"]
    solved = random.choice(probability)
    print("SOLVED =", solved)
    return solved

def vectoring(cv, problem):
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
            decision()
            if solved == "SUCCESS":
                solution = "Reverse --> New Direction --> Vector"
    if (solved=="FAIL" and problem == "Loose Sand"):
        if deflated_Wheels == True:
            print("VECTORING...\n")
            decision()
            if solved == "SUCCESS":
                solution = "Deflate Wheels --> Vector --> Inflate Wheels"
                logging.info('>> ERROR: {} \\ SOLUTION: {} \\ {}'.format(problem, solution, solved))
    cv.notifyAll()
    cv.release()

    

def lift_Wheel(cv,problem):
    global wheel_Lifted
    cv.acquire()
    if problem =="Rock" and solved== "FAIL": 
        print("LIFTING WHEEL\n")
        wheel_Lifted=True
    cv.notifyAll()
    cv.release()
    return wheel_Lifted

def lower_Wheel(cv,problem):
    solution = "Lift wheel --> Vector --> Lower Wheel"
    global wheel_Lifted
    cv.acquire()
    if problem =="Rock" and solved== "FAIL" and wheel_Lifted==True: 
        print("LOWERING WHEEL\n")
        wheel_Lifted=False
        decision()
        if solved == "SUCCESS":
            logging.info('>> ERROR: {} \\ SOLUTION: {} \\ {}'.format(problem, solution, solved))
    cv.notifyAll()
    cv.release()
    return wheel_Lifted

def reverse(cv, problem):
    global reverse_d
    cv.acquire()
    if (problem =="Rock" or problem=="Loose Sand")and solved== "FAIL":
        print("REVERSING 30cm (subtlely)...\n")
        reverse_d = True
    cv.notifyAll()
    cv.release()
    return reverse_d


def change_Direction(cv, problem):
    global rotated
    cv.acquire()
    if problem =="Rock" and solved== "FAIL":
        print("Changing Direction")
        rotated = True
    cv.notifyAll()
    cv.release()
    return rotated


def requestingHelp(cv,problem):
    cv.acquire()
    if (problem =="Rock" or problem=="Loose Sand" or problem=="Rough Terrain") and solved== "FAIL":
        print("Requesting help from headquarters...")
        decision()
        if solved == "SUCCESS":
                solution = "Received instructions from headquarters"
                logging.info('>> ERROR: {} \\ SOLUTION: {} \\ {}'.format(problem, solution, solved))
        else:
            mission_fail = "No solution -- Mission Failure"
            logging.info('>> ERROR: {} \\ SOLUTION: {} \\ {}'.format(problem, mission_fail, solved))
    cv.notifyAll()
    cv.release()

def deflate_Wheels(cv,problem):
    global deflated_Wheels
    cv.acquire()
    if (problem=="Loose Sand") and solved== "FAIL":
        print("Slightly deflating wheels...")
        deflated_Wheels = True
    cv.release()
    return deflated_Wheels

def inflate_Wheels(cv,problem):
    global deflated_Wheels
    cv.acquire()
    if (problem=="Loose Sand") and solved== "FAIL":
        print("Inflating wheels back to normal pressure...")
        deflated_Wheels = False
    cv.release()
    return deflated_Wheels

def Three_point_turn(cv, problem):
    global facing_forward
    cv.acquire()
    if (problem=="Rough Terrain") and solved== "FAIL":
        print("Performing 3-point-turn")
        facing_forward = False
    cv.release()
    return facing_forward

def traversing_backwards(cv, problem):
    global facing_forward
    cv.acquire()
    if (problem=="Rough Terrain") and solved== "FAIL" and facing_forward==False:
        print("Traversing backwards over rough terrain")
    cv.release()

def reorienting(cv,problem):
    global facing_forward
    cv.acquire()
    if (problem=="Rough Terrain") and solved== "FAIL" and facing_forward==False:
        print("Reorienting to face forwards")
        facing_forward = True
        decision()
        if solved == "SUCCESS":
                solution = "3-point-turn --> Traversed backwards over rough terrain --> Reoriented to face forward"
                logging.info('>> ERROR: {} \\ SOLUTION: {} \\ {}'.format(problem, solution, solved))
    cv.release()
    return facing_forward
    
    

        
problist =["Rock", "Loose Sand", "Rough Terrain", "None"]
#problist =["Rock"]
#problist =["Rock","Loose Sand"]
#problist =["Rough Terrain"]
#problist =["None"]
#problist =["Loose Sand"]

lock = Lock()
cv = threading.Condition(lock)

probNumber=0

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
    if problem != "None":
        probNumber=probNumber+1
    

    time.sleep(3)

    print("____________________________________________")
    


