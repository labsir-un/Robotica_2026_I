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

HOME = [0.0, 0.0, 0.0, 0.0, 0.0]

# Configuración objetivo tomada de la Actividad 7.
# Orden: [base, hombro, codo, muñeca, pinza]
TARGET = [25.0, 25.0, 20.0, -20.0, 0.0]

PROFILE_VELOCITY = 20

# Tolerancia para considerar que llegó a la posición final.
# Si en el robot real nunca detecta llegada, súbela a 3.0 o 4.0.
TOLERANCE_DEG = 2.0

# Tiempo máximo esperando que llegue a una pose.
TIMEOUT_SEC = 15.0

# Tiempo quieto antes de empezar cada prueba.
PAUSE_BETWEEN_TESTS = 2.0


class ComparacionSecuencialSimultaneo(Node):
    def __init__(self):
        super().__init__("actividad8_comparacion")

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
        self.log_rows = []

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

    def publish_pose(self, pose_deg):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = JOINTS
        msg.position = [math.radians(q) for q in pose_deg]

        # Publicar varias veces ayuda a que el controlador reciba el comando.
        for _ in range(5):
            self.cmd_pub.publish(msg)
            time.sleep(0.05)

    def get_error_to_pose(self, target_deg):
        errors = []

        for joint, q_target in zip(JOINTS, target_deg):
            q_current = self.current_positions_deg[joint]

            if q_current is None:
                errors.append(float("inf"))
            else:
                errors.append(abs(q_target - q_current))

        return errors

    def wait_until_pose_reached(self, target_deg, label, tolerance_deg=TOLERANCE_DEG):
        """
        Espera hasta que todas las articulaciones estén dentro de la tolerancia.

        Devuelve:
        - reached: True/False
        - elapsed: tiempo hasta alcanzar la pose
        - max_error: error máximo final
        """
        t0 = time.time()
        stable_count = 0
        required_stable_count = 5

        while time.time() - t0 < TIMEOUT_SEC:
            rclpy.spin_once(self, timeout_sec=0.05)

            errors = self.get_error_to_pose(target_deg)
            max_error = max(errors)

            if max_error <= tolerance_deg:
                stable_count += 1
            else:
                stable_count = 0

            if stable_count >= required_stable_count:
                elapsed = time.time() - t0
                self.get_logger().info(
                    f"{label}: pose alcanzada en {elapsed:.2f} s "
                    f"(error máximo = {max_error:.2f}°)"
                )
                return True, elapsed, max_error

        errors = self.get_error_to_pose(target_deg)
        max_error = max(errors)

        self.get_logger().warning(
            f"{label}: timeout. No alcanzó la pose dentro de {TIMEOUT_SEC:.1f} s. "
            f"Error máximo final = {max_error:.2f}°"
        )

        return False, TIMEOUT_SEC, max_error

    def send_and_wait(self, pose_deg, label):
        self.get_logger().info(
            f"{label}: "
            + ", ".join([f"{j}={q:.1f}°" for j, q in zip(JOINTS, pose_deg)])
        )

        self.publish_pose(pose_deg)
        reached, elapsed, max_error = self.wait_until_pose_reached(pose_deg, label)

        self.log_rows.append({
            "modo": label,
            "waist_deseado": pose_deg[0],
            "shoulder_deseado": pose_deg[1],
            "elbow_deseado": pose_deg[2],
            "wrist_deseado": pose_deg[3],
            "gripper_deseado": pose_deg[4],
            "waist_medido": self.current_positions_deg["waist"],
            "shoulder_medido": self.current_positions_deg["shoulder"],
            "elbow_medido": self.current_positions_deg["elbow"],
            "wrist_medido": self.current_positions_deg["wrist"],
            "gripper_medido": self.current_positions_deg["gripper"],
            "tiempo_s": elapsed,
            "pose_alcanzada": reached,
            "error_max_final_deg": max_error,
        })

        return reached, elapsed, max_error

    def run_sequential_test(self):
        self.get_logger().info("=== Prueba 1: Movimiento secuencial ===")

        current_pose = HOME.copy()

        # Asegurar inicio desde HOME.
        self.send_and_wait(HOME, "Secuencial - HOME inicial")
        self.spin_wait(PAUSE_BETWEEN_TESTS)

        t_start = time.time()
        step_times = []

        # Mover en orden: base, hombro, codo, muñeca, pinza.
        for i, joint in enumerate(JOINTS):
            current_pose[i] = TARGET[i]

            reached, elapsed, max_error = self.send_and_wait(
                current_pose,
                f"Secuencial - Paso {i + 1}: {joint}"
            )

            step_times.append(elapsed)

        total_time = time.time() - t_start

        self.get_logger().info(
            f"Tiempo total secuencial hasta la pose final: {total_time:.2f} s"
        )

        return total_time, step_times

    def run_simultaneous_test(self):
        self.get_logger().info("=== Prueba 2: Movimiento simultáneo ===")

        # Volver a HOME para que la comparación sea justa.
        self.send_and_wait(HOME, "Simultáneo - HOME inicial")
        self.spin_wait(PAUSE_BETWEEN_TESTS)

        self.get_logger().info(
            "Simultáneo - enviando todas las articulaciones al mismo tiempo."
        )

        t_start = time.time()
        self.publish_pose(TARGET)

        reached, elapsed_to_target, max_error = self.wait_until_pose_reached(
            TARGET,
            "Simultáneo - Pose final"
        )

        total_time = time.time() - t_start

        self.log_rows.append({
            "modo": "Simultáneo - Pose final",
            "waist_deseado": TARGET[0],
            "shoulder_deseado": TARGET[1],
            "elbow_deseado": TARGET[2],
            "wrist_deseado": TARGET[3],
            "gripper_deseado": TARGET[4],
            "waist_medido": self.current_positions_deg["waist"],
            "shoulder_medido": self.current_positions_deg["shoulder"],
            "elbow_medido": self.current_positions_deg["elbow"],
            "wrist_medido": self.current_positions_deg["wrist"],
            "gripper_medido": self.current_positions_deg["gripper"],
            "tiempo_s": total_time,
            "pose_alcanzada": reached,
            "error_max_final_deg": max_error,
        })

        self.get_logger().info(
            f"Tiempo total simultáneo hasta la pose final: {total_time:.2f} s"
        )

        return total_time, reached, max_error

    def run(self):
        self.get_logger().info(
            "Iniciando Actividad 8: comparación secuencial vs simultáneo."
        )

        self.wait_for_joint_states()
        self.set_speed(PROFILE_VELOCITY)

        sequential_time, step_times = self.run_sequential_test()

        self.spin_wait(PAUSE_BETWEEN_TESTS)

        simultaneous_time, simultaneous_reached, simultaneous_error = (
            self.run_simultaneous_test()
        )

        # Regresar a HOME al final.
        self.send_and_wait(HOME, "HOME final")

        self.save_results(
            sequential_time=sequential_time,
            simultaneous_time=simultaneous_time,
            step_times=step_times,
            simultaneous_reached=simultaneous_reached,
            simultaneous_error=simultaneous_error,
        )

        self.get_logger().info("Actividad 8 finalizada.")

    def save_results(
        self,
        sequential_time,
        simultaneous_time,
        step_times,
        simultaneous_reached,
        simultaneous_error,
    ):
        results_dir = Path.home() / "ros2_jazzy" / "phantom_ws" / "lab05_results_A8"
        results_dir.mkdir(parents=True, exist_ok=True)

        csv_path = results_dir / "actividad8_comparacion.csv"

        fieldnames = [
            "modo",
            "waist_deseado",
            "shoulder_deseado",
            "elbow_deseado",
            "wrist_deseado",
            "gripper_deseado",
            "waist_medido",
            "shoulder_medido",
            "elbow_medido",
            "wrist_medido",
            "gripper_medido",
            "tiempo_s",
            "pose_alcanzada",
            "error_max_final_deg",
        ]

        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.log_rows)

        summary_path = results_dir / "actividad8_resumen.txt"

        with open(summary_path, "w") as f:
            f.write("Actividad 8 - Comparación movimiento secuencial vs simultáneo\n")
            f.write(f"Configuración objetivo: {TARGET}\n")
            f.write(f"Velocidad/Profile Velocity: {PROFILE_VELOCITY}\n")
            f.write(f"Tolerancia de llegada: {TOLERANCE_DEG} deg\n")
            f.write("\n")

            f.write(f"Tiempo total secuencial: {sequential_time:.3f} s\n")
            for i, t in enumerate(step_times, start=1):
                f.write(f"  Paso {i} ({JOINTS[i - 1]}): {t:.3f} s\n")

            f.write("\n")
            f.write(f"Tiempo total simultáneo: {simultaneous_time:.3f} s\n")
            f.write(f"Simultáneo alcanzó pose: {simultaneous_reached}\n")
            f.write(f"Error máximo final simultáneo: {simultaneous_error:.3f} deg\n")
            f.write("\n")

            if simultaneous_time > 0:
                ratio = sequential_time / simultaneous_time
                reduction = sequential_time - simultaneous_time
                f.write(f"Relación secuencial/simultáneo: {ratio:.3f}\n")
                f.write(f"Reducción de tiempo con simultáneo: {reduction:.3f} s\n")
                f.write("\n")

            f.write("Interpretación sugerida:\n")
            f.write(
                "El movimiento secuencial tarda más porque cada articulación espera "
                "a llegar antes de mover la siguiente. El movimiento simultáneo tarda "
                "menos porque todas las articulaciones se desplazan hacia la configuración "
                "objetivo al mismo tiempo. La trayectoria del TCP en el movimiento secuencial "
                "queda dividida por tramos, mientras que en el simultáneo resulta más compacta, "
                "aunque no necesariamente cartesiana.\n"
            )

        self.save_plots(
            results_dir=results_dir,
            sequential_time=sequential_time,
            simultaneous_time=simultaneous_time,
            step_times=step_times,
            simultaneous_error=simultaneous_error,
        )

        self.get_logger().info(f"CSV guardado en: {csv_path}")
        self.get_logger().info(f"Resumen guardado en: {summary_path}")

    def save_plots(
        self,
        results_dir,
        sequential_time,
        simultaneous_time,
        step_times,
        simultaneous_error,
    ):
        # =========================
        # Gráfica 1: tiempo total
        # =========================
        modos = ["Secuencial", "Simultáneo"]
        tiempos = [sequential_time, simultaneous_time]

        plt.figure()
        plt.bar(modos, tiempos)
        plt.ylabel("Tiempo [s]")
        plt.title("Actividad 8 - Tiempo total de ejecución")
        plt.grid(axis="y")

        for i, value in enumerate(tiempos):
            plt.text(i, value, f"{value:.2f} s", ha="center", va="bottom")

        plt.tight_layout()
        path_tiempos = results_dir / "actividad8_tiempo_total.png"
        plt.savefig(path_tiempos, dpi=200)
        plt.close()

        # =========================
        # Gráfica 2: tiempos por paso secuencial
        # =========================
        pasos = ["Base", "Hombro", "Codo", "Muñeca", "Pinza"]

        plt.figure()
        plt.bar(pasos, step_times)
        plt.ylabel("Tiempo [s]")
        plt.title("Actividad 8 - Tiempo por paso secuencial")
        plt.grid(axis="y")

        for i, value in enumerate(step_times):
            plt.text(i, value, f"{value:.2f} s", ha="center", va="bottom")

        plt.tight_layout()
        path_pasos = results_dir / "actividad8_tiempo_pasos_secuencial.png"
        plt.savefig(path_pasos, dpi=200)
        plt.close()

        # =========================
        # Gráfica 3: error máximo final
        # =========================
        sequential_rows = [
            row for row in self.log_rows
            if row["modo"] == "Secuencial - Paso 5: gripper"
        ]

        if sequential_rows:
            sequential_error = sequential_rows[0]["error_max_final_deg"]
        else:
            sequential_error = 0.0

        modos_error = ["Secuencial", "Simultáneo"]
        errores = [sequential_error, simultaneous_error]

        plt.figure()
        plt.bar(modos_error, errores)
        plt.ylabel("Error máximo final [°]")
        plt.title("Actividad 8 - Error máximo final")
        plt.grid(axis="y")

        for i, value in enumerate(errores):
            plt.text(i, value, f"{value:.2f}°", ha="center", va="bottom")

        plt.tight_layout()
        path_error = results_dir / "actividad8_error_maximo_final.png"
        plt.savefig(path_error, dpi=200)
        plt.close()

        self.get_logger().info(f"Gráfica guardada: {path_tiempos}")
        self.get_logger().info(f"Gráfica guardada: {path_pasos}")
        self.get_logger().info(f"Gráfica guardada: {path_error}")


def main():
    rclpy.init()

    node = ComparacionSecuencialSimultaneo()

    try:
        node.run()
    except KeyboardInterrupt:
        node.get_logger().warning("Rutina detenida por el usuario.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()