#!/usr/bin/env python3
"""Programa de demostración de movimientos articulares independientes del PhantomX Pincher.

Permite seleccionar una articulación (base, hombro, codo, muñeca, pinza) y enviarle
posiciones angulares dentro de sus límites. Para cada articulación se ejecutan al menos
tres posiciones distintas y se regresa a la posición de referencia (HOME = 0°).

Los movimientos son progresivos (interpolados) para una visualización suave en RViz.

Uso:
    ros2 run pincher_control joint_position_demo
"""
from __future__ import annotations

import math
import os
import time
from typing import Dict, List, Tuple

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

# Límites articulares en grados (mínimo, máximo)
# Nota: gripper es prismático en mm (0 a 18), se maneja aparte
JOINT_LIMITS_DEG: Dict[str, Tuple[float, float]] = {
    'arm_shoulder_pan_joint': (-150.0, 150.0),
    'arm_shoulder_lift_joint': (-120.0, 120.0),
    'arm_elbow_flex_joint': (-139.0, 139.0),
    'arm_wrist_flex_joint': (-98.0, 103.0),
    'gripper_finger1_joint': (0.0, 18.0),  # mm (prismático)
}

# Nombres de articulaciones en orden
JOINT_NAMES: List[str] = [
    'arm_shoulder_pan_joint',
    'arm_shoulder_lift_joint',
    'arm_elbow_flex_joint',
    'arm_wrist_flex_joint',
    'gripper_finger1_joint',
]

# Nombres amigables para el usuario (español)
JOINT_DISPLAY_NAMES: Dict[str, str] = {
    'arm_shoulder_pan_joint': 'Base (shoulder pan)',
    'arm_shoulder_lift_joint': 'Hombro (shoulder lift)',
    'arm_elbow_flex_joint': 'Codo (elbow flex)',
    'arm_wrist_flex_joint': 'Muñeca (wrist flex)',
    'gripper_finger1_joint': 'Pinza (gripper)',
}

# Posiciones de demostración predefinidas para cada articulación
# Se incluyen al menos 3 posiciones por articulación dentro de sus límites
DEMO_POSITIONS_DEG: Dict[str, List[float]] = {
    'arm_shoulder_pan_joint': [-90.0, -45.0, 45.0, 90.0],
    'arm_shoulder_lift_joint': [-60.0, -30.0, 30.0, 60.0],
    'arm_elbow_flex_joint': [-60.0, -30.0, 30.0, 60.0],
    'arm_wrist_flex_joint': [-50.0, -25.0, 25.0, 50.0],
    'gripper_finger1_joint': [5.0, 10.0, 15.0, 18.0],  # mm
}

# Posición de referencia (HOME) por articulación
HOME_POSITIONS_DEG: Dict[str, float] = {
    'arm_shoulder_pan_joint': 0.0,
    'arm_shoulder_lift_joint': 0.0,
    'arm_elbow_flex_joint': 0.0,
    'arm_wrist_flex_joint': 0.0,
    'gripper_finger1_joint': 0.0,  # mm (abierto)
}

# Parámetros de interpolación
INTERPOLATION_RATE_HZ = 50.0    # Frecuencia de publicación durante interpolación
MOVE_DURATION_SEC = 1.5         # Duración de cada movimiento (segundos)
PAUSE_BETWEEN_MOVES = 0.5      # Pausa entre movimientos sucesivos (segundos)


def _joint_to_radians(joint_name: str, value: float) -> float:
    """Convierte el valor de una articulación a radianes para publicar.

    Para articulaciones revolute convierte grados a radianes.
    Para gripper (prismático) convierte mm a metros.
    """
    if joint_name == 'gripper_finger1_joint':
        return value / 1000.0  # mm a metros
    return math.radians(value)


def _radians_to_joint(joint_name: str, value: float) -> float:
    """Convierte radianes/metros a la unidad de la articulación."""
    if joint_name == 'gripper_finger1_joint':
        return value * 1000.0  # metros a mm
    return math.degrees(value)


class JointPositionDemo(Node):
    """Nodo ROS 2 para demostración de movimientos articulares independientes."""

    def __init__(self) -> None:
        super().__init__('joint_position_demo')
        self.command_publisher = self.create_publisher(JointState, '/pincher/command', 10)

        # Estado actual de cada articulación, para interpolar desde allí
        self.current_positions_deg: Dict[str, float] = {
            name: HOME_POSITIONS_DEG[name] for name in JOINT_NAMES
        }

        # Dar tiempo al sistema para establecer conexiones
        time.sleep(0.5)
        self.get_logger().info('Nodo joint_position_demo iniciado (movimiento interpolado).')

    def publish_joint_position(self, joint_name: str, value: float) -> None:
        """Publica un comando de posición para una articulación específica."""
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = [joint_name]
        msg.position = [_joint_to_radians(joint_name, value)]
        self.command_publisher.publish(msg)

    def move_joint_smooth(self, joint_name: str, target: float,
                          duration: float = MOVE_DURATION_SEC) -> None:
        """Mueve una articulación de forma progresiva (interpolación con suavizado)."""
        start = self.current_positions_deg[joint_name]
        delta = target - start

        if abs(delta) < 0.1:
            self.current_positions_deg[joint_name] = target
            return

        num_steps = max(int(duration * INTERPOLATION_RATE_HZ), 1)
        step_period = duration / num_steps

        for step in range(1, num_steps + 1):
            t = step / num_steps
            t_smooth = (1.0 - math.cos(t * math.pi)) / 2.0
            current = start + delta * t_smooth

            self.publish_joint_position(joint_name, current)
            rclpy.spin_once(self, timeout_sec=0.0)
            time.sleep(step_period)

        # Asegurar la posición final exacta
        self.publish_joint_position(joint_name, target)
        rclpy.spin_once(self, timeout_sec=0.0)
        self.current_positions_deg[joint_name] = target

    def move_to_home_smooth(self, joint_name: str,
                            duration: float = MOVE_DURATION_SEC) -> None:
        """Mueve la articulación a su posición HOME de forma progresiva."""
        self.move_joint_smooth(joint_name, HOME_POSITIONS_DEG[joint_name], duration)

    def move_all_home_smooth(self, duration: float = MOVE_DURATION_SEC) -> None:
        """Mueve todas las articulaciones a HOME de forma progresiva simultánea."""
        starts = {name: self.current_positions_deg[name] for name in JOINT_NAMES}
        targets = {name: HOME_POSITIONS_DEG[name] for name in JOINT_NAMES}

        num_steps = max(int(duration * INTERPOLATION_RATE_HZ), 1)
        step_period = duration / num_steps

        for step in range(1, num_steps + 1):
            t = step / num_steps
            t_smooth = (1.0 - math.cos(t * math.pi)) / 2.0

            msg = JointState()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.name = list(JOINT_NAMES)
            msg.position = [
                _joint_to_radians(name, starts[name] + (targets[name] - starts[name]) * t_smooth)
                for name in JOINT_NAMES
            ]
            self.command_publisher.publish(msg)
            rclpy.spin_once(self, timeout_sec=0.0)
            time.sleep(step_period)

        # Posición final exacta
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(JOINT_NAMES)
        msg.position = [_joint_to_radians(name, HOME_POSITIONS_DEG[name]) for name in JOINT_NAMES]
        self.command_publisher.publish(msg)
        rclpy.spin_once(self, timeout_sec=0.0)

        for name in JOINT_NAMES:
            self.current_positions_deg[name] = HOME_POSITIONS_DEG[name]
        self.get_logger().info('Todas las articulaciones enviadas a HOME.')

    def move_all_smooth(self, targets: List[float],
                        duration: float = MOVE_DURATION_SEC) -> None:
        """Mueve todas las articulaciones simultáneamente a las posiciones objetivo."""
        starts = [self.current_positions_deg[name] for name in JOINT_NAMES]
        deltas = [targets[i] - starts[i] for i in range(len(JOINT_NAMES))]

        if all(abs(d) < 0.1 for d in deltas):
            for i, name in enumerate(JOINT_NAMES):
                self.current_positions_deg[name] = targets[i]
            return

        num_steps = max(int(duration * INTERPOLATION_RATE_HZ), 1)
        step_period = duration / num_steps

        for step in range(1, num_steps + 1):
            t = step / num_steps
            t_smooth = (1.0 - math.cos(t * math.pi)) / 2.0

            msg = JointState()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.name = list(JOINT_NAMES)
            msg.position = [
                _joint_to_radians(JOINT_NAMES[i], starts[i] + deltas[i] * t_smooth)
                for i in range(len(JOINT_NAMES))
            ]
            self.command_publisher.publish(msg)
            rclpy.spin_once(self, timeout_sec=0.0)
            time.sleep(step_period)

        # Posición final exacta
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(JOINT_NAMES)
        msg.position = [_joint_to_radians(JOINT_NAMES[i], targets[i]) for i in range(len(JOINT_NAMES))]
        self.command_publisher.publish(msg)
        rclpy.spin_once(self, timeout_sec=0.0)

        for i, name in enumerate(JOINT_NAMES):
            self.current_positions_deg[name] = targets[i]

        self.get_logger().info(
            f'Vector aplicado: [{", ".join(f"{v:.1f}" for v in targets)}]'
        )


