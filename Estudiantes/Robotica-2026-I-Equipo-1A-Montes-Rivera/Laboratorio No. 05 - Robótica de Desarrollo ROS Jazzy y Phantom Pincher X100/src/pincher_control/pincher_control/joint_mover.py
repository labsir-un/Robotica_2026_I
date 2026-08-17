#!/usr/bin/env python3
import math
import os
import sys
import threading
import time
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import UInt32

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

# Distant configurations for trajectory interpolation (Activity 9)
CONFIG_A = [-60.0, -45.0, 45.0, -30.0, 0.0]
CONFIG_B = [60.0, 30.0, -30.0, 30.0, 0.0]

class JointMoverNode(Node):
    """ROS 2 node that handles publishing commands and subscribing to feedback."""
    def __init__(self) -> None:
        super().__init__('joint_mover')
        self.publisher = self.create_publisher(JointState, '/pincher/command', 10)
        self.speed_publisher = self.create_publisher(UInt32, '/pincher/profile_velocity', 10)
        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_states_callback,
            10
        )
        self.current_positions: Dict[str, float] = {}
        self.lock = threading.Lock()

    def joint_states_callback(self, msg: JointState) -> None:
        with self.lock:
            for name, pos in zip(msg.name, msg.position):
                self.current_positions[name] = pos

    def get_joint_position_deg(self, name: str) -> Optional[float]:
        with self.lock:
            rad = self.current_positions.get(name)
            if rad is not None:
                return math.degrees(rad)
            return None

    def send_command(self, name: str, deg: float) -> None:
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = [name]
        msg.position = [math.radians(deg)]
        self.publisher.publish(msg)

    def send_home_command(self) -> None:
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(JOINT_LIMITS_DEG.keys())
        msg.position = [0.0] * len(msg.name)
        self.publisher.publish(msg)

    def send_speed_command(self, speed_val: int) -> None:
        msg = UInt32()
        msg.data = int(speed_val)
        self.speed_publisher.publish(msg)

    def send_simultaneous_command(self, positions_deg: List[float]) -> None:
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']
        msg.position = [math.radians(val) for val in positions_deg]
        self.publisher.publish(msg)

def spin_thread_target(node: Node) -> None:
    try:
        rclpy.spin(node)
    except Exception:
        pass

def print_menu() -> None:
    print("\n" + "=" * 50)
    print("      PhantomX Pincher X100 - CONTROL ARTICULAR")
    print("=" * 50)
    print("1. Control Articular Manual (seleccionar e ingresar ángulo)")
    print("2. Rutina de Movimientos Independientes Automática (3 posiciones c/u)")
    print("3. Rutina de Movimientos Simultáneos (Actividad 7)")
    print("4. Rutina de Movimientos Secuenciales (Actividad 8 - Configuración 4)")
    print("5. Rutina de Interpolación de Trayectorias (Actividad 9 - Lineal y Cúbica)")
    print("6. Rutina de Trayectoria Sinusoidal (Actividad 10 - 4 Pruebas)")
    print("7. Regresar todo al Home / Posición de Referencia (0°)")
    print("8. Mostrar posiciones actuales de los joints")
    print("9. Salir")
    print("-" * 50)

def manual_control(node: JointMoverNode) -> None:
    print("\n--- CONTROL ARTICULAR MANUAL ---")
    joints = list(JOINT_LIMITS_DEG.keys())
    for i, joint in enumerate(joints, 1):
        name_es = JOINT_TRANSLATIONS[joint]
        print(f"{i}. {name_es} ({joint})")
    
    try:
        choice = int(input("\nSeleccione el número de la articulación: "))
        if choice < 1 or choice > len(joints):
            print("[Error] Selección inválida.")
            return
        joint_name = joints[choice - 1]
    except ValueError:
        print("[Error] Debe ingresar un número entero.")
        return

    lower, upper = JOINT_LIMITS_DEG[joint_name]
    print(f"\nArticulación seleccionada: {JOINT_TRANSLATIONS[joint_name]} ({joint_name})")
    print(f"Límites permitidos: {lower}° a {upper}°")
    
    curr = node.get_joint_position_deg(joint_name)
    if curr is not None:
        print(f"Posición actual: {curr:.2f}°")
    else:
        print("Posición actual: Desconocida (esperando JointState)")

    try:
        angle = float(input(f"Ingrese la posición angular deseada en grados ({lower} a {upper}): "))
        if angle < lower or angle > upper:
            print(f"[Error] El ángulo ingresado está fuera de los límites ({lower}° a {upper}°).")
            return
    except ValueError:
        print("[Error] Debe ingresar un número válido.")
        return

    print(f"\nEnviando comando: {joint_name} -> {angle:.2f}°")
    node.send_command(joint_name, angle)
    time.sleep(10.0)

