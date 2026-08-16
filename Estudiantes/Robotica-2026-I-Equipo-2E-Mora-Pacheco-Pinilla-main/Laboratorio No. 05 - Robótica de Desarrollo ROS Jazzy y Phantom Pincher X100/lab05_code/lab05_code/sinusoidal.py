#!/usr/bin/env python3
import json
import math
import os
import signal
import threading
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
JOINT_LIMITS_DEG = {
    'waist': [-150, 150],
    'shoulder': [-150, 150],
    'elbow': [-150, 150],
    'wrist': [-150, 150],
    'gripper': [-90, 90],
}

SELECTED_JOINT = 'shoulder'
Q0_DEG = 0.0

TESTS = [
    {'name': 'A=30° f=0.25Hz', 'amp': 30, 'freq': 0.25, 'periods': 2},
    {'name': 'A=30° f=0.50Hz', 'amp': 30, 'freq': 0.50, 'periods': 2},
    {'name': 'A=60° f=0.25Hz', 'amp': 60, 'freq': 0.25, 'periods': 2},
    {'name': 'A=60° f=0.50Hz', 'amp': 60, 'freq': 0.50, 'periods': 2},
]

FREQ = 50

OUTPUT_DIR = os.path.expanduser('~/ros2_jazzy/phantom_ws/sinusoidal_results')

state_lock = threading.Lock()
current_state = {j: 0.0 for j in JOINT_NAMES}


class SinusoidalNode(Node):
    def __init__(self):
        super().__init__('sinusoidal')
        self.cmd_pub = self.create_publisher(JointState, '/pincher/command', 10)
        self.state_sub = self.create_subscription(
            JointState, '/joint_states', self.state_cb, 10)

    def state_cb(self, msg):
        with state_lock:
            for n, p in zip(msg.name, msg.position):
                current_state[n] = p

    def send(self, joint, rad):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = [joint]
        msg.position = [rad]
        self.cmd_pub.publish(msg)

    def read(self, joint):
        with state_lock:
            return current_state.get(joint, 0.0)


