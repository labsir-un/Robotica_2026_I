#!/usr/bin/env python3
"""Comando para insertar tus figuras 3D STL (cubo, cilindro) sobre la plataforma blanca en el origen exacto (X=9.6cm, Z=2.75cm)."""

import argparse
import math
import sys
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from visualization_msgs.msg import Marker


COLOR_PALETTE = {
    'red': (0.9, 0.1, 0.1, 1.0),
    'rojo': (0.9, 0.1, 0.1, 1.0),
    'green': (0.0, 0.8, 0.2, 1.0),
    'verde': (0.0, 0.8, 0.2, 1.0),
    'blue': (0.1, 0.3, 0.9, 1.0),
    'azul': (0.1, 0.3, 0.9, 1.0),
    'yellow': (1.0, 0.8, 0.0, 1.0),
    'amarillo': (1.0, 0.8, 0.0, 1.0),
}

SHAPE_MESH_MAP = {
    'cubo': 'package://pincher_description/meshes/cubo.stl',
    'cilindro': 'package://pincher_description/meshes/cilindro.stl',
}


def rpy_to_quaternion(roll_deg: float, pitch_deg: float, yaw_deg: float):
    r = math.radians(roll_deg) / 2.0
    p = math.radians(pitch_deg) / 2.0
    y = math.radians(yaw_deg) / 2.0
    qx = math.sin(r) * math.cos(p) * math.cos(y) - math.cos(r) * math.sin(p) * math.sin(y)
    qy = math.cos(r) * math.sin(p) * math.cos(y) + math.sin(r) * math.cos(p) * math.sin(y)
    qz = math.cos(r) * math.cos(p) * math.sin(y) - math.sin(r) * math.sin(p) * math.cos(y)
    qw = math.cos(r) * math.cos(p) * math.cos(y) + math.sin(r) * math.sin(p) * math.sin(y)
    return qx, qy, qz, qw


class SpawnObjectNode(Node):
    """Nodo que publica la figura 3D STL en la plataforma blanca (origen X=9.6cm, Z=2.75cm)."""

    def __init__(
        self,
        shape: str,
        color: str,
        x: float,
        y: float,
        z: float,
        roll: float,
        pitch: float,
        yaw: float,
        scale: float,
        marker_id: int,
    ) -> None:
        super().__init__('spawn_object_publisher')

        self.pub_marker = self.create_publisher(Marker, '/visualization_marker', 10)

        norm_color = color.lower().strip()
        if norm_color == 'rojo': norm_color = 'red'
        elif norm_color == 'verde': norm_color = 'green'
        elif norm_color == 'azul': norm_color = 'blue'
        elif norm_color == 'amarillo': norm_color = 'yellow'

        # Para el paralelópedo (cubo), pitch=90° lo acuesta a 25mm de alto
        if shape.lower() == 'cubo' and pitch == 0.0 and roll == 0.0:
            pitch = 90.0

        self.marker = Marker()
        self.marker.header.frame_id = 'world'
        self.marker.ns = 'user_shapes'
        self.marker.id = marker_id
        self.marker.type = Marker.MESH_RESOURCE
        self.marker.mesh_resource = SHAPE_MESH_MAP.get(shape.lower(), SHAPE_MESH_MAP['cubo'])
        self.marker.action = Marker.ADD

        # Coordenada world del origen de la plataforma blanca: X=0.096m, Y=0.0m, Z=0.0275m
        self.marker.pose.position.x = 0.096 + (x - 9.6) / 100.0
        self.marker.pose.position.y = y / 100.0
        self.marker.pose.position.z = z / 100.0  # 2.75 cm sobre el cero (apoyado sobre el plato)

        # Orientación RPY
        qx, qy, qz, qw = rpy_to_quaternion(roll, pitch, yaw)
        self.marker.pose.orientation.x = qx
        self.marker.pose.orientation.y = qy
        self.marker.pose.orientation.z = qz
        self.marker.pose.orientation.w = qw

        self.marker.scale.x = scale
        self.marker.scale.y = scale
        self.marker.scale.z = scale

        rgba = COLOR_PALETTE.get(norm_color, (0.0, 0.8, 0.2, 1.0))
        self.marker.color.r = rgba[0]
        self.marker.color.g = rgba[1]
        self.marker.color.b = rgba[2]
        self.marker.color.a = rgba[3]

        self.timer = self.create_timer(0.5, self.timer_callback)

        self.get_logger().info(
            f'✨ Figura STL ({shape.upper()}) colocada sobre la plataforma blanca | Color: {norm_color.upper()} | Posición: X={x}cm, Y={y}cm, Z={z}cm'
        )

    def timer_callback(self) -> None:
        self.marker.header.stamp = self.get_clock().now().to_msg()
        self.pub_marker.publish(self.marker)


def main():
    parser = argparse.ArgumentParser(
        description='Inserta tu figura 3D STL apoyada sobre la plataforma blanca.'
    )
    parser.add_argument('--shape', type=str, default='cubo', choices=['cubo', 'cilindro'])
    parser.add_argument('--color', type=str, default='green', choices=['green', 'verde', 'blue', 'azul', 'red', 'rojo', 'yellow', 'amarillo'])
    parser.add_argument('--x', type=float, default=9.6, help='Origen exacto plataforma blanca X=9.6cm')
    parser.add_argument('--y', type=float, default=0.0)
    parser.add_argument('--z', type=float, default=2.75, help='Altura apoyada sobre el plato Z=2.75cm')
    parser.add_argument('--roll', type=float, default=0.0)
    parser.add_argument('--pitch', type=float, default=0.0)
    parser.add_argument('--yaw', type=float, default=0.0)
    parser.add_argument('--scale', type=float, default=0.01)
    parser.add_argument('--id', type=int, default=1)

    args = parser.parse_args(sys.argv[1:])

    rclpy.init()
    node = SpawnObjectNode(
        args.shape,
        args.color,
        args.x,
        args.y,
        args.z,
        args.roll,
        args.pitch,
        args.yaw,
        args.scale,
        args.id,
    )

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
