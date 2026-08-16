#!/usr/bin/env python3
import math,time
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
class Dancer(Node):
    def __init__(self):
        super().__init__("dancer")
        self.pub=self.create_publisher(JointState,"/pincher/command",10)
        self.names=["waist","shoulder","elbow","wrist","gripper"]
    def send(self,q):
        m=JointState();m.header.stamp=self.get_clock().now().to_msg();m.name=self.names;m.position=[math.radians(x) for x in q];self.pub.publish(m)
    def move(self,a,b,d=0.5,hz=40):
        n=int(d*hz)
        for i in range(n+1):
            t=i/n
            self.send([x+t*(y-x) for x,y in zip(a,b)])
            rclpy.spin_once(self,timeout_sec=0);time.sleep(1/hz)
HOME=[0,0,0,0,0]
POSES=[[25,-10,35,-25,30],[-25,-10,35,-25,0],[35,-35,60,-15,30],[-35,-35,60,-15,0],[20,-15,30,-35,30],[-20,-15,30,-35,0],[0,-40,70,-10,30],[0,-20,40,-20,0]]
def main():
    rclpy.init();n=Dancer()
    while n.pub.get_subscription_count()==0: time.sleep(.1)
    print("Inicia la canción en..."); 
    for i in range(5,0,-1): print(i);time.sleep(1)
    cur=HOME;ini=time.time()
    while time.time()-ini<48:
        for p in POSES: n.move(cur,p);cur=p
        for p in reversed(POSES[:-1]): n.move(cur,p);cur=p
    n.move(cur,HOME,2);n.destroy_node();rclpy.shutdown()
if __name__=="__main__": main()
