import rclpy
import numpy as np
import time
from pincher_lab_utils import PincherLab, JOINTS
from actividad12_ik import ik_exacto_usuario, evaluar_limites

def obtener_mejor_solucion(x, y, z, th, q_act):
    """Calcula las soluciones y selecciona la mas cercana sin violar limites"""
    sol_arriba, sol_abajo = ik_exacto_usuario(x, y, z, th)
    if sol_arriba is None:
        return None
        
    valida_arriba = evaluar_limites(sol_arriba)
    valida_abajo = evaluar_limites(sol_abajo)
    
    if valida_arriba and valida_abajo:
        d_arriba = np.linalg.norm(np.array(sol_arriba) - np.array(q_act))
        d_abajo = np.linalg.norm(np.array(sol_abajo) - np.array(q_act))
        return sol_arriba if d_arriba <= d_abajo else sol_abajo
    elif valida_arriba:
        return sol_arriba
    elif valida_abajo:
        return sol_abajo
    return None

def main():
    rclpy.init()
    node = PincherLab()
    node.spin_for(1.0)
    
    waypoints = [
        (0.15, -0.03, 0.05, 1.5708),  # Esquina 1 (Inicio)
        (0.21, -0.03, 0.05, 1.5708),  # Esquina 2
        (0.21,  0.03, 0.05, 1.5708),  # Esquina 3
        (0.15,  0.03, 0.05, 1.5708),  # Esquina 4
        (0.15, -0.03, 0.05, 1.5708)   # Cierre del cuadrado (Regreso a Esquina 1)
    ]
    
    print("=== Iniciando Trazado Manual ===")
    for x, y, z, th in waypoints:
        q_act = [node.current[j] for j in JOINTS[:4]]
        sol = obtener_mejor_solucion(x, y, z, th, q_act)
        
        if sol is None:
            print(f"Punto inalcanzable o fuera de limites: X={x}, Y={y}, Z={z}")
            continue
            
        q_inicio = {j: node.current[j] for j in JOINTS[:4]}
        q_destino = dict(zip(JOINTS[:4], sol))
        
        node.interp_quintica(q_inicio, q_destino, 1.5)
        node.spin_for(0.05)
        
    print("\nTrayectoria completa. Regresando a posicion Home...")
    q_actual = {j: node.current[j] for j in JOINTS[:4]}
    q_home = {j: 0.0 for j in JOINTS[:4]}
    node.interp_quintica(q_actual, q_home, 2.0)
    
    node.destroy_node()
    rclpy.shutdown()
    print("Proceso finalizado.")

if __name__ == '__main__':
    main()