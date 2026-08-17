#!/usr/bin/env python3

import argparse
import csv
import math
import time
from pathlib import Path

import matplotlib.pyplot as plt

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy

from sensor_msgs.msg import JointState
from std_msgs.msg import UInt32
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point


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

A1 = math.sqrt(L2**2 + Lm**2)
GAMMA = math.atan2(Lm, L2)

# ============================================================
# Límites articulares en grados
# Como es solo simulación, se dejan amplios.
# ============================================================

LIMITS_DEG = {
    "waist": (-150.0, 150.0),
    "shoulder": (-100.0, 100.0),
    "elbow": (-120.0, 120.0),
    "wrist": (-95.0, 95.0),
    "gripper": (-80.0, 90.0),
}

# ============================================================
# Parámetros de ejecución
# ============================================================

PROFILE_VELOCITY = 60

# Tiempo visual para moverse entre puntos consecutivos.
MOVE_TIME_PER_POINT = 0.30

# Tiempo entre comandos interpolados.
DT = 0.04

# Pequeña pausa después de cada punto.
HOLD_POINT_TIME = 0.05

RESULTS_DIR = Path.home() / "ros2_jazzy" / "phantom_ws" / "lab05_results_A14"

BASE_FRAME = "world"

# Topic del trazo virtual en RViz.
MARKER_TOPIC = "/actividad14_trace"


# ============================================================
# Funciones auxiliares
# ============================================================

