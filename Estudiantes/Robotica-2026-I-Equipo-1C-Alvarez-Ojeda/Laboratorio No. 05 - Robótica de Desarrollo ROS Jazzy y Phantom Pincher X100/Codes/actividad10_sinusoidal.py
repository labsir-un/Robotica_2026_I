#!/usr/bin/env python3

import math
import time
import csv
from pathlib import Path

import matplotlib.pyplot as plt

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import UInt32


JOINTS = ["waist", "shoulder", "elbow", "wrist", "gripper"]

HOME = {
    "waist": 0.0,
    "shoulder": 0.0,
    "elbow": 0.0,
    "wrist": 0.0,
    "gripper": 0.0,
}

# =========================
# Configuración de la prueba
# =========================

# Articulación seleccionada para la trayectoria sinusoidal.
# Puedes cambiarla por: "waist", "shoulder", "elbow", "wrist" o "gripper".
SELECTED_JOINT = "wrist"

# q0 en grados.
Q0_DEG = 0.0

# Dos amplitudes en grados.
AMPLITUDES_DEG = [10.0, 20.0]

# Dos frecuencias en Hz.
FREQUENCIES_HZ = [0.05, 0.1]

# Duración de cada prueba en segundos.
DURATION_SEC = 20.0

# Periodo de muestreo/comando.
# 0.05 s equivale a 20 Hz.
DT = 0.05

# Velocidad del robot.
PROFILE_VELOCITY = 200

# Carpeta de resultados.
RESULTS_DIR = Path.home() / "ros2_jazzy" / "phantom_ws" / "lab05_results_A10_3"

# Límites seguros aproximados.
# Ajusta estos límites según lo que ustedes hayan obtenido en la Actividad 6.
SAFE_LIMITS = {
    "waist": (-90.0, 90.0),
    "shoulder": (-45.0, 45.0),
    "elbow": (-70.0, 70.0),
    "wrist": (-70.0, 70.0),
    "gripper": (0.0, 40.0),
}


