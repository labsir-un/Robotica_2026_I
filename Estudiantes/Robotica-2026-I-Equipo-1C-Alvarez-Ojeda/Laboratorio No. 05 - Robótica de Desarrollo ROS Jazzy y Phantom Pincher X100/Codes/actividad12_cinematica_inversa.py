#!/usr/bin/env python3

import argparse
import csv
import math
import time
from pathlib import Path

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import UInt32


# ============================================================
# Articulaciones
# ============================================================

JOINTS = ["waist", "shoulder", "elbow", "wrist", "gripper"]

# ============================================================
# Dimensiones tomadas del robot.xacro
# ============================================================

L1 = 0.0445
L2 = 0.1010
L3 = 0.1010
L4 = 0.1190
Lm = 0.0315

Z0 = 0.08945

# Se combina Lm y L2 en un primer eslabón equivalente.
A1 = math.sqrt(L2**2 + Lm**2)
GAMMA = math.atan2(Lm, L2)

# ============================================================
# Límites seguros en grados
# Ajusta estos valores con los límites de tu Actividad 6.
# ============================================================

LIMITS_DEG = {
    "waist": (-150.0, 150.0),
    "shoulder": (-10.0, 100.0),
    "elbow": (-120.0, 120.0),
    "wrist": (-95.0, 95.0),
    "gripper": (-80.0, 90.0),
}

PROFILE_VELOCITY = 30
WAIT_AFTER_MOVE = 8.0

RESULTS_DIR = Path.home() / "ros2_jazzy" / "phantom_ws" / "lab05_results_A12_2"


# ============================================================
# Cinemática directa reducida para validar soluciones
# ============================================================

def fk_position(q1_deg, q2_deg, q3_deg, q4_deg):
    q1 = math.radians(q1_deg)
    q2 = math.radians(q2_deg)
    q3 = math.radians(q3_deg)
    q4 = math.radians(q4_deg)

    phi = q2 + q3 + q4

    r = (
        Lm * math.cos(q2)
        + L2 * math.sin(q2)
        + L3 * math.sin(q2 + q3)
        + L4 * math.sin(phi)
    )

    z = (
        Z0
        - Lm * math.sin(q2)
        + L2 * math.cos(q2)
        + L3 * math.cos(q2 + q3)
        + L4 * math.cos(phi)
    )

    x = r * math.cos(q1)
    y = r * math.sin(q1)

    pitch_deg = -math.degrees(phi)

    return x, y, z, pitch_deg


def angle_wrap_deg(angle):
    while angle > 180.0:
        angle -= 360.0
    while angle < -180.0:
        angle += 360.0
    return angle


def within_limits(solution):
    for joint, q in zip(JOINTS[:4], solution):
        lower, upper = LIMITS_DEG[joint]
        if q < lower or q > upper:
            return False
    return True


def distance_to_current(solution, current_deg):
    if current_deg is None:
        return 0.0

    total = 0.0

    for joint, q in zip(JOINTS[:4], solution):
        q_current = current_deg.get(joint)

        if q_current is None:
            continue

        diff = angle_wrap_deg(q - q_current)
        total += diff * diff

    return math.sqrt(total)


# ============================================================
# Cinemática inversa geométrica
# ============================================================

def inverse_kinematics(x, y, z, theta_pitch_deg):
    """
    Recibe:
    x, y, z en metros
    theta_pitch_deg en grados

    theta_pitch_deg se interpreta como pitch del TCP.
    En el modelo:
    pitch = -(q2 + q3 + q4)

    Retorna lista de soluciones válidas/candidatas:
    q = [q1, q2, q3, q4]
    """

    solutions = []

    # Base
    q1 = math.degrees(math.atan2(y, x))

    # Coordenada radial
    r = math.sqrt(x**2 + y**2)

    # Relación entre pitch y suma articular del plano
    phi = -math.radians(theta_pitch_deg)

    # Centro de muñeca: se resta el último eslabón L4.
    rw = r - L4 * math.sin(phi)
    zw = z - Z0 - L4 * math.cos(phi)

    D2 = rw**2 + zw**2
    D = math.sqrt(D2)

    # Verificar alcanzabilidad del mecanismo equivalente de dos eslabones.
    d_min = abs(A1 - L3)
    d_max = A1 + L3

    if D < d_min or D > d_max:
        return {
            "reachable": False,
            "reason": (
                f"Punto no alcanzable. Distancia al centro de muñeca D={D:.4f} m, "
                f"rango permitido [{d_min:.4f}, {d_max:.4f}] m."
            ),
            "solutions": [],
        }

    cos_delta = (D2 - A1**2 - L3**2) / (2.0 * A1 * L3)

    # Protección numérica
    cos_delta = max(-1.0, min(1.0, cos_delta))

    # Dos posibles soluciones: codo arriba / codo abajo
    delta_abs = math.acos(cos_delta)

    for label, delta in [
        ("codo_abajo", delta_abs),
        ("codo_arriba", -delta_abs),
    ]:
        # Ángulo del vector al centro de muñeca medido desde la vertical.
        psi = math.atan2(rw, zw)

        # Ecuación geométrica para el primer eslabón equivalente.
        u = psi - math.atan2(
            L3 * math.sin(delta),
            A1 + L3 * math.cos(delta),
        )

        v = u + delta

        # Regresar desde el modelo equivalente al modelo real:
        # u = q2 + gamma
        # v = q2 + q3
        q2 = u - GAMMA
        q3 = v - u + GAMMA
        q4 = phi - v

        q_deg = [
            angle_wrap_deg(q1),
            angle_wrap_deg(math.degrees(q2)),
            angle_wrap_deg(math.degrees(q3)),
            angle_wrap_deg(math.degrees(q4)),
        ]

        x_fk, y_fk, z_fk, pitch_fk = fk_position(*q_deg)

        position_error = math.sqrt(
            (x - x_fk) ** 2
            + (y - y_fk) ** 2
            + (z - z_fk) ** 2
        )

        pitch_error = angle_wrap_deg(theta_pitch_deg - pitch_fk)

        valid_limits = within_limits(q_deg)

        solutions.append({
            "label": label,
            "q_deg": q_deg,
            "valid_limits": valid_limits,
            "x_fk": x_fk,
            "y_fk": y_fk,
            "z_fk": z_fk,
            "pitch_fk_deg": pitch_fk,
            "position_error_m": position_error,
            "pitch_error_deg": pitch_error,
        })

    return {
        "reachable": True,
        "reason": "Punto alcanzable.",
        "solutions": solutions,
    }