def run_auto_test(node: JointMoverNode) -> None:
    print("\n--- INICIANDO RUTINA DE PRUEBA AUTOMÁTICA ---")
    print("Cada articulación se moverá por 3 posiciones de prueba")
    print("independientes y luego regresará a la referencia (0°).")
    print("=" * 60)

    # 3 positions per joint
    test_positions = {
        'waist': [45.0, -45.0, 90.0],
        'shoulder': [30.0, -30.0, 60.0],
        'elbow': [30.0, -30.0, 60.0],
        'wrist': [30.0, -30.0, 60.0],
        'gripper': [45.0, -45.0, 30.0],
    }

    # Step-by-step sequential execution
    for joint, positions in test_positions.items():
        joint_label = JOINT_TRANSLATIONS[joint]
        print(f"\n>>> Probando articulación: {joint_label} ({joint})...")
        
        for idx, pos in enumerate(positions, 1):
            print(f"  [Posición {idx}/3] Moviendo {joint_label} a {pos:.1f}°...")
            node.send_command(joint, pos)
            time.sleep(10.0) # wait for hardware or simulation to reach the position
            
        print(f"  [Referencia] Retornando {joint_label} a 0.0°...")
        node.send_command(joint, 0.0)
        time.sleep(10.0)

    print("\n============================================================")
    print("¡Rutina de prueba automática finalizada con éxito!")
    print("Todas las articulaciones han retornado a la referencia.")
    print("============================================================")

def run_simultaneous_test(node: JointMoverNode) -> None:
    print("\n--- INICIANDO ACTIVIDAD 7: MOVIMIENTO SIMULTÁNEO ---")
    print("Se ejecutarán 5 configuraciones de movimiento simultáneo.")
    print("=" * 60)

    configs = [
        [0.0, 0.0, 0.0, 0.0, 0.0],
        [25.0, 25.0, 20.0, -20.0, 0.0],
        [-35.0, 35.0, -30.0, 30.0, 0.0],
        [85.0, -20.0, 55.0, 25.0, 0.0],
        [80.0, -35.0, 55.0, -45.0, 0.0],
    ]

    for idx, c in enumerate(configs, 1):
        print(f"\n[Configuración {idx}/5] Enviando simultáneamente: {c}...")
        node.send_simultaneous_command(c)
        time.sleep(5.0)

    print(f"\n[Referencia] Retornando a la posición de reposo (0°)...")
    node.send_simultaneous_command([0.0, 0.0, 0.0, 0.0, 0.0])
    time.sleep(5.0)

    print("\n============================================================")
    print("¡Actividad 7: Movimiento Simultáneo completada con éxito!")
    print("============================================================")

