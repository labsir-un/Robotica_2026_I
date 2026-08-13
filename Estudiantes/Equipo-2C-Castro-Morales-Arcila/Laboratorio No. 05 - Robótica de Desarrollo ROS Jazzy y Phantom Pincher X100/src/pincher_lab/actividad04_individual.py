import rclpy
import numpy as np
from pincher_lab_utils import PincherLab, JOINTS

# FUNCIÓN PARA LA OPCIÓN MANUAL
def movimiento_manual(node, home):
    print("\n--- CONTROL MANUAL ---")
    print(f"Articulaciones disponibles: {JOINTS}")
    
    # 1. Pedimos al usuario que escriba la articulación
    articulacion = input("Escribe el nombre de la articulación a mover: ").strip()
    
    # Validamos que lo que escribió exista en el robot
    if articulacion not in JOINTS:
        print("Error: Esa articulación no existe.")
        return # Regresa al menú principal
        
    # 2. Pedimos el ángulo en grados
    try:
        grados = float(input(f"Introduce el ángulo en GRADOS para '{articulacion}': "))
    except ValueError:
        print("Error: Debes introducir un número válido.")
        return

    # 3. Convertimos a radianes
    radianes = grados * np.pi / 180.0
    if articulacion == 'gripper':
        radianes = radianes * 0.4 # Ajuste para la pinza
        
    # 4. Preparamos el comando y movemos el robot
    comando = home.copy()
    comando[articulacion] = radianes
    
    print(f"Moviendo {articulacion} a {grados}°...")
    node.send(comando)
    node.spin_for(2.0) # Esperamos 2 segundos en esa pose
    
    # 5. Regresamos a la posición de referencia
    print("Regresando a posición de referencia (Home)...")
    node.send(home)
    node.spin_for(1.5)


# --- FUNCIÓN PARA EL TEST AUTOMÁTICO ---
def prueba_automatica(node, home):
    print("\n--- INICIANDO TEST AUTOMÁTICO ---")
    angulos_grados = [20, -20, 35]
    
    for j in JOINTS:
        print(f"\nProbando articulación de forma independiente: {j}")
        for g in angulos_grados:
            radianes = g * np.pi / 180.0
            if j == 'gripper':
                radianes = radianes * 0.4
                
            comando_movimiento = home.copy()
            comando_movimiento[j] = radianes
            
            node.send(comando_movimiento)
            node.spin_for(1.0)
            
        # Regresa a Home tras probar las 3 posiciones de esta articulación
        print(f"Regresando {j} a posición de referencia...")
        node.send(home)
        node.spin_for(1.0)
    print("\n--- TEST AUTOMÁTICO FINALIZADO ---")


# --- FUNCIÓN PRINCIPAL ---
def main():
    rclpy.init()
    node = PincherLab()
    
    # Definimos la posición de referencia (Home) con todos los joints en 0.0
    home = {}
    for articulacion in JOINTS:
        home[articulacion] = 0.0

    # Bucle del menú principal
    while rclpy.ok():
        print("\n================ MENÚ DE CONTROL ================")
        print("1. Seleccionar articulación y ángulo manualmente")
        print("2. Ejecutar prueba automática")
        print("3. Salir del programa")
        
        opcion = input("Elige una opción (1, 2 o 3): ").strip()
        
        if opcion == "1":
            movimiento_manual(node, home)
        elif opcion == "2":
            prueba_automatica(node, home)
        elif opcion == "3":
            print("Cerrando el programa...")
            break
        else:
            print("Opción no válida. Intenta de nuevo.")

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()