# ============================================================
# Puntos de prueba
# Se generan a partir de configuraciones seguras conocidas.
# ============================================================

DEMO_Q_CONFIGS = [
    [-60.0, -30.0, 40.0, 80.0],
    [20.0, 15.0, 10.0, -10.0],
    [-20.0, 15.0, -10.0, 15.0],
    [30.0, -10.0, 20.0, 5.0],
    [-30.0, -10.0, 20.0, -10.0],
]


def build_demo_points():
    points = []

    for q1, q2, q3, q4 in DEMO_Q_CONFIGS:
        x, y, z, pitch = fk_position(q1, q2, q3, q4)

        points.append({
            "x": x,
            "y": y,
            "z": z,
            "theta": pitch,
            "source_q": [q1, q2, q3, q4],
        })

    return points


# ============================================================
# Nodo ROS
# ============================================================

class InverseKinematicsNode(Node):
    def __init__(self, execute=True):
        super().__init__("actividad12_cinematica_inversa")

        self.execute = execute
        self.current_positions_deg = {joint: None for joint in JOINTS}

        self.cmd_pub = self.create_publisher(
            JointState,
            "/pincher/command",
            10,
        )

        self.speed_pub = self.create_publisher(
            UInt32,
            "/pincher/profile_velocity",
            10,
        )

        self.joint_sub = self.create_subscription(
            JointState,
            "/joint_states",
            self.joint_state_callback,
            10,
        )

        time.sleep(1.0)

    def joint_state_callback(self, msg):
        for name, pos_rad in zip(msg.name, msg.position):
            if name in self.current_positions_deg:
                self.current_positions_deg[name] = math.degrees(pos_rad)

    def spin_wait(self, seconds):
        t0 = time.time()
        while time.time() - t0 < seconds:
            rclpy.spin_once(self, timeout_sec=0.05)

    def wait_for_joint_states(self):
        self.get_logger().info("Esperando /joint_states...")

        t0 = time.time()
        while time.time() - t0 < 5.0:
            rclpy.spin_once(self, timeout_sec=0.05)

            if all(self.current_positions_deg[j] is not None for j in JOINTS):
                self.get_logger().info("Estados articulares recibidos.")
                return True

        self.get_logger().warning("No se recibieron todos los /joint_states.")
        return False

    def set_speed(self, speed):
        msg = UInt32()
        msg.data = int(speed)

        for _ in range(5):
            self.speed_pub.publish(msg)
            time.sleep(0.1)

        self.get_logger().info(f"Velocidad enviada: {speed}")

    def publish_solution(self, q_deg):
        config = [q_deg[0], q_deg[1], q_deg[2], q_deg[3], 0.0]

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = JOINTS
        msg.position = [math.radians(q) for q in config]

        for _ in range(5):
            self.cmd_pub.publish(msg)
            time.sleep(0.05)

    def solve_point(self, point_id, x, y, z, theta):
        self.get_logger().info(
            f"Punto {point_id}: x={x:.4f}, y={y:.4f}, z={z:.4f}, theta={theta:.2f}°"
        )

        result = inverse_kinematics(x, y, z, theta)

        if not result["reachable"]:
            self.get_logger().warning(result["reason"])

            return {
                "point_id": point_id,
                "x_target_m": x,
                "y_target_m": y,
                "z_target_m": z,
                "theta_target_deg": theta,
                "reachable": False,
                "selected_label": None,
                "q1_waist_deg": None,
                "q2_shoulder_deg": None,
                "q3_elbow_deg": None,
                "q4_wrist_deg": None,
                "position_error_m": None,
                "pitch_error_deg": None,
                "reason": result["reason"],
            }

        valid_solutions = [
            sol for sol in result["solutions"]
            if sol["valid_limits"]
        ]

        for sol in result["solutions"]:
            q = sol["q_deg"]

            self.get_logger().info(
                f"  Solución {sol['label']}: "
                f"q=[{q[0]:.2f}, {q[1]:.2f}, {q[2]:.2f}, {q[3]:.2f}]°, "
                f"límites={'OK' if sol['valid_limits'] else 'NO'}, "
                f"error_pos={sol['position_error_m']:.6f} m"
            )

        if not valid_solutions:
            self.get_logger().warning(
                "El punto es geométricamente alcanzable, pero ninguna solución cumple los límites."
            )

            return {
                "point_id": point_id,
                "x_target_m": x,
                "y_target_m": y,
                "z_target_m": z,
                "theta_target_deg": theta,
                "reachable": False,
                "selected_label": None,
                "q1_waist_deg": None,
                "q2_shoulder_deg": None,
                "q3_elbow_deg": None,
                "q4_wrist_deg": None,
                "position_error_m": None,
                "pitch_error_deg": None,
                "reason": "Sin solución válida por límites articulares.",
            }

        # Seleccionar solución válida más cercana a la configuración actual.
        selected = min(
            valid_solutions,
            key=lambda sol: distance_to_current(
                sol["q_deg"],
                self.current_positions_deg,
            )
        )

        q = selected["q_deg"]

        self.get_logger().info(
            f"  Seleccionada: {selected['label']} -> "
            f"q=[{q[0]:.2f}, {q[1]:.2f}, {q[2]:.2f}, {q[3]:.2f}]°"
        )

        if self.execute:
            self.publish_solution(q)
            self.spin_wait(WAIT_AFTER_MOVE)

        return {
            "point_id": point_id,
            "x_target_m": x,
            "y_target_m": y,
            "z_target_m": z,
            "theta_target_deg": theta,
            "reachable": True,
            "selected_label": selected["label"],
            "q1_waist_deg": q[0],
            "q2_shoulder_deg": q[1],
            "q3_elbow_deg": q[2],
            "q4_wrist_deg": q[3],
            "position_error_m": selected["position_error_m"],
            "pitch_error_deg": selected["pitch_error_deg"],
            "reason": result["reason"],
        }

    def save_csv(self, rows):
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

        csv_path = RESULTS_DIR / "actividad12_cinematica_inversa.csv"

        fieldnames = [
            "point_id",
            "x_target_m",
            "y_target_m",
            "z_target_m",
            "theta_target_deg",
            "reachable",
            "selected_label",
            "q1_waist_deg",
            "q2_shoulder_deg",
            "q3_elbow_deg",
            "q4_wrist_deg",
            "position_error_m",
            "pitch_error_deg",
            "reason",
        ]

        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        self.get_logger().info(f"Resultados guardados en: {csv_path}")

    def run_points(self, points):
        self.wait_for_joint_states()
        self.set_speed(PROFILE_VELOCITY)

        rows = []

        for i, p in enumerate(points, start=1):
            row = self.solve_point(
                point_id=i,
                x=p["x"],
                y=p["y"],
                z=p["z"],
                theta=p["theta"],
            )
            rows.append(row)

            self.spin_wait(1.0)

        self.save_csv(rows)

        self.get_logger().info("Actividad 12 finalizada.")