def run_sequential_test(node: JointMoverNode) -> None:
    print("\n--- INICIANDO ACTIVIDAD 8: MOVIMIENTO SECUENCIAL ---")
    print("Se ejecutará la 4ª configuración moviendo cada articulación una por una.")
    print("Orden de movimiento: Base -> Hombro -> Codo -> Muñeca -> Pinza")
    print("=" * 60)

    # Configuration 4: waist=85.0, shoulder=-20.0, elbow=55.0, wrist=25.0, gripper=0.0
    sequence = [
        ('waist', 85.0, 'Base (waist)'),
        ('shoulder', -20.0, 'Hombro (shoulder)'),
        ('elbow', 55.0, 'Codo (elbow)'),
        ('wrist', 25.0, 'Muñeca (wrist)'),
        ('gripper', 0.0, 'Pinza (gripper)'),
    ]

    for joint, pos, label in sequence:
        print(f"\nMoviendo {label} a {pos:.1f}°...")
        node.send_command(joint, pos)
        time.sleep(4.0)

    print("\n[Referencia] Retornando secuencialmente a la posición de reposo (0°)...")
    # Return in reverse order for safety (Gripper -> Wrist -> Elbow -> Shoulder -> Base)
    for joint, pos, label in reversed(sequence):
        print(f"Retornando {label} a 0.0°...")
        node.send_command(joint, 0.0)
        time.sleep(4.0)

    print("\n============================================================")
    print("¡Actividad 8: Movimiento Secuencial completada con éxito!")
    print("============================================================")

def save_interpolation_plots(time_steps: List[float], positions_data: Dict[str, List[float]], 
                             velocities_data: Dict[str, List[float]], method_name: str, filename: str) -> None:
    results_dir = os.path.join(get_workspace_dir(), 'results', 'interpolacion')
    os.makedirs(results_dir, exist_ok=True)
    filepath = os.path.join(results_dir, filename)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    for joint, positions in positions_data.items():
        label = JOINT_TRANSLATIONS[joint]
        ax1.plot(time_steps, positions, label=label, linewidth=2)
    ax1.set_ylabel('Posición Angular (grados)')
    ax1.set_title(f'Trayectoria - Interpolación {method_name}')
    ax1.grid(True)
    ax1.legend(loc='upper right')
    
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

def generate_comparison_plot() -> None:
    results_dir = os.path.join(get_workspace_dir(), 'results', 'interpolacion')
    os.makedirs(results_dir, exist_ok=True)
    filepath = os.path.join(results_dir, 'comparativa_interpolacion.png')
    
    T = 5.0
    time_steps = np.linspace(0, T, 200)
    pos_start, pos_end = CONFIG_A[0], CONFIG_B[0]
    
    pos_lin = pos_start + (time_steps / T) * (pos_end - pos_start)
    vel_lin = np.full_like(time_steps, (pos_end - pos_start) / T)
    vel_lin[0], vel_lin[-1] = 0.0, 0.0
    
    tau = time_steps / T
    s = 3.0 * (tau ** 2) - 2.0 * (tau ** 3)
    pos_cub = pos_start + s * (pos_end - pos_start)
    ds_dt = (6.0 * tau - 6.0 * (tau ** 2)) / T
    vel_cub = ds_dt * (pos_end - pos_start)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    ax1.plot(time_steps, pos_lin, 'r--', label='Lineal (Discontinua)', linewidth=2.5)
    ax1.plot(time_steps, pos_cub, 'b-', label='Cúbica (Suave)', linewidth=2.5)
    ax1.set_ylabel('Posición Angular (grados)')
    ax1.set_title('Comparativa de Suavidad: Trayectoria Lineal vs. Cúbica (Base)')
    ax1.grid(True)
    ax1.legend(loc='upper left')
    
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

