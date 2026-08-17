import rclpy
import numpy as np
from pincher_lab_utils import PincherLab, JOINTS

def main():
    # 1. Inicializar ROS2 y crear el nodo del robot
    rclpy.init()
    node = PincherLab()
    
    # 2. Definimos las 5 configuraciones en grados
    configuraciones_grados = [
        [0, 0, 0, 0, 0],            # Configuración 1
        [25, 25, 20, -20, 0],        # Configuración 2
        [-35, 35, -30, 30, 0],      # Configuración 3
        [85, -20, 55, 25, 0],       # Configuración 4
        [80, -35, 55, -45, 0],       # Configuración 5
        [0, 0, 0, 0, 0]
    ]
    
    # 3. Recorremos las configuraciones una por una con un bucle
    for config in configuraciones_grados:
        print(f"Moviendo a configuración: {config}")
        
        # Creamos un diccionario vacío para armar la postura actual
        comando_simultaneo = {}
        
        # Usamos un bucle por índice (0 a 4) para relacionar cada articulación con su ángulo
        for i in range(len(JOINTS)):
            nombre_articulacion = JOINTS[i]
            angulo_grados = config[i]
            
            # Convertimos el ángulo de grados a radianes
            angulo_radianes = angulo_grados * np.pi / 180.0
            
            # Guardamos el valor en el diccionario de comandos
            comando_simultaneo[nombre_articulacion] = angulo_radianes
            
        # Enviamos todas las posiciones a la vez para lograr el movimiento simultáneo
        node.send(comando_simultaneo)
        
        # Esperamos 2 segundos para dar tiempo a que el robot complete el movimiento
        node.spin_for(2.0)
        
    # 4. Cerrar el nodo de forma limpia al finalizar todas las pruebas
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()