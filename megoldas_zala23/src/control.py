#!/usr/bin/env python3
'''
2018 Varundev Suresh Babu (University of Virginia)
                MIT License
'''

import rospy
from geometry_msgs.msg import Twist
## from simulator.msg import PIDInput
from control_msgs.msg import PidState
import math
import numpy as np

pub = rospy.Publisher('cmd_vel', Twist, queue_size=1)

kp = 10.
kd = 0.01
kp_vel = 42.0
kd_vel = 0.0

ki = 0.0
servo_offset = 18.0*math.pi/180
prev_error = 0.0
error = 0.0
integral = 0.0
vel_input = 1.0


def control(data):
    global integral
    global prev_error
    global vel_input
    global kp
    global ki
    global kd
    global kd_vel
    global kp_vel
    ## velocity = data.pid_vel
    velocity = data.error_dot
    angle = servo_offset
    ## error = 5*data.pid_error
    error = 5*data.error
    #print "Error Control",error
    if error!=0.0:
        # if abs(error - prev_error)>0.5:
        # 	integral = integral + error
        control_error = kp*error + kd*(error - prev_error)# + ki*integral
        #print "Control", control_error
        # integral = integral/1.3

        # print "Control error",control_error
        angle = angle + control_error*np.pi/180
        # print "Control error",control_error

        control_error_vel = kp_vel*error + kd_vel*(error - prev_error)
        # print "Control error velocity",control_error_vel

        # velocity = velocity - abs(control_error_vel)/10
        if velocity < 0.01:
            velocity = 0.0
        else:
            velocity = velocity + abs(control_error_vel)



    prev_error = error
    #print("Angle in Degrees %.1f" % (angle*180/np.pi)) # Just for reference
    msg_cmd = Twist()

    if (data.header.frame_id == "simple"):
        if velocity < 0:
            velocity = 0.0

        if velocity > 4.0:
            velocity = 4.0

    else:
        if angle > 30*np.pi/180:
            angle = 30*np.pi/180
        if angle < -30*np.pi/180:
            angle = -30*np.pi/180

        # velocity = 1
        # # if angle > 20*np.pi/180 or angle < -20*np.pi/180:
        # # 	velocity = 0.3
        if angle >= 10*np.pi/180 or angle <= -10*np.pi/180:
            velocity = 0.8

        if angle > 20*np.pi/180 or angle < -20*np.pi/180:
            velocity = 0.3

        if angle >= -1*np.pi/180 and angle <= 1*np.pi/180:
            velocity = 2.0

        if velocity < 0:
            velocity = 0.0

        if velocity > 2.5:
            velocity = 2.5



    #print "Velocity",velocity
    #print "Angle",angle


    msg_cmd.linear.x = velocity * 0.2 # TODO: test low speed
    msg_cmd.angular.z = data.error # angle
    pub.publish(msg_cmd)

def listener():
    rospy.init_node('pid_controller', anonymous=True)
    ## rospy.Subscriber("error", PIDInput, control)
    rospy.Subscriber("error", PidState, control)
    global kp
    global ki
    global kd
    global vel_input
    #kp = input("Enter Kp Value: ")
    #ki = input("Enter Ki Value: ")
    #kd = input("Enter Kd Value: ")
    #vel_input = input("Enter Velocity: ")
    rospy.spin()


if __name__ == '__main__':
    print("Listening to error for PID")
    listener()