#!/usr/bin/env python3
import math
import sys
import threading
import time
from typing import Dict, List, Tuple

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

# Drawing plane parameters
Z_UP = 0.20      # Pen lifted height (meters)
Z_DOWN = 0.17    # Pen drawing height (meters)
PITCH = -30.0    # Fixed wrist pitch angle (degrees)
SPEED_DRAW = 20 # Drawing speed (20%)
SPEED_MOVE = 30 # Moving/safe speed (30%)

class FigureTracerNode(Node):
    """ROS 2 Node that handles tracing figures in Cartesian space using Inverse Kinematics."""
    def __init__(self) -> None:
        super().__init__('figure_tracer')
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

def solve_ik(x: float, y: float, z: float, theta_deg: float) -> Tuple[str, List[float]]:
    """
    Solves inverse kinematics and returns the best/safest solution.
    Returns: (status, q_deg)
    """
    # 1. Base rotation (q1)
    q1 = math.atan2(y, x)
    q1_deg = math.degrees(q1)
    
    # Projection distance in horizontal plane
    r = math.sqrt(x**2 + y**2)
    z_rel = z - D1
    
    # Target wrist pitch angle in radians
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
    valid_sols = []
    
    for psi in psi_solutions:
        # Shoulder angle relative to vertical
        phi2 = math.atan2(r_w, z_w) - math.atan2(L3 * math.sin(psi), A2 + L3 * math.cos(psi))
        
        q2 = phi2 - BETA
        q3 = psi + BETA
        q4 = math.pi/2 - theta_h - q2 - q3
        
        # Convert to degrees and normalize to [-180, 180]
        q_sol = [q1_deg, math.degrees(q2), math.degrees(q3), math.degrees(q4)]
        q_sol_norm = [(val + 180.0) % 360.0 - 180.0 for val in q_sol]
        
        if is_within_limits(q_sol_norm):
            valid_sols.append(q_sol_norm)
            
    if not valid_sols:
        return "Límites excedidos para todas las soluciones matemáticas", []
        
    # Prefer the solution closest to a safe neutral posture (where elbow is typically Codo Abajo/Arriba)
    # For drawing, Codo Abajo is usually more stable mechanical posture
    # Or just select the one closest to current position
    return "OK", valid_sols[0]

def interpolate_segment(pA: Tuple[float, float], pB: Tuple[float, float], num_points: int) -> List[Tuple[float, float]]:
    """Generates intermediate points along a straight line segment."""
    points = []
    for i in range(num_points + 1):
        t = i / float(num_points)
        x = pA[0] + t * (pB[0] - pA[0])
        y = pA[1] + t * (pB[1] - pA[1])
        points.append((x, y))
    return points

def execute_trace(node: FigureTracerNode, strokes: List[List[Tuple[float, float]]]) -> None:
    print(f"\nIniciando trazado. {len(strokes)} trazo(s) detectados...")
    
    # 1. Configure safe initial speed
    node.set_speed(SPEED_MOVE)
    time.sleep(0.1)

    for idx, stroke in enumerate(strokes, 1):
        print(f"\n--- Ejecutando Trazo {idx}/{len(strokes)} ---")
        if not stroke:
            continue
            
        start_x, start_y = stroke[0]
        
        # A. Move to starting position (lifted pen)
        print(f"1. Moviendo al inicio del trazo (Z_UP): X={start_x:.3f}, Y={start_y:.3f}")
        status, q_start = solve_ik(start_x, start_y, Z_UP, PITCH)
        if status != "OK":
            print(f"[Error] No se puede iniciar trazo: {status}")
            return
        node.send_command(q_start)
        time.sleep(2.5) # Wait for movement
        
        # B. Lower the pen
        print(f"2. Bajando marcador (Z_DOWN): Z={Z_DOWN:.3f}")
        status, q_down = solve_ik(start_x, start_y, Z_DOWN, PITCH)
        if status != "OK":
            print(f"[Error] No se puede bajar marcador: {status}")
            return
        node.send_command(q_down)
        time.sleep(1.5)
        
        # C. Draw the stroke with interpolated points
        node.set_speed(SPEED_DRAW)
        time.sleep(0.1)
        
        # Interpolate points between vertices in this stroke
        interpolated_path = []
        for v_idx in range(len(stroke) - 1):
            pA = stroke[v_idx]
            pB = stroke[v_idx + 1]
            # Use ~10 points per segment for smooth lines
            segment_pts = interpolate_segment(pA, pB, 8)
            # Avoid duplicating the end point of the segment except for the final one
            if v_idx < len(stroke) - 2:
                interpolated_path.extend(segment_pts[:-1])
            else:
                interpolated_path.extend(segment_pts)
                
        print(f"3. Trazando {len(interpolated_path)} puntos interpolados...")
        for p_idx, (x, y) in enumerate(interpolated_path):
            status, q_val = solve_ik(x, y, Z_DOWN, PITCH)
            if status != "OK":
                print(f"   [Advertencia] Punto inalcanzable ({x:.3f}, {y:.3f}): {status}. Saltando...")
                continue
            
            node.send_command(q_val)
            # Sleep duration between points to allow physical/virtual robot to move
            time.sleep(0.20)
            
        # D. Lift the pen at the end of the stroke
        node.set_speed(SPEED_MOVE)
        time.sleep(0.1)
        end_x, end_y = stroke[-1]
        print(f"4. Levantando marcador al final del trazo (Z_UP): X={end_x:.3f}, Y={end_y:.3f}")
        status, q_up = solve_ik(end_x, end_y, Z_UP, PITCH)
        if status == "OK":
            node.send_command(q_up)
            time.sleep(1.5)
            
    # Return to home position at the end
    print("\nRegresando a posición de Home vertical...")
    node.send_command([0.0, 0.0, 0.0, 0.0])
    time.sleep(3.0)
    print("¡Trazado finalizado con éxito!")

