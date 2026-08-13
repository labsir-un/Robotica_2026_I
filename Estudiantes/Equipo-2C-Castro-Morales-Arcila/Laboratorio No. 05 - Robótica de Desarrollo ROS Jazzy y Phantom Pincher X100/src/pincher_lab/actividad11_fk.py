import rclpy
import time
import numpy as np
from pincher_lab_utils import PincherLab, JOINTS

def calcular_cinematica_directa(q1, q2, q3, q4):

    c1 = np.cos(q1)
    s1 = np.sin(q1)
    c234 = np.cos(q2 + q3 + q4)
    s234 = np.sin(q2 + q3 + q4)
    
    # Ecuaciones de tu hoja en metros
    rho = 0.10595 * np.cos(q2) + 0.100 * np.cos(q2 + q3)
    x = rho * c1
    y = rho * s1
    z = 0.08945 + 0.10595 * np.sin(q2) + 0.100 * np.sin(q2 + q3)
    
    # Orientación
    roll  = np.arctan2(0.0, -c234)
    pitch = np.arctan2(-s234, np.sqrt((c1 * c234)**2 + (s1 * c234)**2))
    yaw   = np.arctan2(s1 * c234, c1 * c234)
    
    return x, y, z, roll, pitch, yaw


def main():
    rclpy.init()
    node = PincherLab()
    
    # Espera de cortesía de 1 segundo para asegurar la conexión de red en ROS2
    node.spin_for(1.0)
    
    # Las 5 configuraciones de la Actividad 7 en grados
    configuraciones_grados = [
        [0, 0, 0, 0, 0],            # Configuración 1
        [25, 25, 20, -20, 0],       # Configuración 2 (La que simularemos)
        [-35, 35, -30, 30, 0],      # Configuración 3
        [85, -20, 55, 25, 0],       # Configuración 4
        [80, -35, 55, -45, 0]       # Configuración 5
    ]
    
    print("CINEMÁTICA DIRECTA ")
    numero_config = 1
    for config in configuraciones_grados:
        q1 = config[0] * np.pi / 180.0
        q2 = config[1] * np.pi / 180.0
        q3 = config[2] * np.pi / 180.0
        q4 = config[3] * np.pi / 180.0
        
        x, y, z, r, p, y_ang = calcular_cinematica_directa(q1, q2, q3, q4)
        
        print(f"\nConfiguración #{numero_config}: Grados = {config[:4]}")
        print(f"  -> X = {x:.4f} m, Y = {y:.4f} m, Z = {z:.4f} m")
        print(f"  -> Roll = {r:.4f} rad, Pitch = {p:.4f} rad, Yaw = {y_ang:.4f} rad")
        print("-" * 70)
        numero_config += 1
        
    print("\nSIMULACIÓN EN TIEMPO REAL")
    print("Enviando Configuración #2 de forma continua al simulador...")
    
    # Preparamos el comando de la Configuración 2
    config_objetivo = configuraciones_grados[1]
    comando_movimiento = {}
    for i in range(len(JOINTS)):
        nombre_articulacion = JOINTS[i]
        comando_movimiento[nombre_articulacion] = config_objetivo[i] * np.pi / 180.0
        
    # ENVIAR EN UN BUCLE ACTIVO DURANTE 4 SEGUNDOS
    # Esto fuerza al simulador a recibir la orden constantemente y moverse sí o sí
    t0 = time.time()
    while (time.time() - t0) < 20.0:
        node.send(comando_movimiento)
        node.spin_for(0.05)  # Envía la posición cada 0.05 segundos (20 Hz)
        
    # Retorno automático a Home de forma continua por 2 segundos
    print("\nPrueba finalizada. Regresando a posición de referencia (Home)...")
    home = {}
    for j in JOINTS:
        home[j] = 0.0
        
    t1 = time.time()
    while (time.time() - t1) < 2.0:
        node.send(home)
        node.spin_for(0.05)
    
    # Apagar el sistema de forma limpia
    node.destroy_node()
    rclpy.shutdown()
    print("Proceso terminado con éxito.")

if __name__ == '__main__':
    main()