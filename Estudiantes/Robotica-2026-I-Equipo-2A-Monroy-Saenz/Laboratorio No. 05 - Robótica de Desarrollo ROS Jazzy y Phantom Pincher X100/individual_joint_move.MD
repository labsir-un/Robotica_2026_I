```python
from __future__ import annotations
import argparse
import math
import time
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

from pincher_control.joint_limits import (
    JOINT_LABELS_ES,
    JOINT_ORDER,
    check_safe,
)

# Tres posiciones de prueba por articulación (grados), dentro del
# rango seguro calculado en joint_limits.py. Regresa a 0.0 (referencia)
# al final de cada articulación.
DEMO_POSITIONS_DEG = {
    "waist": [-40.0, 0.0, 40.0],
    "shoulder": [-30.0, 20.0, -10.0],
    "elbow": [30.0, -30.0, 10.0],
    "wrist": [-40.0, 40.0, 0.0],
    "gripper": [-60.0, 60.0, 0.0],
}


class IndividualJointMover(Node):
    def __init__(self) -> None:
        super().__init__("individual_joint_move")
        self.publisher = self.create_publisher(JointState, "/pincher/command", 10)
        # Da tiempo a que el publisher se registre antes del primer mensaje
        time.sleep(0.3)

    def send(self, joint: str, angle_deg: float) -> None:
        angle_deg = check_safe(joint, angle_deg)
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = [joint]
        msg.position = [math.radians(angle_deg)]
        self.publisher.publish(msg)
        self.get_logger().info(
            f"{JOINT_LABELS_ES[joint]} ({joint}) -> {angle_deg:.1f}°"
        )

    def go_home(self, joint: str) -> None:
        self.send(joint, 0.0)


def run_demo(node: IndividualJointMover, settle_s: float = 2.0) -> None:
    for joint in JOINT_ORDER:
        node.get_logger().info(f"--- Articulación: {JOINT_LABELS_ES[joint]} ---")
        for angle in DEMO_POSITIONS_DEG[joint]:
            node.send(joint, angle)
            time.sleep(settle_s)
        node.go_home(joint)
        time.sleep(settle_s)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Ejecuta 3 posiciones por articulación y regresa a la referencia.",
    )
    parser.add_argument(
        "--settle",
        type=float,
        default=2.0,
        help="Segundos de espera entre movimientos en modo demo.",
    )
    args, _ = parser.parse_known_args()

    rclpy.init()
    node = IndividualJointMover()
    try:
        if args.demo:
            run_demo(node, settle_s=args.settle)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
```
