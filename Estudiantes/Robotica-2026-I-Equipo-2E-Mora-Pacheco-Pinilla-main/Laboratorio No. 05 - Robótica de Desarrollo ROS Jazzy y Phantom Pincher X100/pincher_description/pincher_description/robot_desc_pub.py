#!/usr/bin/env python3
"""Publish robot_description on /robot_description topic (Transient Local QoS)."""
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy, HistoryPolicy
from std_msgs.msg import String


class RobotDescPublisher(Node):
    def __init__(self):
        super().__init__('robot_desc_publisher')
        self.declare_parameter('robot_description', '')
        urdf = self.get_parameter('robot_description').get_parameter_value().string_value
        qos = QoSProfile(
            depth=1,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
        )
        self.pub = self.create_publisher(String, 'robot_description', qos)
        self.timer = self.create_timer(0.5, lambda: self._publish(urdf))

    def _publish(self, urdf):
        msg = String(data=urdf)
        self.pub.publish(msg)
        self.get_logger().info('robot_description published (%d bytes)' % len(urdf))
        self.timer.cancel()
        self.timer = self.create_timer(5.0, lambda: self.pub.publish(String(data=urdf)))


def main():
    rclpy.init()
    node = RobotDescPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()