def run_interpolation_test(node: JointMoverNode) -> None:
    print("\n--- INICIANDO ACTIVIDAD 9: INTERPOLACIÓN DE TRAYECTORIAS ---")
    print("Se ejecutarán sucesivamente la interpolación lineal y cúbica")
    print("entre la Configuración A (Inicio) y la Configuración B (Final).")
    print("=" * 60)

    duration = 5.0
    freq = 50.0
    dt = 1.0 / freq
    steps = int(duration * freq)

    # 1. Linear
    print("\nMoviendo a la Configuración A (Inicio)...")
    node.send_simultaneous_command(CONFIG_A)
    time.sleep(4.0)

    print("Iniciando trayectoria Lineal hacia Configuración B...")
    time_steps = []
    positions_history_lin = {joint: [] for joint in JOINT_LIMITS_DEG.keys()}
    velocities_history_lin = {joint: [] for joint in JOINT_LIMITS_DEG.keys()}
    joints_list = list(JOINT_LIMITS_DEG.keys())
    const_vels = [(CONFIG_B[i] - CONFIG_A[i]) / duration for i in range(5)]

    start_time = time.time()
    for step in range(steps + 1):
        t = step * dt
        time_steps.append(t)
        
        curr_pos = []
        for i, joint in enumerate(joints_list):
            q = CONFIG_A[i] + (t / duration) * (CONFIG_B[i] - CONFIG_A[i])
            curr_pos.append(q)
            positions_history_lin[joint].append(q)
            if step == 0 or step == steps:
                velocities_history_lin[joint].append(0.0)
            else:
                velocities_history_lin[joint].append(const_vels[i])

        node.send_simultaneous_command(curr_pos)
        elapsed = time.time() - start_time
        sleep_time = (step + 1) * dt - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

    save_interpolation_plots(time_steps, positions_history_lin, velocities_history_lin, 'Lineal', 'interpolacion_lineal.png')

    # 2. Cubic
    print("\nMoviendo a la Configuración A (Inicio)...")
    node.send_simultaneous_command(CONFIG_A)
    time.sleep(4.0)

    print("Iniciando trayectoria Cúbica hacia Configuración B...")
    time_steps = []
    positions_history_cub = {joint: [] for joint in JOINT_LIMITS_DEG.keys()}
    velocities_history_cub = {joint: [] for joint in JOINT_LIMITS_DEG.keys()}

    start_time = time.time()
    for step in range(steps + 1):
        t = step * dt
        time_steps.append(t)
        
        tau = t / duration
        s = 3.0 * (tau ** 2) - 2.0 * (tau ** 3)
        ds_dt = (6.0 * tau - 6.0 * (tau ** 2)) / duration
        
        curr_pos = []
        for i, joint in enumerate(joints_list):
            q = CONFIG_A[i] + s * (CONFIG_B[i] - CONFIG_A[i])
            curr_pos.append(q)
            positions_history_cub[joint].append(q)
            v = ds_dt * (CONFIG_B[i] - CONFIG_A[i])
            velocities_history_cub[joint].append(v)

        node.send_simultaneous_command(curr_pos)
        elapsed = time.time() - start_time
        sleep_time = (step + 1) * dt - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

    save_interpolation_plots(time_steps, positions_history_cub, velocities_history_cub, 'Cúbica (Spline)', 'interpolacion_cubica.png')
    generate_comparison_plot()

    print("\nRetornando todas las articulaciones a Home...")
    node.send_home_command()
    time.sleep(2.0)
    print("=" * 60)
    print("¡Actividad 9: Interpolación finalizada!")
    print("=" * 60)

def save_sinusoidal_plot(time_steps: List[float], desired: List[float], measured: List[float], 
                          max_err: float, rmse: float, test_num: int, A: float, f: float) -> None:
    results_dir = os.path.join(get_workspace_dir(), 'results', 'sinusoidal')
    os.makedirs(results_dir, exist_ok=True)
    filepath = os.path.join(results_dir, f'test_{test_num}.png')
    
    plt.figure(figsize=(10, 6))
    plt.plot(time_steps, desired, 'r--', label='Deseada', linewidth=2)
    plt.plot(time_steps, measured, 'b-', label='Medida', linewidth=1.5)
    plt.xlabel('Tiempo (segundos)')
    plt.ylabel('Posición Angular Base (grados)')
    plt.title(f'Prueba Sinusoidal {test_num} (A={A}°, f={f} Hz)\nMax Error: {max_err:.3f}°, RMSE: {rmse:.3f}°')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close()
    print(f"[Graficado] Gráfica de la prueba {test_num} guardada en: {filepath}")

