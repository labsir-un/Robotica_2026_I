
#!/usr/bin/env python3
import math,time
import numpy as np
import matplotlib.pyplot as plt
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

class PincherCommander(Node):
    def __init__(self):
        super().__init__("pincher_commander")
        self.pub=self.create_publisher(JointState,"/pincher/command",10)
        self.sub=self.create_subscription(JointState,"/joint_states",self.cb,10)
        self.joints=["waist","shoulder","elbow","wrist","gripper"]
        self.q_medida=[0.0]*5
    def cb(self,msg):
        self.q_medida=[math.degrees(x) for x in msg.position]
    def publicar(self,q):
        m=JointState()
        m.header.stamp=self.get_clock().now().to_msg()
        m.name=self.joints
        m.position=[math.radians(x) for x in q]
        self.pub.publish(m)
    def mover_suave(self,qi,qf,duracion=2,hz=50):
        pasos=int(duracion*hz)
        for i in range(pasos+1):
            a=i/pasos
            q=[x+a*(y-x) for x,y in zip(qi,qf)]
            self.publicar(q)
            rclpy.spin_once(self,timeout_sec=0)
            time.sleep(1/hz)
    def senoidal(self,idx,A,f,duracion=10,hz=50,q0=None):
        if q0 is None: q0=[0,0,0,0,0]
        t0=time.time()
        tt=[];qd=[];qm=[]
        while True:
            t=time.time()-t0
            if t>duracion: break
            q=q0.copy()
            q[idx]=q0[idx]+A*math.sin(2*math.pi*f*t)
            self.publicar(q)
            rclpy.spin_once(self,timeout_sec=0)
            tt.append(t);qd.append(q[idx]);qm.append(self.q_medida[idx])
            time.sleep(1/hz)
        e=np.array(qd)-np.array(qm)
        print(f"Error máximo: {np.max(np.abs(e)):.3f}°")
        print(f"RMSE: {np.sqrt(np.mean(e**2)):.3f}°")
        plt.figure()
        plt.plot(tt,qd,label="Deseada")
        plt.plot(tt,qm,label="Medida")
        plt.grid();plt.legend()
        plt.xlabel("Tiempo [s]");plt.ylabel("Ángulo [°]")
        plt.title("Seguimiento articular")
        plt.show()

def main():
    rclpy.init()
    n=PincherCommander()
    while n.pub.get_subscription_count()==0:
        print("Esperando controlador...");time.sleep(.2)
    print("1. Movimiento secuencial")
    print("2. Movimiento simultáneo")
    print("3. Movimiento senoidal")
    op=input("Opción: ")
    qi=[0,0,0,0,0]
    q1=[80,0,0,0,0];q2=[80,-35,0,0,0];q3=[80,-35,55,0,0];q4=[80,-35,55,-45,0]
    if op=="1":
        qa=qi
        for q in [q1,q2,q3,q4]:
            n.mover_suave(qa,q);qa=q
    elif op=="2":
        n.mover_suave(qi,q4,4)
    elif op=="3":
        print("Articulación: 1.Base 2.Hombro 3.Codo 4.Muñeca 5.Pinza")
        idx=int(input("Seleccione: "))-1
        A=float(input("Amplitud [°]: "))
        f=float(input("Frecuencia [Hz]: "))
        d=float(input("Duración [s]: "))
        n.senoidal(idx,A,f,d,q0=qi)
    n.destroy_node();rclpy.shutdown()
if __name__=="__main__":
    main()