def get_square_strokes() -> List[List[Tuple[float, float]]]:
    # Center at (0.14, 0.0), size 0.06 x 0.06
    # Vertices: P1 -> P2 -> P3 -> P4 -> P1
    return [[
        (0.11, -0.03),
        (0.17, -0.03),
        (0.17, 0.03),
        (0.11, 0.03),
        (0.11, -0.03)
    ]]

def get_triangle_strokes() -> List[List[Tuple[float, float]]]:
    # Center at (0.14, 0.0), side 0.06
    # Vertices: P1 -> P2 -> P3 -> P1
    return [[
        (0.11, -0.03),
        (0.17, 0.0),
        (0.11, 0.03),
        (0.11, -0.03)
    ]]

def get_circle_strokes() -> List[List[Tuple[float, float]]]:
    # Center at (0.14, 0.0), radius 0.03
    circle_pts = []
    num_pts = 36
    for i in range(num_pts + 1):
        angle = math.radians(i * (360.0 / num_pts))
        x = 0.14 + 0.03 * math.cos(angle)
        y = 0.03 * math.sin(angle)
        circle_pts.append((x, y))
    return [circle_pts]

def get_initials_strokes() -> List[List[Tuple[float, float]]]:
    # Initials "JR" (Jesus Rivera) and "IM" (Isaac Montes) -> "JI" (Jesus & Isaac)
    # J: Y in [-0.04, -0.01]. Top bar at X=0.17. Vertical at Y=-0.025. Hook at bottom.
    # I: Y in [0.01, 0.04]. Top bar at X=0.17. Vertical at Y=0.025. Bottom bar at X=0.11.
    return [
        # --- LETTER J ---
        # J Top horizontal bar
        [(0.17, -0.04), (0.17, -0.01)],
        # J Vertical stem and hook
        [(0.17, -0.025), (0.12, -0.025), (0.11, -0.025), (0.11, -0.04), (0.125, -0.04)],
        
        # --- LETTER I ---
        # I Top horizontal bar
        [(0.17, 0.01), (0.17, 0.04)],
        # I Vertical stem
        [(0.17, 0.025), (0.11, 0.025)],
        # I Bottom horizontal bar
        [(0.11, 0.01), (0.11, 0.04)]
    ]

def main(args=None) -> None:
    rclpy.init(args=args)
    node = FigureTracerNode()

    # Spin ROS 2 in a background thread
    spin_thread = threading.Thread(target=spin_thread_target, args=(node,), daemon=True)
    spin_thread.start()

    time.sleep(0.5)

    try:
        while True:
            print("\n" + "=" * 60)
            print("         PhantomX Pincher X100 - TRAZADO DE FIGURAS")
            print("=" * 60)
            print("1. Dibujar un Cuadrado (Square)")
            print("2. Dibujar un Triángulo (Triangle)")
            print("3. Dibujar un Círculo (Circle)")
            print("4. Dibujar Iniciales del Equipo (JI)")
            print("5. Salir")
            print("-" * 60)
            
            choice = input("Seleccione una opción: ").strip()
            if choice == '1':
                execute_trace(node, get_square_strokes())
            elif choice == '2':
                execute_trace(node, get_triangle_strokes())
            elif choice == '3':
                execute_trace(node, get_circle_strokes())
            elif choice == '4':
                execute_trace(node, get_initials_strokes())
            elif choice == '5':
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