def run_sinusoidal_test(node: JointMoverNode) -> None:
    print("\n--- INICIANDO ACTIVIDAD 10: TRAYECTORIA SINUSOIDAL ---")
    print("Se realizarán 4 pruebas en la Base (waist):")
    print("1. A=30.0°, f=0.10 Hz")
    print("2. A=30.0°, f=0.25 Hz")
    print("3. A=60.0°, f=0.10 Hz")
    print("4. A=60.0°, f=0.25 Hz")
    print("=" * 60)

    tests = [
        (30.0, 0.1),
        (30.0, 0.25),
        (60.0, 0.1),
        (60.0, 0.25),
    ]

    for idx, (A, f) in enumerate(tests, 1):
        print(f"\n>>> Iniciando Prueba {idx}/4: Amplitud = {A}°, Frecuencia = {f} Hz...")
        print("Regresando articulaciones a Home...")
        node.send_home_command()
        time.sleep(3.0)

        duration = 10.0
        freq = 50.0
        dt = 1.0 / freq
        steps = int(duration * freq)

        time_steps = []
        desired_history = []
        measured_history = []

        start_time = time.time()
        for step in range(steps + 1):
            t = step * dt
            time_steps.append(t)

            # Target position
            q_des = A * math.sin(2.0 * math.pi * f * t)
            desired_history.append(q_des)

            # Command joint
            node.send_command('waist', q_des)

            # Read measured position
            q_meas = node.get_joint_position_deg('waist')
            if q_meas is None:
                q_meas = 0.0
            measured_history.append(q_meas)

            # Non-blocking exact time sleeping
            elapsed = time.time() - start_time
            sleep_time = (step + 1) * dt - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

        # Calculations
        desired_arr = np.array(desired_history)
        measured_arr = np.array(measured_history)
        errors = desired_arr - measured_arr
        max_err = np.max(np.abs(errors))
        rmse = np.sqrt(np.mean(errors ** 2))

        print(f"Prueba {idx} finalizada.")
        print(f"  Error Máximo: {max_err:.3f}°")
        print(f"  Error Cuadrático Medio (RMSE): {rmse:.3f}°")

        # Save plot
        save_sinusoidal_plot(time_steps, desired_history, measured_history, max_err, rmse, idx, A, f)

    # Return to home
    print("\nRetornando todas las articulaciones a Home...")
    node.send_home_command()
    time.sleep(2.0)
    print("=" * 60)
    print("¡Actividad 10: Trayectoria Sinusoidal finalizada!")
    print("=" * 60)

def show_positions(node: JointMoverNode) -> None:
    print("\n--- POSICIONES ACTUALES ---")
    for joint, label in JOINT_TRANSLATIONS.items():
        pos = node.get_joint_position_deg(joint)
        if pos is not None:
            print(f"{label:<20} ({joint}): {pos:8.2f}°")
        else:
            print(f"{label:<20} ({joint}): Desconocida")

def main(args=None) -> None:
    rclpy.init(args=args)
    node = JointMoverNode()

    # Start ROS node spinning in a separate thread so console input is non-blocking
    spin_thread = threading.Thread(target=spin_thread_target, args=(node,), daemon=True)
    spin_thread.start()

    print("Esperando a recibir información de /joint_states...")
    # Wait up to 3 seconds for initial joint states
    for _ in range(30):
        if node.current_positions:
            break
        time.sleep(0.1)

    # Configurar velocidad al 30% por seguridad
    print("Configurando velocidad de las articulaciones al 30%...")
    node.send_speed_command(30)

    try:
        while True:
            print_menu()
            choice = input("Seleccione una opción (1-9): ").strip()
            if choice == '1':
                manual_control(node)
            elif choice == '2':
                run_auto_test(node)
            elif choice == '3':
                run_simultaneous_test(node)
            elif choice == '4':
                run_sequential_test(node)
            elif choice == '5':
                run_interpolation_test(node)
            elif choice == '6':
                run_sinusoidal_test(node)
            elif choice == '7':
                print("\nEnviando comando HOME a todas las articulaciones...")
                node.send_home_command()
                time.sleep(1.0)
                print("Comando HOME enviado.")
            elif choice == '8':
                show_positions(node)
            elif choice == '9':
                print("\nSaliendo del programa...")
                break
            else:
                print("[Error] Opción no válida. Intente nuevamente.")
    except KeyboardInterrupt:
        print("\nSaliendo por interrupción de teclado...")
    finally:
        # Shutdown ROS 2 cleanly
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
