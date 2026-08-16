#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math
import time

class PhantomXSequencer(Node):
    def __init__(self):
        super().__init__('phantomx_sequencer')
        self.publisher_ = self.create_publisher(JointState, '/pincher/command', 10)
        self.joint_names = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']
        
        # Posición de referencia inicial (Home)
        self.reference_position = [0.0, 0.0, 0.0, 0.0, 0.0]
        
        # Límites experimentales convertidos de grados a radianes
        self.limits = {
            'waist': (math.radians(-110.0), math.radians(110.0)),       # [-1.919, 1.919] rad
            'shoulder': (math.radians(-100.0), math.radians(105.0)),   # [-1.745, 1.832] rad
            'elbow': (math.radians(-90.0), math.radians(108.0)),       # [-1.570, 1.884] rad
            'wrist': (math.radians(-100.0), math.radians(90.0)),       # [-1.745, 1.570] rad
            'gripper': (math.radians(-54.0), math.radians(54.0))       # [-0.942, 0.942] rad
        }

    def check_limits(self, name, pos):
        """Valida y satura la posición dentro de los rangos seguros calibrados"""
        low, high = self.limits[name]
        if pos < low:
            return low
        if pos > high:
            return high
        return pos

    def publish_joint_state(self, names, positions):
        """Publica un estado articular en el tópico de control"""
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = names
        msg.position = [float(p) for p in positions]
        self.publisher_.publish(msg)

    
    def run_actividad_4(self):
        """Movimiento independiente de cada articulación con selección manual y rutina de 3 puntos"""
        while True:
            print("\n--- Ejecutando Actividad 4: Movimientos Independientes ---")
            print("1. [Modo Manual] Seleccionar articulación e ingresar ángulo")
            print("2. [Modo Automático] Rutina de evaluación (3 posiciones + Home por motor)")
            print("3. Regresar al menú principal")
            
            opc = input("Selección (1-3): ").strip()
            
            if opc == '1':
                # Requerimiento: "Permita seleccionar una articulación y enviarle una posición angular"
                print("\nSeleccione la articulación a mover:")
                for i, name in enumerate(self.joint_names):
                    print(f"{i+1}. {name}")
                
                try:
                    j_sel = int(input("Opción (1-5): "))
                    if 1 <= j_sel <= 5:
                        joint_name = self.joint_names[j_sel - 1]
                        angle_deg = float(input(f"Ingrese la posición angular para '{joint_name}' (en grados): "))
                        angle_rad = math.radians(angle_deg)
                        
                        safe_rad = self.check_limits(joint_name, angle_rad)
                        print(f"Transmitiendo comando a {joint_name}: {math.degrees(safe_rad):.1f}°...")
                        self.publish_joint_state([joint_name], [safe_rad])
                        time.sleep(1.0)
                    else:
                        print("Selección de articulación inválida.")
                except ValueError:
                    print("Entrada no válida. Use números.")
                    
            elif opc == '2':
                # Requerimiento: "Para cada articulación, ejecute al menos tres posiciones diferentes... y regrese a la posición de referencia"
                # Definimos 3 posiciones seguras (en grados) para cada motor
                rutinas_prueba = {
                    'waist': [45.0, -45.0, 90.0],
                    'shoulder': [30.0, -30.0, 60.0],
                    'elbow': [45.0, -45.0, 75.0],
                    'wrist': [30.0, -30.0, 60.0],
                    'gripper': [20.0, -20.0, 45.0]
                }
                
                print("\nIniciando rutina de validación automática...")
                for name in self.joint_names:
                    print(f"\n>> Validando motor: {name.upper()}")
                    
                    # Ejecuta las 3 posiciones
                    for i, pos_deg in enumerate(rutinas_prueba[name]):
                        pos_rad = math.radians(pos_deg)
                        safe_rad = self.check_limits(name, pos_rad)
                        
                        print(f"  Paso {i+1}/3: Moviendo a {pos_deg}°")
                        self.publish_joint_state([name], [safe_rad])
                        time.sleep(1.5) # Pausa para que el servo alcance la posición
                    
                    # Regresa a Home (0.0)
                    print(f"  Regresando {name} a la posición de referencia (0.0°)")
                    self.publish_joint_state([name], [0.0])
                    time.sleep(1.5)
                
                print("\n✅ Rutina de validación completada para los 5 motores.")
                
            elif opc == '3':
                break
            else:
                print("Opción inválida.")
    # ==========================================================

    def run_actividad_7(self):
        """Movimiento simultáneo: Envía las 5 articulaciones al mismo tiempo mostrando el diagnóstico"""
        print("\n--- Ejecutando Actividad 7: Movimiento Simultáneo ---")
        
        # Matrices con las configuraciones de la guía en grados para la impresión en consola
        configuraciones_deg = [
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [25.0, 25.0, 20.0, -20.0, 0.0],
            [-35.0, 35.0, -30.0, 30.0, 0.0],
            [85.0, -20.0, 55.0, 25.0, 0.0],
            [80.0, -35.0, 55.0, -45.0, 0.0]
        ]
        
        # Conversión automática a radianes para el procesamiento del hardware
        configuraciones_rad = [
            [math.radians(ang) for ang in config] for config in configuraciones_deg
        ]
        
        for i, config in enumerate(configuraciones_rad):
            print(f"\n========================================================")
            print(f" TRANSMITIENDO SIMULTÁNEAMENTE CONFIGURACIÓN N° {i+1} ")
            print(f"========================================================")
            
            # Mostramos en pantalla los ángulos objetivos en grados para claridad del usuario
            angulos_format = configuraciones_deg[i]
            print(f" Consignas enviadas (Grados):")
            print(f"  -> waist:    {angulos_format[0]:>6.1f}°")
            print(f"  -> shoulder: {angulos_format[1]:>6.1f}°")
            print(f"  -> elbow:    {angulos_format[2]:>6.1f}°")
            print(f"  -> wrist:    {angulos_format[3]:>6.1f}°")
            print(f"  -> gripper:  {angulos_format[4]:>6.1f}°")
            print(f"--------------------------------------------------------")
            
            # Validación de límites de seguridad
            safe_config = [self.check_limits(self.joint_names[j], config[j]) for j in range(5)]
            
            # Envío de comando al bus físico
            self.publish_joint_state(self.joint_names, safe_config)
            
            # Espera física para que los servos completen la trayectoria dinámica
            time.sleep(1.5) 
            
            # Mecanismo de confirmación obligatorio para poder avanzar de forma segura
            input(f"⚙️ Configuración N° {i+1} alcanzada en el hardware. Presione ENTER para pasar a la siguiente...")
    def run_actividad_8(self):
        """Movimiento secuencial: Permite seleccionar una configuración de la Actividad 7 y ejecutarla eje por eje"""
        print("\n--- Ejecutando Actividad 8: Movimiento Secuencial de una Configuración ---")
        configuraciones = [
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [math.radians(25), math.radians(25), math.radians(20), math.radians(-20), 0.0],
            [math.radians(-35), math.radians(35), math.radians(-30), math.radians(30), 0.0],
            [math.radians(85), math.radians(-20), math.radians(55), math.radians(25), 0.0],
            [math.radians(80), math.radians(-35), math.radians(55), math.radians(-45), 0.0]
        ]
        
        print("Seleccione cuál de las 5 configuraciones de la Actividad 7 desea ejecutar secuencialmente:")
        print("1. Configuración 1 [0, 0, 0, 0, 0]")
        print("2. Configuración 2 [25, 25, 20, -20, 0]")
        print("3. Configuración 3 [-35, 35, -30, 30, 0]")
        print("4. Configuración 4 [85, -20, 55, 25, 0]")
        print("5. Configuración 5 [80, -35, 55, -45, 0]")
        
        try:
            seleccion = int(input("Selección (1-5): ")) - 1
            if 0 <= seleccion < len(configuraciones):
                target_config = configuraciones[seleccion]
                print(f"\nIniciando secuencia eje por eje para alcanzar la Configuración N° {seleccion + 1}...")
                
                for i, name in enumerate(self.joint_names):
                    safe_pos = self.check_limits(name, target_config[i])
                    print(f"Paso secuencial: Moviendo únicamente {name} a {math.degrees(safe_pos):.1f}° ({safe_pos:.3f} rad)")
                    self.publish_joint_state([name], [safe_pos])
                    time.sleep(2.0)
                    
                print("Secuencia finalizada con éxito.")
            else:
                print("Número de configuración fuera de rango.")
        except ValueError:
            print("Entrada inválida. Debe ingresar un número entero.")

    def run_actividad_9(self, target_config, duration=4.0, steps=40):
        """Actividad 9: Interpolación lineal de trayectorias (Suavizado)"""
        print("\n--- Ejecutando Actividad 9: Trayectoria Interpolada ---")
        start_config = [0.0, 0.0, 0.0, 0.0, 0.0] 
        dt = duration / steps
        
        for step in range(steps + 1):
            t = step / steps
            current_config = []
            for j in range(5):
                q0 = start_config[j]
                qf = target_config[j]
                qi = q0 + t * (qf - q0)
                current_config.append(self.check_limits(self.joint_names[j], qi))
                
            self.publish_joint_state(self.joint_names, current_config)
            time.sleep(dt)
        print("Trayectoria interpolada finalizada.")

    def run_actividad_10(self, joint_idx=0, amplitude_deg=30.0, frequency=0.25, duration=10.0):
        """Actividad 10: Generación de trayectoria sinusoidal continua"""
        amplitude = math.radians(amplitude_deg)
        name = self.joint_names[joint_idx]
        print(f"\n--- Ejecutando Actividad 10: Trayectoria Sinusoidal en {name} ---")
        
        start_time = time.time()
        while (time.time() - start_time) < duration:
            t = time.time() - start_time
            q_t = 0.0 + amplitude * math.sin(2 * math.pi * frequency * t)
            safe_pos = self.check_limits(name, q_t)
            
            self.publish_joint_state([name], [safe_pos])
            time.sleep(0.02) 
        
        self.publish_joint_state([name], [0.0])
        print("Prueba sinusoidal completada.")

