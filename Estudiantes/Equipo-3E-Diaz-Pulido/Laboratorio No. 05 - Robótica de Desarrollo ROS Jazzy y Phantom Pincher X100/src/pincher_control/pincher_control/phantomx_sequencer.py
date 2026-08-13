#!/usr/bin/env python3
"""
Módulo de control cinemático avanzado para el Phantom X Pincher X100 (Lab 05)
Integración de ROS 2 Jazzy con las librerías analíticas de Cinemática e Interpolación.

"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math
import time
import numpy as np
import matplotlib.pyplot as plt
import yaml
import os
import glob

# Importación de los módulos matemáticos y analíticos proporcionados
from pincher_control.Kin import Kinematic
from pincher_control.limits_pincher import Limits
from pincher_control.tracer import Tracer

class PhantomXSequencer(Node):
    def __init__(self):
        super().__init__('phantomx_sequencer')
        self.publisher_ = self.create_publisher(JointState, '/pincher/command', 10)
        self.subscriber_ = self.create_subscription(JointState, '/joint_states', self.joint_state_callback, 10)
        self.joint_names = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']
        self.poses_file = '/home/jose-luis/ros2_jazzy/phantom_ws/src/pincher_control/config/poses_guardadas.yaml'
        self.saved_poses = self.cargar_poses()

        
        # Límites seguros globales en radianes para validación de bajo nivel del hardware
        self.limits_rad = {
            'waist': (math.radians(-110.0), math.radians(110.0)),
            'shoulder': (math.radians(-100.0), math.radians(105.0)),
            'elbow': (math.radians(-90.0), math.radians(108.0)),
            'wrist': (math.radians(-100.0), math.radians(90.0)),
            'gripper': (math.radians(-54.0), math.radians(54.0))
        }
        
        # Inicialización del modelo cinemático (Dimensiones y offsets físicos)
        self.robot_kin = Kinematic(
            l1=128, l2=106, l3=106, w1=0, w2=0, w3=0, lTool=96, wTool=0, thetaTool=0, phi=None, 
            offset_t2=90.0, dir_t2=-1.0,  
            offset_t3=0.0, dir_t3=-1.0,
            offset_t4=0.0, dir_t4=-1.0  
        )
        self.limits_analyzer = Limits(self.robot_kin)
        self.tracer = Tracer(self.robot_kin, self.limits_analyzer)
        
        obstaculos = [
        # Caja 1: A la izquierda, inclinada 45 grados en Yaw
        {'type': 'box', 'center': [200, 100, 40], 'dims': [30, 80, 80], 'rpy': [0, 0, 45], 'name': 'Caja 1 Azul (Inclinada a 45)'},
        
        # Caja 2: A la derecha, inclinada 45 grados en Yaw
        {'type': 'box', 'center': [200, -100, 40], 'dims': [30, 80, 80], 'rpy': [0, 0, -45], 'name': 'Caja 2 Verde (Inclinada a -45)'},
        
        # Caja 3: A la izquierda recta
        {'type': 'box', 'center': [30, 110, 30], 'dims': [30, 80, 60], 'rpy': [0, 0, 90], 'name': 'Caja 3 Amarilla '},
        
        # Caja 4: A La derecha recta
        {'type': 'box', 'center': [30, -110, 30], 'dims': [30, 80, 60], 'rpy': [0, 0, 90], 'name': 'Caja 4 Roja '},
        
        
        # Piso
        {'type': 'box', 'center': [0, 0, -152.5], 'dims': [600, 600, 300], 'rpy': [0, 0, 0], 'name': 'Piso '},
        
        
        # Cilindro: Atrás del robot
        {'type': 'cylinder', 'center': [260, 0, 0], 'radius': 25, 'height': 140, 'name': 'Columna Camara'}
    ]
        self.tracer.mapear_obstaculos(obstaculos)
        
        # Estado interno del robot mantenido en GRADOS para compatibilidad directa con los algoritmos
        self.current_joint_angles_deg = [0.0, 0.0, 0.0, 0.0]
        self.current_gripper_rad = 0.0

    def joint_state_callback(self, msg):
        """Actualiza el estado interno con la posición física real del hardware reportada por ROS 2"""
        try:
            # Buscamos los índices dinámicamente por si el driver los publica en otro orden
            w_idx = msg.name.index('waist')
            s_idx = msg.name.index('shoulder')
            e_idx = msg.name.index('elbow')
            wr_idx = msg.name.index('wrist')
            
            # Sobrescribimos el vector interno de posición (convirtiendo de rad a grados)
            self.current_joint_angles_deg = [
                math.degrees(msg.position[w_idx]),
                math.degrees(msg.position[s_idx]),
                math.degrees(msg.position[e_idx]),
                math.degrees(msg.position[wr_idx])
            ]
            
            if 'gripper' in msg.name:
                g_idx = msg.name.index('gripper')
                self.current_gripper_rad = msg.position[g_idx]
        except ValueError:
            pass # Faltan articulaciones en el mensaje actual, se ignora    

    def check_limits_and_saturate(self, name, pos_rad):
        """Valida que la posición en radianes esté dentro del rango seguro del hardware"""
        low, high = self.limits_rad[name]
        if pos_rad < low: return low
        if pos_rad > high: return high
        return pos_rad

    def publish_hardware_command(self, names, positions_rad):
        """Publica el vector de comandos de posición en radianes hacia el driver de ROS 2"""
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = names
        msg.position = [float(p) for p in positions_rad]
        self.publisher_.publish(msg)

    def run_forward_kinematics(self):
        """Calcula la cinemática directa permitiendo lectura real o ingreso manual"""
        print("\n--- [Cinemática Directa] ---")
        print("1. Calcular usando la posición FÍSICA ACTUAL del robot")
        print("2. Ingresar ángulos teóricos manualmente")
        opc = input("Selección (1/2, Enter para 1): ").strip()

        if opc == '2':
            try:
                q1 = float(input("  waist (grados): "))
                q2 = float(input("  shoulder (grados): "))
                q3 = float(input("  elbow (grados): "))
                q4 = float(input("  wrist (grados): "))
                angulos = [q1, q2, q3, q4]
            except ValueError:
                print("Entrada inválida. Operación cancelada.")
                return
        else:
            angulos = self.current_joint_angles_deg
            
        print(f"\nCalculando para: [waist={angulos[0]:.1f}°, shoulder={angulos[1]:.1f}°, elbow={angulos[2]:.1f}°, wrist={angulos[3]:.1f}°]")
        
        if hasattr(self.robot_kin, 'get_pose'):
            x, y, z, r, p, yaw = self.robot_kin.get_pose(angulos[0], angulos[1], angulos[2], angulos[3])
            print(f"Posición del TCP -> X: {x:.2f} mm, Y: {y:.2f} mm, Z: {z:.2f} mm")
            print(f"Orientación RPY  -> [{r:.2f}°, {p:.2f}°, {yaw:.2f}°]")
        elif hasattr(self.robot_kin, 'DirKin'):
            matriz = self.robot_kin.DirKin(angulos[0], angulos[1], angulos[2], angulos[3])
            print("Matriz de Transformación Homogénea del TCP:")
            print(matriz)
        else:
            print("Error crítico: No se encontró la función de cinemática directa.")

    def run_inverse_kinematics_move(self):
        """Calcula la cinemática inversa expandiendo la dimensión para asegurar 5 articulaciones"""
        print("\n--- [Cinemática Inversa y Movimiento Seguro] ---")
        try:
            x = float(input("Ingrese coordenada X objetivo (mm): "))
            y = float(input("Ingrese coordenada Y objetivo (mm): "))
            z = float(input("Ingrese coordenada Z objetivo (mm): "))
            theta4 = float(input("Ingrese ángulo de aproximación de la muñeca theta4 (grados): "))
        except ValueError:
            print("Entrada inválida. Operación cancelada.")
            return

        inv = self.tracer.trace_inverse(x, y, z, theta4=theta4)
        
        if inv['Estado'] == "Éxito":
            print("\nSoluciones encontradas en el espacio de trabajo:")
            for idx, sol in enumerate(inv['Soluciones']):
                status_colision = "¡Riesgo de COLISIÓN!" if sol['Colision'] else "Trayecto Seguro"
                angulos_str = ", ".join([f"{a:.1f}°" for a in sol['Configuracion']])
                print(f"  {idx + 1}. Configuración [{sol['Tipo']}]: [{angulos_str}] -> Estado: {status_colision}")
            
            sel = input("\nSeleccione el número de la solución para enviar al robot (o 'c' para cancelar): ")
            if sel.isdigit() and 1 <= int(sel) <= len(inv['Soluciones']):
                elegida = inv['Soluciones'][int(sel) - 1]
                if elegida['Colision']:
                    print("Operación cancelada de forma automática: La trayectoria elegida golpearía un obstáculo.")
                    return
                
                print(f"Transmitiendo consignas al manipulador...")
                
                # Extraer la configuración calculada de forma segura
                config = list(elegida['Configuracion'])
                
                # Corrección dimensional: Si devuelve 3 elementos, se añade theta4 para completar el brazo plano
                if len(config) == 3:
                    config.append(theta4)
                
                # Mapeo final a radianes inyectando el actuador final (Garantiza longitud 5)
                positions_rad = [math.radians(q) for q in config] + [self.current_gripper_rad]
                names_to_send = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']
                
                safe_positions = [self.check_limits_and_saturate(names_to_send[i], positions_rad[i]) for i in range(5)]
                self.publish_hardware_command(names_to_send, safe_positions)
                
                self.current_joint_angles_deg = config
                print("Posición alcanzada con éxito.")
            else:
                print("Operación cancelada.")
        else:
            print(f"Error en el cálculo: {inv['Mensaje']}")

    def run_advanced_interpolation(self):
        """Genera trayectorias continuas, ejecuta el movimiento y grafica los encoders reales"""
        print("\n--- [Trayectorias Suaves con Diagnóstico de Obstáculos] ---")
        print(f"Configuración actual: {[round(a,1) for a in self.current_joint_angles_deg]}°")
        print("Ingrese los valores de consigna de llegada (en grados):")
        try:
            q1 = float(input("  waist (grados): "))
            q2 = float(input("  shoulder (grados): "))
            q3 = float(input("  elbow (grados): "))
            q4 = float(input("  wrist (grados): "))
            method = input("Seleccione perfil de velocidad ('lineal' o 'quintica'): ").strip().lower()
            if method not in ['lineal', 'quintica']:
                print("Perfil no detectado. Se ejecutará por defecto interpolación 'quintica'.")
                method = 'quintica'
        except ValueError:
            print("Entrada inválida. Operación cancelada.")
            return

        q_inicial = self.current_joint_angles_deg
        q_final = [q1, q2, q3, q4]
        steps = 25  
        tiempo_total = 4.0 # Duración definida para el movimiento

        print(f"\nCalculando interpolación polinomial tipo {method}...")
        trayectoria, colisiones = self.tracer.interpolar_trayectoria(
            q_start=q_inicial,
            q_end=q_final,
            steps=steps,
            method=method,
            validar_colisiones=True
        )

        print("\n--- MONITOREO DE TRAYECTORIA Y COLISIONES ---")
        for i, q in enumerate(trayectoria):
            print(f"Paso {i+1}/{steps} | Ángulos: {[round(a, 1) for a in q]} | Estado Colisión: {colisiones[i]}")

        if any("Seguro" not in str(estado) for estado in colisiones):
            print("\n[¡ALERTA DE SEGURIDAD!] El planificador detectó interferencias con el entorno en esta trayectoria.")
            forzar = input("¿Desea forzar el movimiento bajo su propio riesgo? (s/N): ").strip().lower()
            if forzar != 's':
                print("Operación cancelada por seguridad.")
                return
        
        # ==========================================================
        # EJECUCIÓN Y GRABACIÓN DE ENCODERS (DATOS REALES)
        # ==========================================================
        print("\nIniciando streaming de comandos hacia el hardware y grabando encoders...")
        dt = tiempo_total / steps 
        
        # Listas para almacenar la telemetría en tiempo real
        tiempos_reales = []
        enc_waist = []
        enc_shoulder = []
        enc_elbow = []
        enc_wrist = []
        
        t_inicio = time.time()
        
        for paso, q_deg in enumerate(trayectoria):
            config = list(q_deg)
            if len(config) == 3:
                config.append(q_final[3])
                
            rad_joints = [math.radians(angle) for angle in config] + [self.current_gripper_rad]
            names_to_send = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']
            
            safe_rad = [self.check_limits_and_saturate(names_to_send[i], rad_joints[i]) for i in range(5)]
            self.publish_hardware_command(names_to_send, safe_rad)
            
            # Esperamos el delta de tiempo físico para que el robot se mueva
            time.sleep(dt)
            
            # Capturamos los datos reportados por los Dynamixel gracias al hilo en segundo plano
            t_actual = time.time() - t_inicio
            tiempos_reales.append(t_actual)
            enc_waist.append(self.current_joint_angles_deg[0])
            enc_shoulder.append(self.current_joint_angles_deg[1])
            enc_elbow.append(self.current_joint_angles_deg[2])
            enc_wrist.append(self.current_joint_angles_deg[3])
            
        self.current_joint_angles_deg = q_final
        print("Movimiento físico completado.")

        # ==========================================================
        # GENERACIÓN DE GRÁFICA POST-MOVIMIENTO (DATOS DE ENCODERS)
        # ==========================================================
        print("Generando gráfica de telemetría real...")
        plt.figure(figsize=(10, 6))
        
        # Graficamos los datos que grabamos directamente del hardware
        plt.plot(tiempos_reales, enc_waist, label='Real Waist (θ1)', linewidth=2.5, marker='o', markersize=4)
        plt.plot(tiempos_reales, enc_shoulder, label='Real Shoulder (θ2)', linewidth=2.5, marker='o', markersize=4)
        plt.plot(tiempos_reales, enc_elbow, label='Real Elbow (θ3)', linewidth=2.5, marker='o', markersize=4)
        plt.plot(tiempos_reales, enc_wrist, label='Real Wrist (θ4)', linewidth=2.5, marker='o', markersize=4)
        
        plt.title(f'Perfil REAL de Posición Angular (Leído por Encoders) - {method.capitalize()}')
        plt.xlabel('Tiempo de ejecución (segundos)')
        plt.ylabel('Posición Angular Física (Grados)')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Guardamos la gráfica
        nombre_grafica = f"Telemetria_Real_Interpolacion_{method.capitalize()}.png"
        plt.savefig(nombre_grafica, dpi=300, bbox_inches='tight')
        print(f"✅ ¡Gráfica de telemetría guardada exitosamente como '{nombre_grafica}'!")
        
        plt.show(block=False)
        plt.pause(2.0)

    def run_actividad_4(self):
        """Verificación básica aislada de articulaciones"""
        print("\n--- Ejecutando Actividad 4: Movimientos Independientes ---")
        test_positions_rad = [0.4, 0.8, -0.4]
        names = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']
        
        for name in names:
            print(f"Probando articulación de forma aislada: {name}")
            for pos in test_positions_rad:
                safe_pos = self.check_limits_and_saturate(name, pos)
                self.publish_hardware_command([name], [safe_pos])
                time.sleep(1.5)
            self.publish_hardware_command([name], [0.0])
            time.sleep(1.0)
        self.current_joint_angles_deg = [0.0, 0.0, 0.0, 0.0]

    def run_actividad_10(self):
        """Actividad 10: Generación de trayectoria sinusoidal con análisis de error y gráficas"""
        print("\n--- Ejecutando Actividad 10: Trayectoria Sinusoidal y Análisis ---")
        
        # 1. Seleccionar una articulación
        print("Seleccione la articulación para la prueba:")
        for i, name in enumerate(self.joint_names[:4]): # Excluimos el gripper para esta prueba
            print(f"{i+1}. {name}")
        
        try:
            sel = int(input("Opción (1-4): ")) - 1
            if not (0 <= sel <= 3):
                print("Selección inválida.")
                return
        except ValueError:
            print("Entrada inválida.")
            return

        joint_name = self.joint_names[sel]
        
        # 2. Configurar las 4 pruebas (2 Amplitudes x 2 Frecuencias)
        q0_deg = 0.0              # Posición de equilibrio (0 grados)
        amplitudes = [15.0, 30.0] # Amplitudes en grados
        frecuencias = [0.15, 0.3] # Frecuencias en Hz
        duracion = 6.0            # Duración de cada prueba en segundos
        
        pruebas = [
            (amplitudes[0], frecuencias[0]),
            (amplitudes[0], frecuencias[1]),
            (amplitudes[1], frecuencias[0]),
            (amplitudes[1], frecuencias[1])
        ]
        
        print(f"\nPosicionando {joint_name} en el origen (0.0°)...")
        self.publish_hardware_command([joint_name], [0.0])
        time.sleep(2.0)
        
        # 3. Ejecutar las 4 iteraciones
        for idx, (A, f) in enumerate(pruebas):
            print(f"\n========================================================")
            print(f" PRUEBA {idx+1}/4 | Amplitud (A): {A}° | Frecuencia (f): {f} Hz")
            print(f"========================================================")
            
            t_data = []
            q_des_data = []
            q_med_data = []
            errores = []
            
            A_rad = math.radians(A)
            q0_rad = math.radians(q0_deg)
            
            start_time = time.time()
            
            # Ejecución de la ecuación armónica
            while (time.time() - start_time) < duracion:
                t = time.time() - start_time
                
                # q(t) = q0 + A * sin(2 * pi * f * t)
                q_t_rad = q0_rad + A_rad * math.sin(2 * math.pi * f * t)
                safe_pos_rad = self.check_limits_and_saturate(joint_name, q_t_rad)
                
                # Envío de consigna al bus
                self.publish_hardware_command([joint_name], [safe_pos_rad])
                time.sleep(0.02) # dt de muestreo físico
                
                # Lectura real desde los encoders y cálculo de error instantáneo
                q_med_deg = self.current_joint_angles_deg[sel]
                q_des_deg = math.degrees(safe_pos_rad)
                
                t_data.append(t)
                q_des_data.append(q_des_deg)
                q_med_data.append(q_med_deg)
                errores.append(abs(q_des_deg - q_med_deg))
                
            # Retorno al origen tras cada prueba por seguridad
            self.publish_hardware_command([joint_name], [0.0])
            time.sleep(1.5)
            
            # 4. Cálculo de Indicadores Analíticos
            error_maximo = max(errores)
            mse = sum(e**2 for e in errores) / len(errores) # Mean Squared Error
            rmse = math.sqrt(mse)                           # Root Mean Square Error
            
            print("Resultados:")
            print(f"  -> Error Máximo Registrado: {error_maximo:.3f}°")
            print(f"  -> Error Cuadrático Medio (RMSE): {rmse:.3f}°")
            
            # 5. Generación de Gráficas y Guardado Automático
            plt.figure(figsize=(9, 5))
            plt.plot(t_data, q_des_data, label='Posición Deseada $q(t)$', linestyle='--', color='blue', linewidth=2)
            plt.plot(t_data, q_med_data, label='Posición Medida (Encoder)', color='red', alpha=0.8, linewidth=2)
            
            plt.title(f'Actividad 10 - Prueba {idx+1}: {joint_name.capitalize()} (A={A}°, f={f} Hz)')
            plt.xlabel('Tiempo (segundos)')
            plt.ylabel('Posición Angular (Grados)')
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.7)
            
            nombre_archivo = f'Grafica_Act10_{joint_name}_Prueba{idx+1}.png'
            plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
            print(f"  -> Gráfica guardada correctamente como: '{nombre_archivo}'")
            
            # Muestra rápida sin congelar el programa
            plt.show(block=False)
            plt.pause(1.5)
            plt.close()

        print("\n✅ Finalizadas las 4 pruebas. Listo para el reporte de laboratorio.")
    
    def run_measure_error(self):
        """Envía una configuración articular, espera a que el robot se posicione y calcula el error estacionario"""
        print("\n--- [Medición de Error de Posicionamiento] ---")
        print("Ingrese los ángulos de consigna (en grados) para los 5 motores:")
        try:
            q1 = float(input("  waist (grados): "))
            q2 = float(input("  shoulder (grados): "))
            q3 = float(input("  elbow (grados): "))
            q4 = float(input("  wrist (grados): "))
            q5 = float(input("  gripper (grados): "))
        except ValueError:
            print("Entrada inválida. Operación cancelada.")
            return

        # 1. Empaquetar y convertir consignas a radianes
        target_deg = [q1, q2, q3, q4, q5]
        target_rad = [math.radians(q) for q in target_deg]
        names_to_send = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']

        # Saturación de seguridad
        safe_rad = [self.check_limits_and_saturate(names_to_send[i], target_rad[i]) for i in range(5)]
        
        # 2. Enviar comando físico
        print("\nTransmitiendo consignas al hardware...")
        self.publish_hardware_command(names_to_send, safe_rad)
        
        # 3. Pausa estratégica: Damos tiempo a que los motores venzan la inercia y lleguen al setpoint
        print("Esperando 3 segundos para estabilización del control PID...")
        time.sleep(3.0)
        
        # 4. Lectura de encoders desde el estado interno (actualizado por el callback en 2do plano)
        actual_deg = self.current_joint_angles_deg.copy()
        actual_gripper_deg = math.degrees(self.current_gripper_rad)
        actual_deg.append(actual_gripper_deg) # Añadimos la pinza para tener los 5 valores

        # 5. Cálculo e impresión del error
        print("\n================ RESULTADOS DE MEDICIÓN ================")
        print(f"{'MOTOR':<10} | {'CONSIGNA':>9} | {'ENCODER':>9} | {'ERROR ABSOLUTO':>14}")
        print("-" * 52)
        
        errores = []
        for i, name in enumerate(names_to_send):
            teorico = target_deg[i]
            real = actual_deg[i]
            error = abs(teorico - real)
            errores.append(error)
            print(f"{name:<10} | {teorico:>8.2f}° | {real:>8.2f}° | {error:>13.2f}°")
            
        print("-" * 52)
        error_promedio = sum(errores) / len(errores)
        print(f"Error Absoluto Promedio del Sistema: {error_promedio:.2f}°")
        print("========================================================")

    # ==========================================================
    # MÉTODOS PARA ACTIVIDAD 13: ENSEÑANZA Y REPETICIÓN (YAML)
    # ==========================================================
    def cargar_poses(self):
        """Carga las poses desde el archivo YAML si existe"""
        if os.path.exists(self.poses_file):
            with open(self.poses_file, 'r') as file:
                return yaml.safe_load(file) or {}
        return {}

    def guardar_poses_yaml(self):
        """Sobrescribe el archivo YAML con el diccionario actual de poses"""
        with open(self.poses_file, 'w') as file:
            yaml.dump(self.saved_poses, file, default_flow_style=False)

    def capturar_pose(self, nombre_pose):
        """Lee los encoders actuales y guarda la configuración"""
        # Extraemos los 4 motores en grados y la pinza en grados para el YAML
        config = self.current_joint_angles_deg.copy()
        config.append(math.degrees(self.current_gripper_rad))
        
        # Redondeamos a 2 decimales para que el YAML quede limpio
        config_redondeada = [round(val, 2) for val in config]
        
        self.saved_poses[nombre_pose] = config_redondeada
        self.guardar_poses_yaml()
        print(f"✅ Pose '{nombre_pose}' guardada con éxito en YAML: {config_redondeada}")

    def reproducir_secuencia(self, nombres_poses, tiempo_transicion):
        """Ejecuta una lista de poses respetando el tiempo de transición"""
        print("\n--- INICIANDO REPRODUCCIÓN COREOGRÁFICA ---")
        print("🔴 PRESIONE Ctrl+C EN CUALQUIER MOMENTO PARA DETENER DE EMERGENCIA 🔴")
        try:
            for nombre in nombres_poses:
                if nombre not in self.saved_poses:
                    print(f"Advertencia: La pose '{nombre}' no existe. Saltando...")
                    continue

                print(f"Moviendo a pose: [{nombre}]...")
                target_deg = self.saved_poses[nombre]
                
                # Convertimos el objetivo leído del YAML a radianes para los motores
                target_rad = [math.radians(q) for q in target_deg]
                
                # Capturamos dónde está el robot físicamente en este instante
                current_rad = [math.radians(q) for q in self.current_joint_angles_deg] + [self.current_gripper_rad]

                # Calculamos los pasos para la interpolación lineal
                tasa_refresco = 20.0 # 20 Hz
                pasos = int(tiempo_transicion * tasa_refresco)
                if pasos < 1: pasos = 1
                dt = tiempo_transicion / pasos

                for paso in range(1, pasos + 1):
                    t = paso / pasos
                    interp_rad = []
                    for i in range(5):
                        interp_rad.append(current_rad[i] + t * (target_rad[i] - current_rad[i]))

                    names_to_send = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']
                    safe_rad = [self.check_limits_and_saturate(names_to_send[i], interp_rad[i]) for i in range(5)]
                    self.publish_hardware_command(names_to_send, safe_rad)
                    time.sleep(dt)

                # Pequeña pausa estabilizadora al llegar a la pose
                time.sleep(0.2)

            print("✅ Secuencia finalizada con éxito.")
        except KeyboardInterrupt:
            # Captura el Ctrl+C para cumplir con el requisito 7 (Detener la reproducción)
            print("\n\n[PARADA DE EMERGENCIA] Reproducción detenida por el usuario.")
            print("El robot mantendrá su posición actual por seguridad.")

    def run_actividad_13(self):
        """Sub-menú interactivo para gestionar la enseñanza"""
        while rclpy.ok():
            print("\n--- ACT 13: MODO DE ENSEÑANZA Y REPETICIÓN ---")
            print(f"Poses almacenadas actualmente: {len(self.saved_poses)}")
            print("1. Capturar configuración física actual y nombrar pose")
            print("2. Ver catálogo de poses guardadas en YAML")
            print("3. Reproducir todas las poses guardadas (En orden de registro)")
            print("4. Reproducir una secuencia personalizada")
            print("5. Volver al menú principal")
            
            opc = input("Selección: ").strip()
            
            if opc == '1':
                nombre = input("Ingrese un nombre para esta pose (ej: 'home', 'agarre1', 'arriba'): ").strip()
                if nombre:
                    self.capturar_pose(nombre)
                else:
                    print("Nombre inválido.")
            elif opc == '2':
                print("\nPoses guardadas en 'poses_guardadas.yaml':")
                for k, v in self.saved_poses.items():
                    print(f" - {k}: {v}")
            elif opc == '3':
                if len(self.saved_poses) == 0:
                    print("No hay poses. Agregue poses primero.")
                    continue
                try:
                    t = float(input("Tiempo de transición entre poses (segundos): "))
                    # Reproduce todas las llaves del diccionario en el orden en que se crearon
                    self.reproducir_secuencia(list(self.saved_poses.keys()), t)
                except ValueError:
                    print("Tiempo inválido.")
            elif opc == '4':
                if len(self.saved_poses) == 0:
                    print("No hay poses. Agregue poses primero.")
                    continue
                print(f"Poses disponibles: {', '.join(self.saved_poses.keys())}")
                sec = input("Ingrese los nombres separados por coma (ej: home, agarre1, home): ")
                secuencia = [s.strip() for s in sec.split(',') if s.strip()]
                try:
                    t = float(input("Tiempo de transición entre poses (segundos): "))
                    self.reproducir_secuencia(secuencia, t)
                except ValueError:
                    print("Tiempo inválido.")
            elif opc == '5':
                break
            else:
                print("Opción no válida.")

    # ==========================================================
    # MÉTODOS PARA ACTIVIDAD 14: TRAZADO DE FIGURAS PUNTO A PUNTO Y ARCHIVOS YAML
    # ==========================================================
    def obtener_ruta_yaml_figura(self, nombre):
        """Retorna la ruta absoluta para un archivo YAML individual en la carpeta config"""
        return f'/home/jose-luis/ros2_jazzy/phantom_ws/src/pincher_control/config/{nombre}.yaml'

    def get_ik_segura(self, x, y, z, theta4):
        """Filtra y extrae una configuración articular válida y sin colisiones para un punto (X,Y,Z)"""
        inv = self.tracer.trace_inverse(x, y, z, theta4=theta4)
        if inv['Estado'] == 'Éxito':
            for sol in inv['Soluciones']:
                if not sol['Colision']:
                    config = list(sol['Configuracion'])
                    if len(config) == 3: 
                        config.append(theta4)
                    return config
        return None
    
    def compilar_figura_cartesiana(self):
        """Genera los puntos, resuelve IK, interpola X, Y, Z, THETA4 y PINZA, y guarda en YAML"""
        print("\n--- COMPILADOR DE TRAYECTORIAS Y FIGURAS ---")
        nombre = input("Ingrese el nombre del archivo para guardar (ej. 'circulo', 'ruta1'): ").strip()
        tipo = input("Tipo (cuadrado / triangulo / circulo / iniciales / puntos): ").strip().lower()
        
        # NUEVO FORMATO 6D: (X, Y, Z, theta4_muñeca, pinza, tiempo)
        pts_cartesianos = [] 
        
        # =========================================================
        # MODO 1: INSERCIÓN MANUAL (CONTROL TOTAL DE PINZA POR PUNTO)
        # =========================================================
        if tipo == 'puntos':
            print("\n--- MODO DE INSERCIÓN LIBRE (PUNTO A PUNTO) ---")
            print("Define la posición (X,Y,Z), orientación (Theta4), PINZA y tiempo por cada punto.")
                
            contador = 1
            while True:
                print(f"\nIngresando Punto {contador}:")
                try:
                    px = float(input("  Coordenada X (mm): "))
                    py = float(input("  Coordenada Y (mm): "))
                    pz = float(input("  Coordenada Z (mm): "))
                    p_th4 = float(input("  Ángulo de la muñeca Theta4 (grados): "))
                    p_grip = float(input("  Ángulo de la Pinza (grados) [Ej: 0 cerrado, 50 abierto]: ")) # <-- NUEVO
                    
                    if contador == 1:
                        t_seg = 0.0 # El primer punto es el inicio, no tiene tiempo de llegada
                    else:
                        t_seg = float(input("  Tiempo de transición desde el punto anterior (segundos): "))
                        
                    # Guardamos la tupla con los 6 valores
                    pts_cartesianos.append((px, py, pz, p_th4, p_grip, t_seg))
                    contador += 1
                except ValueError:
                    print("Entrada inválida, no se guardó el punto.")
                    
                cont = input("¿Añadir el siguiente punto? (s/n): ").strip().lower()
                if cont != 's':
                    break
                    
            if len(pts_cartesianos) < 2:
                print("❌ Error: Necesitas ingresar al menos 2 puntos.")
                return

        # =========================================================
        # MODO 2: FIGURAS PREDEFINIDAS
        # =========================================================
        else:
            try:
                cx = float(input("Coordenada X del centro (mm) [Recomendado: 180]: "))
                cy = float(input("Coordenada Y del centro (mm) [Recomendado: 0]: "))
                z_dib = float(input("Altura Z de trazado (mm) [Tocar la hoja]: "))
                size = float(input("Tamaño característico / Lado / Diámetro (mm): "))
                t4 = float(input("Ángulo theta4 de ataque de la muñeca (grados): "))
                p_grip = float(input("Ángulo de la pinza para sostener el marcador (grados): ")) # <-- NUEVO
                
                t_aire = float(input("Tiempo para movimientos en el aire (segundos) [Ej: 1.0]: "))
                t_trazo = float(input("Tiempo por cada trazo en el papel (segundos) [Ej: 2.5]: "))
            except ValueError:
                print("Datos inválidos.")
                return

            z_up = z_dib + 30.0  
            
            # Incorporamos el ángulo de la pinza (p_grip) en todas las tuplas
            if tipo == 'cuadrado':
                d = size / 2.0
                pts_cartesianos = [
                    (cx-d, cy-d, z_up, t4, p_grip, 0.0),            
                    (cx-d, cy-d, z_dib, t4, p_grip, t_aire),        
                    (cx+d, cy-d, z_dib, t4, p_grip, t_trazo),       
                    (cx+d, cy+d, z_dib, t4, p_grip, t_trazo),       
                    (cx-d, cy+d, z_dib, t4, p_grip, t_trazo),       
                    (cx-d, cy-d, z_dib, t4, p_grip, t_trazo),       
                    (cx-d, cy-d, z_up, t4, p_grip, t_aire)          
                ]
            elif tipo == 'triangulo':
                d = size / 2.0
                pts_cartesianos = [
                    (cx-d, cy-d, z_up, t4, p_grip, 0.0), 
                    (cx-d, cy-d, z_dib, t4, p_grip, t_aire),
                    (cx+d, cy-d, z_dib, t4, p_grip, t_trazo), 
                    (cx, cy+d, z_dib, t4, p_grip, t_trazo), 
                    (cx-d, cy-d, z_dib, t4, p_grip, t_trazo), 
                    (cx-d, cy-d, z_up, t4, p_grip, t_aire)
                ]
            elif tipo == 'circulo':
                radio = size / 2.0
                pts_cartesianos.append((cx + radio, cy, z_up, t4, p_grip, 0.0))
                pts_cartesianos.append((cx + radio, cy, z_dib, t4, p_grip, t_aire)) 
                t_segmento_circulo = t_trazo / 4.0 
                for i in range(1, 17): 
                    angulo = (2 * math.pi / 16) * i
                    pts_cartesianos.append((cx + radio * math.cos(angulo), cy + radio * math.sin(angulo), z_dib, t4, p_grip, t_segmento_circulo))
                pts_cartesianos.append((cx + radio, cy, z_up, t4, p_grip, t_aire)) 
            elif tipo == 'iniciales':
                s = size
                pts_cartesianos.extend([
                    (cx-s, cy+s/2, z_up, t4, p_grip, 0.0), (cx-s, cy+s/2, z_dib, t4, p_grip, t_aire), 
                    (cx-s, cy-s/2, z_dib, t4, p_grip, t_trazo), (cx-s/2, cy-s/2, z_dib, t4, p_grip, t_trazo), 
                    (cx-s/2, cy-s/4, z_dib, t4, p_grip, t_trazo), (cx-s/2, cy-s/4, z_up, t4, p_grip, t_aire),
                    (cx+s/4, cy+s/2, z_up, t4, p_grip, t_aire), (cx+s/4, cy+s/2, z_dib, t4, p_grip, t_aire), 
                    (cx+s/4, cy-s/2, z_dib, t4, p_grip, t_trazo), (cx+s*0.8, cy-s/4, z_dib, t4, p_grip, t_trazo), 
                    (cx+s*0.8, cy+s/4, z_dib, t4, p_grip, t_trazo), (cx+s/4, cy+s/2, z_dib, t4, p_grip, t_trazo), 
                    (cx+s/4, cy+s/2, z_up, t4, p_grip, t_aire)
                ])
            else:
                print("Figura no reconocida.")
                return

        # =========================================================
        # COMPILACIÓN CINEMÁTICA Y GUARDADO
        # =========================================================
        print(f"\nCalculando cinemática inversa e interpolación completa (Brazo + Orientación + Pinza)...")
        trayectoria_articular = []

        for i in range(len(pts_cartesianos) - 1):
            p_actual = pts_cartesianos[i]
            p_siguiente = pts_cartesianos[i+1]
            
            # Desempaquetamos los 6 valores
            x1, y1, z1, th4_1, grip_1, _ = p_actual
            x2, y2, z2, th4_2, grip_2, tiempo_segmento = p_siguiente
            
            q1 = self.get_ik_segura(x1, y1, z1, th4_1)
            q2 = self.get_ik_segura(x2, y2, z2, th4_2)
            
            if not q1 or not q2:
                print(f"❌ Error cinemático en el tramo de {p_actual[:3]} a {p_siguiente[:3]}.")
                return

            # Agregamos la pinza a los arreglos de ángulos ANTES de enviar al interpolador
            q1.append(grip_1)
            q2.append(grip_2)

            steps = max(int(tiempo_segmento / 0.05), 2)
            dt_calculado = tiempo_segmento / steps
            
            # El interpolador ahora procesa arreglos de 5 elementos (base, hombro, codo, muñeca, pinza)
            segmento, _ = self.tracer.interpolar_trayectoria(q1, q2, steps=steps, method='lineal', validar_colisiones=False)
            
            start_idx = 0 if i == 0 else 1
            for q in segmento[start_idx:]:
                q_full = list(q)
                
                # El 6to elemento es el tiempo dt para la reproducción
                q_full.append(round(dt_calculado, 4)) 
                
                trayectoria_articular.append([round(x, 4) for x in q_full])

        ruta_archivo = self.obtener_ruta_yaml_figura(nombre)
        with open(ruta_archivo, 'w') as file:
            yaml.dump(trayectoria_articular, file, default_flow_style=False)
            
        print(f"✅ ¡Compilación exitosa! Trama guardada en:\n{ruta_archivo}")

    def dibujar_trayectoria_yaml(self):
        """Lee un archivo YAML, decodifica posiciones y perfiles, y ejecuta el trazado (Normal o Cíclico)"""
        ruta_busqueda = '/home/jose-luis/ros2_jazzy/phantom_ws/src/pincher_control/config/*.yaml'
        archivos_disponibles = [os.path.basename(f) for f in glob.glob(ruta_busqueda)]
        
        if not archivos_disponibles:
            print("No se encontraron archivos .yaml en la carpeta config.")
            return
            
        print("\n--- ARCHIVOS DE TRAYECTORIA DISPONIBLES ---")
        for f in archivos_disponibles:
            if f != 'poses_guardadas.yaml':
                print(f" - {f.replace('.yaml', '')}")
                
        nombre = input("\nIngrese el nombre del archivo a trazar: ").strip()
        ruta_archivo = self.obtener_ruta_yaml_figura(nombre)
        
        if not os.path.exists(ruta_archivo):
            print("❌ El archivo solicitado no existe.")
            return
            
        with open(ruta_archivo, 'r') as file:
            trayectoria = yaml.safe_load(file)
            
        # --- NUEVO: PREGUNTA AL USUARIO POR EL MODO CÍCLICO ---
        ciclico = input("¿Desea ejecutar esta trayectoria en bucle infinito? (s/n): ").strip().lower()
        es_ciclico = (ciclico == 's')
        
        print(f"\nIniciando trazado de '{nombre}'...")
        if es_ciclico:
            print("🔴 MODO CÍCLICO ACTIVADO: PRESIONE [Ctrl+C] EN CUALQUIER MOMENTO PARA DETENER 🔴")
            
        try:
            # Bucle infinito controlado
            while True:
                for config in trayectoria:
                    # Los primeros 5 elementos son las articulaciones
                    rad_joints = [math.radians(ang) for ang in config[:5]]
                    
                    # El 6to elemento es el tiempo (Retrocompatibilidad: si no existe, asume 0.05s)
                    dt_frame = config[5] if len(config) >= 6 else 0.05
                    
                    names_to_send = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']
                    safe_rad = [self.check_limits_and_saturate(names_to_send[i], rad_joints[i]) for i in range(5)]
                    
                    self.publish_hardware_command(names_to_send, safe_rad)
                    time.sleep(dt_frame) # Espera dinámica que permite variar la velocidad
                
                # Si el usuario no eligió el modo cíclico, rompemos el bucle al terminar la primera pasada
                if not es_ciclico:
                    break
                else:
                    # Pequeña pausa estabilizadora de medio segundo antes de reiniciar el ciclo
                    time.sleep(0.5)
                    
            print("✅ Trazado finalizado con éxito.")
            
        except KeyboardInterrupt:
            # --- NUEVO: CAPTURA DEL COMANDO DE PARADA ---
            print("\n\n[PARADA ACEPTADA] Reproducción cíclica detenida por el usuario.")
            print("El Phantom mantendrá su posición actual por seguridad.")



    def run_actividad_14(self):
        """Sub-menú interactivo para el trazado de figuras y rutas"""
        while rclpy.ok():
            print("\n--- ACT 14: DIBUJO DE TRAYECTORIAS CARTESIANAS ---")
            print("1. Crear, compilar y guardar nueva figura en archivo .yaml")
            print("2. Cargar archivo .yaml y ejecutar trazado en el robot")
            print("3. Volver al menú principal")
            
            opc = input("Selección: ").strip()
            if opc == '1':
                self.compilar_figura_cartesiana()
            elif opc == '2':
                self.dibujar_trayectoria_yaml()
            elif opc == '3':
                break
            else:
                print("Opción no válida.")