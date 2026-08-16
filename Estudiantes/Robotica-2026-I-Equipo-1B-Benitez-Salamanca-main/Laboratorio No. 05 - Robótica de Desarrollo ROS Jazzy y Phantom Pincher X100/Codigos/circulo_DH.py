
#!/usr/bin/env python3
import math,time
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

# DH (m)
d1=0.0925
a2=0.10571
a3=0.1000
a4=0.0666

OFFSET2=70.67
OFFSET3=70.67

CENTER=(0.18,0.0,0.10)
RADIUS=0.03
POINTS=180

class Circle(Node):
    def __init__(self):
        super().__init__("circle")
        self.pub=self.create_publisher(JointState,"/pincher/command",10)
        self.names=["waist","shoulder","elbow","wrist","gripper"]

    def send(self,qdeg):
        m=JointState()
        m.header.stamp=self.get_clock().now().to_msg()
        m.name=self.names
        m.position=[math.radians(x) for x in qdeg]
        self.pub.publish(m)

def ik(x,y,z):
    q1=math.atan2(y,x)
    phi=0.0
    r=math.hypot(x,y)
    rw=r-a4*math.cos(phi)
    zw=(z-d1)-a4*math.sin(phi)
    D=(rw*rw+zw*zw-a2*a2-a3*a3)/(2*a2*a3)
    D=max(-1,min(1,D))
    q3=math.atan2(math.sqrt(1-D*D),D)
    q2=math.atan2(zw,rw)-math.atan2(a3*math.sin(q3),a2+a3*math.cos(q3))
    q4=phi-q2-q3
    # aplicar offsets DH
    q2=math.degrees(q2)+OFFSET2
    q3=math.degrees(q3)-OFFSET3
    q4=math.degrees(q4)
    return [math.degrees(q1),q2,q3,q4,0]

def main():
    rclpy.init()
    node=Circle()
    while node.pub.get_subscription_count()==0:
        time.sleep(0.1)
    cx,cy,cz=CENTER
    for i in range(POINTS+1):
        t=2*math.pi*i/POINTS
        x=cx+RADIUS*math.cos(t)
        y=cy
        z=cz+RADIUS*math.sin(t)
        node.send(ik(x,y,z))
        rclpy.spin_once(node,timeout_sec=0)
        time.sleep(0.02)
    node.destroy_node()
    rclpy.shutdown()

if __name__=="__main__":
    main()
