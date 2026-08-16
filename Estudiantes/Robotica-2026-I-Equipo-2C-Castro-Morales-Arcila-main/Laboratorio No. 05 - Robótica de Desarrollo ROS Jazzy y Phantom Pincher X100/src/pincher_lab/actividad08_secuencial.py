import rclpy
import numpy as np
from pincher_lab_utils import PincherLab, JOINTS

def main():
    # 1. Inicializar ROS2 y el nodo del robot
    rclpy.init()
    node = PincherLab()
    
    # 2. Definimos la configuración elegida en grados (Configuración #2)
    config_grados = [25, 25, 20, -20, 0]
    
    # 3. Convertimos los grados a radianes
    posiciones_objetivo = {}
    for i in range(len(JOINTS)):
        nombre_articulacion = JOINTS[i]
        grados = config_grados[i]
        radianes = grados * np.pi / 180.0
        posiciones_objetivo[nombre_articulacion] = radianes

    print("--- INICIANDO MOVIMIENTO SECUENCIAL ---")

    # 4. Bucle para mover secuencialmente cada articulación una por una
    for j in JOINTS:
        print(f"Moviendo la articulación de forma aislada: {j}")
        
        # Leemos la postura actual del robot
        comando_paso = node.current.copy()
        
        # Modificamos únicamente la articulación de este turno
        comando_paso[j] = posiciones_objetivo[j]
        
        # Enviamos el comando y esperamos 1.5 segundos
        node.send(comando_paso)
        node.spin_for(1.5)
        
    print("--- MOVIMIENTO SECUENCIAL FINALIZADO ---")
    
    # REGRESO A HOME
    print("Regresando a la posición de referencia (Home)...")
    
    # Creamos el diccionario de home con todas las articulaciones en cero
    home = {}
    for articulacion in JOINTS:
        home[articulacion] = 0.0
        
    # Enviamos al robot a home y esperamos 2.0 segundos para que termine de llegar
    node.send(home)
    node.spin_for(2.0)
        
    # 5. Apagar el nodo de forma limpia
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()