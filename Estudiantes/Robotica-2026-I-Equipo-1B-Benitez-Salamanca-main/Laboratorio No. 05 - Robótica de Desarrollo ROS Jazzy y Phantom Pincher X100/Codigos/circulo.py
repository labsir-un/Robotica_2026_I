#!/usr/bin/env python3
"""
circulo.py
Dibuja un círculo en RViz usando cinemática inversa geométrica simplificada
para el PhantomX Pincher.
Ajusta los parámetros de centro/radio según sea necesario.
"""
import math,time
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

L1=0.0445
L2=0.1010
L3=0.1010
L4=0.1190

CENTER_X=5
CENTER_Y=0
CENTER_Z=5
RADIUS=0.01
POINTS=120

class Drawer(Node):
    def __init__(self):
        super().__init__('circle_drawer')
        self.pub=self.create_publisher(JointState,'/pincher/command',10)
        self.names=["waist","shoulder","elbow","wrist","gripper"]

    def send(self,q):
        m=JointState()
        m.header.stamp=self.get_clock().now().to_msg()
        m.name=self.names
        m.position=[math.radians(a) for a in q]
        self.pub.publish(m)

def ik(x,y,z):
    q1=math.atan2(y,x)
    r=math.hypot(x,y)-L4
    z=z-L1
    D=(r*r+z*z-L2*L2-L3*L3)/(2*L2*L3)
    D=max(-1,min(1,D))
    q3=math.atan2(math.sqrt(1-D*D),D)
    q2=math.atan2(z,r)-math.atan2(L3*math.sin(q3),L2+L3*math.cos(q3))
    q4=-(q2+q3)
    return [math.degrees(q1),math.degrees(q2),math.degrees(q3),math.degrees(q4),0]

def main():
    rclpy.init()
    n=Drawer()
    while n.pub.get_subscription_count()==0:
        time.sleep(.1)
    for i in range(POINTS+1):
        t=2*math.pi*i/POINTS
        x=CENTER_X+RADIUS*math.cos(t)
        y=CENTER_Y
        z=CENTER_Z+RADIUS*math.sin(t)
        n.send(ik(x,y,z))
        rclpy.spin_once(n,timeout_sec=0)
        time.sleep(0.03)
    n.destroy_node()
    rclpy.shutdown()

if __name__=="__main__":
    main()
