#!/usr/bin/env python3
import math
import os
import sys
import threading
import time
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import UInt32

# Safe software limits
JOINT_LIMITS_DEG = {
    'waist': (-140.0, 139.0),
    'shoulder': (-106.0, 64.0),
    'elbow': (-131.0, 137.0),
    'wrist': (-93.0, 93.0),
    'gripper': (-110.0, 110.0),
}

def get_workspace_dir() -> str:
    prefix = os.environ.get('COLCON_PREFIX_PATH', '')
    if not prefix:
        prefix = os.environ.get('AMENT_PREFIX_PATH', '')
    if prefix:
        first_prefix = prefix.split(os.pathsep)[0]
        return os.path.abspath(os.path.join(first_prefix, '..'))
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(script_dir, '..', '..', '..'))

JOINT_TRANSLATIONS = {
    'waist': 'Base (waist)',
    'shoulder': 'Hombro (shoulder)',
    'elbow': 'Codo (elbow)',
    'wrist': 'Muñeca (wrist)',
    'gripper': 'Pinza (gripper)',
}

# Start and end configurations (in degrees)
CONFIG_A = [-60.0, -45.0, 45.0, -30.0, 0.0]
CONFIG_B = [60.0, 30.0, -30.0, 30.0, 0.0]

class TrajectoryInterpolatorNode(Node):
    """ROS 2 Node that handles sending commands and setting speed limits."""
    def __init__(self) -> None:
        super().__init__('trajectory_interpolator')
        self.publisher = self.create_publisher(JointState, '/pincher/command', 10)
        self.speed_publisher = self.create_publisher(UInt32, '/pincher/profile_velocity', 10)

    def send_simultaneous_command(self, positions_deg: List[float]) -> None:
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']
        msg.position = [math.radians(val) for val in positions_deg]
        self.publisher.publish(msg)

    def set_speed(self, speed_val: int) -> None:
        msg = UInt32()
        msg.data = int(speed_val)
        self.speed_publisher.publish(msg)

def spin_thread_target(node: Node) -> None:
    try:
        rclpy.spin(node)
    except Exception:
        pass

def save_plots(time_steps: List[float], positions_data: Dict[str, List[float]], 
               velocities_data: Dict[str, List[float]], method_name: str, filename: str) -> None:
    """Generates and saves position and velocity plots using Matplotlib."""
    results_dir = os.path.join(get_workspace_dir(), 'results', 'interpolacion')
    os.makedirs(results_dir, exist_ok=True)
    filepath = os.path.join(results_dir, filename)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    # Position plot
    for joint, positions in positions_data.items():
        label = JOINT_TRANSLATIONS[joint]
        ax1.plot(time_steps, positions, label=label, linewidth=2)
    ax1.set_ylabel('Posición Angular (grados)')
    ax1.set_title(f'Trayectoria - Interpolación {method_name}')
    ax1.grid(True)
    ax1.legend(loc='upper right')
    
    # Velocity plot
    for joint, velocities in velocities_data.items():
        label = JOINT_TRANSLATIONS[joint]
        ax2.plot(time_steps, velocities, label=label, linewidth=2)
    ax2.set_xlabel('Tiempo (segundos)')
    ax2.set_ylabel('Velocidad Angular (grados/s)')
    ax2.grid(True)
    ax2.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close()
    print(f"[Graficado] Gráfica guardada en: {filepath}")

def run_linear_interpolation(node: TrajectoryInterpolatorNode, duration: float = 5.0, freq: float = 50.0) -> None:
    print("\n--- INICIANDO INTERPOLACIÓN LINEAL ---")
    print("Moviendo primero a la Configuración A (Inicio)...")
    node.send_simultaneous_command(CONFIG_A)
    time.sleep(4.0)

    print("Iniciando trayectoria lineal hacia Configuración B...")
    steps = int(duration * freq)
    dt = 1.0 / freq
    time_steps = []
    positions_history = {joint: [] for joint in JOINT_LIMITS_DEG.keys()}
    velocities_history = {joint: [] for joint in JOINT_LIMITS_DEG.keys()}
    
    joints_list = list(JOINT_LIMITS_DEG.keys())

    # Velocities for linear interpolation are constant
    const_vels = [(CONFIG_B[i] - CONFIG_A[i]) / duration for i in range(5)]

    start_time = time.time()
    for step in range(steps + 1):
        t = step * dt
        time_steps.append(t)
        
        # Calculate current position
        curr_pos = []
        for i, joint in enumerate(joints_list):
            q = CONFIG_A[i] + (t / duration) * (CONFIG_B[i] - CONFIG_A[i])
            curr_pos.append(q)
            positions_history[joint].append(q)
            
            # Velocity is const_vels, but 0 at the exact start and end boundaries
            if step == 0 or step == steps:
                velocities_history[joint].append(0.0)
            else:
                velocities_history[joint].append(const_vels[i])

        node.send_simultaneous_command(curr_pos)
        
        # Non-blocking exact time sleeping
        elapsed = time.time() - start_time
        sleep_time = (step + 1) * dt - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

    print("Trayectoria lineal finalizada.")
    save_plots(time_steps, positions_history, velocities_history, 'Lineal', 'interpolacion_lineal.png')

