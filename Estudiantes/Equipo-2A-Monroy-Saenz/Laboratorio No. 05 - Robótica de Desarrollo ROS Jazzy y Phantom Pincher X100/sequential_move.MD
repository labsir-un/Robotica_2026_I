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

# Configuraciones de la Actividad 7 (base, hombro, codo, muñeca, pinza)
CONFIGURATIONS_DEG = {
    1: (0, 0, 0, 0, 0),
    2: (25, 25, 20, -20, 0),
    3: (-35, 35, -30, 30, 0),
    4: (85, -20, 55, 25, 0),
    5: (80, -35, 55, -45, 0),
}


class SequentialMover(Node):
    def __init__(self) -> None:
        super().__init__("sequential_move")
        self.publisher = self.create_publisher(JointState, "/pincher/command", 10)
        time.sleep(0.3)

    def send_one(self, joint: str, angle_deg: float) -> None:
        angle_deg = check_safe(joint, angle_deg)
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = [joint]
        msg.position = [math.radians(angle_deg)]
        self.publisher.publish(msg)
        self.get_logger().info(
            f"[secuencial] {JOINT_LABELS_ES[joint]} ({joint}) -> {angle_deg:.1f}°"
        )


def run_sequential(node: SequentialMover, config_id: int, settle_s: float) -> float:
    values = CONFIGURATIONS_DEG[config_id]
    t0 = time.monotonic()
    for joint, angle in zip(JOINT_ORDER, values):
        node.send_one(joint, angle)
        time.sleep(settle_s)
    elapsed = time.monotonic() - t0
    node.get_logger().info(f"Movimiento secuencial completo en {elapsed:.2f} s")
    return elapsed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=int,
        default=2,
        choices=sorted(CONFIGURATIONS_DEG),
        help="Cuál configuración de la Actividad 7 usar (default: 2).",
    )
    parser.add_argument(
        "--settle",
        type=float,
        default=1.5,
        help="Segundos de espera entre cada articulación.",
    )
    args, _ = parser.parse_known_args()

    rclpy.init()
    node = SequentialMover()
    try:
        run_sequential(node, args.config, args.settle)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
```