def print_menu() -> None:
    """Muestra el menú principal."""
    print('\n' + '=' * 60)
    print('    CONTROL DE POSICIÓN ARTICULAR - PhantomX Pincher')
    print('          (Movimientos progresivos interpolados)')
    print('=' * 60)
    print('\nSeleccione una opción:\n')
    print('  1.  Base (shoulder pan)    — Rotación de la base')
    print('  2.  Hombro (shoulder lift) — Articulación del hombro')
    print('  3.  Codo (elbow flex)      — Articulación del codo')
    print('  4.  Muñeca (wrist flex)    — Articulación de la muñeca')
    print('  5.  Pinza (gripper)        — Apertura/cierre de la pinza')
    print('  6.  Demo completa          — Recorre todas las articulaciones')
    print('  7.  Posición manual        — Ingresar articulación y valor')
    print('  8.  HOME (todas)           — Enviar todas a posición de referencia')
    print('  9.  Vector articular       — Mover todas con un vector (q1,q2,q3,q4,q5)')
    print(' 10.  Interpolación          — Interpolar entre dos configuraciones')
    print(' 11.  Trayectoria senoidal   — q(t) = q0 + A·sin(2πft) con 4 pruebas')
    print(' 12.  Cinemática inversa     — Mover a (x,y,z,θ) en espacio cartesiano')
    print(' 13.  Cinemática directa     — Calcular (x,y,z,roll,pitch,yaw) desde q1..q4')
    print(' 14.  Enseñanza de poses     — Guardar, nombrar y reproducir poses (YAML)')
    print(' 15.  Trazado de figuras     — Dibujar cuadrado/triángulo/círculo con IK')
    print(' 16.  Coreografía robótica   — "Pedro Pedro Pedro" ')
    print('  0.  Salir')
    print('-' * 60)


def _unit_label(joint_name: str) -> str:
    """Devuelve la unidad de medida de la articulación."""
    return 'mm' if joint_name == 'gripper_finger1_joint' else '°'


def print_joint_info(joint_name: str) -> None:
    """Imprime información sobre los límites de una articulación."""
    lower, upper = JOINT_LIMITS_DEG[joint_name]
    positions = DEMO_POSITIONS_DEG[joint_name]
    home = HOME_POSITIONS_DEG[joint_name]
    unit = _unit_label(joint_name)
    print(f'\n  Articulación: {JOINT_DISPLAY_NAMES[joint_name]}')
    print(f'  Límites: [{lower:.0f}{unit}, {upper:.0f}{unit}]')
    print(f'  Posición HOME: {home}{unit}')
    print(f'  Posiciones de demo: {positions}')
    print(f'  Duración por movimiento: {MOVE_DURATION_SEC}s\n')


def run_joint_demo(node: JointPositionDemo, joint_name: str) -> None:
    """Ejecuta la secuencia de demostración para una articulación."""
    print_joint_info(joint_name)
    positions = DEMO_POSITIONS_DEG[joint_name]
    home = HOME_POSITIONS_DEG[joint_name]
    unit = _unit_label(joint_name)

    print(f'  Iniciando secuencia para {JOINT_DISPLAY_NAMES[joint_name]}...\n')

    # Primero ir a HOME
    print(f'  [0] Ir a HOME ({home}{unit})...')
    node.move_to_home_smooth(joint_name)
    time.sleep(PAUSE_BETWEEN_MOVES)

    # Recorrer cada posición de demostración
    lower, upper = JOINT_LIMITS_DEG[joint_name]
    for i, target in enumerate(positions, start=1):
        clamped = max(lower, min(upper, target))
        print(f'  [{i}] Moviendo a {clamped:.1f}{unit}...')
        node.move_joint_smooth(joint_name, clamped)
        time.sleep(PAUSE_BETWEEN_MOVES)

    # Regresar a HOME
    print(f'  [{len(positions) + 1}] Regresando a HOME ({home}{unit})...')
    node.move_to_home_smooth(joint_name)
    time.sleep(PAUSE_BETWEEN_MOVES)

    print(f'\n  ✓ Secuencia completada para {JOINT_DISPLAY_NAMES[joint_name]}.')


def run_full_demo(node: JointPositionDemo) -> None:
    """Ejecuta la demostración completa para todas las articulaciones."""
    print('\n' + '=' * 60)
    print('    DEMO COMPLETA - Movimientos progresivos independientes')
    print('=' * 60)

    print('\n  Enviando todas las articulaciones a HOME...')
    node.move_all_home_smooth()
    time.sleep(PAUSE_BETWEEN_MOVES)

    for joint_name in JOINT_NAMES:
        print(f'\n{"─" * 50}')
        run_joint_demo(node, joint_name)

    print(f'\n{"─" * 50}')
    print('\n  Enviando todas las articulaciones a HOME final...')
    node.move_all_home_smooth()
    time.sleep(PAUSE_BETWEEN_MOVES)

    print('\n' + '=' * 60)
    print('    ✓ DEMO COMPLETA FINALIZADA')
    print('=' * 60)


def manual_position(node: JointPositionDemo) -> None:
    """Permite al usuario ingresar manualmente una articulación y posición."""
    print('\n  Articulaciones disponibles:')
    for i, name in enumerate(JOINT_NAMES, start=1):
        lower, upper = JOINT_LIMITS_DEG[name]
        unit = _unit_label(name)
        print(f'    {i}. {JOINT_DISPLAY_NAMES[name]} [{lower:.0f}{unit}, {upper:.0f}{unit}]')

    try:
        joint_idx = int(input('\n  Número de articulación (1-5): ')) - 1
        if joint_idx < 0 or joint_idx >= len(JOINT_NAMES):
            print('  ✗ Articulación no válida.')
            return
    except ValueError:
        print('  ✗ Entrada no válida.')
        return

    joint_name = JOINT_NAMES[joint_idx]
    lower, upper = JOINT_LIMITS_DEG[joint_name]
    unit = _unit_label(joint_name)

    try:
        value = float(input(f'  Valor [{lower:.0f}, {upper:.0f}] ({unit}): '))
    except ValueError:
        print('  ✗ Valor no numérico.')
        return

    clamped = max(lower, min(upper, value))
    print(f'\n  Moviendo {JOINT_DISPLAY_NAMES[joint_name]} a {clamped:.1f}{unit}...')
    node.move_joint_smooth(joint_name, clamped)
    print('  ✓ Movimiento completado.')