class TrayectoriaSinusoidal(Node):
    def __init__(self):
        super().__init__("actividad10_sinusoidal")

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

        self.current_positions_deg = {joint: None for joint in JOINTS}

        time.sleep(1.0)

    def joint_state_callback(self, msg):
        for name, pos_rad in zip(msg.name, msg.position):
            if name in self.current_positions_deg:
                self.current_positions_deg[name] = math.degrees(pos_rad)

    def spin_wait(self, seconds):
        t0 = time.time()
        while time.time() - t0 < seconds:
            rclpy.spin_once(self, timeout_sec=0.02)

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

    def publish_pose_deg(self, pose_dict):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = JOINTS
        msg.position = [math.radians(pose_dict[joint]) for joint in JOINTS]

        self.cmd_pub.publish(msg)

    def send_home(self, hold_time=2.0):
        self.get_logger().info("Enviando HOME...")
        for _ in range(10):
            self.publish_pose_deg(HOME)
            time.sleep(0.05)

        self.spin_wait(hold_time)

    def check_safe_trajectory(self, joint_name, q0_deg, amplitude_deg):
        q_min = q0_deg - amplitude_deg
        q_max = q0_deg + amplitude_deg

        safe_min, safe_max = SAFE_LIMITS[joint_name]

        if q_min < safe_min or q_max > safe_max:
            raise ValueError(
                f"La trayectoria no es segura para {joint_name}. "
                f"Rango solicitado: [{q_min:.1f}, {q_max:.1f}]°, "
                f"límite seguro: [{safe_min:.1f}, {safe_max:.1f}]°."
            )

    def run_single_test(self, amplitude_deg, frequency_hz, test_id):
        self.check_safe_trajectory(
            SELECTED_JOINT,
            Q0_DEG,
            amplitude_deg,
        )

        self.get_logger().info(
            f"Prueba {test_id}: {SELECTED_JOINT}, "
            f"q0={Q0_DEG:.1f}°, A={amplitude_deg:.1f}°, f={frequency_hz:.2f} Hz"
        )

        rows = []

        # Ir a q0 antes de iniciar la onda.
        initial_pose = dict(HOME)
        initial_pose[SELECTED_JOINT] = Q0_DEG

        for _ in range(10):
            self.publish_pose_deg(initial_pose)
            time.sleep(0.05)

        self.spin_wait(2.0)

        t_start = time.time()

        while True:
            now = time.time()
            t = now - t_start

            if t > DURATION_SEC:
                break

            q_des = Q0_DEG + amplitude_deg * math.sin(
                2.0 * math.pi * frequency_hz * t
            )

            pose = dict(HOME)
            pose[SELECTED_JOINT] = q_des

            self.publish_pose_deg(pose)

            rclpy.spin_once(self, timeout_sec=0.01)

            q_med = self.current_positions_deg.get(SELECTED_JOINT)

            if q_med is not None:
                error = q_des - q_med

                rows.append({
                    "test_id": test_id,
                    "joint": SELECTED_JOINT,
                    "amplitude_deg": amplitude_deg,
                    "frequency_hz": frequency_hz,
                    "time_s": t,
                    "q_deseado_deg": q_des,
                    "q_medido_deg": q_med,
                    "error_deg": error,
                })

            sleep_time = DT - (time.time() - now)
            if sleep_time > 0:
                time.sleep(sleep_time)

        # Volver a HOME al terminar cada prueba.
        self.send_home(hold_time=2.0)

        return rows

    def compute_metrics(self, rows):
        errors = [row["error_deg"] for row in rows]

        if not errors:
            return None

        error_max_abs = max(abs(e) for e in errors)
        mse = sum(e ** 2 for e in errors) / len(errors)
        rmse = math.sqrt(mse)
        error_mean = sum(errors) / len(errors)

        return {
            "error_max_abs_deg": error_max_abs,
            "error_promedio_deg": error_mean,
            "mse_deg2": mse,
            "rmse_deg": rmse,
        }

    def save_test_plot(self, rows, test_id, amplitude_deg, frequency_hz):
        times = [row["time_s"] for row in rows]
        q_des = [row["q_deseado_deg"] for row in rows]
        q_med = [row["q_medido_deg"] for row in rows]
        errors = [row["error_deg"] for row in rows]

        plt.figure()
        plt.plot(times, q_des, label="Posición deseada")
        plt.plot(times, q_med, label="Posición medida")
        plt.xlabel("Tiempo [s]")
        plt.ylabel("Posición angular [°]")
        plt.title(
            f"Actividad 10 - {SELECTED_JOINT} | "
            f"A={amplitude_deg:.1f}°, f={frequency_hz:.2f} Hz"
        )
        plt.grid(True)
        plt.legend()
        plt.tight_layout()

        plot_path = RESULTS_DIR / f"actividad10_test_{test_id}_posicion.png"
        plt.savefig(plot_path, dpi=200)
        plt.close()

        plt.figure()
        plt.plot(times, errors, label="Error")
        plt.xlabel("Tiempo [s]")
        plt.ylabel("Error [°]")
        plt.title(
            f"Error - {SELECTED_JOINT} | "
            f"A={amplitude_deg:.1f}°, f={frequency_hz:.2f} Hz"
        )
        plt.grid(True)
        plt.legend()
        plt.tight_layout()

        error_plot_path = RESULTS_DIR / f"actividad10_test_{test_id}_error.png"
        plt.savefig(error_plot_path, dpi=200)
        plt.close()

        self.get_logger().info(f"Gráfica guardada: {plot_path}")
        self.get_logger().info(f"Gráfica guardada: {error_plot_path}")

    def save_results(self, all_rows, summary_rows):
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

        csv_path = RESULTS_DIR / "actividad10_datos.csv"
        summary_path = RESULTS_DIR / "actividad10_resumen.csv"

        fieldnames = [
            "test_id",
            "joint",
            "amplitude_deg",
            "frequency_hz",
            "time_s",
            "q_deseado_deg",
            "q_medido_deg",
            "error_deg",
        ]

        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)

        summary_fieldnames = [
            "test_id",
            "joint",
            "amplitude_deg",
            "frequency_hz",
            "error_max_abs_deg",
            "error_promedio_deg",
            "mse_deg2",
            "rmse_deg",
        ]

        with open(summary_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=summary_fieldnames)
            writer.writeheader()
            writer.writerows(summary_rows)

        self.get_logger().info(f"Datos guardados en: {csv_path}")
        self.get_logger().info(f"Resumen guardado en: {summary_path}")

    def run(self):
        self.get_logger().info("Iniciando Actividad 10: trayectoria sinusoidal.")

        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

        self.wait_for_joint_states()
        self.set_speed(PROFILE_VELOCITY)

        self.send_home(hold_time=2.0)

        all_rows = []
        summary_rows = []

        test_id = 1

        for amplitude in AMPLITUDES_DEG:
            for frequency in FREQUENCIES_HZ:
                rows = self.run_single_test(
                    amplitude_deg=amplitude,
                    frequency_hz=frequency,
                    test_id=test_id,
                )

                metrics = self.compute_metrics(rows)

                if metrics is not None:
                    summary_row = {
                        "test_id": test_id,
                        "joint": SELECTED_JOINT,
                        "amplitude_deg": amplitude,
                        "frequency_hz": frequency,
                        **metrics,
                    }

                    summary_rows.append(summary_row)

                    self.get_logger().info(
                        f"Prueba {test_id}: "
                        f"error max={metrics['error_max_abs_deg']:.3f}°, "
                        f"MSE={metrics['mse_deg2']:.3f}, "
                        f"RMSE={metrics['rmse_deg']:.3f}°"
                    )

                    self.save_test_plot(
                        rows=rows,
                        test_id=test_id,
                        amplitude_deg=amplitude,
                        frequency_hz=frequency,
                    )

                all_rows.extend(rows)

                test_id += 1

                self.spin_wait(2.0)

        self.send_home(hold_time=2.0)

        self.save_results(
            all_rows=all_rows,
            summary_rows=summary_rows,
        )

        self.get_logger().info("Actividad 10 finalizada.")


def main():
    rclpy.init()

    node = TrayectoriaSinusoidal()

    try:
        node.run()
    except KeyboardInterrupt:
        node.get_logger().warning("Rutina detenida por el usuario.")
    except ValueError as e:
        node.get_logger().error(str(e))
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()