def angle_wrap_deg(angle):
    while angle > 180.0:
        angle -= 360.0
    while angle < -180.0:
        angle += 360.0
    return angle


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
    solutions = []

    q1 = math.degrees(math.atan2(y, x))

    r = math.sqrt(x**2 + y**2)

    phi = -math.radians(theta_pitch_deg)

    rw = r - L4 * math.sin(phi)
    zw = z - Z0 - L4 * math.cos(phi)

    D2 = rw**2 + zw**2
    D = math.sqrt(D2)

    d_min = abs(A1 - L3)
    d_max = A1 + L3

    if D < d_min or D > d_max:
        return {
            "reachable": False,
            "reason": (
                f"Punto no alcanzable. D={D:.4f} m, "
                f"rango permitido [{d_min:.4f}, {d_max:.4f}] m."
            ),
            "solutions": [],
        }

    cos_delta = (D2 - A1**2 - L3**2) / (2.0 * A1 * L3)
    cos_delta = max(-1.0, min(1.0, cos_delta))

    delta_abs = math.acos(cos_delta)

    for label, delta in [
        ("codo_abajo", delta_abs),
        ("codo_arriba", -delta_abs),
    ]:
        psi = math.atan2(rw, zw)

        u = psi - math.atan2(
            L3 * math.sin(delta),
            A1 + L3 * math.cos(delta),
        )

        v = u + delta

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
            (x - x_fk)**2
            + (y - y_fk)**2
            + (z - z_fk)**2
        )

        pitch_error = angle_wrap_deg(theta_pitch_deg - pitch_fk)

        solutions.append({
            "label": label,
            "q_deg": q_deg,
            "valid_limits": within_limits(q_deg),
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
# Generación de figuras cartesianas
# ============================================================

def interpolate_line(p0, p1, n):
    points = []

    for i in range(n):
        alpha = i / float(n)

        x = p0[0] + alpha * (p1[0] - p0[0])
        y = p0[1] + alpha * (p1[1] - p0[1])
        z = p0[2] + alpha * (p1[2] - p0[2])
        theta = p0[3] + alpha * (p1[3] - p0[3])

        points.append({
            "x": x,
            "y": y,
            "z": z,
            "theta": theta,
        })

    return points


def build_square_points(
    center_x=0.120,
    center_y=-0.090,
    z=0.300,
    side=0.120,
    theta=-35.0,
    points_per_side=12,
):
    half = side / 2.0

    vertices = [
        [center_x - half, center_y - half, z, theta],
        [center_x + half, center_y - half, z, theta],
        [center_x + half, center_y + half, z, theta],
        [center_x - half, center_y + half, z, theta],
        [center_x - half, center_y - half, z, theta],
    ]

    points = []

    for i in range(len(vertices) - 1):
        points.extend(
            interpolate_line(
                vertices[i],
                vertices[i + 1],
                points_per_side,
            )
        )

    points.append({
        "x": vertices[-1][0],
        "y": vertices[-1][1],
        "z": vertices[-1][2],
        "theta": vertices[-1][3],
    })

    return points


def build_triangle_points(
    center_x=0.110,
    center_y=-0.090,
    z=0.300,
    size=0.156,
    theta=-35.0,
    points_per_side=14,
):
    h = size * math.sqrt(3.0) / 2.0

    vertices = [
        [center_x, center_y + 2.0*h/3.0, z, theta],
        [center_x - size/2.0, center_y - h/3.0, z, theta],
        [center_x + size/2.0, center_y - h/3.0, z, theta],
        [center_x, center_y + 2.0*h/3.0, z, theta],
    ]

    points = []

    for i in range(len(vertices) - 1):
        points.extend(
            interpolate_line(
                vertices[i],
                vertices[i + 1],
                points_per_side,
            )
        )

    points.append({
        "x": vertices[-1][0],
        "y": vertices[-1][1],
        "z": vertices[-1][2],
        "theta": vertices[-1][3],
    })

    return points


def build_circle_points(
    center_x=0.140,
    center_y=-0.090,
    z=0.300,
    radius=0.078,
    theta=-35.0,
    num_points=48,
):
    points = []

    for i in range(num_points + 1):
        a = 2.0 * math.pi * i / num_points

        x = center_x + radius * math.cos(a)
        y = center_y + radius * math.sin(a)

        points.append({
            "x": x,
            "y": y,
            "z": z,
            "theta": theta,
        })

    return points


def build_figure_points(figure):
    if figure == "square":
        return build_square_points()

    if figure == "triangle":
        return build_triangle_points()

    if figure == "circle":
        return build_circle_points()

    raise ValueError(f"Figura no reconocida: {figure}")


# ============================================================
# Nodo ROS
# ============================================================

class FigureTracerNode(Node):
    def __init__(self, move_time=MOVE_TIME_PER_POINT):
        super().__init__("actividad14_trazado_figura")

        self.move_time = move_time

        self.current_positions_deg = {joint: None for joint in JOINTS}
        self.last_commanded_config = [0.0, 0.0, 0.0, 0.0, 0.0]

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

        marker_qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )

        self.marker_pub = self.create_publisher(
            Marker,
            MARKER_TOPIC,
            marker_qos,
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

        self.get_logger().warning(
            "No se recibieron todos los /joint_states. "
            "Se usará HOME como referencia inicial."
        )
        return False

    def set_speed(self, speed):
        msg = UInt32()
        msg.data = int(speed)

        for _ in range(5):
            self.speed_pub.publish(msg)
            time.sleep(0.1)

        self.get_logger().info(f"Velocidad enviada: {speed}")

    def get_current_config_deg(self):
        current = []

        for i, joint in enumerate(JOINTS):
            q = self.current_positions_deg.get(joint)

            if q is None:
                q = self.last_commanded_config[i]

            current.append(q)

        return current

    def publish_config_once(self, config_deg):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = JOINTS
        msg.position = [math.radians(q) for q in config_deg]

        self.cmd_pub.publish(msg)

    def send_config_interpolated(self, target_config):
        start = self.get_current_config_deg()
        target = list(target_config)

        steps = max(1, int(self.move_time / DT))

        for k in range(steps + 1):
            alpha = k / steps

            config = [
                start[i] + alpha * (target[i] - start[i])
                for i in range(len(JOINTS))
            ]

            self.publish_config_once(config)

            rclpy.spin_once(self, timeout_sec=0.0)
            time.sleep(DT)

        for _ in range(3):
            self.publish_config_once(target)
            time.sleep(0.03)

        self.last_commanded_config = target

    def select_solution(self, result):
        valid_solutions = [
            sol for sol in result["solutions"]
            if sol["valid_limits"]
        ]

        if not valid_solutions:
            return None

        # Preferir una postura visualmente más natural.
        preferred_label = "codo_arriba"

        preferred = [
            sol for sol in valid_solutions
            if sol["label"] == preferred_label
        ]

        if preferred:
            return preferred[0]

        # Si no existe codo_arriba válido, usar la más cercana.
        selected = min(
            valid_solutions,
            key=lambda sol: distance_to_current(
                sol["q_deg"],
                self.current_positions_deg,
            )
        )

        return selected

    # ========================================================
    # Marcadores de RViz
    # ========================================================

    def make_point(self, x, y, z):
        p = Point()
        p.x = float(x)
        p.y = float(y)
        p.z = float(z)
        return p

    def publish_line_marker(
        self,
        points,
        marker_id,
        namespace,
        rgba,
        scale=0.006,
    ):
        marker = Marker()
        marker.header.frame_id = BASE_FRAME
        marker.header.stamp = self.get_clock().now().to_msg()

        marker.ns = namespace
        marker.id = marker_id
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD

        marker.pose.orientation.w = 1.0

        marker.scale.x = scale

        marker.color.r = rgba[0]
        marker.color.g = rgba[1]
        marker.color.b = rgba[2]
        marker.color.a = rgba[3]

        for p in points:
            marker.points.append(
                self.make_point(p["x"], p["y"], p["z"])
            )

        self.marker_pub.publish(marker)

    def publish_sphere_marker(
        self,
        point,
        marker_id,
        namespace="punto_actual",
    ):
        marker = Marker()
        marker.header.frame_id = BASE_FRAME
        marker.header.stamp = self.get_clock().now().to_msg()

        marker.ns = namespace
        marker.id = marker_id
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD

        marker.pose.position.x = float(point["x"])
        marker.pose.position.y = float(point["y"])
        marker.pose.position.z = float(point["z"])
        marker.pose.orientation.w = 1.0

        marker.scale.x = 0.018
        marker.scale.y = 0.018
        marker.scale.z = 0.018

        marker.color.r = 1.0
        marker.color.g = 0.2
        marker.color.b = 0.2
        marker.color.a = 1.0

        self.marker_pub.publish(marker)

    # ========================================================
    # Ejecución
    # ========================================================

    def trace_figure(self, figure_points, figure_name):
        self.wait_for_joint_states()
        self.set_speed(PROFILE_VELOCITY)

        rows = []
        visited_points = []

        self.get_logger().info(
            f"Iniciando trazado de figura '{figure_name}' "
            f"con {len(figure_points)} puntos cartesianos."
        )

        # Publicar la figura deseada completa.
        self.publish_line_marker(
            figure_points,
            marker_id=1,
            namespace="figura_deseada",
            rgba=(0.1, 0.7, 1.0, 0.8),
            scale=0.004,
        )

        for i, point in enumerate(figure_points, start=1):
            x = point["x"]
            y = point["y"]
            z = point["z"]
            theta = point["theta"]

            result = inverse_kinematics(x, y, z, theta)

            if not result["reachable"]:
                self.get_logger().warning(
                    f"Punto {i} no alcanzable: {result['reason']}"
                )

                rows.append({
                    "point_id": i,
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
                })

                continue

            selected = self.select_solution(result)

            if selected is None:
                self.get_logger().warning(
                    f"Punto {i}: alcanzable geométricamente, "
                    "pero sin solución dentro de límites."
                )

                rows.append({
                    "point_id": i,
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
                })

                continue

            q = selected["q_deg"]
            target_config = [q[0], q[1], q[2], q[3], 0.0]

            self.get_logger().info(
                f"Punto {i}/{len(figure_points)}: "
                f"x={x:.4f}, y={y:.4f}, z={z:.4f}, theta={theta:.1f}° -> "
                f"{selected['label']} q=[{q[0]:.2f}, {q[1]:.2f}, {q[2]:.2f}, {q[3]:.2f}]°"
            )

            self.send_config_interpolated(target_config)
            self.spin_wait(HOLD_POINT_TIME)

            visited_points.append(point)

            if len(visited_points) >= 2:
                self.publish_line_marker(
                    visited_points,
                    marker_id=2,
                    namespace="trazo_ejecutado",
                    rgba=(0.0, 1.0, 0.0, 1.0),
                    scale=0.007,
                )

            self.publish_sphere_marker(
                point,
                marker_id=3,
            )

            rows.append({
                "point_id": i,
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
                "reason": "Punto ejecutado.",
            })

        self.save_results(rows, figure_points, figure_name)

        self.get_logger().info("Actividad 14 finalizada.")

    def save_results(self, rows, figure_points, figure_name):
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

        csv_path = RESULTS_DIR / f"actividad14_{figure_name}_puntos.csv"

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

        x_values = [p["x"] for p in figure_points]
        y_values = [p["y"] for p in figure_points]

        plt.figure()
        plt.plot(x_values, y_values, marker="o")
        plt.xlabel("x [m]")
        plt.ylabel("y [m]")
        plt.title(f"Actividad 14 - Figura cartesiana: {figure_name}")
        plt.axis("equal")
        plt.grid(True)
        plt.tight_layout()

        plot_path = RESULTS_DIR / f"actividad14_{figure_name}_xy.png"
        plt.savefig(plot_path, dpi=200)
        plt.close()

        self.get_logger().info(f"CSV guardado en: {csv_path}")
        self.get_logger().info(f"Gráfica guardada en: {plot_path}")


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Actividad 14 - Trazado de figura en RViz usando IK"
    )

    parser.add_argument(
        "--figure",
        choices=["square", "triangle", "circle"],
        default="square",
        help="Figura a trazar: square, triangle o circle.",
    )

    parser.add_argument(
        "--move-time",
        type=float,
        default=MOVE_TIME_PER_POINT,
        help="Tiempo de movimiento entre puntos consecutivos [s].",
    )

    args = parser.parse_args()

    figure_points = build_figure_points(args.figure)

    rclpy.init()

    node = FigureTracerNode(
        move_time=args.move_time,
    )

    try:
        node.trace_figure(
            figure_points=figure_points,
            figure_name=args.figure,
        )
    except KeyboardInterrupt:
        node.get_logger().warning("Rutina detenida por el usuario.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()