#!/usr/bin/env python3

import csv
import math
import time
from pathlib import Path

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import UInt32

import matplotlib.pyplot as plt


JOINTS = ["waist", "shoulder", "elbow", "wrist", "gripper"]

HOME = {
    "waist": 0.0,
    "shoulder": 0.0,
    "elbow": 0.0,
    "wrist": 0.0,
    "gripper": 0.0,
}

# Cinco posiciones por articulación.
# Empieza conservador para no pegar contra topes ni bloques.
TESTS = {
    "waist": [-60.0, -15.0, 0.0, 25.0, 70.0],
    "shoulder": [-40.0, -25.0, 0.0, 15.0, 60.0],
    "elbow": [-75.0, -30.5, 0.0, 22.5, 55.0],
    "wrist": [-35.0, -15.0, 0.0, 20.0, 75.0],
    "gripper": [3.0, 10.5, 15.0, 24.5, 55.0],
}

class CalibracionArticular(Node):
    def __init__(self):
        super().__init__("actividad5_calibracion")

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

        self.last_positions_deg = None

        time.sleep(1.0)

    def joint_state_callback(self, msg):
        positions = {}

        for name, pos_rad in zip(msg.name, msg.position):
            positions[name] = math.degrees(pos_rad)

        self.last_positions_deg = positions

    def wait_seconds(self, seconds):
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

    def send_pose(self, pose_deg, label="", settle_time=4.0):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = JOINTS
        msg.position = [math.radians(pose_deg[j]) for j in JOINTS]

        # Publicar varias veces ayuda a que el controlador reciba el comando.
        for _ in range(5):
            self.cmd_pub.publish(msg)
            time.sleep(0.05)

        self.get_logger().info(label)
        self.wait_seconds(settle_time)

        if self.last_positions_deg is None:
            raise RuntimeError("No se recibió /joint_states.")

        return dict(self.last_positions_deg)

    def run(self):
        results_dir = Path.home() / "ros2_jazzy" / "phantom_ws" / "lab05_results4"
        results_dir.mkdir(parents=True, exist_ok=True)

        rows = []

        self.set_speed(30)

        self.send_pose(HOME, "HOME inicial", settle_time=4.0)

        for joint in JOINTS:
            self.get_logger().info(f"Calibrando articulación: {joint}")

            for q_des in TESTS[joint]:
                pose = dict(HOME)
                pose[joint] = q_des

                measured = self.send_pose(
                    pose,
                    label=f"{joint}: q_deseado = {q_des:.2f} grados",
                    settle_time=4.0,
                )

                q_med = measured.get(joint, None)

                if q_med is None:
                    self.get_logger().warning(f"No se encontró medición para {joint}.")
                    continue

                error = q_des - q_med

                rows.append({
                    "articulacion": joint,
                    "q_deseado_deg": q_des,
                    "q_medido_deg": q_med,
                    "error_deg": error,
                })

                self.get_logger().info(
                    f"{joint}: deseado={q_des:.2f}°, "
                    f"medido={q_med:.2f}°, "
                    f"error={error:.2f}°"
                )

            self.send_pose(HOME, f"Retorno a HOME después de {joint}", settle_time=4.0)

        self.send_pose(HOME, "HOME final", settle_time=4.0)

        csv_path = results_dir / "actividad5_calibracion.csv"

        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "articulacion",
                    "q_deseado_deg",
                    "q_medido_deg",
                    "error_deg",
                ],
            )
            writer.writeheader()
            writer.writerows(rows)

        self.get_logger().info(f"CSV guardado en: {csv_path}")

        summary_rows = []

        for joint in JOINTS:
            joint_rows = [r for r in rows if r["articulacion"] == joint]

            if not joint_rows:
                continue

            errors = [r["error_deg"] for r in joint_rows]

            error_max_abs = max(abs(e) for e in errors)
            error_promedio = sum(errors) / len(errors)

            # Se toma como desplazamiento de cero la componente constante promedio.
            desplazamiento_cero = error_promedio

            summary_rows.append({
                "articulacion": joint,
                "error_max_abs_deg": error_max_abs,
                "error_promedio_deg": error_promedio,
                "desplazamiento_cero_sugerido_deg": desplazamiento_cero,
            })

            x = list(range(1, len(joint_rows) + 1))
            qd = [r["q_deseado_deg"] for r in joint_rows]
            qm = [r["q_medido_deg"] for r in joint_rows]

            plt.figure()
            plt.plot(x, qd, marker="o", label="Posición deseada")
            plt.plot(x, qm, marker="o", label="Posición medida")
            plt.xlabel("Prueba")
            plt.ylabel("Ángulo [deg]")
            plt.title(f"Calibración articular - {joint}")
            plt.grid(True)
            plt.legend()
            plt.tight_layout()

            fig_path = results_dir / f"actividad5_{joint}.png"
            plt.savefig(fig_path, dpi=200)
            plt.close()

            self.get_logger().info(f"Gráfica guardada: {fig_path}")

        summary_path = results_dir / "actividad5_resumen.csv"

        with open(summary_path, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "articulacion",
                    "error_max_abs_deg",
                    "error_promedio_deg",
                    "desplazamiento_cero_sugerido_deg",
                ],
            )
            writer.writeheader()
            writer.writerows(summary_rows)

        self.get_logger().info(f"Resumen guardado en: {summary_path}")
        self.get_logger().info("Actividad 5 finalizada.")


def main():
    rclpy.init()
    node = CalibracionArticular()

    try:
        node.run()
    except KeyboardInterrupt:
        node.get_logger().warning("Rutina detenida por el usuario.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()