def vector_position(node: JointPositionDemo) -> None:
    """Permite mover todas las articulaciones con un vector."""
    print('\n  Movimiento por vector articular')
    print('  Formato: q1,q2,q3,q4,q5')
    print('  Orden: [pan(°), lift(°), elbow(°), wrist(°), gripper(mm)]')
    print('  Límites:')
    for name in JOINT_NAMES:
        lower, upper = JOINT_LIMITS_DEG[name]
        unit = _unit_label(name)
        print(f'    {JOINT_DISPLAY_NAMES[name]:28s} [{lower:.0f}{unit}, {upper:.0f}{unit}]')

    try:
        raw = input('\n  Vector (q1,q2,q3,q4,q5): ').strip()
        raw = raw.strip('()[] ')
        values = [float(v.strip()) for v in raw.split(',')]
    except ValueError:
        print('  ✗ Formato no válido. Use números separados por comas.')
        return

    if len(values) != len(JOINT_NAMES):
        print(f'  ✗ Se requieren {len(JOINT_NAMES)} valores, se recibieron {len(values)}.')
        return

    # Limitar a los límites articulares
    clamped = []
    for i, name in enumerate(JOINT_NAMES):
        lower, upper = JOINT_LIMITS_DEG[name]
        val = max(lower, min(upper, values[i]))
        if val != values[i]:
            unit = _unit_label(name)
            print(f'  ⚠ {JOINT_DISPLAY_NAMES[name]}: {values[i]:.1f} → {val:.1f}{unit} (limitado)')
        clamped.append(val)

    # Selección de modo
    print('\n  Modo de ejecución:')
    print('    a) Simultáneo — Todas al mismo tiempo')
    print('    b) Secuencial — Una a la vez')
    try:
        modo = input('\n  Modo (a/b): ').strip().lower()
    except (EOFError, ValueError):
        modo = 'a'

    if modo == 'b':
        print('\n  Ejecutando movimiento SECUENCIAL...')
        t_start = time.perf_counter()
        for i, name in enumerate(JOINT_NAMES):
            node.move_joint_smooth(name, clamped[i])
        elapsed = time.perf_counter() - t_start
        print(f'\n  ✓ Movimiento secuencial completado.')
        print(f'  ⏱ Tiempo total: {elapsed:.3f} segundos')
    else:
        print('\n  Ejecutando movimiento SIMULTÁNEO...')
        t_start = time.perf_counter()
        node.move_all_smooth(clamped)
        elapsed = time.perf_counter() - t_start
        print(f'\n  ✓ Movimiento simultáneo completado.')
        print(f'  ⏱ Tiempo total: {elapsed:.3f} segundos')


def _parse_vector(prompt: str) -> List[float] | None:
    """Parsea un vector de 5 valores ingresado por el usuario."""
    try:
        raw = input(prompt).strip()
        raw = raw.strip('()[] ')
        values = [float(v.strip()) for v in raw.split(',')]
    except ValueError:
        print('  ✗ Formato no válido. Use números separados por comas.')
        return None
    if len(values) != len(JOINT_NAMES):
        print(f'  ✗ Se requieren {len(JOINT_NAMES)} valores, se recibieron {len(values)}.')
        return None
    return values


def _clamp_vector(values: List[float]) -> List[float]:
    """Limita un vector a los rangos articulares."""
    clamped = []
    for i, name in enumerate(JOINT_NAMES):
        lower, upper = JOINT_LIMITS_DEG[name]
        clamped.append(max(lower, min(upper, values[i])))
    return clamped


def _cubic_interpolation(t: float) -> float:
    """Interpolación cúbica (Hermite): q(t) = 3t² - 2t³."""
    return 3.0 * t * t - 2.0 * t * t * t


def _linear_interpolation(t: float) -> float:
    """Interpolación lineal pura: q(t) = t."""
    return t


def interpolation_trajectory(node: JointPositionDemo) -> None:
    """Interpola entre dos configuraciones articulares."""
    print('\n' + '=' * 60)
    print('    INTERPOLACIÓN ENTRE DOS CONFIGURACIONES')
    print('=' * 60)
    print('\n  Ingrese dos configuraciones articulares.')
    print('  Formato: q1,q2,q3,q4,q5 (pan°, lift°, elbow°, wrist°, gripper mm)')

    print('\n  --- Configuración INICIAL (A) ---')
    values_a = _parse_vector('  Vector A: ')
    if values_a is None:
        return
    abs_a = _clamp_vector(values_a)

    print('\n  --- Configuración FINAL (B) ---')
    values_b = _parse_vector('  Vector B: ')
    if values_b is None:
        return
    abs_b = _clamp_vector(values_b)

    print(f'\n  Config A: [{", ".join(f"{v:.1f}" for v in abs_a)}]')
    print(f'  Config B: [{", ".join(f"{v:.1f}" for v in abs_b)}]')

    # Duración
    try:
        dur_input = input(f'\n  Duración del trayecto (s) [{MOVE_DURATION_SEC * 2}]: ').strip()
        duration = float(dur_input) if dur_input else MOVE_DURATION_SEC * 2
        duration = max(0.5, duration)
    except ValueError:
        duration = MOVE_DURATION_SEC * 2

    # Tipo de interpolación
    print('\n  Tipo de interpolación:')
    print('    a) Lineal — velocidad constante')
    print('    b) Cúbica — suave, vel=0 en extremos')
    try:
        tipo = input('\n  Tipo (a/b): ').strip().lower()
    except (EOFError, ValueError):
        tipo = 'a'

    if tipo == 'b':
        interp_func = _cubic_interpolation
        interp_name = 'Cúbica (3t² - 2t³)'
    else:
        interp_func = _linear_interpolation
        interp_name = 'Lineal (t)'

    print(f'\n  Interpolación: {interp_name}, Duración: {duration:.2f} s')

    # Mover a configuración A
    print('\n  Moviendo a configuración inicial A...')
    node.move_all_smooth(abs_a)
    time.sleep(PAUSE_BETWEEN_MOVES)

    # Preparar grabación
    data_log: List[Tuple[float, List[float]]] = []
    deltas = [abs_b[i] - abs_a[i] for i in range(len(JOINT_NAMES))]
    num_steps = max(int(duration * INTERPOLATION_RATE_HZ), 1)
    step_period = duration / num_steps

    print(f'  Ejecutando trayectoria ({num_steps} pasos)...')
    t_start = time.perf_counter()
    data_log.append((0.0, list(abs_a)))

    for step in range(1, num_steps + 1):
        t_normalized = step / num_steps
        t_interp = interp_func(t_normalized)
        positions = [abs_a[i] + deltas[i] * t_interp for i in range(len(JOINT_NAMES))]

        msg = JointState()
        msg.header.stamp = node.get_clock().now().to_msg()
        msg.name = list(JOINT_NAMES)
        msg.position = [_joint_to_radians(JOINT_NAMES[i], positions[i]) for i in range(len(JOINT_NAMES))]
        node.command_publisher.publish(msg)
        rclpy.spin_once(node, timeout_sec=0.0)

        t_elapsed = time.perf_counter() - t_start
        data_log.append((t_elapsed, list(positions)))
        time.sleep(step_period)

    # Posición final
    msg = JointState()
    msg.header.stamp = node.get_clock().now().to_msg()
    msg.name = list(JOINT_NAMES)
    msg.position = [_joint_to_radians(JOINT_NAMES[i], abs_b[i]) for i in range(len(JOINT_NAMES))]
    node.command_publisher.publish(msg)
    rclpy.spin_once(node, timeout_sec=0.0)

    t_total = time.perf_counter() - t_start
    data_log.append((t_total, list(abs_b)))

    for i, name in enumerate(JOINT_NAMES):
        node.current_positions_deg[name] = abs_b[i]

    print(f'\n  ✓ Trayectoria completada.')
    print(f'  ⏱ Tiempo total: {t_total:.3f} segundos')
    print(f'  Puntos registrados: {len(data_log)}')

    # Exportar datos
    output_dir = os.path.expanduser('~/ros2_jazzy/phantom_ws')
    filename = f'interpolation_data_{tipo}_{int(time.time())}.txt'
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w') as f:
        f.write(f'% Interpolación {interp_name} - PhantomX Pincher\n')
        f.write(f'% Config A: [{", ".join(f"{v:.1f}" for v in abs_a)}]\n')
        f.write(f'% Config B: [{", ".join(f"{v:.1f}" for v in abs_b)}]\n')
        f.write(f'% Duración: {t_total:.3f} s\n')
        f.write(f'% Columnas: tiempo q1 q2 q3 q4 q5\n%\n')
        for t_sample, pos in data_log:
            row = [f'{t_sample:.6f}'] + [f'{p:.4f}' for p in pos]
            f.write('\t'.join(row) + '\n')

    print(f'\n  Datos exportados a: {filepath}')

    # Gráfica
    try:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 6))
        times = [entry[0] for entry in data_log]
        for j, name in enumerate(JOINT_NAMES):
            angles = [entry[1][j] for entry in data_log]
            ax.plot(times, angles, linewidth=1.5, label=JOINT_DISPLAY_NAMES[name])
        ax.set_xlabel('Tiempo (s)')
        ax.set_ylabel('Valor articular')
        ax.set_title(f'Interpolación {interp_name} — A → B')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        img_path = filepath.replace('.txt', '.png')
        fig.savefig(img_path, dpi=150)
        print(f'  Gráfica guardada en: {img_path}')
        plt.show()
    except ImportError:
        print('  ⚠ matplotlib no disponible.')
    except Exception as e:
        print(f'  ⚠ No se pudo mostrar la gráfica: {e}')


