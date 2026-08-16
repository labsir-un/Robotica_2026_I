#!/usr/bin/env python3
"""Publicador interactivo de prueba para simular detecciones de visión y mallas STL 3D en RViz."""

import argparse
import sys
import time
from geometry_msgs.msg import Point
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from visualization_msgs.msg import Marker


COLOR_MAP = {
    'green': (0.0, 0.8, 0.2, 1.0),
    'blue': (0.1, 0.3, 0.9, 1.0),
    'red': (0.9, 0.1, 0.1, 1.0),
    'yellow': (1.0, 0.8, 0.0, 1.0),
}

SHAPE_MESHES = {
    'cubo': 'package://pincher_description/meshes/cubo.stl',
    'cilindro': 'package://pincher_description/meshes/cilindro.stl',
    'triangulo': 'package://pincher_description/meshes/triangulo30x25.stl',
    'pentagono': 'package://pincher_description/meshes/pentagono25x25.stl',
}


def main():
    parser = argparse.ArgumentParser(description='Simula la detección de una figura STL 3D para pruebas en RViz.')
    parser.add_argument(
        '--color',
        type=str,
        default='green',
        choices=['green', 'blue', 'red', 'yellow'],
        help='Color de la canasta objetivo (green, blue, red, yellow).',
    )
    parser.add_argument(
        '--shape',
        type=str,
        default='cubo',
        choices=['cubo', 'cilindro', 'triangulo', 'pentagono'],
        help='Forma STL de la figura (cubo, cilindro, triangulo, pentagono).',
    )
    parser.add_argument('--x', type=float, default=12.0, help='Coordenada X en cm (relativo a la base del robot).')
    parser.add_argument('--y', type=float, default=0.0, help='Coordenada Y en cm (relativo a la base del robot).')

    args = parser.parse_args(sys.argv[1:])

    rclpy.init()
    node = Node('test_block_publisher')

    pub_point = node.create_publisher(Point, 'vision/coordenada_pieza', 10)
    pub_color = node.create_publisher(String, 'vision/color_pieza', 10)
    pub_marker = node.create_publisher(Marker, '/visualization_marker', 10)

    node.get_logger().info('Esperando descubrimiento DDS de subscriptores (1.5s)...')
    time.sleep(1.5)

    # 1. Crear marcador visual de Malla STL 3D para RViz
    marker = Marker()
    marker.header.frame_id = 'phantomx_pincher_arm_base_link'
    marker.header.stamp = node.get_clock().now().to_msg()
    marker.ns = 'simulated_shapes'
    marker.id = 1
    marker.type = Marker.MESH_RESOURCE
    marker.mesh_resource = SHAPE_MESHES.get(args.shape, SHAPE_MESHES['cubo'])
    marker.action = Marker.ADD

    # Convertir cm a metros para RViz
    marker.pose.position.x = args.x / 100.0
    marker.pose.position.y = args.y / 100.0
    marker.pose.position.z = 0.0125  # Superficie de la bandeja blanca

    marker.pose.orientation.w = 1.0
    marker.scale.x = 0.001  # Escala STL 1:1 (mm a m)
    marker.scale.y = 0.001
    marker.scale.z = 0.001

    rgba = COLOR_MAP.get(args.color, (0.0, 0.8, 0.2, 1.0))
    marker.color.r = rgba[0]
    marker.color.g = rgba[1]
    marker.color.b = rgba[2]
    marker.color.a = rgba[3]

    # 2. Publicar tópico de visión
    color_msg = String()
    color_msg.data = args.color

    point_msg = Point()
    point_msg.x = args.x
    point_msg.y = args.y
    point_msg.z = 0.0

    # Publicar 5 veces para garantizar recepción
    for _ in range(5):
        pub_marker.publish(marker)
        pub_color.publish(color_msg)
        pub_point.publish(point_msg)
        rclpy.spin_once(node, timeout_sec=0.1)
        time.sleep(0.1)

    node.get_logger().info(
        f'✅ Figura STL 3D ({args.shape.upper()}) simulada en RViz: Color={args.color.upper()} | Posición=({args.x}cm, {args.y}cm)'
    )

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
