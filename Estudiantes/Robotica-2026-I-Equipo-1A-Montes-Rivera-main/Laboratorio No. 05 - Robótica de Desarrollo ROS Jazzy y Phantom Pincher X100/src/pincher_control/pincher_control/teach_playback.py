#!/usr/bin/env python3
import math
import os
import sys
import threading
import time
from typing import Dict, List, Optional
import yaml

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import UInt32
from std_srvs.srv import SetBool

# YAML File path
def get_workspace_dir() -> str:
    prefix = os.environ.get('COLCON_PREFIX_PATH', '')
    if not prefix:
        prefix = os.environ.get('AMENT_PREFIX_PATH', '')
    if prefix:
        first_prefix = prefix.split(os.pathsep)[0]
        return os.path.abspath(os.path.join(first_prefix, '..'))
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(script_dir, '..', '..', '..'))

YAML_DIR = os.path.join(get_workspace_dir(), 'src', 'pincher_control', 'config')
YAML_PATH = os.path.join(YAML_DIR, 'saved_poses.yaml')

JOINT_NAMES = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']

class TeachPlaybackNode(Node):
    """ROS 2 Node for teaching and playing back joint poses."""
    def __init__(self) -> None:
        super().__init__('teach_playback')
        self.publisher = self.create_publisher(JointState, '/pincher/command', 10)
        self.speed_publisher = self.create_publisher(UInt32, '/pincher/profile_velocity', 10)
        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_states_callback,
            10
        )
        # Service client for torque
        self.torque_client = self.create_client(SetBool, '/pincher/torque_enable')
        
        self.current_positions: Dict[str, float] = {}
        self.joint_names: List[str] = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']
        self.lock = threading.Lock()
        self.poses: List[Dict] = []
        self.transition_time = 4.0 # Default transition time in seconds
        
        # Thread control
        self.playback_active = False
        self.playback_thread: Optional[threading.Thread] = None

    def joint_states_callback(self, msg: JointState) -> None:
        with self.lock:
            if msg.name and len(msg.name) > 0:
                self.joint_names = list(msg.name)
            for name, pos in zip(msg.name, msg.position):
                self.current_positions[name] = math.degrees(pos)

    def get_current_pose(self) -> Optional[List[float]]:
        with self.lock:
            if self.joint_names and all(name in self.current_positions for name in self.joint_names):
                return [self.current_positions[name] for name in self.joint_names]
            return None

    def send_torque_request(self, enable: bool) -> bool:
        if not self.torque_client.service_is_ready():
            self.get_logger().warning('Servicio /pincher/torque_enable no disponible.')
            return False
        
        req = SetBool.Request()
        req.data = enable
        future = self.torque_client.call_async(req)
        
        # Wait for response using polling since executor is already spinning in a background thread
        start_wait = time.time()
        while not future.done() and (time.time() - start_wait) < 2.0:
            time.sleep(0.01)
            
        if future.done():
            try:
                res = future.result()
                return res.success
            except Exception as e:
                self.get_logger().error(f'Fallo al llamar servicio de torque: {e}')
        return False

    def send_simultaneous_command(self, positions_deg: List[float]) -> None:
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
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

def play_poses_worker(node: TeachPlaybackNode) -> None:
    """Thread function to execute play trajectories using cubic interpolation."""
    print("\n--- INICIANDO REPRODUCCIÓN ---")
    
    # 1. Enable torque
    print("Habilitando torque en todos los motores...")
    if not node.send_torque_request(True):
        print("[Error] No se pudo habilitar el torque. Abortando reproducción.")
        node.playback_active = False
        return

    # Set transition speed to 30% for safety
    node.set_speed(30)
    time.sleep(0.5)

    freq = 50.0
    dt = 1.0 / freq
    steps = int(node.transition_time * freq)

    for idx, pose in enumerate(node.poses, 1):
        if not node.playback_active:
            break
            
        name = pose['name']
        target_joints = pose['joints']
        print(f"\nMoviendo a pose {idx}/{len(node.poses)}: '{name}'...")
        
        # Get start joint positions
        start_joints = node.get_current_pose()
        if start_joints is None:
            print("[Advertencia] No se pudo obtener la pose actual. Usando destino anterior.")
            start_joints = target_joints

        start_time = time.time()
        for step in range(steps + 1):
            if not node.playback_active:
                break
                
            t = step * dt
            tau = t / node.transition_time
            # Cubic trajectory function: s(t) = 3*tau^2 - 2*tau^3
            s = 3.0 * (tau ** 2) - 2.0 * (tau ** 3)
            
            # Interpolate
            curr_pos = []
            for j in range(len(node.joint_names)):
                # If target has fewer joints than currently active, default to starting position
                target_val = target_joints[j] if j < len(target_joints) else start_joints[j]
                q = start_joints[j] + s * (target_val - start_joints[j])
                curr_pos.append(q)
                
            node.send_simultaneous_command(curr_pos)
            
            # Compensate sleep time
            elapsed = time.time() - start_time
            sleep_time = (step + 1) * dt - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

        # Wait at the destination pose for 1 second
        if node.playback_active:
            time.sleep(1.0)

    print("\n============================================================")
    print("¡Reproducción finalizada con éxito!")
    print("============================================================")
    node.playback_active = False

def print_menu() -> None:
    print("\n" + "=" * 60)
    print("      PhantomX Pincher X100 - ENSEÑANZA Y REPETICIÓN")
    print("=" * 60)
    print("1. Deshabilitar Torque (Modo Enseñanza Guiado Manual)")
    print("2. Guardar Pose Actual (desde /joint_states)")
    print("3. Cargar poses desde archivo YAML")
    print("4. Guardar poses registradas a archivo YAML")
    print("5. Iniciar Reproducción de Poses")
    print("6. Detener Reproducción")
    print("7. Modificar tiempo de transición (actual: {:.1f}s)".format(TeachPlaybackNode_transition_time_val))
    print("8. Mostrar poses en memoria")
    print("9. Salir")
    print("-" * 60)

