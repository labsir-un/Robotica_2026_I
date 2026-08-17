#!/usr/bin/env python3
"""Nodo de comprobación de rutina de prueba paso a paso para el robot PhantomX Pincher X100 con Herramienta de Vacío (Chupa/Ventosa)."""

import math
import time
from typing import Dict, List, Optional, Tuple

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String
from visualization_msgs.msg import Marker


COLOR_RGBA = {
    'yellow': (1.0, 0.8, 0.0, 1.0),
    'blue': (0.1, 0.3, 0.9, 1.0),
    'green': (0.0, 0.8, 0.2, 1.0),
    'red': (0.9, 0.1, 0.1, 1.0),
}


class TestRoutineNode(Node):
    """Ejecuta la rutina de prueba de 6 pasos para el sistema de vacío en orden: Amarillo -> Azul -> Verde -> Roja."""

    def __init__(self) -> None:
        super().__init__('test_routine_node')

        self.L1 = 0.105  # Brazo superior (m)
        self.L2 = 0.105  # Antebrazo (m)
        self.L3 = 0.075  # Gripper base (m)

        # Centroide de la plataforma blanca (en cm)
        self.white_platform_cm = (9.6, 0.0)

        # Centroides de las 4 canecas (en cm)
        self.bin_coords_cm: Dict[str, Tuple[float, float]] = {
            'yellow': (-1.35, -12.8), # 1. Caneca Lateral Derecha (Amarilla)
            'blue': (19.4, -9.3),     # 2. Caneca Frontal Derecha (Azul)
            'green': (19.4, 9.3),     # 3. Caneca Frontal Izquierda (Verde)
            'red': (-1.35, 12.8),     # 4. Caneca Lateral Izquierda (Roja)
        }

        # Poses predefinidas (en grados) - Gripper fijo en 0.0 (desactivado)
        self.pose_home_deg = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.pose_scan_deg = [0.0, -90.0, 90.0, 90.0, 0.0]
        self.current_pose_deg = list(self.pose_home_deg)

        self.command_pub = self.create_publisher(JointState, '/pincher/command', 10)
        self.status_pub = self.create_publisher(String, '/pincher/status', 10)
        self.vacuum_pub = self.create_publisher(String, '/pincher/vacuum', 10)
        self.marker_pub = self.create_publisher(Marker, '/visualization_marker', 10)

        # Parámetros ROS 2 para compensación de posición física y herramienta de vacío
        self.declare_parameter('offset_x_cm', 0.0)   # Compensación gestionada en cámara vision_node (2.0 cm)
        self.declare_parameter('offset_y_cm', 0.0)
        self.declare_parameter('z_approach_cm', 8.0)  # Aproximación segura a Z=8 cm
        self.declare_parameter('z_surface_cm', 5.0)   # Z=5.0 cm: Elevado 1 cm para contacto exacto de succión

        self.offset_x_cm = float(self.get_parameter('offset_x_cm').value)
        self.offset_y_cm = float(self.get_parameter('offset_y_cm').value)
        self.z_approach_cm = float(self.get_parameter('z_approach_cm').value)
        self.z_surface_cm = float(self.get_parameter('z_surface_cm').value)

        self.get_logger().info('🧲 Nodo de Prueba de Rutina Pick & Place con HERRAMIENTA DE VACÍO iniciado.')
        time.sleep(1.0)

        # Iniciar en Home
        self.publish_joint_degrees(self.pose_home_deg, 'Home')
        time.sleep(1.0)

        # Ejecutar secuencia completa de las 4 cestas
        self.run_full_test_sequence()

    def compute_ik_3d(self, x_cm: float, y_cm: float, z_cm: float) -> Optional[List[float]]:
        """Calcula cinemática inversa 3D analítica para el TCP de la chupa de vacío."""
        x_w = (x_cm + self.offset_x_cm) / 100.0
        y_w = (y_cm + self.offset_y_cm) / 100.0
        z_w = z_cm / 100.0

        z_shoulder_world = 0.110
        # Longitud efectiva hasta la superficie inferior de la chupa de succión TCP (0.125m)
        tool_length = 0.125  

        waist_deg = math.degrees(math.atan2(y_w, x_w))
        r_target = math.sqrt(x_w**2 + y_w**2)

        L1 = 0.105
        L2 = 0.105

        # Orientación vertical hacia abajo (180° a 110°)
        for orient_deg in range(180, 110, -5):
            orient_rad = math.radians(orient_deg)
            r_wrist = r_target - tool_length * math.sin(orient_rad)
            z_wrist_rel_shoulder = (z_w - tool_length * math.cos(orient_rad)) - z_shoulder_world

            D2 = r_wrist**2 + z_wrist_rel_shoulder**2
            D = math.sqrt(D2)

            cos_elbow = (D2 - L1**2 - L2**2) / (2 * L1 * L2)
            if -1.0 <= cos_elbow <= 1.0:
                e_rad = math.acos(cos_elbow)
                gamma = math.atan2(r_wrist, z_wrist_rel_shoulder)
                alpha = math.atan2(L2 * math.sin(e_rad), L1 + L2 * math.cos(e_rad))
                s_rad = gamma - alpha
                w_rad = orient_rad - (s_rad + e_rad)

                return [waist_deg, math.degrees(s_rad), math.degrees(e_rad), math.degrees(w_rad)]

        self.get_logger().error(f'❌ IK no alcanzable para ({x_cm}, {y_cm}, {z_cm})')
        return None

    def publish_joint_degrees(self, degrees: List[float], label: str) -> None:
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']
        msg.position = [math.radians(deg) for deg in degrees]
        self.command_pub.publish(msg)

        status_msg = String()
        status_msg.data = f'Prueba (Vacío): {label}'
        self.status_pub.publish(status_msg)

    def animate_to_pose(self, target_deg: List[float], label: str, duration_sec: float = 1.5) -> None:
        steps = 15
        dt = duration_sec / steps
        start_deg = list(self.current_pose_deg)

        self.get_logger().info(f'▶️ [{label}] -> {[round(d, 1) for d in target_deg]}')

        for step in range(1, steps + 1):
            ratio = step / float(steps)
            interp_deg = [start_deg[i] + ratio * (target_deg[i] - start_deg[i]) for i in range(len(target_deg))]
            self.publish_joint_degrees(interp_deg, label)
            time.sleep(dt)

        self.current_pose_deg = list(target_deg)

    def _publish_block_marker(self, x_cm: float, y_cm: float, z_cm: float, color: str) -> None:
        marker = Marker()
        marker.header.frame_id = 'world'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'test_block'
        marker.id = 1
        marker.type = Marker.CUBE
        marker.action = Marker.ADD

        marker.pose.position.x = x_cm / 100.0
        marker.pose.position.y = y_cm / 100.0
        marker.pose.position.z = z_cm / 100.0

        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.025
        marker.scale.y = 0.025
        marker.scale.z = 0.025

        rgba = COLOR_RGBA.get(color, (1.0, 1.0, 1.0, 1.0))
        marker.color.r = rgba[0]
        marker.color.g = rgba[1]
        marker.color.b = rgba[2]
        marker.color.a = rgba[3]

        self.marker_pub.publish(marker)

    def run_full_test_sequence(self) -> None:
        order = [
            ('yellow', '1. Amarillo'),
            ('blue', '2. Azul'),
            ('green', '3. Verde'),
            ('red', '4. Roja'),
        ]

        wx, wy = self.white_platform_cm

        for color, name in order:
            self.get_logger().info(f'\n========================================')
            self.get_logger().info(f'🚀 INICIANDO RUTINA DE VACÍO: CANASTA {name.upper()}')
            self.get_logger().info(f'========================================')

            # 1: Pase a posición de Scan
            self.animate_to_pose(self.pose_scan_deg, f'Paso 1 ({name}): Mover a Scan', duration_sec=1.5)
            self.get_logger().info(f'⏳ Pausa en pose Scan (5 segundos) para Canasta {name}...')
            time.sleep(5.0)

            # 2: Pre-pick seguro a Z=8.0 cm (por encima de la plataforma)
            ik_pre_pick = self.compute_ik_3d(wx, wy, self.z_approach_cm)
            if not ik_pre_pick:
                continue
            pose_pre_pick = ik_pre_pick + [0.0]
            self.animate_to_pose(pose_pre_pick, f'Paso 2 ({name}): Pre-pick sobre Centroide (Z={self.z_approach_cm}cm)', duration_sec=1.5)

            # 3: Descenso suave a la cara superior del cubo (Z=4.0 cm) y Activación de Vacío
            ik_pick = self.compute_ik_3d(wx, wy, self.z_surface_cm)
            if not ik_pick:
                continue
            pose_pick = ik_pick + [0.0]  # Garra mecánica desactivada

            self.animate_to_pose(pose_pick, f'Paso 3 ({name}): Descenso a Cara del Cubo (Z={self.z_surface_cm}cm)', duration_sec=1.2)
            self._publish_block_marker(wx, wy, 2.75, color)
            
            # ACTIVAR VACÍO (Reemplaza a la garra mecánica)
            self.vacuum_pub.publish(String(data='VACUUM_ON'))
            self.get_logger().info(f'🧲 BOMBA DE VACÍO ACTIVADA (Succión en cubo {name})')
            time.sleep(0.5)

            # 4: Subida vertical a Z=12.0 cm con el cubo sujetado por vacío
            ik_lift = self.compute_ik_3d(wx, wy, 12.0)
            if not ik_lift:
                continue
            pose_lift = ik_lift + [0.0]
            self._publish_block_marker(wx, wy, 12.0, color)
            self.animate_to_pose(pose_lift, f'Paso 4 ({name}): Subida Vertical Lift (Z=12.0cm)', duration_sec=1.5)

            # 5: Traslado a la canasta objetivo y desprendimiento por desactivación de vacío
            bx, by = self.bin_coords_cm[color]
            ik_pre_drop = self.compute_ik_3d(bx, by, 12.0)
            ik_drop = self.compute_ik_3d(bx, by, 6.0)

            if ik_pre_drop and ik_drop:
                pose_pre_drop = ik_pre_drop + [0.0]
                pose_drop = ik_drop + [0.0]

                self._publish_block_marker(bx, by, 12.0, color)
                self.animate_to_pose(pose_pre_drop, f'Paso 5 ({name}): Traslado a Centroide Canasta {name} (Z=12.0cm)', duration_sec=1.8)
                self._publish_block_marker(bx, by, 6.0, color)
                self.animate_to_pose(pose_drop, f'Paso 5 ({name}): Descenso en Canasta {name} (Z=6.0cm)', duration_sec=1.2)
                
                # DESACTIVAR VACÍO (Liberación del cubo)
                self.vacuum_pub.publish(String(data='VACUUM_OFF'))
                self.get_logger().info(f'💨 BOMBA DE VACÍO DESACTIVADA (Cubo soltado en Canasta {name})')
                time.sleep(0.5)

            # 6: Retorno a posición de scan
            self.animate_to_pose(self.pose_scan_deg, f'Paso 6 ({name}): Retorno a posición de Scan', duration_sec=1.5)

            self.get_logger().info(f'✅ RUTINA DE VACÍO COMPLETADA PARA CANASTA {name.upper()}\n')

        # Retorno final a Home al terminar las 4 canecas
        self.animate_to_pose(self.pose_home_deg, 'Fin de Prueba: Retorno a Home', duration_sec=1.5)
        self.get_logger().info('🎉 PRUEBA DE VACÍO COMPLETADA CON ÉXITO PARA LAS 4 CESTAS.')


def main(args=None) -> None:
    rclpy.init(args=args)
    node = TestRoutineNode()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
