#!/usr/bin/env python3

import argparse
import csv
import math
import time
from pathlib import Path

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.time import Time
from rclpy.duration import Duration

from sensor_msgs.msg import JointState
from std_msgs.msg import UInt32

import tf2_ros
from tf2_ros import TransformException


# ============================================================
# Articulaciones del robot
# ============================================================

JOINTS = ["waist", "shoulder", "elbow", "wrist", "gripper"]

# Configuraciones de la Actividad 7:
# [base, hombro, codo, muñeca, pinza]
ACT7_CONFIGS = [
    [0.0,   0.0,   0.0,   0.0,   0.0],
    [25.0,  25.0,  20.0, -20.0,  0.0],
    [-35.0, 35.0, -30.0,  30.0,  0.0],
    [85.0, -20.0,  55.0,  25.0,  0.0],
    [80.0, -35.0,  55.0, -45.0,  0.0],
]

# ============================================================
# Dimensiones tomadas del robot.xacro
# ============================================================

L1 = 0.0445
L2 = 0.1010
L3 = 0.1010
L4 = 0.1190
Lm = 0.0315

BETA = math.atan2(L2, Lm)

# Frame que se toma como TCP para comparar con RViz.
# En tu xacro, joint4 conecta link4 con gripper_bar.
TARGET_FRAME = "gripper_bar"
BASE_FRAME = "world"

PROFILE_VELOCITY = 30

RESULTS_DIR = Path.home() / "ros2_jazzy" / "phantom_ws" / "lab05_results_A11_2"


# ============================================================
# Funciones de transformaciones homogéneas
# ============================================================

def rx(angle):
    c = math.cos(angle)
    s = math.sin(angle)

    return np.array([
        [1.0, 0.0, 0.0],
        [0.0, c, -s],
        [0.0, s, c],
    ])


def ry(angle):
    c = math.cos(angle)
    s = math.sin(angle)

    return np.array([
        [c, 0.0, s],
        [0.0, 1.0, 0.0],
        [-s, 0.0, c],
    ])


def rz(angle):
    c = math.cos(angle)
    s = math.sin(angle)

    return np.array([
        [c, -s, 0.0],
        [s, c, 0.0],
        [0.0, 0.0, 1.0],
    ])


def rpy_to_matrix(roll, pitch, yaw):
    """
    Convención usada por URDF:
    R = Rz(yaw) * Ry(pitch) * Rx(roll)
    """
    return rz(yaw) @ ry(pitch) @ rx(roll)


def transform_xyz(x, y, z):
    T = np.eye(4)
    T[0:3, 3] = [x, y, z]
    return T


def transform_rotation(R):
    T = np.eye(4)
    T[0:3, 0:3] = R
    return T


def transform_rpy(roll, pitch, yaw):
    return transform_rotation(rpy_to_matrix(roll, pitch, yaw))


def matrix_to_rpy(R):
    """
    Extrae roll, pitch, yaw de una matriz de rotación con la convención:
    R = Rz(yaw) * Ry(pitch) * Rx(roll)
    """
    if abs(R[2, 0]) < 1.0 - 1e-9:
        pitch = math.asin(-R[2, 0])
        roll = math.atan2(R[2, 1], R[2, 2])
        yaw = math.atan2(R[1, 0], R[0, 0])
    else:
        pitch = math.pi / 2.0 if R[2, 0] < 0.0 else -math.pi / 2.0
        roll = 0.0
        yaw = math.atan2(-R[0, 1], R[1, 1])

    return roll, pitch, yaw


def quaternion_to_matrix(qx, qy, qz, qw):
    """
    Convierte cuaternión ROS a matriz de rotación.
    """
    norm = math.sqrt(qx*qx + qy*qy + qz*qz + qw*qw)

    if norm == 0.0:
        return np.eye(3)

    qx /= norm
    qy /= norm
    qz /= norm
    qw /= norm

    return np.array([
        [
            1.0 - 2.0*(qy*qy + qz*qz),
            2.0*(qx*qy - qz*qw),
            2.0*(qx*qz + qy*qw),
        ],
        [
            2.0*(qx*qy + qz*qw),
            1.0 - 2.0*(qx*qx + qz*qz),
            2.0*(qy*qz - qx*qw),
        ],
        [
            2.0*(qx*qz - qy*qw),
            2.0*(qy*qz + qx*qw),
            1.0 - 2.0*(qx*qx + qy*qy),
        ],
    ])


# ============================================================
# Cinemática directa según robot.xacro
# ============================================================

