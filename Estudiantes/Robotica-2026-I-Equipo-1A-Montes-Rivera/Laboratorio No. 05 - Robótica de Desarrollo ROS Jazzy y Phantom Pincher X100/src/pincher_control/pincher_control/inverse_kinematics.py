#!/usr/bin/env python3
import math
import sys
import threading
import time
from typing import Dict, List, Optional, Tuple

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import UInt32

# Robot parameters
L1 = 0.0445
L2 = 0.1010
L3 = 0.1010
L4 = 0.1190
Lm = 0.0315

BETA = math.atan2(Lm, L2) # ~17.31 degrees
A2 = math.sqrt(Lm**2 + L2**2) # ~0.1058 meters
D1 = 0.08945 # Height base to shoulder

# Safe software limits
JOINT_LIMITS_DEG = {
    'waist': (-140.0, 139.0),
    'shoulder': (-106.0, 64.0),
    'elbow': (-131.0, 137.0),
    'wrist': (-93.0, 93.0),
}

class InverseKinematicsNode(Node):
    """ROS 2 Node that handles receiving joint state feedback and sending joint commands."""
    def __init__(self) -> None:
        super().__init__('inverse_kinematics')
        self.publisher = self.create_publisher(JointState, '/pincher/command', 10)
        self.speed_publisher = self.create_publisher(UInt32, '/pincher/profile_velocity', 10)
        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_states_callback,
            10
        )
        self.current_positions: List[float] = [0.0, 0.0, 0.0, 0.0]
        self.feedback_received = False
        self.lock = threading.Lock()

    def joint_states_callback(self, msg: JointState) -> None:
        with self.lock:
            # We map waist, shoulder, elbow, wrist joints
            mapping = {'waist': 0, 'shoulder': 1, 'elbow': 2, 'wrist': 3}
            for name, pos in zip(msg.name, msg.position):
                if name in mapping:
                    self.current_positions[mapping[name]] = math.degrees(pos)
            self.feedback_received = True

    def get_current_config(self) -> List[float]:
        with self.lock:
            return list(self.current_positions)

    def send_command(self, q_deg: List[float]) -> None:
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']
        # Set gripper to 0 by default during IK tests
        msg.position = [math.radians(val) for val in q_deg] + [0.0]
        self.publisher.publish(msg)

    def set_speed(self, speed_val: int) -> None:
        msg = UInt32()
        msg.data = int(speed_val)
        self.speed_publisher.publish(msg)

def spin_thread_target(node: Node) -> None:
    try:
        rclpy.spin(node)
    except Exception:
        pass

def is_within_limits(q_deg: List[float]) -> bool:
    """Checks if a configuration is within the safe software limits."""
    w, s, e, wr = q_deg
    limits = JOINT_LIMITS_DEG
    return (limits['waist'][0] <= w <= limits['waist'][1] and
            limits['shoulder'][0] <= s <= limits['shoulder'][1] and
            limits['elbow'][0] <= e <= limits['elbow'][1] and
            limits['wrist'][0] <= wr <= limits['wrist'][1])

def solve_ik(x: float, y: float, z: float, theta_deg: float) -> Tuple[str, List[Dict]]:
    """
    Solves inverse kinematics for the 4-DOF manipulator.
    Returns status and list of solution dictionaries containing:
      - 'q': List of angles [q1, q2, q3, q4] in degrees
      - 'type': 'Codo Arriba' or 'Codo Abajo'
      - 'valid': bool
    """
    solutions = []
    
    # 1. Base rotation (q1)
    q1 = math.atan2(y, x)
    q1_deg = math.degrees(q1)
    
    # Projection distance in horizontal plane
    r = math.sqrt(x**2 + y**2)
    z_rel = z - D1
    
    # Target wrist pitch angle in radians (theta_deg is pitch relative to horizontal)
    theta_h = math.radians(theta_deg)
    
    # Position of wrist joint relative to shoulder
    r_w = r - L4 * math.cos(theta_h)
    z_w = z_rel - L4 * math.sin(theta_h)
    
    # 2. Planar 2-link solver
    D_sq = r_w**2 + z_w**2
    cos_psi = (D_sq - A2**2 - L3**2) / (2.0 * A2 * L3)
    
    if abs(cos_psi) > 1.0:
        return "Fuera del espacio de trabajo (Wrist inalcanzable)", []
    
    # Two mathematical solutions for the elbow joint
    psi_solutions = [math.acos(cos_psi), -math.acos(cos_psi)]
    
    for psi in psi_solutions:
        # Shoulder angle relative to vertical
        phi2 = math.atan2(r_w, z_w) - math.atan2(L3 * math.sin(psi), A2 + L3 * math.cos(psi))
        
        q2 = phi2 - BETA
        q3 = psi + BETA
        
        # Wrist angle q4 (decoupled planar sum)
        # q2 + q3 + q4 = pi/2 - theta_h
        q4 = math.pi/2 - theta_h - q2 - q3
        
        # Convert to degrees and normalize to [-180, 180]
        q_sol = [q1_deg, math.degrees(q2), math.degrees(q3), math.degrees(q4)]
        q_sol_norm = []
        for val in q_sol:
            val_norm = (val + 180.0) % 360.0 - 180.0
            q_sol_norm.append(val_norm)
            
        # Determine elbow type based on psi
        # psi > 0 means the elbow is bent downwards (Codo Abajo)
        # psi < 0 means the elbow is bent upwards (Codo Arriba)
        sol_type = "Codo Abajo" if psi >= 0 else "Codo Arriba"
        valid = is_within_limits(q_sol_norm)
        
        solutions.append({
            'q': q_sol_norm,
            'type': sol_type,
            'valid': valid
        })
        
    return "OK", solutions