def main():
    parser = argparse.ArgumentParser(
        description="Actividad 12 - Cinemática inversa PhantomX Pincher X100"
    )

    parser.add_argument("--x", type=float, help="Coordenada x objetivo [m].")
    parser.add_argument("--y", type=float, help="Coordenada y objetivo [m].")
    parser.add_argument("--z", type=float, help="Coordenada z objetivo [m].")
    parser.add_argument(
        "--theta",
        type=float,
        help="Pitch objetivo del TCP [deg].",
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Ejecuta cinco puntos cartesianos de prueba.",
    )

    parser.add_argument(
        "--no-execute",
        action="store_true",
        help="Calcula la IK pero no mueve el robot.",
    )

    args = parser.parse_args()

    if args.demo:
        points = build_demo_points()
    else:
        if args.x is None or args.y is None or args.z is None or args.theta is None:
            raise SystemExit(
                "Debes usar --demo o indicar --x --y --z --theta."
            )

        points = [{
            "x": args.x,
            "y": args.y,
            "z": args.z,
            "theta": args.theta,
        }]

    rclpy.init()

    node = InverseKinematicsNode(
        execute=not args.no_execute,
    )

    try:
        node.run_points(points)
    except KeyboardInterrupt:
        node.get_logger().warning("Rutina detenida por el usuario.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()