def sinusoidal_trajectory(node: JointPositionDemo) -> None:
    """Ejecuta trayectorias senoidales q(t) = q0 + A·sin(2πft) en una articulación."""
    print('\n' + '=' * 60)
    print('    TRAYECTORIA SENOIDAL: q(t) = q₀ + A·sin(2πft)')
    print('=' * 60)

    print('\n  Seleccione la articulación:')
    for i, name in enumerate(JOINT_NAMES, start=1):
        lower, upper = JOINT_LIMITS_DEG[name]
        unit = _unit_label(name)
        print(f'    {i}. {JOINT_DISPLAY_NAMES[name]} [{lower:.0f}{unit}, {upper:.0f}{unit}]')

    try:
        joint_idx = int(input('\n  Articulación (1-5): ')) - 1
        if joint_idx < 0 or joint_idx >= len(JOINT_NAMES):
            print('  ✗ Articulación no válida.')
            return
    except ValueError:
        print('  ✗ Entrada no válida.')
        return

    joint_name = JOINT_NAMES[joint_idx]
    lower, upper = JOINT_LIMITS_DEG[joint_name]
    q0 = HOME_POSITIONS_DEG[joint_name]
    unit = _unit_label(joint_name)

    print(f'\n  Articulación: {JOINT_DISPLAY_NAMES[joint_name]}')
    print(f'  q₀ (centro) = {q0:.1f}{unit}')
    max_amp = min(upper - q0, q0 - lower)
    print(f'  Amplitud máxima permitida: {max_amp:.1f}{unit}')

    try:
        a1 = float(input(f'\n  Amplitud A1 ({unit}): '))
        a2 = float(input(f'  Amplitud A2 ({unit}): '))
    except ValueError:
        print('  ✗ Valor no numérico.')
        return

    a1 = min(abs(a1), max_amp)
    a2 = min(abs(a2), max_amp)
    if a1 <= 0 or a2 <= 0:
        print('  ✗ Las amplitudes deben ser positivas.')
        return

    try:
        f1 = float(input('  Frecuencia f1 (Hz): '))
        f2 = float(input('  Frecuencia f2 (Hz): '))
    except ValueError:
        print('  ✗ Valor no numérico.')
        return

    if f1 <= 0 or f2 <= 0:
        print('  ✗ Las frecuencias deben ser positivas.')
        return

    pruebas = [
        (a1, f1, f'A={a1:.1f}{unit}, f={f1:.2f}Hz'),
        (a1, f2, f'A={a1:.1f}{unit}, f={f2:.2f}Hz'),
        (a2, f1, f'A={a2:.1f}{unit}, f={f1:.2f}Hz'),
        (a2, f2, f'A={a2:.1f}{unit}, f={f2:.2f}Hz'),
    ]

    print(f'\n  Se ejecutarán 4 pruebas (1 ciclo cada una):')
    for i, (a, f, desc) in enumerate(pruebas, start=1):
        print(f'    Prueba {i}: {desc} (T={1.0/f:.3f}s)')

    input('\n  Presione Enter para iniciar...')

    all_results: List[Tuple[str, List[float], List[float]]] = []

    for prueba_num, (amp, freq, label) in enumerate(pruebas, start=1):
        period = 1.0 / freq
        num_steps = max(int(period * INTERPOLATION_RATE_HZ), 10)
        step_period = period / num_steps

        print(f'\n  ── Prueba {prueba_num}/4: {label} ──')

        node.move_joint_smooth(joint_name, q0, duration=min(1.0, period))
        time.sleep(0.3)

        times: List[float] = []
        angles: List[float] = []

        t_start = time.perf_counter()
        for step in range(num_steps + 1):
            t = step * step_period
            q = q0 + amp * math.sin(2.0 * math.pi * freq * t)
            q = max(lower, min(upper, q))

            node.publish_joint_position(joint_name, q)
            rclpy.spin_once(node, timeout_sec=0.0)

            t_real = time.perf_counter() - t_start
            times.append(t_real)
            angles.append(q)

            if step < num_steps:
                time.sleep(step_period)

        node.current_positions_deg[joint_name] = q0
        t_total = time.perf_counter() - t_start
        print(f'    ✓ Completada. Tiempo real: {t_total:.3f}s')
        all_results.append((label, times, angles))

    print('\n  Regresando a HOME...')
    node.move_to_home_smooth(joint_name)

    # Exportar
    output_dir = os.path.expanduser('~/ros2_jazzy/phantom_ws')
    filename = f'sinusoidal_{joint_name}_{int(time.time())}.txt'
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w') as f:
        f.write(f'% Trayectoria senoidal - {JOINT_DISPLAY_NAMES[joint_name]}\n')
        f.write(f'% q(t) = {q0:.1f} + A*sin(2*pi*f*t)\n')
        f.write(f'% Columnas: t1 q1 t2 q2 t3 q3 t4 q4\n%\n')
        max_len = max(len(r[1]) for r in all_results)
        for row in range(max_len):
            row_values = []
            for _, times_p, angles_p in all_results:
                idx = min(row, len(times_p) - 1)
                row_values.append(f'{times_p[idx]:.6f}')
                row_values.append(f'{angles_p[idx]:.4f}')
            f.write('\t'.join(row_values) + '\n')

    print(f'\n  Datos exportados a: {filepath}')

    # Gráfica
    try:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        for i, (label, times_p, angles_p) in enumerate(all_results):
            ax.plot(times_p, angles_p, color=colors[i], linewidth=1.5,
                    label=f'P{i+1}: {label}')
        ax.axhline(y=q0, color='gray', linewidth=1.0, linestyle=':',
                   label=f'q₀ = {q0:.1f}{unit}')
        ax.set_xlabel('Tiempo (s)')
        ax.set_ylabel(f'Valor ({unit})')
        ax.set_title(f'Trayectoria senoidal — {JOINT_DISPLAY_NAMES[joint_name]}')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        img_path = filepath.replace('.txt', '.png')
        fig.savefig(img_path, dpi=150)
        print(f'  Gráfica guardada en: {img_path}')
        plt.show()
    except ImportError:
        print('  ⚠ matplotlib no disponible.')
    except Exception as e:
        print(f'  ⚠ No se pudo mostrar la gráfica: {e}')