# Global helper to print menu transition time
TeachPlaybackNode_transition_time_val = 4.0

def main(args=None) -> None:
    global TeachPlaybackNode_transition_time_val
    rclpy.init(args=args)
    node = TeachPlaybackNode()

    # Spin ROS 2 node in background
    spin_thread = threading.Thread(target=spin_thread_target, args=(node,), daemon=True)
    spin_thread.start()

    # Wait up to 3 seconds for initial joint states
    print("Esperando información de /joint_states...")
    for _ in range(30):
        if node.get_current_pose() is not None:
            break
        time.sleep(0.1)

    # Auto-load existing poses at startup if YAML exists
    if os.path.exists(YAML_PATH):
        try:
            with open(YAML_PATH, 'r') as f:
                data = yaml.safe_load(f)
                if data and 'poses' in data:
                    node.poses = data['poses']
                    print(f"\n[Auto-Load] Se cargaron {len(node.poses)} poses existentes de {YAML_PATH}")
        except Exception as e:
            print(f"[Advertencia] No se pudo auto-cargar poses: {e}")

    try:
        while True:
            TeachPlaybackNode_transition_time_val = node.transition_time
            print_menu()
            choice = input("Seleccione una opción: ").strip()
            
            if choice == '1':
                print("\nDeshabilitando torque en los motores (guiado manual)...")
                if node.send_torque_request(False):
                    print("[OK] Torque desactivado. Puedes mover el brazo libremente.")
                else:
                    print("[Error] No se pudo desactivar el torque. ¿Está corriendo el driver?")
                    
            elif choice == '2':
                pose = node.get_current_pose()
                if pose is None:
                    print("[Error] No se ha recibido información de /joint_states todavía.")
                    continue
                name = input("Ingrese un nombre para esta pose: ").strip()
                if not name:
                    name = f"pose_{len(node.poses) + 1}"
                node.poses.append({
                    'name': name,
                    'joints': [round(val, 2) for val in pose]
                })
                print(f"[Guardado] Pose '{name}' registrada en memoria: {node.poses[-1]['joints']}")
                
                # Auto-save to YAML file immediately
                try:
                    os.makedirs(YAML_DIR, exist_ok=True)
                    with open(YAML_PATH, 'w') as f:
                        yaml.safe_dump({'poses': node.poses}, f, default_flow_style=False)
                    print(f"[Auto-Save] Guardado persistente actualizado en: {YAML_PATH}")
                except Exception as e:
                    print(f"[Error] Fallo al auto-guardar en YAML: {e}")
                
            elif choice == '3':
                if not os.path.exists(YAML_PATH):
                    print(f"[Error] El archivo {YAML_PATH} no existe.")
                    continue
                try:
                    with open(YAML_PATH, 'r') as f:
                        data = yaml.safe_load(f)
                        if data and 'poses' in data:
                            node.poses = data['poses']
                            print(f"[YAML] Cargadas {len(node.poses)} poses desde {YAML_PATH}")
                        else:
                            print("[Error] El archivo YAML no tiene la estructura correcta.")
                except Exception as e:
                    print(f"[Error] Fallo al cargar YAML: {e}")
                    
            elif choice == '4':
                if not node.poses:
                    print("[Error] No hay poses registradas en memoria para guardar.")
                    continue
                try:
                    os.makedirs(YAML_DIR, exist_ok=True)
                    with open(YAML_PATH, 'w') as f:
                        yaml.safe_dump({'poses': node.poses}, f, default_flow_style=False)
                    print(f"[YAML] Guardadas {len(node.poses)} poses en: {YAML_PATH}")
                except Exception as e:
                    print(f"[Error] Fallo al guardar YAML: {e}")
                    
            elif choice == '5':
                if not node.poses:
                    print("[Error] No hay poses en memoria para reproducir.")
                    continue
                if node.playback_active:
                    print("[Advertencia] Ya hay una reproducción en curso.")
                    continue
                node.playback_active = True
                node.playback_thread = threading.Thread(target=play_poses_worker, args=(node,), daemon=True)
                node.playback_thread.start()
                
            elif choice == '6':
                if node.playback_active:
                    print("\nDeteniendo reproducción...")
                    node.playback_active = False
                    if node.playback_thread:
                        node.playback_thread.join(timeout=1.0)
                    print("[OK] Reproducción detenida.")
                else:
                    print("[Info] No hay reproducción activa.")
                    
            elif choice == '7':
                try:
                    t_val = float(input("Ingrese el tiempo de transición en segundos (actual: {:.1f}s): ".format(node.transition_time)))
                    if t_val <= 0.1:
                        print("[Error] El tiempo debe ser mayor a 0.1 segundos.")
                    else:
                        node.transition_time = t_val
                        print(f"[Configuración] Tiempo de transición actualizado a: {node.transition_time}s")
                except ValueError:
                    print("[Error] Debe ingresar un valor numérico.")
                    
            elif choice == '8':
                if not node.poses:
                    print("\nNo hay poses en memoria.")
                else:
                    print("\n--- POSES EN MEMORIA ---")
                    for idx, p in enumerate(node.poses, 1):
                        print(f"  {idx}. {p['name']:<15} : {p['joints']}")
                        
            elif choice == '9':
                if node.playback_active:
                    node.playback_active = False
                    if node.playback_thread:
                        node.playback_thread.join(timeout=1.0)
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
