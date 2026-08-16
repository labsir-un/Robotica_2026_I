#!/usr/bin/env python3
import json
import math
import os
import signal
import time

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

DEG = math.pi / 180.0

JOINT_NAMES = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']
JOINT_LABELS = ['Base', 'Hombro', 'Codo', 'Muñeca', 'Pinza']

OUTPUT_DIR = os.path.expanduser('~/ros2_jazzy/phantom_ws/interpolation_results')

CONFIG_A = {'waist': 0, 'shoulder': 0, 'elbow': 0, 'wrist': 0, 'gripper': 0}
CONFIG_B = {'waist': 85, 'shoulder': -20, 'elbow': 55, 'wrist': 25, 'gripper': 0}

FREQ = 50
TOTAL_TIME = 3.0

class InterpolationNode(Node):
    def __init__(self):
        super().__init__('interpolation')
        self.cmd_pub = self.create_publisher(JointState, '/pincher/command', 10)
        self.get_logger().info('Nodo interpolation iniciado')

    def send(self, positions):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(JOINT_NAMES)
        msg.position = [positions[j] * DEG for j in JOINT_NAMES]
        self.cmd_pub.publish(msg)

    def wait_key(self):
        try:
            input('  Presiona Enter para continuar...')
        except (EOFError, KeyboardInterrupt):
            pass

def linear_traj(q0, qf, n):
    t = np.linspace(0, 1, n)
    q = np.zeros((n, len(q0)))
    for i in range(len(q0)):
        q[:, i] = q0[i] + (qf[i] - q0[i]) * t
    return q

def cubic_traj(q0, qf, n):
    t = np.linspace(0, 1, n)
    q = np.zeros((n, len(q0)))
    for i in range(len(q0)):
        q[:, i] = q0[i] + (qf[i] - q0[i]) * (3 * t**2 - 2 * t**3)
    return q

def compute_vel_acc(q, dt):
    vel = np.gradient(q, dt, axis=0)
    acc = np.gradient(vel, dt, axis=0)
    return vel, acc

def plot_results(t, q_lin, q_cub, vel_lin, vel_cub, acc_lin, acc_cub, output_dir, config_name):
    os.makedirs(output_dir, exist_ok=True)

    n_joints = len(JOINT_NAMES)
    fig, axes = plt.subplots(n_joints, 3, figsize=(14, 2.5 * n_joints))
    fig.suptitle(f'Interpolación — {config_name}', fontweight='bold', fontsize=13)

    for i in range(n_joints):
        ax_pos = axes[i, 0]
        ax_vel = axes[i, 1]
        ax_acc = axes[i, 2]

        ax_pos.plot(t, q_lin[:, i], '--', color='#2b6cb0', linewidth=1.5, label='Lineal')
        ax_pos.plot(t, q_cub[:, i], '-', color='#e53e3e', linewidth=1.5, label='Cúbica')
        ax_pos.set_ylabel(f'{JOINT_LABELS[i]} (°)')
        ax_pos.legend(fontsize=7)
        ax_pos.grid(True, alpha=0.3)

        ax_vel.plot(t, vel_lin[:, i], '--', color='#2b6cb0', linewidth=1.5, label='Lineal')
        ax_vel.plot(t, vel_cub[:, i], '-', color='#e53e3e', linewidth=1.5, label='Cúbica')
        ax_vel.set_ylabel(f'Vel (°/s)')
        ax_vel.legend(fontsize=7)
        ax_vel.grid(True, alpha=0.3)

        ax_acc.plot(t, acc_lin[:, i], '--', color='#2b6cb0', linewidth=1.5, label='Lineal')
        ax_acc.plot(t, acc_cub[:, i], '-', color='#e53e3e', linewidth=1.5, label='Cúbica')
        ax_acc.set_ylabel(f'Ac (°/s²)')
        ax_acc.legend(fontsize=7)
        ax_acc.grid(True, alpha=0.3)

        if i == n_joints - 1:
            ax_pos.set_xlabel('Tiempo (s)')
            ax_vel.set_xlabel('Tiempo (s)')
            ax_acc.set_xlabel('Tiempo (s)')

    plt.tight_layout()
    path = os.path.join(output_dir, f'interpolacion_{config_name.lower().replace(" ", "_")}.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  📊 Gráfica guardada: {path}')