# ======================================================================
# CINEMÁTICA INVERSA
# ======================================================================
# Parámetros DH del robot (mm)
_IK_D1 = 35.0    # L1: offset vertical base a shoulder lift
_IK_A2 = 107.5   # L2: shoulder lift a elbow
_IK_A3 = 107.5   # L3: elbow a wrist
_IK_A4 = 54.5    # L4: wrist a end effector
_IK_OFFSETS = [0.0, math.pi / 2, 0.0, 0.0]  # offset DH en junta 2

# Límites articulares para IK (4 revolute, en rad)
_IK_QLIM_DEG = [
    (-150.0, 150.0),   # arm_shoulder_pan_joint
    (-120.0, 120.0),   # arm_shoulder_lift_joint
    (-139.0, 139.0),   # arm_elbow_flex_joint
    (-98.0, 103.0),    # arm_wrist_flex_joint
]
_IK_QLIM = [(math.radians(lo), math.radians(hi)) for lo, hi in _IK_QLIM_DEG]


def _ik_solve(x: float, y: float, z: float, theta_deg: float,
              q_actual: List[float]) -> Tuple[List[float], Dict] | Tuple[None, Dict]:
    """Calcula la cinemática inversa para (x,y,z) con orientación theta.

    Returns:
        (q_sel, info): q_sel = [q1,q2,q3,q4] en radianes, o None.
    """
    phi = math.radians(theta_deg)
    d1, a2, a3, a4 = _IK_D1, _IK_A2, _IK_A3, _IK_A4
    offsets = _IK_OFFSETS

    candidatos: List[List[float]] = []

    theta1_opts = [math.atan2(y, x), math.atan2(-y, -x)]

    for i, theta1_dh in enumerate(theta1_opts):
        theta1 = theta1_dh - offsets[0]
        r = math.hypot(x, y) if i == 0 else -math.hypot(x, y)
        zc = z - d1

        rw = r - a4 * math.cos(phi)
        zw = zc - a4 * math.sin(phi)

        cos_t3 = (rw**2 + zw**2 - a2**2 - a3**2) / (2 * a2 * a3)
        if abs(cos_t3) > 1.0:
            continue

        for signo in (1, -1):  # +1 codo abajo, -1 codo arriba
            sin_t3 = signo * math.sqrt(1.0 - cos_t3**2)
            theta3_dh = math.atan2(sin_t3, cos_t3)
            theta2_dh = (math.atan2(zw, rw)
                         - math.atan2(a3 * sin_t3, a2 + a3 * cos_t3))
            theta4_dh = phi - theta2_dh - theta3_dh

            q1 = theta1
            q2 = theta2_dh - offsets[1]
            q3 = theta3_dh - offsets[2]
            q4 = theta4_dh - offsets[3]
            candidatos.append([q1, q2, q3, q4, float(signo)])

    info: Dict = {'motivo': '', 'n_validas': 0, 'todas': candidatos, 'tipo_codo': ''}

    if not candidatos:
        info['motivo'] = 'fuera del alcance geométrico'
        return None, info

    # Descartar las que violan límites
    validas = []
    for c in candidatos:
        dentro = all(_IK_QLIM[j][0] <= c[j] <= _IK_QLIM[j][1] for j in range(4))
        if dentro:
            validas.append(c)

    info['n_validas'] = len(validas)

    if not validas:
        info['motivo'] = 'todas las soluciones violan los límites articulares'
        return None, info

    # Elegir la más cercana a la configuración actual
    dists = [sum((c[j] - q_actual[j])**2 for j in range(4))**0.5 for c in validas]
    idx_min = dists.index(min(dists))
    q_sel = validas[idx_min][:4]
    info['tipo_codo'] = 'codo abajo' if validas[idx_min][4] == 1.0 else 'codo arriba'

    return q_sel, info


def inverse_kinematics(node: JointPositionDemo) -> None:
    """Cinemática inversa: el usuario ingresa (x,y,z,θ) y el robot se mueve."""
    print('\n' + '=' * 60)
    print('    CINEMÁTICA INVERSA — PhantomX Pincher')
    print('=' * 60)
    print('\n  Parámetros DH del robot:')
    print(f'    d1 = {_IK_D1} mm (base a shoulder)')
    print(f'    a2 = {_IK_A2} mm (shoulder a elbow)')
    print(f'    a3 = {_IK_A3} mm (elbow a wrist)')
    print(f'    a4 = {_IK_A4} mm (wrist a end effector)')
    print(f'    Alcance máx ≈ {_IK_A2 + _IK_A3 + _IK_A4:.1f} mm')
    print('\n  Ingrese posición deseada del efector final (mm).')
    print('  theta = orientación del último eslabón en el plano (°)')
    print("  Escriba 'salir' para volver al menú.\n")

    # Config actual en radianes (4 revolute)
    q_actual = [
        math.radians(node.current_positions_deg['arm_shoulder_pan_joint']),
        math.radians(node.current_positions_deg['arm_shoulder_lift_joint']),
        math.radians(node.current_positions_deg['arm_elbow_flex_joint']),
        math.radians(node.current_positions_deg['arm_wrist_flex_joint']),
    ]

    while True:
        try:
            entrada = input("  x (mm) [o 'salir']: ").strip()
        except EOFError:
            break
        if entrada.lower() == 'salir':
            break

        try:
            x = float(entrada)
            y = float(input('  y (mm): '))
            z = float(input('  z (mm): '))
            theta = float(input('  theta (°): '))
        except ValueError:
            print('  ✗ Entrada inválida.\n')
            continue

        q_sel, info = _ik_solve(x, y, z, theta, q_actual)

        if q_sel is None:
            print(f'  ✗ Punto NO ALCANZABLE. Motivo: {info["motivo"]}')
            print(f'    Candidatos evaluados: {len(info["todas"])}\n')
            continue

        q_deg = [math.degrees(q) for q in q_sel]
        print(f'\n  ✓ Solución encontrada ({info["tipo_codo"]}):')
        print(f'    [pan, lift, elbow, wrist] = '
              f'[{", ".join(f"{v:.2f}" for v in q_deg)}]°')
        print(f'    Soluciones válidas: {info["n_validas"]}')

        # Mover el robot (mantener gripper en su posición actual)
        gripper_val = node.current_positions_deg['gripper_finger1_joint']
        targets = q_deg + [gripper_val]
        node.move_all_smooth(targets)
        q_actual = list(q_sel)
        print('    Robot movido a la configuración.\n')


# ======================================================================
# CINEMÁTICA DIRECTA
# ======================================================================
def _dh_matrix(theta: float, d: float, a: float, alpha: float, offset: float) -> List[List[float]]:
    """Matriz de transformación homogénea DH estándar 4x4 (con offset)."""
    th = theta + offset
    ct, st = math.cos(th), math.sin(th)
    ca, sa = math.cos(alpha), math.sin(alpha)
    return [
        [ct, -st * ca,  st * sa, a * ct],
        [st,  ct * ca, -ct * sa, a * st],
        [0.0,      sa,       ca,      d],
        [0.0,     0.0,      0.0,    1.0],
    ]


