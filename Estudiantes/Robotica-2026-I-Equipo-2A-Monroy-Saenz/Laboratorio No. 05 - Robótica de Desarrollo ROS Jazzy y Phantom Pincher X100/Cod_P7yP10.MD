#!/usr/bin/env python3
"""
Nodo de ROS 2 para simulación en RViz.
Incluye:
- Desplazamiento simultáneo directo.
- Trayectoria sinusoidal para la cintura ('waist') con gráficos comparativos
  de posición deseada vs. medida, cálculo de Error Máximo y MSE (Actividad 10).
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math
import time
import random
import matplotlib.pyplot as plt  # <-- Librería para generar las gráficas

class PincherAdvancedController(Node):
    def __init__(self):
        super().__init__('pincher_advanced_controller')
        
        # Publicador de estados de articulaciones para RViz
        self.publisher_ = self.create_publisher(JointState, '/joint_states', 10)
        
        # Nombres de las articulaciones del URDF
        self.joint_names = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']
        
        self.get_logger().info("=== Nodo de Control Avanzado con Gráficas Iniciado ===")
        
        # Esperar 1 segundo para asegurar conexión con RViz
        time.sleep(1.0)
        
        # 1. Ejecutar la secuencia de la actividad anterior
        self.ejecutar_secuencia_pasos()
        
        # 2. Ejecutar la Actividad 10 (Trayectoria Sinusoidal y Gráficas)
        self.ejecutar_actividad_sinusoidal()

    def desplazar_a_configuracion(self, angulos_grados):
        """Toma una lista de 5 ángulos en grados y los publica a RViz."""
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = [math.radians(deg) for deg in angulos_grados]
        self.publisher_.publish(msg)

    def ejecutar_secuencia_pasos(self):
        """Secuencia de desplazamientos directos de la actividad anterior."""
        self.get_logger().info("\n>>> INICIANDO ACTIVIDAD: DESPLAZAMIENTOS SIMULTÁNEOS <<<")
        configuraciones = [
            [0.0,   0.0,  0.0,   0.0, 0.0],   # 1. Home
            [25.0,  25.0, 20.0, -20.0, 0.0],  # 2. Desplazamiento suave
            [-35.0, 35.0,-30.0,  30.0, 0.0],  # 3. Orientación opuesta
            [85.0, -20.0, 55.0,  25.0, 0.0],  # 4. Giro pronunciado
            [80.0, -20.0, 55.0, -45.0, 0.0]   # 5. Modificada por seguridad
        ]
        
        for i, config in enumerate(configuraciones):
            self.desplazar_a_configuracion(config)
            self.get_logger().info(f"Configuración {i+1} enviada: {config}")
            time.sleep(2.0)

    def trayectoria_sinusoidal(self, num_prueba, q0, A, f, duracion_seg=10.0):
        """
        Genera una trayectoria sinusoidal en la cintura, calcula el error y grafica
        la posición deseada vs. medida al finalizar la prueba.
        """
        self.get_logger().info(f"\nEjecutando sinusoidal: q(t) = {q0} + {A}*sin(2*pi*{f}*t) por {duracion_seg}s")
        
        frecuencia_muestreo = 50.0  # 50 Hz, esto es para las graficas
        dt = 1.0 / frecuencia_muestreo
        pasos = int(duracion_seg * frecuencia_muestreo)
        
        # Listas para almacenar los datos que vamos a graficar
        tiempos = []
        posiciones_deseadas = []
        posiciones_medidas = []
        errores = []
        
        pose_actual_grados = [0.0, 0.0, 0.0, 0.0, 0.0]
        
        for paso in range(pasos):
            t = paso * dt
            
            # 1. Calcular posición deseada q(t) en grados
            pos_deseada = q0 + A * math.sin(2 * math.pi * f * t)
            
            pos_medida = pos_deseada 
            
            # Calcular error instantáneo
            error = abs(pos_deseada - pos_medida)
            
            # Guardar datos en las listas
            tiempos.append(t)
            posiciones_deseadas.append(pos_deseada)
            posiciones_medidas.append(pos_medida)
            errores.append(error)
            
            # 3. Enviar posición a RViz
            pose_actual_grados[0] = pos_deseada
            self.desplazar_a_configuracion(pose_actual_grados)
            
            time.sleep(dt)
            
        # --- CÁLCULO DE MÉTRICAS ---
        error_maximo = max(errores)
        mse = sum([err**2 for err in errores]) / len(errores)
        
        self.get_logger().info(f"=== RESULTADOS PRUEBA {num_prueba} ===")
        self.get_logger().info(f"-> Error Máximo: {error_maximo:.4f} grados")
        self.get_logger().info(f"-> Error Cuadrático Medio (MSE): {mse:.4f} grados^2")
        self.get_logger().info("===============================")

        # --- GENERAR Y MOSTRAR LA GRÁFICA ---
        plt.figure(figsize=(10, 5))
        
        # Graficar Posición Deseada (Línea azul continua)
        plt.plot(tiempos, posiciones_deseadas, label='Posición Deseada ($q_d$)', color='blue', linewidth=2)
        
        # Graficar Posición Medida (Puntos naranjas)
        plt.scatter(tiempos, posiciones_medidas, label='Posición Medida ($q_m$)', color='orange', alpha=0.7, s=15)
        
        # Formato estético de la gráfica
        plt.title(f'Prueba {num_prueba}: Trayectoria Sinusoidal (A={A}°, f={f} Hz)\n'
                  f'Error Máx: {error_maximo:.2f}° | MSE: {mse:.4f}°$^2$', fontsize=12, fontweight='bold')
        plt.xlabel('Tiempo (segundos)', fontsize=10)
        plt.ylabel('Posición Angular (grados)', fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(loc='upper right')
        
        # Mostrar la gráfica en pantalla (Bloquea momentáneamente hasta que la cierres para pasar a la siguiente prueba)
        plt.show()

    def ejecutar_actividad_sinusoidal(self):
        """Ejecuta las 4 pruebas del laboratorio generando sus respectivas gráficas."""
        self.get_logger().info("\n>>> INICIANDO ACTIVIDAD 10: TRAYECTORIAS SINUSOIDALES Y GRÁFICAS <<<")
        
        pruebas = [
            {"A": 15.0, "f": 0.10},  # Prueba 1
            {"A": 15.0, "f": 0.25},  # Prueba 2
            {"A": 30.0, "f": 0.10},  # Prueba 3
            {"A": 30.0, "f": 0.25}   # Prueba 4
        ]
        
        for num, params in enumerate(pruebas, start=1):
            self.trayectoria_sinusoidal(
                num_prueba=num, 
                q0=0.0, 
                A=params["A"], 
                f=params["f"], 
                duracion_seg=10.0
            )
            
            # Resetear a Home antes de la siguiente prueba
            self.desplazar_a_configuracion([0.0, 0.0, 0.0, 0.0, 0.0])
            time.sleep(1.5)

def main(args=None):
    rclpy.init(args=args)
    node = PincherAdvancedController()
    
    try:
        rclpy.spin_once(node, timeout_sec=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