def fk_xacro(q1_deg, q2_deg, q3_deg, q4_deg):
    """
    Calcula la cinemática directa usando la misma cadena cinemática
    definida en robot.xacro.

    Entradas:
    q1_deg: waist
    q2_deg: shoulder
    q3_deg: elbow
    q4_deg: wrist

    Salida:
    T_world_tcp: matriz homogénea 4x4 desde world hasta gripper_bar.
    """

    q1 = math.radians(q1_deg)
    q2 = math.radians(q2_deg)
    q3 = math.radians(q3_deg)
    q4 = math.radians(q4_deg)

    T = np.eye(4)

    # ------------------------------------------------------------
    # joint waist
    # <origin xyz="0 0 ${0.08945-L1}" rpy="0 0 0"/>
    # <axis xyz="0 0 1"/>
    # ------------------------------------------------------------
    T = T @ transform_xyz(0.0, 0.0, 0.08945 - L1)
    T = T @ transform_rotation(rz(q1))

    # ------------------------------------------------------------
    # joint shoulder
    # <origin xyz="0 0 ${L1}" rpy="${-pi/2} 0 0"/>
    # <axis xyz="0 0 1"/>
    # ------------------------------------------------------------
    T = T @ transform_xyz(0.0, 0.0, L1)
    T = T @ transform_rpy(-math.pi / 2.0, 0.0, 0.0)
    T = T @ transform_rotation(rz(q2))

    # ------------------------------------------------------------
    # joint elbow
    # <origin xyz="${Lm} ${-L2} 0"
    #         rpy="0 0 ${-atan2(L2,Lm) - pi/2}"/>
    # <axis xyz="0 0 1"/>
    # ------------------------------------------------------------
    T = T @ transform_xyz(Lm, -L2, 0.0)
    T = T @ transform_rpy(0.0, 0.0, -BETA - math.pi / 2.0)
    T = T @ transform_rotation(rz(q3))

    # ------------------------------------------------------------
    # joint wrist
    # <origin xyz="${L3*cos(beta)} ${L3*sin(beta)} 0"
    #         rpy="0 0 ${beta}"/>
    # <axis xyz="0 0 1"/>
    # ------------------------------------------------------------
    T = T @ transform_xyz(
        L3 * math.cos(BETA),
        L3 * math.sin(BETA),
        0.0,
    )
    T = T @ transform_rpy(0.0, 0.0, BETA)
    T = T @ transform_rotation(rz(q4))

    # ------------------------------------------------------------
    # joint4 fijo hacia gripper_bar
    # <origin xyz="${L4} 0 0" rpy="${-pi/2} 0 ${-pi/2}"/>
    # ------------------------------------------------------------
    T = T @ transform_xyz(L4, 0.0, 0.0)
    T = T @ transform_rpy(-math.pi / 2.0, 0.0, -math.pi / 2.0)

    return T


def pose_from_transform(T):
    x, y, z = T[0:3, 3]
    roll, pitch, yaw = matrix_to_rpy(T[0:3, 0:3])

    return {
        "x_m": x,
        "y_m": y,
        "z_m": z,
        "roll_deg": math.degrees(roll),
        "pitch_deg": math.degrees(pitch),
        "yaw_deg": math.degrees(yaw),
    }


# ============================================================
# Nodo ROS para comparar con RViz usando TF
# ============================================================

