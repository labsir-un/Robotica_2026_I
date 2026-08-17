import rclpy, time
from rclpy.node import Node
from sensor_msgs.msg import JointState

JOINTS = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']

LIMITS = {
    'waist':   (-2.6180, 2.6180),
    'shoulder':(-2.6180, 2.6180),
    'elbow':   (-2.6180, 2.6180),
    'wrist':   (-2.6180, 2.6180),
    'gripper': (-1.5708, 1.5708),
}

class PincherLab(Node):
    def __init__(self):
        super().__init__('pincher_lab_node')
        self.pub = self.create_publisher(JointState,'/pincher/command',10)
        self.sub = self.create_subscription(JointState,'/joint_states',self._cb,10)
        self.current = {j:0.0 for j in JOINTS}
        for _ in range(20): rclpy.spin_once(self, timeout_sec=0.1)

    def _cb(self,msg):
        for n,p in zip(msg.name,msg.position):
            if n in self.current: self.current[n]=p

    def send(self,targets:dict):
        for j,v in targets.items():
            lo,hi = LIMITS[j]
            if not (lo<=v<=hi): raise ValueError(f'{j}={v:.3f} fuera de limite [{lo:.3f},{hi:.3f}]')
        msg = JointState(); msg.name=list(targets.keys()); msg.position=list(targets.values())
        self.pub.publish(msg)

    def spin_for(self, seconds):
        end = time.time()+seconds
        while time.time() < end: rclpy.spin_once(self, timeout_sec=0.02)

    def interp_lineal(self,qi,qf,dur,hz=50):
        n=int(dur*hz)
        for k in range(n+1):
            s=k/n; self.send({j: qi[j]+s*(qf[j]-qi[j]) for j in qi}); self.spin_for(1/hz)

    def interp_quintica(self,qi,qf,dur,hz=50):
        n=int(dur*hz)
        for k in range(n+1):
            t=k/n; s=10*t**3-15*t**4+6*t**5
            self.send({j: qi[j]+s*(qf[j]-qi[j]) for j in qi}); self.spin_for(1/hz)
