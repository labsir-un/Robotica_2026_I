
#!/usr/bin/env python3
import sys, math
import numpy as np



import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import time


def dh(theta,d,a,alpha):
    ct,st=np.cos(theta),np.sin(theta)
    ca,sa=np.cos(alpha),np.sin(alpha)
    return np.array([
        [ct,-st*ca, st*sa,a*ct],
        [st, ct*ca,-ct*sa,a*st],
        [0,     sa,    ca,   d],
        [0,      0,     0,   1]
    ],float)

def rpy_from_R(R):
    pitch=math.atan2(-R[2,0], math.sqrt(R[0,0]**2+R[1,0]**2))
    if abs(math.cos(pitch))<1e-8:
        roll=0
        yaw=math.atan2(-R[0,1],R[1,1])
    else:
        roll=math.atan2(R[2,1],R[2,2])
        yaw=math.atan2(R[1,0],R[0,0])
    return roll,pitch,yaw

if len(sys.argv)!=5:
    print("Uso: python3 fk_phantom.py q1 q2 q3 q4")
    sys.exit(1)

q1,q2,q3,q4=[math.radians(float(x)) for x in sys.argv[1:]]

theta = [
    q1,
    q2 - math.radians(70.67),
    q3 + math.radians(70.67),
    q4
]

d = [
    92.5,
    0,
    0,
    0
]

a = [
    0,
    105.71,
    100,
    66.6
]

alpha = [
    -math.pi/2,
    0,
    0,
    0
]

T_NOA = np.array([
    [ 0,  0,  1,    47],
    [-1,  0,  0,   0.0],
    [ 0, -1,  0,   0.0],
    [ 0,  0,  0,   1.0]
], dtype=float)


A=[]

T = np.eye(4)

for i in range(4):
    Ai = dh(theta[i], d[i], a[i], alpha[i])
    T = T @ Ai

    print(f"\nT0_{i+1} =")
    print(np.round(T,4))

    print(f"Origen {i+1}: ({T[0,3]:.3f}, {T[1,3]:.3f}, {T[2,3]:.3f})")

T = T@T_NOA

print("\nT0_TCP =")
print(np.round(T,4))

x,y,z=T[0,3],T[1,3],T[2,3]
roll,pitch,yaw=rpy_from_R(T[:3,:3])

print("\n===== TCP =====")
print(f"x = {x:.3f} mm")
print(f"y = {y:.3f} mm")
print(f"z = {z:.3f} mm")
print(f"roll  = {math.degrees(roll):.3f} deg")
print(f"pitch = {math.degrees(pitch):.3f} deg")
print(f"yaw   = {math.degrees(yaw):.3f} deg")





JOINT_NAMES = [
    "waist",
    "shoulder",
    "elbow",
    "wrist",
    "gripper"
]


class SmoothCommander(Node):

    def __init__(self):
        super().__init__("fk_phantom")

        self.publisher = self.create_publisher(
            JointState,
            "/pincher/command",
            10
        )

        self.current = [0.0] * 5

        self.subscription = self.create_subscription(
            JointState,
            "/joint_states",
            self.joint_callback,
            10
        )

    def joint_callback(self, msg):
        self.current = list(msg.position)

    def publish(self, q):

        msg = JointState()

        msg.header.stamp = self.get_clock().now().to_msg()

        msg.name = JOINT_NAMES

        msg.position = q

        self.publisher.publish(msg)


print("\nEsperando estado actual del robot...")

rclpy.init()

node = SmoothCommander()

while rclpy.ok():

    rclpy.spin_once(node, timeout_sec=0.1)

    if len(node.current) == 5:
        break


start = node.current.copy()

target = [
    q1,
    q2,
    q3,
    q4,
    0.0
]

duration = 3.0
frequency = 200
steps = int(duration * frequency)

print("Moviendo robot...")

for i in range(steps + 1):

    alpha = i / steps

    q = [
        start[j] + alpha * (target[j] - start[j])
        for j in range(5)
    ]

    node.publish(q)

    rclpy.spin_once(node, timeout_sec=0)

    time.sleep(1 / frequency)

print("Movimiento terminado.")

node.destroy_node()

rclpy.shutdown()