class CinematicaDirectaNode(Node):
    def __init__(self, compare_rviz=True, wait_time=3.0):
        super().__init__("actividad11_cinematica_directa")

        self.compare_rviz = compare_rviz
        self.wait_time = wait_time

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

        if self.compare_rviz:
            self.tf_buffer = tf2_ros.Buffer()
            self.tf_listener = tf2_ros.TransformListener(
                self.tf_buffer,
                self,
            )
        else:
            self.tf_buffer = None
            self.tf_listener = None

        time.sleep(1.0)

    def spin_wait(self, seconds):
        t0 = time.time()
        while time.time() - t0 < seconds:
            rclpy.spin_once(self, timeout_sec=0.05)

    def set_speed(self, speed):
        msg = UInt32()
        msg.data = int(speed)

        for _ in range(5):
            self.speed_pub.publish(msg)
            time.sleep(0.1)

        self.get_logger().info(f"Velocidad enviada: {speed}")

    def publish_config(self, config_deg):
        """
        Publica la configuración completa:
        [waist, shoulder, elbow, wrist, gripper]
        """
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = JOINTS
        msg.position = [math.radians(q) for q in config_deg]

        for _ in range(5):
            self.cmd_pub.publish(msg)
            time.sleep(0.05)

    def lookup_rviz_pose(self):
        """
        Lee el transform world -> gripper_bar publicado por robot_state_publisher.
        Esta es la posición observada en RViz.
        """
        if not self.compare_rviz:
            return None

        try:
            tf = self.tf_buffer.lookup_transform(
                BASE_FRAME,
                TARGET_FRAME,
                Time(),
                timeout=Duration(seconds=1.0),
            )
        except TransformException as ex:
            self.get_logger().warning(
                f"No se pudo leer TF {BASE_FRAME} -> {TARGET_FRAME}: {ex}"
            )
            return None

        translation = tf.transform.translation
        rotation = tf.transform.rotation

        R = quaternion_to_matrix(
            rotation.x,
            rotation.y,
            rotation.z,
            rotation.w,
        )

        roll, pitch, yaw = matrix_to_rpy(R)

        return {
            "x_rviz_m": translation.x,
            "y_rviz_m": translation.y,
            "z_rviz_m": translation.z,
            "roll_rviz_deg": math.degrees(roll),
            "pitch_rviz_deg": math.degrees(pitch),
            "yaw_rviz_deg": math.degrees(yaw),
        }

    def evaluate_config(self, config_id, config_deg):
        q1, q2, q3, q4, q5 = config_deg

        T_calc = fk_xacro(q1, q2, q3, q4)
        pose_calc = pose_from_transform(T_calc)

        rviz_pose = None
        position_error_m = None

        if self.compare_rviz:
            self.get_logger().info(
                f"Enviando configuración {config_id}: "
                f"[{q1}, {q2}, {q3}, {q4}, {q5}] grados"
            )

            self.publish_config(config_deg)
            self.spin_wait(self.wait_time)

            rviz_pose = self.lookup_rviz_pose()

            if rviz_pose is not None:
                dx = pose_calc["x_m"] - rviz_pose["x_rviz_m"]
                dy = pose_calc["y_m"] - rviz_pose["y_rviz_m"]
                dz = pose_calc["z_m"] - rviz_pose["z_rviz_m"]

                position_error_m = math.sqrt(dx*dx + dy*dy + dz*dz)

        row = {
            "config_id": config_id,
            "q1_waist_deg": q1,
            "q2_shoulder_deg": q2,
            "q3_elbow_deg": q3,
            "q4_wrist_deg": q4,
            "q5_gripper_deg": q5,
            **pose_calc,
            "x_rviz_m": None,
            "y_rviz_m": None,
            "z_rviz_m": None,
            "roll_rviz_deg": None,
            "pitch_rviz_deg": None,
            "yaw_rviz_deg": None,
            "position_error_m": position_error_m,
        }

        if rviz_pose is not None:
            row.update(rviz_pose)

        return row

    def run(self, configs):
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

        self.set_speed(PROFILE_VELOCITY)

        rows = []

        for i, config in enumerate(configs, start=1):
            row = self.evaluate_config(i, config)
            rows.append(row)
            self.print_row(row)

        csv_path = RESULTS_DIR / "actividad11_cinematica_directa.csv"
        self.save_csv(rows, csv_path)

        self.get_logger().info(f"Resultados guardados en: {csv_path}")
        self.get_logger().info("Actividad 11 finalizada.")

    def print_row(self, row):
        text = (
            f"Config {row['config_id']}: "
            f"x={row['x_m']:.4f} m, "
            f"y={row['y_m']:.4f} m, "
            f"z={row['z_m']:.4f} m, "
            f"roll={row['roll_deg']:.2f}°, "
            f"pitch={row['pitch_deg']:.2f}°, "
            f"yaw={row['yaw_deg']:.2f}°"
        )

        if row["position_error_m"] is not None:
            text += f", error posición vs RViz={row['position_error_m']:.6f} m"

        self.get_logger().info(text)

    def save_csv(self, rows, csv_path):
        fieldnames = [
            "config_id",
            "q1_waist_deg",
            "q2_shoulder_deg",
            "q3_elbow_deg",
            "q4_wrist_deg",
            "q5_gripper_deg",
            "x_m",
            "y_m",
            "z_m",
            "roll_deg",
            "pitch_deg",
            "yaw_deg",
            "x_rviz_m",
            "y_rviz_m",
            "z_rviz_m",
            "roll_rviz_deg",
            "pitch_rviz_deg",
            "yaw_rviz_deg",
            "position_error_m",
        ]

        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(
        description="Actividad 11 - Cinemática directa PhantomX Pincher X100"
    )

    parser.add_argument(
        "--q",
        nargs=4,
        type=float,
        metavar=("Q1", "Q2", "Q3", "Q4"),
        help="Evalúa una sola configuración q1 q2 q3 q4 en grados.",
    )

    parser.add_argument(
        "--no-rviz",
        action="store_true",
        help="Solo calcula la cinemática directa; no publica comandos ni compara con RViz.",
    )

    parser.add_argument(
        "--wait",
        type=float,
        default=10.0,
        help="Tiempo de espera en segundos después de enviar cada configuración.",
    )

    args = parser.parse_args()

    if args.q is not None:
        q1, q2, q3, q4 = args.q
        configs = [[q1, q2, q3, q4, 0.0]]
    else:
        configs = ACT7_CONFIGS

    rclpy.init()

    node = CinematicaDirectaNode(
        compare_rviz=not args.no_rviz,
        wait_time=args.wait,
    )

    try:
        node.run(configs)
    except KeyboardInterrupt:
        node.get_logger().warning("Rutina detenida por el usuario.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()