def run_ik_and_execute(node: InverseKinematicsNode, x: float, y: float, z: float, theta: float) -> None:
    print(f"\nCalculando IK para: X={x:.3f} m, Y={y:.3f} m, Z={z:.3f} m, Pitch={theta:.1f}°")
    
    status, solutions = solve_ik(x, y, z, theta)
    if status != "OK":
        print(f"[Error] {status}")
        return

    curr_config = node.get_current_config()
    print(f"Configuración actual del robot: {curr_config}")
    
    valid_sols = []
    print("\nSoluciones posibles encontradas:")
    for idx, sol in enumerate(solutions, 1):
        q_str = ", ".join([f"{val:.2f}°" for val in sol['q']])
        status_str = "VÁLIDA (dentro de límites)" if sol['valid'] else "INVÁLIDA (excede límites)"
        print(f"  Solución {idx} ({sol['type']}): [{q_str}] -> {status_str}")
        if sol['valid']:
            # Calculate distance to current configuration
            dist = sum((sol['q'][i] - curr_config[i])**2 for i in range(4))
            valid_sols.append((sol, dist))
            
    if not valid_sols:
        print("[Error] Ninguna de las soluciones está dentro de los límites de seguridad.")
        return
        
    # Sort by distance and pick closest
    valid_sols.sort(key=lambda item: item[1])
    best_sol, best_dist = valid_sols[0]
    
    q_best = best_sol['q']
    print(f"\n--> Seleccionada la solución {best_sol['type']} (distancia cuadrática: {best_dist:.1f})")
    print(f"--> Enviando comando: [{', '.join([f'{val:.2f}°' for val in q_best])}]")
    node.send_command(q_best)
    time.sleep(4.0)

def main(args=None) -> None:
    rclpy.init(args=args)
    node = InverseKinematicsNode()

    # Spin ROS 2 in a background thread
    spin_thread = threading.Thread(target=spin_thread_target, args=(node,), daemon=True)
    spin_thread.start()

    # Set speed to 30% for safety
    print("Configurando velocidad inicial del bus al 30%...")
    node.set_speed(30)
    time.sleep(0.5)

    # 5 test Cartesian positions
    # 1. Home vertical equivalent (pitch = 90 deg)
    # 2. Extended forward horizontal (pitch = 0 deg)
    # 3. Side left tilted down (pitch = -20 deg)
    # 4. Side right tilted up (pitch = 45 deg)
    # 5. Unreachable position (outside workspace)
    test_positions = [
        (0.0315, 0.0, 0.41045, 90.0),
        (0.150, 0.0, 0.250, 0.0),
        (0.100, -0.100, 0.200, -20.0),
        (0.080, 0.080, 0.350, 45.0),
        (0.400, 0.0, 0.500, 0.0)
    ]

    try:
        while True:
            print("\n" + "=" * 60)
            print("         PhantomX Pincher X100 - CINEMÁTICA INVERSA")
            print("=" * 60)
            print("1. Ejecutar las 5 posiciones cartesianas de prueba")
            print("2. Ingresar posición cartesiana manual (x, y, z, pitch)")
            print("3. Salir")
            print("-" * 60)
            
            choice = input("Seleccione una opción: ").strip()
            if choice == '1':
                print("\nEvaluando 5 posiciones cartesianas de prueba...")
                for idx, pos in enumerate(test_positions, 1):
                    print(f"\n--- PRUEBA {idx}/5 ---")
                    run_ik_and_execute(node, pos[0], pos[1], pos[2], pos[3])
                    time.sleep(1.0)
            elif choice == '2':
                try:
                    x = float(input("Ingrese X (m): "))
                    y = float(input("Ingrese Y (m): "))
                    z = float(input("Ingrese Z (m): "))
                    pitch = float(input("Ingrese Pitch (grados con respecto a horizontal): "))
                    run_ik_and_execute(node, x, y, z, pitch)
                except ValueError:
                    print("[Error] Debe ingresar valores numéricos válidos.")
            elif choice == '3':
                print("\nSaliendo...")
                break
            else:
                print("[Error] Opción no válida. Intente de nuevo.")
    except KeyboardInterrupt:
        print("\nSaliendo por interrupción de teclado...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
