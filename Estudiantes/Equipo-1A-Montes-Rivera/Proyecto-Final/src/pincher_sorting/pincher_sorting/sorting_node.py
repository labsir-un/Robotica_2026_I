#!/usr/bin/env python3
"""Nodo de máquina de estados Pick & Place automatizado con Cinemática Inversa 3D Dinámica Continua para PhantomX Pincher con Herramienta de Vacío."""

import math
import time
from typing import Dict, List, Optional, Tuple

from geometry_msgs.msg import Point
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String
from visualization_msgs.msg import Marker


COLOR_RGBA = {
    'green': (0.0, 0.8, 0.2, 1.0),
    'blue': (0.1, 0.3, 0.9, 1.0),
    'red': (0.9, 0.1, 0.1, 1.0),
    'yellow': (1.0, 0.8, 0.0, 1.0),
}


class SortingNode(Node):
    """Nodo Pick & Place con poses predefinidas (home, scan, recovery, pre_drop_*) y dinámicas (pre_pick, pick, lift, drop) usando Sistema de Succión por Vacío."""

    def __init__(self) -> None:
        super().__init__('sorting_node')

        self.L1 = 0.105  # Brazo superior
        self.L2 = 0.105  # Antebrazo
        self.L3 = 0.075  # Gripper base

        # Poses predefinidas (en grados) - Gripper fijo en 0.0 (desactivado)
        self.pose_home_deg = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.pose_scan_deg = [0.0, -90.0, 90.0, 90.0, 0.0]
        self.pose_recovery_deg = [0.0, -28.6, 86.0, 57.3, 0.0]

        # Poses estáticas de aproximación pre_drop por caneca (en grados)
        self.pose_pre_drop_deg: Dict[str, List[float]] = {
            'green': [25.5, -20.0, 51.5, 57.3, 0.0],
            'blue': [-25.5, -20.0, 51.5, 57.3, 0.0],
            'red': [96.0, -20.0, 51.5, 57.3, 0.0],
            'yellow': [-96.0, -20.0, 51.5, 57.3, 0.0],
        }

        self.current_pose_deg = list(self.pose_home_deg)

        # Coordenadas exactas del origen 3D de cada caneca en el mundo (en cm)
        self.bin_world_coords_cm: Dict[str, Tuple[float, float, float]] = {
            'green': (19.4, 9.3, 1.6),    # Caneca Frontal Izquierda
            'blue': (19.4, -9.3, 1.6),    # Caneca Frontal Derecha
            'red': (-1.35, 12.8, 1.6),    # Caneca Lateral Izquierda
            'yellow': (-1.35, -12.8, 1.6),# Caneca Lateral Derecha
        }

        self.command_pub = self.create_publisher(JointState, '/pincher/command', 10)
        self.status_pub = self.create_publisher(String, '/pincher/status', 10)
        self.vacuum_pub = self.create_publisher(String, '/pincher/vacuum', 10)
        self.marker_pub = self.create_publisher(Marker, '/visualization_marker', 10)

        self.sub_point = self.create_subscription(Point, 'vision/coordenada_pieza', self._point_callback, 10)
        self.sub_color = self.create_subscription(String, 'vision/color_pieza', self._color_callback, 10)

        self.current_color: Optional[str] = None
        self.last_color_time: float = 0.0
        self.is_busy: bool = False

        # Parámetros ROS 2 para compensación de posición física y herramienta de vacío
        self.declare_parameter('offset_x_cm', 0.0)   # Compensación gestionada en cámara vision_node (2.0 cm)
        self.declare_parameter('offset_y_cm', 0.0)
        self.declare_parameter('z_approach_cm', 8.0)
        self.declare_parameter('z_surface_cm', 5.0)  # Z=5.0 cm: Elevado 1 cm para contacto exacto de succión

        self.offset_x_cm = float(self.get_parameter('offset_x_cm').value)
        self.offset_y_cm = float(self.get_parameter('offset_y_cm').value)
        self.z_approach_cm = float(self.get_parameter('z_approach_cm').value)
        self.z_surface_cm = float(self.get_parameter('z_surface_cm').value)

        self.get_logger().info('🤖 Nodo de Clasificación Pick & Place con HERRAMIENTA DE VACÍO iniciado.')
        # Iniciar en pose home
        self.publish_joint_degrees(self.pose_home_deg, 'home')

    def _color_callback(self, msg: String) -> None:
        color = msg.data.lower().strip()
        if color in self.bin_world_coords_cm:
            self.current_color = color
            self.last_color_time = time.time()
            self.get_logger().info(f'🎨 Color de pieza confirmado por Visión: {color.upper()}')

    def _point_callback(self, msg: Point) -> None:
        if self.is_busy:
            return

        start_wait = time.time()
        while self.current_color is None and (time.time() - start_wait < 1.5):
            time.sleep(0.05)

        if self.current_color is None:
            self.get_logger().warn('⚠️ Se recibió coordenada pero aún no se ha recibido el color de la pieza. Omitiendo rutina.')
            return

        target_color = self.current_color
        self.current_color = None  # Consumir el color para obligar a una nueva confirmación
        self.is_busy = True
        self.get_logger().info(f'🚀 INICIANDO RUTINA PICK & PLACE (VACÍO) -> Coordenadas: (X={msg.x:.2f}cm, Y={msg.y:.2f}cm, Z={msg.z:.2f}cm) | Caneca: {target_color.upper()}')
        self._execute_pick_and_place(msg.x, msg.y, target_color)
        self.is_busy = False

    def compute_ik_3d(self, x_cm: float, y_cm: float, z_cm: float) -> Optional[List[float]]:
        """Calcula cinemática inversa 3D analítica exacta para el TCP de la chupa de vacío."""
        x_w = (x_cm + self.offset_x_cm) / 100.0
        y_w = (y_cm + self.offset_y_cm) / 100.0
        z_w = z_cm / 100.0

        z_shoulder_world = 0.110
        tool_length = 0.125  # Longitud desde articulación muñeca hasta la punta de la chupa TCP

        waist_deg = math.degrees(math.atan2(y_w, x_w))
        r_target = math.sqrt(x_w**2 + y_w**2)

        L1 = 0.105
        L2 = 0.105

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

        self.get_logger().warn(f'⚠️ No se encontró solución IK para (X={x_cm}cm, Y={y_cm}cm, Z={z_cm}cm)')
        return None

    def publish_joint_degrees(self, degrees: List[float], label: str) -> None:
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']
        msg.position = [math.radians(deg) for deg in degrees]
        self.command_pub.publish(msg)

        status_msg = String()
        status_msg.data = f'Pose (Vacío): {label}'
        self.status_pub.publish(status_msg)

    def animate_to_pose(self, target_deg: List[float], label: str, duration_sec: float = 1.5) -> None:
        steps = 15
        dt = duration_sec / steps
        start_deg = list(self.current_pose_deg)

        self.get_logger().info(f'Movimiento a Pose [{label}] -> {[round(d, 1) for d in target_deg]}')

        for step in range(1, steps + 1):
            ratio = step / float(steps)
            interp_deg = [start_deg[i] + ratio * (target_deg[i] - start_deg[i]) for i in range(len(target_deg))]
            self.publish_joint_degrees(interp_deg, label)
            time.sleep(dt)

        self.current_pose_deg = list(target_deg)

    def _execute_recovery_routine(self, reason: str) -> None:
        """Rutina de recuperación segura en caso de fallo de agarre o cinemática."""
        self.get_logger().warn(f'🚨 Ejecutando rutina RECOVERY debido a: {reason}')

        # 1. Desactivar bomba de vacío de inmediato
        self.vacuum_pub.publish(String(data='VACUUM_OFF'))
        self.get_logger().info('💨 Vacío desactivado por seguridad.')

        # 2. Mover a pose de recuperación (elevada)
        self.animate_to_pose(self.pose_recovery_deg, 'recovery (pose elevada)', duration_sec=1.5)

        # 3. Retornar a pose de escaneo/inicio
        self.animate_to_pose(self.pose_scan_deg, 'scan (post-recovery)', duration_sec=1.5)
        self.get_logger().info('✅ Recuperación completada. Sistema listo para nuevo ciclo.')

    def _execute_pick_and_place(self, x_cm: float, y_cm: float, color: str) -> None:
        try:
            # Pose 0: Mover a SCAN para libre visibilidad
            self.animate_to_pose(self.pose_scan_deg, 'scan', duration_sec=1.0)

            # Pose 1: pre_pick (Aproximación vertical segura a Z = 8.0 cm)
            ik_pre_pick = self.compute_ik_3d(x_cm, y_cm, self.z_approach_cm)
            if ik_pre_pick is None:
                self._execute_recovery_routine('Fallo IK en pre_pick')
                return
            pose_pre_pick = ik_pre_pick + [0.0]

            # Pose 2: pick (Descenso suave a superficie superior del cubo Z = 4.0 cm y succión)
            ik_pick = self.compute_ik_3d(x_cm, y_cm, self.z_surface_cm)
            if ik_pick is None:
                self._execute_recovery_routine('Fallo IK en pick')
                return
            pose_pick = ik_pick + [0.0]

            # Pose 3: lift (Elevación vertical a Z = 12.0 cm con pieza sujetada por vacío)
            ik_lift = self.compute_ik_3d(x_cm, y_cm, 12.0)
            if ik_lift is None:
                self._execute_recovery_routine('Fallo IK en lift')
                return
            pose_lift = ik_lift + [0.0]

            # Coordenadas de la caneca de destino
            bx_cm, by_cm, _ = self.bin_world_coords_cm.get(color, self.bin_world_coords_cm['green'])

            # Pose 4: pre_drop_<color> (Aproximación a la caneca correspondiente)
            pose_pre_drop = self.pose_pre_drop_deg.get(color, self.pose_pre_drop_deg['green'])

            # Pose 5: drop (Descenso en la caneca a Z = 6.0 cm y desactivación de vacío)
            ik_drop = self.compute_ik_3d(bx_cm, by_cm, 6.0)
            if ik_drop is None:
                self._execute_recovery_routine('Fallo IK en drop')
                return
            pose_drop = ik_drop + [0.0]

            # --- EJECUCIÓN DEL CICLO PICK & PLACE CON HERRAMIENTA DE VACÍO ---
            # Paso 1: pre_pick
            self.animate_to_pose(pose_pre_pick, 'pre_pick', duration_sec=1.5)

            # Paso 2: pick (Descenso + Activación de Vacío)
            self.animate_to_pose(pose_pick, f'pick (descenso a cara superior cubo Z={self.z_surface_cm}cm)', duration_sec=1.2)
            self.vacuum_pub.publish(String(data='VACUUM_ON'))
            self.get_logger().info('🧲 BOMBA DE VACÍO ACTIVADA')
            time.sleep(0.5)

            # Paso 3: lift
            self.animate_to_pose(pose_lift, 'lift (elevación con cubo)', duration_sec=1.5)

            # Paso 4: pre_drop_<color>
            self.animate_to_pose(pose_pre_drop, f'pre_drop_{color}', duration_sec=1.8)

            # Paso 5: drop (Descenso + Desactivación de Vacío)
            self.animate_to_pose(pose_drop, f'drop ({color})', duration_sec=1.2)
            self.vacuum_pub.publish(String(data='VACUUM_OFF'))
            self.get_logger().info(f'💨 BOMBA DE VACÍO DESACTIVADA (Cubo soltado en Canasta {color.upper()})')
            time.sleep(0.5)

            # Paso final: Retorno a SCAN / HOME
            self.animate_to_pose(self.pose_scan_deg, 'scan (retorno)', duration_sec=1.5)
            self.get_logger().info(f'✅ Ciclo completado para pieza {color.upper()}')

        except Exception as e:
            self._execute_recovery_routine(f'Excepción no controlada: {e}')


def main(args=None) -> None:
    rclpy.init(args=args)
    node = SortingNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
