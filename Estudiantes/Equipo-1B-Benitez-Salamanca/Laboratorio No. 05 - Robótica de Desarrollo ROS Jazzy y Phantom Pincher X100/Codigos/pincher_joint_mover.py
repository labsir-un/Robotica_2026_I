#!/usr/bin/env python3
"""Programa para mover articulaciones individuales del PhantomX Pincher.

Requiere el nodo `pincher_controller` corriendo en modo sin hardware:

    ros2 run pincher_control pincher_controller --ros-args -p use_hardware:=false

Ofrece dos modos de uso:

1. INTERACTIVO: selecciona una articulación por número y escribe el ángulo
   (en radianes) que quieres enviarle.
2. AUTOMÁTICO: recorre las 5 articulaciones, ejecuta 3 posiciones distintas
   dentro de límites razonables para cada una, y vuelve a la posición de
   referencia (HOME) entre cada prueba y al finalizar.

Ejecución:
    python3 pincher_joint_mover.py            # modo interactivo
    python3 pincher_joint_mover.py --auto      # modo automático (demo)
"""

from __future__ import annotations

import argparse
import math
import time
from typing import Dict, List

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_srvs.srv import Trigger

# Nombres de las articulaciones, en el mismo orden que declara pincher_controller.
JOINT_NAMES: List[str] = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']

# Límites aproximados en radianes para cada articulación (ajusta estos valores
# según el MotorProfile real de tu robot -- estos son conservadores para no
# saturar los motores durante la prueba).
JOINT_LIMITS: Dict[str, float] = {
    'waist': 2.61,    
    'shoulder': 2.61,
    'elbow': 2.61,
    'wrist': 2.61,
    'gripper': 1.57,
}

# Tres posiciones de prueba por articulación: negativa, cero/leve, positiva.
# Se calculan como fracciones del límite para mantenerse siempre dentro de rango.
def test_positions(joint: str) -> List[float]:
    limit = JOINT_LIMITS[joint]
    return [-0.6 * limit, 0.3 * limit, 0.9 * limit]


class PincherJointMover(Node):
    """Publica comandos articulares individuales y llama al servicio HOME."""

    def __init__(self) -> None:
        super().__init__('pincher_joint_mover')
        self.command_publisher = self.create_publisher(
            JointState, '/pincher/command', 10
        )
        self.home_client = self.create_client(Trigger, '/pincher/home')

    def send_joint_position(self, joint_name: str, radians: float) -> None:
        """Envía una posición a una sola articulación (las demás no se tocan)."""
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = [joint_name]
        msg.position = [radians]
        self.command_publisher.publish(msg)
        self.get_logger().info(
            f'-> {joint_name}: {radians:.3f} rad ({math.degrees(radians):.1f} deg)'
        )

    def go_home(self, wait_for_service_sec: float = 3.0) -> bool:
        """Llama al servicio /pincher/home para volver a la posición de referencia."""
        if not self.home_client.wait_for_service(timeout_sec=wait_for_service_sec):
            self.get_logger().error(
                'El servicio /pincher/home no está disponible. '
                '¿Está corriendo pincher_controller?'
            )
            return False

        future = self.home_client.call_async(Trigger.Request())
        rclpy.spin_until_future_complete(self, future, timeout_sec=wait_for_service_sec)

        if future.result() is None:
            self.get_logger().error('No se recibió respuesta del servicio HOME.')
            return False

        result = future.result()
        self.get_logger().info(f'HOME: {result.message}')
        return result.success


def run_interactive(node: PincherJointMover) -> None:
    """Modo interactivo: el usuario elige articulación y ángulo por consola."""
    print('\n=== Control individual de articulaciones - PhantomX Pincher ===')
    print('(nodo en modo sin hardware: use_hardware:=false)\n')

    while True:
        print('Articulaciones disponibles:')
        for i, name in enumerate(JOINT_NAMES, start=1):
            limit = JOINT_LIMITS[name]
            print(f'  {i}. {name:<10} (límite aprox: ±{limit:.2f} rad, '
                  f'±{math.degrees(limit):.0f} deg)')
        print('  0. Salir')
        print('  h. Ir a HOME (posición de referencia)')

        choice = input('\nSelecciona articulación (número), "h" o "0": ').strip().lower()

        if choice == '0':
            print('Saliendo...')
            break

        if choice == 'h':
            node.go_home()
            continue

        if not choice.isdigit() or not (1 <= int(choice) <= len(JOINT_NAMES)):
            print('Opción inválida, intenta de nuevo.\n')
            continue

        joint_name = JOINT_NAMES[int(choice) - 1]
        limit = JOINT_LIMITS[joint_name]

        try:
            angle_str = input(
                f'Ángulo para "{joint_name}" en radianes '
                f'(rango sugerido -{limit:.2f} a {limit:.2f}): '
            ).strip()
            angle = float(angle_str)
        except ValueError:
            print('Debes ingresar un número válido.\n')
            continue

        if abs(angle) > limit:
            print(f'Aviso: {angle:.3f} rad excede el límite sugerido (±{limit:.2f}). '
                  'El nodo lo recortará automáticamente si supera el límite físico real.')

        node.send_joint_position(joint_name, angle)
        # Pequeña pausa para que el publisher entregue el mensaje antes de seguir.
        time.sleep(0.2)
        print()


def run_automatic(node: PincherJointMover, hold_time_sec: float = 1.5) -> None:
    """Modo automático: 3 posiciones por articulación, regresando a HOME entre cada una."""
    print('\n=== Modo automático: prueba de las 5 articulaciones ===\n')

    # Posición inicial de referencia.
    node.go_home()
    time.sleep(hold_time_sec)

    for joint_name in JOINT_NAMES:
        print(f'--- Articulación: {joint_name} ---')
        for idx, angle in enumerate(test_positions(joint_name), start=1):
            node.send_joint_position(joint_name, angle)
            time.sleep(hold_time_sec)
            print(f'  Posición {idx}/3 alcanzada, regresando a HOME...')
            node.go_home()
            time.sleep(hold_time_sec)
        print(f'--- {joint_name} completado ---\n')

    print('Secuencia automática finalizada. Robot en posición de referencia.\n')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--auto', action='store_true',
        help='Ejecuta la secuencia automática de prueba en vez del modo interactivo.'
    )
    parser.add_argument(
        '--hold', type=float, default=1.5,
        help='Segundos de espera en cada posición durante el modo automático (default: 1.5).'
    )
    args = parser.parse_args()

    rclpy.init()
    node = PincherJointMover()

    try:
        if args.auto:
            run_automatic(node, hold_time_sec=args.hold)
        else:
            run_interactive(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()