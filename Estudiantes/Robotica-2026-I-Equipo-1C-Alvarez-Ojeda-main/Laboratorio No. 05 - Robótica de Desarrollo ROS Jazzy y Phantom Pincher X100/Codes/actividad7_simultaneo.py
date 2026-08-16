#!/usr/bin/env python3

import math
import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import UInt32


JOINTS = ["waist", "shoulder", "elbow", "wrist", "gripper"]

# Configuraciones de la Actividad 7 en grados:
# [base, hombro, codo, muñeca, pinza]
CONFIGS = [
    [0.0,   0.0,   0.0,   0.0,  0.0],
    [25.0,  25.0,  20.0, -20.0, 0.0],
    [-35.0, 35.0, -30.0,  30.0, 0.0],
    [85.0, -20.0,  55.0,  25.0, 0.0],
    [80.0, -35.0,  55.0, -45.0, 0.0],
]

# Para primera prueba real, puedes poner SCALE = 0.5.
# Para ejecutar la guía completa, deja SCALE = 1.0.
SCALE = 1.0

# Tiempo de espera entre configuraciones
HOLD_TIME = 4.0

# Velocidad baja/recomendada para probar en robot real
PROFILE_VELOCITY = 20


class MovimientoSimultaneo(Node):
    def __init__(self):
        super().__init__("actividad7_simultaneo")

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

        time.sleep(1.0)

    def set_speed(self, speed):
        msg = UInt32()
        msg.data = int(speed)

        for _ in range(5):
            self.speed_pub.publish(msg)
            time.sleep(0.1)

        self.get_logger().info(f"Velocidad enviada: {speed}")

    def send_config(self, config_deg, label):
        config_scaled = [q * SCALE for q in config_deg]

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = JOINTS
        msg.position = [math.radians(q) for q in config_scaled]

        for _ in range(5):
            self.cmd_pub.publish(msg)
            time.sleep(0.05)

        text = ", ".join(
            [f"{joint}={q:.1f}°" for joint, q in zip(JOINTS, config_scaled)]
        )

        self.get_logger().info(f"{label}: {text}")
        time.sleep(HOLD_TIME)

    def run(self):
        self.get_logger().info("Iniciando Actividad 7: movimiento simultáneo.")

        self.set_speed(PROFILE_VELOCITY)

        # Ir a HOME antes de empezar
        self.send_config(CONFIGS[0], "HOME inicial")

        for i, config in enumerate(CONFIGS, start=1):
            self.send_config(config, f"Configuración {i}")

        # Volver a HOME al finalizar
        self.send_config(CONFIGS[0], "HOME final")

        self.get_logger().info("Actividad 7 finalizada.")


def main():
    rclpy.init()
    node = MovimientoSimultaneo()

    try:
        node.run()
    except KeyboardInterrupt:
        node.get_logger().warning("Rutina detenida por el usuario.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()