def run_cubic_interpolation(node: TrajectoryInterpolatorNode, duration: float = 5.0, freq: float = 50.0) -> None:
    print("\n--- INICIANDO INTERPOLACIÓN CÚBICA ---")
    print("Moviendo primero a la Configuración A (Inicio)...")
    node.send_simultaneous_command(CONFIG_A)
    time.sleep(4.0)

    print("Iniciando trayectoria cúbica hacia Configuración B...")
    steps = int(duration * freq)
    dt = 1.0 / freq
    time_steps = []
    positions_history = {joint: [] for joint in JOINT_LIMITS_DEG.keys()}
    velocities_history = {joint: [] for joint in JOINT_LIMITS_DEG.keys()}
    
    joints_list = list(JOINT_LIMITS_DEG.keys())

    start_time = time.time()
    for step in range(steps + 1):
        t = step * dt
        time_steps.append(t)
        
        # Normalized time
        tau = t / duration
        # Normalized cubic profile: s(t) = 3*tau^2 - 2*tau^3
        s = 3.0 * (tau ** 2) - 2.0 * (tau ** 3)
        # Derivative of s(t) with respect to t: ds/dt = (6*tau - 6*tau^2) / duration
        ds_dt = (6.0 * tau - 6.0 * (tau ** 2)) / duration
        
        curr_pos = []
        for i, joint in enumerate(joints_list):
            # Cubic position
            q = CONFIG_A[i] + s * (CONFIG_B[i] - CONFIG_A[i])
            curr_pos.append(q)
            positions_history[joint].append(q)
            
            # Cubic velocity
            v = ds_dt * (CONFIG_B[i] - CONFIG_A[i])
            velocities_history[joint].append(v)

        node.send_simultaneous_command(curr_pos)
        
        # Non-blocking exact time sleeping
        elapsed = time.time() - start_time
        sleep_time = (step + 1) * dt - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

    print("Trayectoria cúbica finalizada.")
    save_plots(time_steps, positions_history, velocities_history, 'Cúbica (Spline)', 'interpolacion_cubica.png')

def generate_comparison_plot() -> None:
    """Generates a comparison overlay plot of the first joint (Base) to highlight the difference in smoothness."""
    results_dir = os.path.join(get_workspace_dir(), 'results', 'interpolacion')
    os.makedirs(results_dir, exist_ok=True)
    filepath = os.path.join(results_dir, 'comparativa_interpolacion.png')
    
    T = 5.0
    time_steps = np.linspace(0, T, 200)
    
    # Calculate positions
    pos_start, pos_end = CONFIG_A[0], CONFIG_B[0]
    
    # Linear
    pos_lin = pos_start + (time_steps / T) * (pos_end - pos_start)
    vel_lin = np.full_like(time_steps, (pos_end - pos_start) / T)
    vel_lin[0], vel_lin[-1] = 0.0, 0.0 # boundaries
    
    # Cubic
    tau = time_steps / T
    s = 3.0 * (tau ** 2) - 2.0 * (tau ** 3)
    pos_cub = pos_start + s * (pos_end - pos_start)
    ds_dt = (6.0 * tau - 6.0 * (tau ** 2)) / T
    vel_cub = ds_dt * (pos_end - pos_start)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    # Position compare
    ax1.plot(time_steps, pos_lin, 'r--', label='Lineal (Discontinua)', linewidth=2.5)
    ax1.plot(time_steps, pos_cub, 'b-', label='Cúbica (Suave)', linewidth=2.5)
    ax1.set_ylabel('Posición Angular (grados)')
    ax1.set_title('Comparativa de Suavidad: Trayectoria Lineal vs. Cúbica (Base)')
    ax1.grid(True)
    ax1.legend(loc='upper left')
    
    # Velocity compare
    ax2.plot(time_steps, vel_lin, 'r--', label='Lineal (Impactos de Aceleración en t=0 y t=5)', linewidth=2.5)
    ax2.plot(time_steps, vel_cub, 'b-', label='Cúbica (Perfil Suave/Continuo)', linewidth=2.5)
    ax2.set_xlabel('Tiempo (segundos)')
    ax2.set_ylabel('Velocidad Angular (grados/s)')
    ax2.grid(True)
    ax2.legend(loc='upper left')
    
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close()
    print(f"[Graficado] Gráfica comparativa guardada en: {filepath}")

def print_menu() -> None:
    print("\n" + "=" * 60)
    print("     PhantomX Pincher X100 - INTERPOLACIÓN DE TRAYECTORIAS")
    print("=" * 60)
    print("1. Ejecutar Interpolación Lineal (A -> B)")
    print("2. Ejecutar Interpolación Cúbica (A -> B)")
    print("3. Generar Gráfica Comparativa Directa")
    print("4. Regresar a Home (0°)")
    print("5. Salir")
    print("-" * 60)

def main(args=None) -> None:
    rclpy.init(args=args)
    node = TrajectoryInterpolatorNode()

    # Start spin thread
    spin_thread = threading.Thread(target=spin_thread_target, args=(node,), daemon=True)
    spin_thread.start()

    # Set moving speed to 30% on start for safety
    print("Configurando velocidad inicial del bus al 30%...")
    node.set_speed(30)
    time.sleep(0.5)

    try:
        while True:
            print_menu()
            choice = input("Seleccione una opción (1-5): ").strip()
            if choice == '1':
                run_linear_interpolation(node)
            elif choice == '2':
                run_cubic_interpolation(node)
            elif choice == '3':
                generate_comparison_plot()
            elif choice == '4':
                print("\nEnviando comando HOME a todas las articulaciones...")
                node.send_simultaneous_command([0.0, 0.0, 0.0, 0.0, 0.0])
                time.sleep(3.0)
                print("Comando HOME enviado.")
            elif choice == '5':
                print("\nSaliendo...")
                break
            else:
                print("[Error] Opción no válida. Intente de nuevo.")
    except KeyboardInterrupt:
        print("\nSaliendo por interrupción de teclado...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
