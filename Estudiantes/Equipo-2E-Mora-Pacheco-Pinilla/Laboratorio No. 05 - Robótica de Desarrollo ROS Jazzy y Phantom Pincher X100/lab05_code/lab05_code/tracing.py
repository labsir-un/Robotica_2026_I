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

L0 = 0.089
L1 = 0.101
L2 = 0.101
L3 = 0.119

JOINT_LIMITS_DEG = {
    'waist': (-150, 150),
    'shoulder': (-150, 150),
    'elbow': (-150, 150),
    'wrist': (-150, 150),
    'gripper': (-90, 90),
}

OUTPUT_DIR = os.path.expanduser('~/ros2_jazzy/phantom_ws/tracing_results')

state_lock = threading.Lock()
current_state = {j: 0.0 for j in JOINT_NAMES}


class TracingNode(Node):
    def __init__(self):
        super().__init__('tracing')
        self.cmd_pub = self.create_publisher(JointState, '/pincher/command', 10)
        self.state_sub = self.create_subscription(JointState, '/joint_states', self.state_cb, 10)

    def state_cb(self, msg):
        with state_lock:
            for n, p in zip(msg.name, msg.position):
                current_state[n] = p

    def send(self, positions_deg):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(JOINT_NAMES)
        msg.position = [positions_deg[j] * DEG for j in JOINT_NAMES]
        self.cmd_pub.publish(msg)


def dh_transform(alpha, a, d, theta):
    ct = math.cos(theta)
    st = math.sin(theta)
    ca = math.cos(alpha)
    sa = math.sin(alpha)
    return np.array([
        [ct, -st, 0, a],
        [st*ca, ct*ca, -sa, -d*sa],
        [st*sa, ct*sa, ca, d*ca],
        [0, 0, 0, 1],
    ])


def fk(q_deg):
    q = [math.radians(v) for v in q_deg[:4]]
    T = np.eye(4)
    params = [
        (0, 0, L0, q[0]),
        (-math.pi/2, 0, 0, q[1]),
        (0, L1, 0, q[2]),
        (0, L2, 0, q[3]),
        (0, L3, 0, 0),
    ]
    for alpha, a, d, theta in params:
        T = T @ dh_transform(alpha, a, d, theta)
    return T[0, 3], T[1, 3], T[2, 3]


def ik(x, y, z, elbow_up=False):
    q1 = math.degrees(math.atan2(y, x))
    r = math.sqrt(x*x + y*y)
    z_eff = L0 + L3 - z
    d_sq = r*r + z_eff*z_eff
    max_reach = L1 + L2
    if d_sq > max_reach * max_reach:
        return None
    d = math.sqrt(d_sq)
    cos_q3 = (d*d - L1*L1 - L2*L2) / (2 * L1 * L2)
    cos_q3 = max(-1.0, min(1.0, cos_q3))
    q3 = math.degrees(math.acos(cos_q3))
    if elbow_up:
        q3 = -q3
    alpha = math.atan2(L2 * math.sin(math.radians(q3)), L1 + L2 * math.cos(math.radians(q3)))
    q2 = math.degrees(math.atan2(z_eff, r) - alpha)
    q4 = -90 - q2 - q3
    result = [q1, q2, q3, q4, 0.0]
    limits = [JOINT_LIMITS_DEG[j] for j in JOINT_NAMES]
    for i in range(5):
        if result[i] < limits[i][0] or result[i] > limits[i][1]:
            return None
    return result


def generate_shape(shape, size=0.05, center_dist=0.14, center_z=0.10, n_pts_per_edge=30):
    if shape == 'triangle':
        h = size * math.sqrt(3) / 2
        verts = [
            (0, h/3),
            (-size/2, -h/3 + h/2),
            (size/2, -h/3 + h/2),
        ]
    elif shape == 'square':
        verts = [
            (-size/2, -size/2),
            (size/2, -size/2),
            (size/2, size/2),
            (-size/2, size/2),
        ]
    else:
        return []
    points = []
    nv = len(verts)
    for i in range(nv):
        y0, z0 = verts[i]
        y1, z1 = verts[(i + 1) % nv]
        last = (i == nv - 1)
        limit = n_pts_per_edge if last else n_pts_per_edge - 1
        for j in range(limit + 1):
            frac = j / n_pts_per_edge
            wy = y0 + (y1 - y0) * frac
            wz = center_z + z0 + (z1 - z0) * frac
            points.append((center_dist, wy, wz))
    return points


def trace_shape(node, shape, size, center_dist, center_z, use_hw, running):
    desired_path = generate_shape(shape, size, center_dist, center_z)
    if not desired_path:
        return None, None, None

    q_prev = None
    actual_path = []
    joint_traj = []

    for pt in desired_path:
        if not running:
            break
        wx, wy, wz = pt
        q = ik(wx, wy, wz, elbow_up=True)
        if q is None:
            q = ik(wx, wy, wz, elbow_up=False)
        if q is None:
            continue
        clamped = {}
        valid = True
        for j, name in enumerate(JOINT_NAMES):
            lim = JOINT_LIMITS_DEG[name]
            v = max(lim[0], min(lim[1], q[j]))
            clamped[name] = v
            if abs(v - q[j]) > 0.5:
                valid = False
        if not valid:
            continue
        if q_prev is not None:
            max_step = 15.0
            for name in JOINT_NAMES:
                diff = clamped[name] - q_prev[name]
                if abs(diff) > max_step:
                    n_interp = int(abs(diff) / max_step) + 1
                    for k in range(1, n_interp + 1):
                        frac = k / n_interp
                        interp = {n: q_prev[n] + (clamped[n] - q_prev[n]) * frac for n in JOINT_NAMES}
                        if use_hw:
                            node.send(interp)
                            time.sleep(0.04)
                        joint_traj.append(interp)
                        fx, fy, fz = fk([interp[n] for n in JOINT_NAMES])
                        actual_path.append((fy, fz))
                    q_prev = clamped
                    continue
        if use_hw:
            node.send(clamped)
            time.sleep(0.04)
        joint_traj.append(clamped)
        fx, fy, fz = fk([clamped[n] for n in JOINT_NAMES])
        actual_path.append((fy, fz))
        q_prev = clamped

    desired_2d = [(p[1], p[2]) for p in desired_path]
    return desired_2d, actual_path, joint_traj