def _mat_mult(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
    """Multiplica dos matrices 4x4."""
    result = [[0.0]*4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            s = 0.0
            for k in range(4):
                s += A[i][k] * B[k][j]
            result[i][j] = s
    return result


def _rotation_to_rpy(R: List[List[float]]) -> Tuple[float, float, float]:
    """Extrae roll, pitch, yaw (ZYX) de una matriz de rotación 3x3."""
    # pitch
    sy = math.sqrt(R[0][0]**2 + R[1][0]**2)
    singular = sy < 1e-6

    if not singular:
        roll = math.atan2(R[2][1], R[2][2])
        pitch = math.atan2(-R[2][0], sy)
        yaw = math.atan2(R[1][0], R[0][0])
    else:
        roll = math.atan2(-R[1][2], R[1][1])
        pitch = math.atan2(-R[2][0], sy)
        yaw = 0.0

    return roll, pitch, yaw


def _fkine(q_rad: List[float]) -> Tuple[float, float, float, float, float, float]:
    """Cinemática directa: dado q=[q1,q2,q3,q4] en rad, devuelve (x,y,z,roll,pitch,yaw).

    Posición en mm, ángulos en grados.
    """
    d1, a2, a3, a4 = _IK_D1, _IK_A2, _IK_A3, _IK_A4
    offsets = _IK_OFFSETS

    T1 = _dh_matrix(q_rad[0], d1, 0.0, math.pi / 2, offsets[0])
    T2 = _dh_matrix(q_rad[1], 0.0, a2, 0.0, offsets[1])
    T3 = _dh_matrix(q_rad[2], 0.0, a3, 0.0, offsets[2])
    T4 = _dh_matrix(q_rad[3], 0.0, a4, 0.0, offsets[3])

    T01 = T1
    T02 = _mat_mult(T01, T2)
    T03 = _mat_mult(T02, T3)
    T04 = _mat_mult(T03, T4)

    x = T04[0][3]
    y = T04[1][3]
    z = T04[2][3]

    # Extraer RPY de la submatriz de rotación
    R = [row[:3] for row in T04[:3]]
    roll, pitch, yaw = _rotation_to_rpy(R)

    return x, y, z, math.degrees(roll), math.degrees(pitch), math.degrees(yaw)


def forward_kinematics(node: JointPositionDemo) -> None:
    """Cinemática directa: recibe q1,q2,q3,q4 y calcula x,y,z,roll,pitch,yaw."""
    print('\n' + '=' * 60)
    print('    CINEMÁTICA DIRECTA — PhantomX Pincher')
    print('=' * 60)
    print('\n  Límites articulares:')
    rev_names = JOINT_NAMES[:4]
    for name in rev_names:
        lo, hi = JOINT_LIMITS_DEG[name]
        print(f'    {JOINT_DISPLAY_NAMES[name]:28s} [{lo:.0f}°, {hi:.0f}°]')
    print('\n  Opciones:')
    print('    a) Ingresar vector [q1,q2,q3,q4] en grados')
    print('    b) Usar la posición actual del robot')

    try:
        modo = input('\n  Opción (a/b): ').strip().lower()
    except (EOFError, ValueError):
        modo = 'b'

    if modo == 'a':
        try:
            raw = input('  Vector [q1,q2,q3,q4] (°): ').strip().strip('()[] ')
            values = [float(v.strip()) for v in raw.split(',')]
        except ValueError:
            print('  ✗ Formato no válido.')
            return
        if len(values) != 4:
            print(f'  ✗ Se requieren 4 valores, se recibieron {len(values)}.')
            return
        q_deg = values
    else:
        q_deg = [
            node.current_positions_deg['arm_shoulder_pan_joint'],
            node.current_positions_deg['arm_shoulder_lift_joint'],
            node.current_positions_deg['arm_elbow_flex_joint'],
            node.current_positions_deg['arm_wrist_flex_joint'],
        ]
        print(f'\n  Posición actual: [{", ".join(f"{v:.2f}" for v in q_deg)}]°')

    q_rad = [math.radians(v) for v in q_deg]
    x, y, z, roll, pitch, yaw = _fkine(q_rad)

    print('\n  ┌─────────────────────────────────────────────┐')
    print('  │       RESULTADO CINEMÁTICA DIRECTA           │')
    print('  ├─────────────────────────────────────────────┤')
    print(f'  │  q = [{", ".join(f"{v:.1f}" for v in q_deg)}]°')
    print('  ├─────────────────────────────────────────────┤')
    print(f'  │  x     = {x:10.3f} mm                       │')
    print(f'  │  y     = {y:10.3f} mm                       │')
    print(f'  │  z     = {z:10.3f} mm                       │')
    print(f'  │  roll  = {roll:10.3f} °                      │')
    print(f'  │  pitch = {pitch:10.3f} °                      │')
    print(f'  │  yaw   = {yaw:10.3f} °                      │')
    print('  ├─────────────────────────────────────────────┤')
    dist = math.sqrt(x*x + y*y + z*z)
    print(f'  │  |P|   = {dist:10.3f} mm (dist. al origen)  │')
    print('  └─────────────────────────────────────────────┘')

    # Opción de mover el robot a esa configuración
    if modo == 'a':
        try:
            mover = input('\n  ¿Mover el robot a esta configuración? (s/n): ').strip().lower()
        except (EOFError, ValueError):
            mover = 'n'
        if mover == 's':
            gripper_val = node.current_positions_deg['gripper_finger1_joint']
            targets = q_deg + [gripper_val]
            # Limitar
            for i, name in enumerate(JOINT_NAMES[:4]):
                lo, hi = JOINT_LIMITS_DEG[name]
                targets[i] = max(lo, min(hi, targets[i]))
            node.move_all_smooth(targets)
            print('  ✓ Robot movido a la configuración.')


# ======================================================================
# ENSEÑANZA Y REPETICIÓN DE POSES
# ======================================================================
_POSES_YAML_PATH = os.path.expanduser('~/ros2_jazzy/phantom_ws/poses.yaml')


def _load_poses() -> Dict[str, List[float]]:
    """Carga las poses guardadas desde el archivo YAML."""
    if not os.path.isfile(_POSES_YAML_PATH):
        return {}
    try:
        import yaml
        with open(_POSES_YAML_PATH, 'r') as f:
            data = yaml.safe_load(f)
        if data is None:
            return {}
        return {k: list(v) for k, v in data.items()}
    except Exception:
        return {}


def _save_poses(poses: Dict[str, List[float]]) -> None:
    """Guarda las poses en el archivo YAML."""
    import yaml
    with open(_POSES_YAML_PATH, 'w') as f:
        yaml.dump(poses, f, default_flow_style=True, sort_keys=False)


def teach_poses(node: JointPositionDemo) -> None:
    """Modo de enseñanza y repetición de poses."""
    print('\n' + '=' * 60)
    print('    ENSEÑANZA Y REPETICIÓN DE POSES')
    print('=' * 60)

    poses = _load_poses()
    transition_time = MOVE_DURATION_SEC
    stop_playback = False

    print(f'  Archivo de poses: {_POSES_YAML_PATH}')
    print(f'  Poses cargadas: {len(poses)}')

    while True:
        print(f'\n  {"─" * 50}')
        print(f'  Poses almacenadas: {len(poses)} | Transición: {transition_time:.1f}s')
        if poses:
            print(f'  Nombres: {", ".join(poses.keys())}')
        print(f'  {"─" * 50}')
        print('  Opciones:')
        print('    1) Mover robot (vector q1,q2,q3,q4,q5)')
        print('    2) Guardar pose actual con un nombre')
        print('    3) Listar poses guardadas')
        print('    4) Reproducir todas las poses en orden')
        print('    5) Modificar tiempo de transición')
        print('    6) Eliminar una pose')
        print('    7) Volver al menú principal')

        try:
            op = input('\n  Opción: ').strip()
        except EOFError:
            break

        if op == '7':
            break

        elif op == '1':
            print('  Formato: q1,q2,q3,q4,q5 (pan°, lift°, elbow°, wrist°, gripper mm)')
            try:
                raw = input('  Vector: ').strip().strip('()[] ')
                values = [float(v.strip()) for v in raw.split(',')]
            except ValueError:
                print('  ✗ Formato no válido.')
                continue
            if len(values) != 5:
                print('  ✗ Se requieren 5 valores.')
                continue
            clamped = _clamp_vector(values)
            node.move_all_smooth(clamped, duration=transition_time)
            print('  ✓ Robot movido.')

        elif op == '2':
            try:
                nombre = input('  Nombre para esta pose: ').strip()
            except EOFError:
                continue
            if not nombre:
                print('  ✗ Nombre vacío.')
                continue
            current = [node.current_positions_deg[n] for n in JOINT_NAMES]
            poses[nombre] = current
            _save_poses(poses)
            print(f'  ✓ Pose "{nombre}" guardada: '
                  f'[{", ".join(f"{v:.1f}" for v in current)}]')

        elif op == '3':
            if not poses:
                print('  (sin poses guardadas)')
            else:
                print(f'\n  {"#":<4s} {"Nombre":<20s} {"Configuración"}')
                print(f'  {"─"*4} {"─"*20} {"─"*40}')
                for i, (name, vals) in enumerate(poses.items(), 1):
                    print(f'  {i:<4d} {name:<20s} [{", ".join(f"{v:.1f}" for v in vals)}]')
                print(f'\n  Total: {len(poses)} poses')

        elif op == '4':
            if len(poses) < 1:
                print('  ✗ No hay poses para reproducir.')
                continue
            print(f'\n  Reproduciendo {len(poses)} poses '
                  f'(transición={transition_time:.1f}s)...')
            print('  (Ctrl+C para detener)\n')
            stop_playback = False
            try:
                for i, (name, vals) in enumerate(poses.items(), 1):
                    if stop_playback:
                        break
                    print(f'  [{i}/{len(poses)}] → "{name}"')
                    node.move_all_smooth(vals, duration=transition_time)
                    time.sleep(0.3)
                print('\n  ✓ Reproducción completada.')
            except KeyboardInterrupt:
                stop_playback = True
                print('\n  ⏹ Reproducción detenida.')

        elif op == '5':
            try:
                t = float(input(f'  Nuevo tiempo de transición (s) [{transition_time:.1f}]: ').strip() or str(transition_time))
                transition_time = max(0.3, t)
                print(f'  ✓ Tiempo de transición: {transition_time:.1f}s')
            except ValueError:
                print('  ✗ Valor no válido.')

        elif op == '6':
            if not poses:
                print('  (sin poses)')
                continue
            try:
                raw = input('  Nombres a eliminar (separados por coma): ').strip()
            except EOFError:
                continue
            nombres = [n.strip() for n in raw.split(',') if n.strip()]
            eliminadas = []
            no_encontradas = []
            for nombre in nombres:
                if nombre in poses:
                    del poses[nombre]
                    eliminadas.append(nombre)
                else:
                    no_encontradas.append(nombre)
            if eliminadas:
                _save_poses(poses)
                print(f'  ✓ Eliminadas: {", ".join(eliminadas)}')
            if no_encontradas:
                print(f'  ✗ No encontradas: {", ".join(no_encontradas)}')

        else:
            print('  ✗ Opción no válida.')


# ======================================================================
# TRAZADO DE FIGURAS
# ======================================================================
def _generate_square(cx: float, cy: float, z: float, side: float, n_points: int) -> List[Tuple[float, float, float]]:
    """Genera puntos de un cuadrado centrado en (cx, cy) a altura z."""
    half = side / 2.0
    corners = [
        (cx - half, cy - half, z),
        (cx + half, cy - half, z),
        (cx + half, cy + half, z),
        (cx - half, cy + half, z),
    ]
    points = []
    pts_per_side = max(n_points // 4, 2)
    for i in range(4):
        p1 = corners[i]
        p2 = corners[(i + 1) % 4]
        for j in range(pts_per_side):
            t = j / pts_per_side
            x = p1[0] + (p2[0] - p1[0]) * t
            y = p1[1] + (p2[1] - p1[1]) * t
            points.append((x, y, z))
    points.append(corners[0])  # cerrar
    return points


def _generate_triangle(cx: float, cy: float, z: float, side: float, n_points: int) -> List[Tuple[float, float, float]]:
    """Genera puntos de un triángulo equilátero centrado en (cx, cy) a altura z."""
    h = side * math.sqrt(3) / 2.0
    corners = [
        (cx, cy + 2.0 * h / 3.0, z),
        (cx - side / 2.0, cy - h / 3.0, z),
        (cx + side / 2.0, cy - h / 3.0, z),
    ]
    points = []
    pts_per_side = max(n_points // 3, 2)
    for i in range(3):
        p1 = corners[i]
        p2 = corners[(i + 1) % 3]
        for j in range(pts_per_side):
            t = j / pts_per_side
            x = p1[0] + (p2[0] - p1[0]) * t
            y = p1[1] + (p2[1] - p1[1]) * t
            points.append((x, y, z))
    points.append(corners[0])  # cerrar
    return points


def _generate_circle(cx: float, cy: float, z: float, radius: float, n_points: int) -> List[Tuple[float, float, float]]:
    """Genera puntos de un círculo centrado en (cx, cy) a altura z."""
    points = []
    for i in range(n_points + 1):
        angle = 2.0 * math.pi * i / n_points
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        points.append((x, y, z))
    return points


def draw_figure(node: JointPositionDemo) -> None:
    """Traza una figura geométrica usando cinemática inversa."""
    print('\n' + '=' * 60)
    print('    TRAZADO DE FIGURAS — Cinemática Inversa')
    print('=' * 60)
    print('\n  El robot traza la figura en un plano a altura z constante.')
    print(f'  Alcance máx ≈ {_IK_A2 + _IK_A3 + _IK_A4:.0f} mm')
    print('\n  Seleccione la figura:')
    print('    1) Cuadrado')
    print('    2) Triángulo')
    print('    3) Círculo')

    try:
        fig = input('\n  Figura (1/2/3): ').strip()
    except EOFError:
        return

    if fig not in ('1', '2', '3'):
        print('  ✗ Opción no válida.')
        return

    # Parámetros de la figura
    try:
        cx = float(input('  Centro X (mm) [150]: ').strip() or '150')
        cy = float(input('  Centro Y (mm) [0]: ').strip() or '0')
        z = float(input('  Altura Z (mm) [50]: ').strip() or '50')
        if fig == '3':
            size = float(input('  Radio (mm) [40]: ').strip() or '40')
        else:
            size = float(input('  Lado (mm) [60]: ').strip() or '60')
        n_pts = int(input('  Puntos por figura [20]: ').strip() or '20')
        theta = float(input('  Theta orientación (°) [0]: ').strip() or '0')
        dur_input = input(f'  Tiempo entre puntos (s) [{0.3}]: ').strip()
        dt = float(dur_input) if dur_input else 0.3
    except ValueError:
        print('  ✗ Valor no válido.')
        return

    # Generar puntos
    if fig == '1':
        points = _generate_square(cx, cy, z, size, n_pts)
        fig_name = 'Cuadrado'
    elif fig == '2':
        points = _generate_triangle(cx, cy, z, size, n_pts)
        fig_name = 'Triángulo'
    else:
        points = _generate_circle(cx, cy, z, size, n_pts)
        fig_name = 'Círculo'

    print(f'\n  Figura: {fig_name} | {len(points)} puntos')
    print(f'  Centro: ({cx}, {cy}) mm | Z={z} mm | Theta={theta}°')

    # Config actual en rad
    q_actual = [
        math.radians(node.current_positions_deg['arm_shoulder_pan_joint']),
        math.radians(node.current_positions_deg['arm_shoulder_lift_joint']),
        math.radians(node.current_positions_deg['arm_elbow_flex_joint']),
        math.radians(node.current_positions_deg['arm_wrist_flex_joint']),
    ]

    print(f'\n  Trazando (Ctrl+C para detener)...\n')
    inalcanzables = 0

    try:
        for i, (px, py, pz) in enumerate(points):
            q_sel, info = _ik_solve(px, py, pz, theta, q_actual)

            if q_sel is None:
                inalcanzables += 1
                if inalcanzables <= 3:
                    print(f'  ⚠ Punto {i+1} ({px:.1f},{py:.1f},{pz:.1f}) inalcanzable')
                continue

            q_deg = [math.degrees(q) for q in q_sel]
            gripper_val = node.current_positions_deg['gripper_finger1_joint']
            targets = q_deg + [gripper_val]
            node.move_all_smooth(targets, duration=dt)
            q_actual = list(q_sel)

        print(f'\n  ✓ Trazado completado.')
        if inalcanzables > 0:
            print(f'  ⚠ Puntos inalcanzables: {inalcanzables}/{len(points)}')

    except KeyboardInterrupt:
        print('\n  ⏹ Trazado detenido.')


# ======================================================================
# COREOGRAFÍA ROBÓTICA — "Pedro Pedro Pedro"
# ======================================================================
def choreography(node: JointPositionDemo) -> None:
    """Coreografía robótica sincronizada con 'Pedro Pedro Pedro' (50s)."""
    print('\n' + '=' * 60)
    print('    COREOGRAFÍA ROBÓTICA — "Pedro Pedro Pedro"')
    print('=' * 60)
    print('\n  Duración: 50 segundos')
    print('  Cabeceo cada 1s + giro 360° cada 7s')
    print('  Segundo 42+: todo el cuerpo baila')
    print('  Ctrl+C para detener.')

    input('\n  Presione Enter para iniciar...')

    TOTAL_DURATION = 50.0
    BEAT_PERIOD = 1.0
    ROTATION_PERIOD = 7.0
    VIGOROUS_START = 40.0
    RATE_HZ = 25.0

    # Amplitudes normales del cabeceo
    LIFT_AMP = 30.0
    ELBOW_AMP = 25.0
    WRIST_AMP = 15.0

    # Posición media
    LIFT_BASE = -40.0
    ELBOW_BASE = 50.0
    WRIST_BASE = -20.0

    step_period = 1.0 / RATE_HZ
    total_steps = int(TOTAL_DURATION * RATE_HZ)

    print(f'\n  ♪ Iniciando coreografía... ♪\n')
    t_start = time.perf_counter()

    try:
        for step in range(total_steps + 1):
            t = step * step_period
            beat_phase = 2.0 * math.pi * t / BEAT_PERIOD

            # --- Giro en Z: ida y vuelta cada ROTATION_PERIOD ---
            pan_mod = (t / ROTATION_PERIOD * 600.0) % 600.0
            if pan_mod <= 300.0:
                pan = -150.0 + pan_mod
            else:
                pan = 150.0 - (pan_mod - 300.0)

            if t >= VIGOROUS_START:
                # === VIGOROSO: todo el cuerpo baila ===
                # Giro más rápido (sacudida lateral)
                shake = 40.0 * math.sin(beat_phase * 2.0)
                pan = pan + shake

                # Cabeceo normal pero con cuerpo moviéndose
                lift = LIFT_BASE + LIFT_AMP * math.sin(beat_phase)
                elbow = ELBOW_BASE + ELBOW_AMP * math.sin(beat_phase)
                # Wrist se mueve con frecuencia doble (temblor)
                wrist = WRIST_BASE + WRIST_AMP * math.sin(beat_phase * 2.0)
                # Pinza se agita rápido
                gripper = 9.0 + 9.0 * math.sin(beat_phase * 3.0)
            else:
                # === NORMAL: cabeceo + giro suave ===
                lift = LIFT_BASE + LIFT_AMP * math.sin(beat_phase)
                elbow = ELBOW_BASE + ELBOW_AMP * math.sin(beat_phase)
                wrist = WRIST_BASE + WRIST_AMP * math.sin(beat_phase + math.pi)
                gripper = 9.0 + 9.0 * math.sin(math.pi * t / 2.0)

            # Limitar
            pan = max(-150.0, min(150.0, pan))
            lift = max(-120.0, min(120.0, lift))
            elbow = max(-139.0, min(139.0, elbow))
            wrist = max(-98.0, min(103.0, wrist))
            gripper = max(0.0, min(18.0, gripper))

            # Publicar
            msg = JointState()
            msg.header.stamp = node.get_clock().now().to_msg()
            msg.name = list(JOINT_NAMES)
            msg.position = [
                math.radians(pan),
                math.radians(lift),
                math.radians(elbow),
                math.radians(wrist),
                gripper / 1000.0,
            ]
            node.command_publisher.publish(msg)
            rclpy.spin_once(node, timeout_sec=0.0)

            # Log solo en momentos clave
            if step == 0:
                print('  ♪ Bailando...')
            elif abs(t - VIGOROUS_START) < step_period:
                print(f'  [{t:.0f}s] 🔥 ¡Todo el cuerpo baila!')

            time.sleep(step_period)

        # Finalizar en HOME
        print(f'  [{TOTAL_DURATION:.0f}s] Regresando a HOME...')
        node.move_all_home_smooth(duration=1.5)

        t_total = time.perf_counter() - t_start
        print(f'\n  ♪ ¡Coreografía completada! ({t_total:.1f}s) ♪')

    except KeyboardInterrupt:
        print('\n\n  ⏹ Coreografía detenida.')
        print('  Enviando a HOME...')
        node.move_all_home_smooth(duration=1.0)


def main(args=None) -> None:
    """Punto de entrada principal del programa."""
    rclpy.init(args=args)
    node = JointPositionDemo()

    try:
        print('\n  Inicializando: enviando todas las articulaciones a HOME...')
        node.move_all_home_smooth(duration=1.0)
        time.sleep(0.5)

        while rclpy.ok():
            print_menu()
            try:
                opcion = input('  Opción: ').strip()
            except EOFError:
                break

            if opcion == '0':
                print('\n  Enviando a HOME antes de salir...')
                node.move_all_home_smooth()
                time.sleep(0.5)
                print('  ¡Hasta luego!')
                break
            elif opcion == '1':
                run_joint_demo(node, 'arm_shoulder_pan_joint')
            elif opcion == '2':
                run_joint_demo(node, 'arm_shoulder_lift_joint')
            elif opcion == '3':
                run_joint_demo(node, 'arm_elbow_flex_joint')
            elif opcion == '4':
                run_joint_demo(node, 'arm_wrist_flex_joint')
            elif opcion == '5':
                run_joint_demo(node, 'gripper_finger1_joint')
            elif opcion == '6':
                run_full_demo(node)
            elif opcion == '7':
                manual_position(node)
            elif opcion == '8':
                node.move_all_home_smooth()
                print('  ✓ Todas las articulaciones enviadas a HOME.')
                time.sleep(0.5)
            elif opcion == '9':
                vector_position(node)
            elif opcion == '10':
                interpolation_trajectory(node)
            elif opcion == '11':
                sinusoidal_trajectory(node)
            elif opcion == '12':
                inverse_kinematics(node)
            elif opcion == '13':
                forward_kinematics(node)
            elif opcion == '14':
                teach_poses(node)
            elif opcion == '15':
                draw_figure(node)
            elif opcion == '16':
                choreography(node)
            else:
                print('  ✗ Opción no válida. Intente de nuevo.')

    except KeyboardInterrupt:
        print('\n\n  Interrupción detectada. Enviando a HOME...')
        node.move_all_home_smooth(duration=1.0)
        time.sleep(0.5)
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
