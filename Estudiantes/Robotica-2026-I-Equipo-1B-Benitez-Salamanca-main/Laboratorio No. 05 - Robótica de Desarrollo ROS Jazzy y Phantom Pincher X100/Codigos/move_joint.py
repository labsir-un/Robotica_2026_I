#!/usr/bin/env python3

import math
import sys
import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


JOINT_NAMES = [
    "waist",
    "shoulder",
    "elbow",
    "wrist",
    "gripper"
]


class SmoothCommander(Node):

    def __init__(self):
        super().__init__("smooth_commander")

        self.publisher = self.create_publisher(
            JointState,
            "/pincher/command",
            10
        )

        self.current = [0.0] * 5

        self.subscription = self.create_subscription(
            JointState,
            "/joint_states",
            self.joint_callback,
            10
        )

    def joint_callback(self, msg):
        self.current = list(msg.position)

    def publish(self, q):

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = JOINT_NAMES
        msg.position = q

        self.publisher.publish(msg)


def main():

    if len(sys.argv) != 6:
        print("Uso:")
        print("python3 move_joint.py waist shoulder elbow wrist gripper")
        print("Ángulos en grados.")
        return

    target = [
        math.radians(float(x))
        for x in sys.argv[1:]
    ]

    rclpy.init()

    node = SmoothCommander()

    print("Esperando /joint_states...")

    while rclpy.ok():

        rclpy.spin_once(node, timeout_sec=0.1)

        if len(node.current) == 5:
            break

    start = node.current.copy()

    duration = 3.0          # segundos
    frequency = 200          # Hz
    steps = int(duration * frequency)

    print("Moviendo...")

    for i in range(steps + 1):

        alpha = i / steps

        q = [
            start[j] + alpha * (target[j] - start[j])
            for j in range(5)
        ]

        node.publish(q)

        rclpy.spin_once(node, timeout_sec=0)

        time.sleep(1 / frequency)

    print("Movimiento terminado.")

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()