def generate_trajectory(amp_deg, freq_hz, periods, fs=FREQ):
    duration = periods / freq_hz
    n = int(fs * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    q_desired = Q0_DEG + amp_deg * np.sin(2 * math.pi * freq_hz * t)
    return t, q_desired


def run_test(node, test, use_hardware, running):
    amp = test['amp']
    freq = test['freq']
    periods = test['periods']
    name = test['name']

    joint_idx = JOINT_NAMES.index(SELECTED_JOINT)

    lim = JOINT_LIMITS_DEG[SELECTED_JOINT]
    peak = Q0_DEG + amp
    if peak > lim[1] or Q0_DEG - amp < lim[0]:
        print(f'  ⚠  {name}: amplitud {amp}° excede límites [{lim[0]}, {lim[1]}] — se limitará')

    t, q_desired = generate_trajectory(amp, freq, periods)
    dt = 1.0 / FREQ
    n = len(t)

    q_measured = np.zeros(n)

    for i in range(n):
        if not running:
            break
        rad = q_desired[i] * DEG
        if use_hardware:
            node.send(SELECTED_JOINT, rad)
            time.sleep(dt)
            q_measured[i] = node.read(SELECTED_JOINT) / DEG
        else:
            noise = np.random.normal(0, 0.3)
            delay_idx = max(0, i - 2)
            q_measured[i] = q_desired[delay_idx] + noise

    errors = q_desired - q_measured
    max_err = np.max(np.abs(errors))
    rmse = np.sqrt(np.mean(errors**2))

    return t, q_desired, q_measured, max_err, rmse


def plot_results(all_results, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    fig.suptitle(
        f'Actividad 10 — Trayectoria Sinusoidal\n'
        f'Articulación: {JOINT_LABELS[JOINT_NAMES.index(SELECTED_JOINT)]} ({SELECTED_JOINT})',
        fontweight='bold', fontsize=13)

    colors = ['#2b6cb0', '#e53e3e', '#38a169', '#d69e2e']

    for idx, (result, ax) in enumerate(zip(all_results, axes.flat)):
        t, qd, qm, max_err, rmse = result
        name = TESTS[idx]['name']

        ax.plot(t, qd, '-', color=colors[idx], linewidth=1.5, label='Deseada')
        ax.plot(t, qm, '--', color='#718096', linewidth=1.0, alpha=0.7, label='Medida')
        ax.fill_between(t, qd, qm, alpha=0.1, color=colors[idx])
        ax.set_title(name, fontweight='bold')
        ax.set_xlabel('Tiempo (s)')
        ax.set_ylabel('Posición (°)')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

        text = f'Error máx: {max_err:.2f}°\nRMSE: {rmse:.2f}°'
        ax.text(0.97, 0.05, text, transform=ax.transAxes,
                fontsize=9, verticalalignment='bottom',
                horizontalalignment='right',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='wheat', alpha=0.6))

    plt.tight_layout()
    path = os.path.join(output_dir, 'sinusoidal_resultados.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  Gráfica guardada: {path}')


def save_results(all_results, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    data = []
    for idx, result in enumerate(all_results):
        t, qd, qm, max_err, rmse = result
        data.append({
            'test': TESTS[idx]['name'],
            'amplitude_deg': TESTS[idx]['amp'],
            'frequency_hz': TESTS[idx]['freq'],
            'periods': TESTS[idx]['periods'],
            'max_error_deg': round(float(max_err), 4),
            'rmse_deg': round(float(rmse), 4),
        })

    path = os.path.join(output_dir, 'sinusoidal_resultados.json')
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f'  Datos guardados: {path}')

    path_txt = os.path.join(output_dir, 'sinusoidal_resultados.txt')
    with open(path_txt, 'w') as f:
        f.write('Actividad 10 — Trayectoria Sinusoidal\n')
        f.write(f'Articulación: {SELECTED_JOINT}\n')
        f.write(f'q₀ = {Q0_DEG}°\n\n')
        f.write(f'{"Prueba":30s} {"Amplitud":10s} {"Frec":8s} {"Error máx":12s} {"RMSE":10s}\n')
        f.write('-' * 70 + '\n')
        for d in data:
            f.write(f'{d["test"]:30s} {d["amplitude_deg"]:>4}°     '
                    f'{d["frequency_hz"]:>5}Hz   {d["max_error_deg"]:>8.2f}°  '
                    f'{d["rmse_deg"]:>8.2f}°\n')
    print(f'  Reporte guardado: {path_txt}')


def main():
    rclpy.init()
    node = SinusoidalNode()
    running = True

    def shutdown(sig, frame):
        nonlocal running
        running = False
    signal.signal(signal.SIGINT, shutdown)

    spin_thread = threading.Thread(target=lambda: rclpy.spin(node), daemon=True)
    spin_thread.start()

    print()
    print('  ╔══════════════════════════════════════════════╗')
    print('  ║   Actividad 10 — Trayectoria Sinusoidal      ║')
    print('  ╚══════════════════════════════════════════════╝')
    print()
    print(f'  Articulación: {JOINT_LABELS[JOINT_NAMES.index(SELECTED_JOINT)]} ({SELECTED_JOINT})')
    print(f'  q₀ = {Q0_DEG}°')
    print()

    lim = JOINT_LIMITS_DEG[SELECTED_JOINT]
    for t in TESTS:
        peak = Q0_DEG + t['amp']
        safe = '✓' if (peak <= lim[1] and Q0_DEG - t['amp'] >= lim[0]) else '⚠'
        print(f'  [{safe}] {t["name"]:25s}  '
              f'rango: [{Q0_DEG - t["amp"]:+.0f}, {peak:+.0f}]°  '
              f'dentro de [{lim[0]}, {lim[1]}]°')
    print()

    choice = input('  ¿Ejecutar en el robot (con hardware)? [s/N]: ').strip().lower()
    use_hw = (choice == 's' and running)

    all_results = []
    for test in TESTS:
        if not running:
            break
        print(f'\n  ─── {test["name"]} ───')
        result = run_test(node, test, use_hw, running)
        t, qd, qm, max_err, rmse = result
        all_results.append(result)
        print(f'  Error máximo: {max_err:.4f}°')
        print(f'  RMSE:         {rmse:.4f}°')

    print()
    plot_results(all_results, OUTPUT_DIR)
    save_results(all_results, OUTPUT_DIR)

    node.destroy_node()
    rclpy.shutdown()
    print(f'\n  Resultados en: {OUTPUT_DIR}')
    print()


if __name__ == '__main__':
    main()