def compute_error(desired, actual):
    n = min(len(desired), len(actual))
    if n == 0:
        return 0, 0
    errors = []
    for i in range(n):
        dy = desired[i][0] - actual[i][0]
        dz = desired[i][1] - actual[i][1]
        errors.append(math.sqrt(dy*dy + dz*dz))
    return max(errors), math.sqrt(sum(e*e for e in errors) / len(errors))


def plot_results(desired, actual, shape, size, output_dir, max_err, rmse):
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.suptitle(f'Trazado — {shape.capitalize()} ({size*100:.0f} cm)', fontweight='bold', fontsize=13)

    if desired:
        dy = [p[0] for p in desired]
        dz = [p[1] for p in desired]
        ax.plot(dy, dz, '-', color='#2b6cb0', linewidth=1.5, label='Deseada', zorder=3)

    if actual:
        ay = [p[0] for p in actual]
        az = [p[1] for p in actual]
        ax.plot(ay, az, '--', color='#e53e3e', linewidth=1.0, alpha=0.7, label='Real (FK)', zorder=2)

    ax.set_xlabel('Y (m)')
    ax.set_ylabel('Z (m)')
    ax.set_title(f'Error máx: {max_err*1000:.1f} mm | RMSE: {rmse*1000:.1f} mm')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')

    plt.tight_layout()
    path = os.path.join(output_dir, f'trazado_{shape}.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  Gráfica guardada: {path}')


def save_results(results, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, 'trazado_resultados.json')
    with open(path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f'  Datos guardados: {path}')


def main():
    rclpy.init()
    node = TracingNode()
    running = True

    def shutdown(sig, frame):
        nonlocal running
        running = False
    signal.signal(signal.SIGINT, shutdown)

    spin_thread = threading.Thread(target=lambda: rclpy.spin(node), daemon=True)
    spin_thread.start()

    print()
    print('  ╔══════════════════════════════════════════════╗')
    print('  ║   Actividad 14 — Trazado de una Figura       ║')
    print('  ╚══════════════════════════════════════════════╝')
    print()
    print(f'  Dimensiones del robot:')
    print(f'    L₀ (base)   = {L0*1000:.0f} mm')
    print(f'    L₁ (brazo)  = {L1*1000:.0f} mm')
    print(f'    L₂ (antebrazo) = {L2*1000:.0f} mm')
    print(f'    L₃ (muñeca) = {L3*1000:.0f} mm')
    print()

    shapes = ['triangle', 'square']
    sizes = [0.04, 0.06]
    center_dist = 0.13
    center_z = 0.10

    choice = input('  ¿Ejecutar en el robot (con hardware)? [s/N]: ').strip().lower()
    use_hw = (choice == 's' and running)

    all_results = []
    for shape in shapes:
        for size in sizes:
            if not running:
                break
            print(f'\n  ─── {shape.capitalize()} ({size*100:.0f} cm) ───')
            desired, actual, traj = trace_shape(node, shape, size, center_dist, center_z, use_hw, running)
            if desired and actual:
                max_err, rmse = compute_error(desired, actual)
                all_results.append({
                    'shape': shape,
                    'size_cm': round(size * 100, 1),
                    'n_waypoints': len(desired),
                    'max_error_mm': round(max_err * 1000, 2),
                    'rmse_mm': round(rmse * 1000, 2),
                })
                print(f'  Puntos deseados: {len(desired)}')
                print(f'  Puntos reales:   {len(actual)}')
                print(f'  Error máximo:    {max_err*1000:.2f} mm')
                print(f'  RMSE:            {rmse*1000:.2f} mm')
                plot_results(desired, actual, shape, size, OUTPUT_DIR, max_err, rmse)
            else:
                print(f'  No se pudo trazar (puntos fuera de alcance)')
            if not use_hw:
                time.sleep(0.5)

    if all_results:
        save_results(all_results, OUTPUT_DIR)
        print(f'\n  Resumen:')
        print(f'  {"Figura":15s} {"Tamaño":8s} {"Puntos":8s} {"Error máx":12s} {"RMSE":10s}')
        print(f'  {"-"*53}')
        for r in all_results:
            print(f'  {r["shape"]:15s} {r["size_cm"]:>4.0f} cm  {r["n_waypoints"]:>4d}     {r["max_error_mm"]:>7.2f} mm  {r["rmse_mm"]:>7.2f} mm')

    node.destroy_node()
    rclpy.shutdown()
    print(f'\n  Resultados en: {OUTPUT_DIR}')
    print()


if __name__ == '__main__':
    main()