def main():
    rclpy.init()
    node = InterpolationNode()
    running = True

    def shutdown(sig, frame):
        nonlocal running
        running = False
    signal.signal(signal.SIGINT, shutdown)

    print(f'\n  ╔══════════════════════════════════════════════╗')
    print(f'  ║   Actividad 9 — Interpolación de Trayectorias ║')
    print(f'  ╚══════════════════════════════════════════════╝')
    print(f'')

    q0 = np.array([CONFIG_A[j] for j in JOINT_NAMES])
    qf = np.array([CONFIG_B[j] for j in JOINT_NAMES])
    n = int(FREQ * TOTAL_TIME)
    dt = 1.0 / FREQ
    t = np.linspace(0, TOTAL_TIME, n)

    print(f'  Configuración A (inicio):')
    for j, v in zip(JOINT_LABELS, q0):
        print(f'    {j:10s}: {v:+.0f}°')
    print(f'  Configuración B (final):')
    for j, v in zip(JOINT_LABELS, qf):
        print(f'    {j:10s}: {v:+.0f}°')
    print(f'  Duración: {TOTAL_TIME} s  |  Frecuencia: {FREQ} Hz  |  Puntos: {n}')
    print(f'')

    q_lin = linear_traj(q0, qf, n)
    q_cub = cubic_traj(q0, qf, n)
    vel_lin, acc_lin = compute_vel_acc(q_lin, dt)
    vel_cub, acc_cub = compute_vel_acc(q_cub, dt)

    print(f'  ─── Interpolación Lineal ───')
    print(f'  Velocidad máxima: {np.max(np.abs(vel_lin)):.1f} °/s')
    print(f'  Aceleración máxima: {np.max(np.abs(acc_lin)):.1f} °/s²')
    print(f'  Jerk máximo: {np.max(np.abs(np.gradient(acc_lin, dt, axis=0))):.1f} °/s³')
    print(f'')

    print(f'  ─── Interpolación Cúbica ───')
    print(f'  Velocidad máxima: {np.max(np.abs(vel_cub)):.1f} °/s')
    print(f'  Aceleración máxima: {np.max(np.abs(acc_cub)):.1f} °/s²')
    print(f'  Jerk máximo: {np.max(np.abs(np.gradient(acc_cub, dt, axis=0))):.1f} °/s³')
    print(f'')

    choice = input('  ¿Ejecutar en el robot? [s/N]: ').strip().lower()
    if choice == 's' and running:
        print(f'\n  Enviando trayectoria LINEAL...')
        for i in range(n):
            if not running:
                break
            pos = {name: float(q_lin[i, idx]) for idx, name in enumerate(JOINT_NAMES)}
            node.send(pos)
            time.sleep(dt)
        print(f'  Trayectoria lineal completada.')
        node.wait_key()

        print(f'\n  Enviando trayectoria CÚBICA...')
        for i in range(n):
            if not running:
                break
            pos = {name: float(q_cub[i, idx]) for idx, name in enumerate(JOINT_NAMES)}
            node.send(pos)
            time.sleep(dt)
        print(f'  Trayectoria cúbica completada.')

    plot_results(t, q_lin, q_cub, vel_lin, vel_cub, acc_lin, acc_cub,
                 OUTPUT_DIR, 'Config A a B')

    print(f'\n  Resultados guardados en: {OUTPUT_DIR}')
    print(f'  Gráfica: interpolacion_config_a_a_b.png')
    print(f'')

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