def main(args=None):
    rclpy.init(args=args)
    sequencer = PhantomXSequencer()
    
    print("=====================================================")
    print("   NODO CONSOLIDADO DE PRUEBAS CINEMÁTICAS (LAB 5)   ")
    print("=====================================================")
    
    while rclpy.ok():
        print("\nSeleccione la actividad técnica a ejecutar:")
        print("4. Actividad 4: Movimientos independientes (Manual y Automático)")
        print("7. Actividad 7: Movimiento simultáneo (5 configuraciones)")
        print("8. Actividad 8: Movimiento secuencial (Eje por eje)")
        print("9. Actividad 9: Interpolación lineal de trayectorias")
        print("10. Actividad 10: Generación de trayectoria sinusoidal")
        print("q. Salir del secuenciador")
        
        opcion = input("Selección: ").strip().lower()
        
        if opcion == 'q':
            break
        elif opcion == '4':
            sequencer.run_actividad_4()
        elif opcion == '7':
            sequencer.run_actividad_7()
        elif opcion == '8':
            sequencer.run_actividad_8()
        elif opcion == '9':
            sequencer.run_actividad_9([0.5, 0.4, 0.4, 0.3, 0.0])
        elif opcion == '10':
            sequencer.run_actividad_10(joint_idx=0, amplitude_deg=30.0, frequency=0.25)
        else:
            print("Opción no válida.")
            
    sequencer.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()