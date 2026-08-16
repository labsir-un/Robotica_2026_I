#!/usr/bin/env python3
"""Nodo de prueba para posicionar el brazo en el centro de la plataforma blanca y publicar la esfera roja de forma continua."""

import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String
from visualization_msgs.msg import Marker


class GoToTrayOriginNode(Node):
    """Nodo con temporizador de 2 Hz para mantener la esfera roja y el comando activos en RViz."""

    def __init__(self) -> None:
        super().__init__('go_to_tray_origin_node')

        self.cmd_pub = self.create_publisher(JointState, '/pincher/command', 10)
        self.status_pub = self.create_publisher(String, '/pincher/status', 10)
        self.marker_pub = self.create_publisher(Marker, '/visualization_marker', 10)

        # Ángulos URDF exactos para el centro de la plataforma blanca:
        # Waist = 0.0°, Shoulder = +13.0°, Elbow = +129.0°, Wrist = +32.0° -> Alcanza X=9.61cm, Z=1.50cm
        self.target_deg = [0.0, 13.0, 129.0, 32.0, 0.0]

        # 1. Crear Marcador de Esfera Roja
        self.marker = Marker()
        self.marker.header.frame_id = 'world'
        self.marker.ns = 'tray_origin_target'
        self.marker.id = 999
        self.marker.type = Marker.SPHERE
        self.marker.action = Marker.ADD

        self.marker.pose.position.x = 0.096
        self.marker.pose.position.y = 0.0
        self.marker.pose.position.z = 0.04  # 4 cm sobre el centro de la bandeja (muy visible)

        self.marker.pose.orientation.w = 1.0
        self.marker.scale.x = 0.04  # 4 cm de diámetro
        self.marker.scale.y = 0.04
        self.marker.scale.z = 0.04

        self.marker.color.r = 1.0  # Rojo brillante
        self.marker.color.g = 0.0
        self.marker.color.b = 0.0
        self.marker.color.a = 0.9  # Visible y nítida

        # Temporizador a 2 Hz (cada 0.5 segundos re-publica)
        self.timer = self.create_timer(0.5, self.timer_callback)

        self.get_logger().info('🎯 Moviendo brazo al centro de la plataforma blanca y publicando esfera roja a 2 Hz...')

    def timer_callback(self) -> None:
        stamp = self.get_clock().now().to_msg()

        # Actualizar timestamp y publicar esfera roja en RViz
        self.marker.header.stamp = stamp
        self.marker_pub.publish(self.marker)

        # Publicar articulaciones del robot
        msg = JointState()
        msg.header.stamp = stamp
        msg.name = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']
        msg.position = [math.radians(deg) for deg in self.target_deg]
        self.cmd_pub.publish(msg)

        status_msg = String()
        status_msg.data = 'Moviendo al centro de la plataforma blanca (zonaRecoleccion_link)'
        self.status_pub.publish(status_msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = GoToTrayOriginNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
