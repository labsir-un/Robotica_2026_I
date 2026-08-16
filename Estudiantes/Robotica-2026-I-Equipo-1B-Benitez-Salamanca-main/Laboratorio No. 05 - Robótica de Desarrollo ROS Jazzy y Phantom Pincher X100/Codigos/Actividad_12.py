#!/usr/bin/env python3

import sys
import math
import rclpy
import time
from rclpy.node import Node
from sensor_msgs.msg import JointState


JOINT_NAMES = [
    "waist",
    "shoulder",
    "elbow",
    "wrist",
    "gripper"
]


class SmoothCommander(Node):

    def __init__(self):
        super().__init__("ik_phantom")

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

class PhantomIK:

    def __init__(self):


        # Longitudes (mm)
        self.l1 = 105.71
        self.l2 = 100.0
        self.l3 = 113.6

        self.base_height = 92.5

        # Límites mecánicos
        self.joint_limits = [

        (-2.618 + 0.10,  2.618 - 0.10),   # Base
        (-2.00  + 0.10,  2.00  - 0.10),   # Hombro
        (-2.15  + 0.10,  1.571 - 0.10),   # Codo
        (-2.00  + 0.10,  2.30  - 0.10),   # Muñeca

]

    def within_limits(self, q):

        for i in range(4):
            if q[i] < self.joint_limits[i][0] or q[i] > self.joint_limits[i][1]:
                return False

        return True

    def distance(self, q1, q2):

        d = 0

        for i in range(4):
            d += (q1[i]-q2[i])**2

        return math.sqrt(d)
    
    @staticmethod
    def _dh(theta, d, a, alpha):
        ct, st = math.cos(theta), math.sin(theta)
        ca, sa = math.cos(alpha), math.sin(alpha)
        return [
            [ct, -st*ca,  st*sa, a*ct],
            [st,  ct*ca, -ct*sa, a*st],
            [0,      sa,     ca,    d],
            [0,       0,      0,    1]
        ]

    @staticmethod
    def _mat_mult(A, B):
        result = [[0.0]*4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                result[i][j] = sum(A[i][k]*B[k][j] for k in range(4))
        return result

    def _fk_positions(self, q1, q2, q3, q4):
        """
        Replica EXACTA de fk_phantom.py: mismos signos, mismo OFFSET,
        mismo T_NOA. Devuelve la posición (x,y,z) de cada origen de joint
        y del TCP, en el mismo orden que imprime fk_phantom.py.
        """
        OFFSET = math.radians(70.67)

        theta = [q1, q2 - OFFSET, q3 + OFFSET, q4]
        d = [self.base_height, 0, 0, 0]
        a = [0, self.l1, self.l2, 66.6]
        alpha = [-math.pi/2, 0, 0, 0]

        T_NOA = [
            [0,  0, 1, 47.0],
            [-1, 0, 0,  0.0],
            [0, -1, 0,  0.0],
            [0,  0, 0,  1.0]
        ]

        T = [[1.0 if i==j else 0.0 for j in range(4)] for i in range(4)]
        posiciones = []

        for i in range(4):
            Ai = self._dh(theta[i], d[i], a[i], alpha[i])
            T = self._mat_mult(T, Ai)
            posiciones.append((T[0][3], T[1][3], T[2][3]))

        T = self._mat_mult(T, T_NOA)
        posiciones.append((T[0][3], T[1][3], T[2][3]))   # TCP

        return posiciones   # [hombro, codo, muneca, bracket, TCP]

    def structure_clear(self, q1, q2, q3, q4, margin=20.0):
        """
        Verifica que ningun punto de la estructura (radio = margin)
        quede por debajo del piso (z=0).
        """
        posiciones = self._fk_positions(q1, q2, q3, q4)

        for nombre, (x, y, z) in zip(
            ["hombro", "codo", "muneca", "bracket", "TCP"], posiciones
        ):
            if z - margin < 0:
                print(f"Rechazado: '{nombre}' quedaria a z={z:.2f}mm "
                    f"(estructura tocaria el piso, margen={margin}mm)")
                return False

        return True

    def solve(self, Px, Py, Pz, theta):
        q1 = math.atan2(Py, Px)
        r = math.sqrt(Px**2 + Py**2)
        rw = r - self.l3*math.cos(theta)
        zw = Pz - self.l3*math.sin(theta)
        H = math.sqrt((zw-self.base_height)**2 + rw**2)

        if H > self.l1+self.l2 or H < abs(self.l1-self.l2):
            print("Punto NO alcanzable")
            return None

        cos_q3 = (H**2 - self.l1**2 - self.l2**2)/(2*self.l1*self.l2)
        if abs(cos_q3) > 1:
            print("Punto NO alcanzable")
            return None

        soluciones = []
        OFFSET = math.radians(70.67)

        for signo in [1, -1]:
            q3 = math.atan2(signo*math.sqrt(1-cos_q3**2), cos_q3)
            q3 = q3 - OFFSET
            gamma = (q3 + OFFSET)
            beta = math.atan2(rw, zw - self.base_height)
            lamb = math.atan2(self.l2*math.sin(gamma), self.l1 + self.l2*math.cos(gamma))
            q2 = (beta - lamb) + OFFSET - math.pi/2
            q4 = -theta - q3 - q2

            if not self.structure_clear(q1, q2, q3, q4):
                continue

            soluciones.append([q1, q2, q3, q4])

        if not soluciones:
            print("Ninguna solucion evita colision con el piso")
            return None

        return soluciones
    
    def execute(self, soluciones):

        if soluciones is None:
            return

        node = SmoothCommander()

        print("Esperando estado actual...")

        while rclpy.ok():

            rclpy.spin_once(node, timeout_sec=0.1)

            if len(node.current) == 5:
                break

        actual = node.current.copy()

        validas = []

        for i, q in enumerate(soluciones):

            if self.within_limits(q):

                if i == 0:
                    print("\nCodo arriba:")
                else:
                    print("\nCodo abajo:")

                print([round(math.degrees(x),2) for x in q])

                validas.append(q)

            else:

                if i == 0:
                    print("\nCodo arriba descartado (límites)")
                else:
                    print("\nCodo abajo descartado (límites)")

        if len(validas) == 0:

            print("\nNo existe solución válida.")

            node.destroy_node()

            return

        mejor = min(
            validas,
            key=lambda x: self.distance(actual[:4], x)
        )

        print("\nEjecutando solución más cercana...")

        start = actual

        target = [
            mejor[0],
            mejor[1],
            mejor[2],
            mejor[3],
            0.0
        ]

        duration = 3.0
        frequency = 200
        steps = int(duration * frequency)

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
    
def main():

    if len(sys.argv) != 5:

        print("Uso:")
        print("python3 ik_phantom.py X Y Z THETA")
        return

    Px = float(sys.argv[1])
    Py = float(sys.argv[2])
    Pz = float(sys.argv[3])

    theta = math.radians(float(sys.argv[4]))

    rclpy.init()

    robot = PhantomIK()

    soluciones = robot.solve(Px, Py, Pz, theta)

    robot.execute(soluciones)

    rclpy.shutdown()


if __name__ == "__main__":
    main()

