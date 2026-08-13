import rclpy
import numpy as np
import time
from pincher_lab_utils import PincherLab, JOINTS, LIMITS

# Dimensiones del robot en metros
L1 = 0.08945
L2 = 0.100
Lm = 0.035
L3 = 0.100
L4 = 0.12915

# Constantes geometricas calculadas
Lr = np.sqrt(L2**2 + Lm**2)
beta = np.arctan2(Lm, L2)
psi = (np.pi / 2.0) - beta

def ik_exacto_usuario(xT, yT, zT, theta):
    """Calculo de cinematica inversa analitica basada en desacople de muneca"""
    q1 = np.arctan2(yT, xT)
    
    # Vector de aproximacion
    ax = np.sin(theta) * np.cos(q1)
    ay = np.sin(theta) * np.sin(q1)
    az = np.cos(theta)
    
    # Posicion del centro de la muneca (p_w)
    xw = xT - L4 * ax
    yw = yT - L4 * ay
    zw = zT - L4 * az
    
    r = np.sqrt(xw**2 + yw**2)
    h = zw - L1
    c = np.sqrt(r**2 + h**2)
    
    # Verificacion de alcance geometrico
    if (c < np.abs(Lr - L3)) or (c > (Lr + L3)):
        return None, None
        
    phi = np.arccos((Lr**2 + L3**2 - c**2) / (2.0 * Lr * L3))
    alpha = np.arccos((Lr**2 + c**2 - L3**2) / (2.0 * Lr * c))
    gamma = np.arctan2(h, r)
    
    # Configuracion codo arriba
    q2_arriba = (np.pi / 2.0) - beta - alpha - gamma
    q3_arriba = np.pi - psi - phi
    q4_arriba = theta - q2_arriba - q3_arriba - (np.pi / 2.0)
    
    # Configuracion codo abajo
    q2_abajo = (np.pi / 2.0) - (gamma - alpha + beta)
    q3_abajo = -np.pi + (phi - psi)
    q4_abajo = theta - q2_abajo - q3_abajo - (np.pi / 2.0)
    
    # Ajuste de angulos al rango [-pi, pi)
    sol_arriba = [q1, np.arctan2(np.sin(q2_arriba), np.cos(q2_arriba)), 
                      np.arctan2(np.sin(q3_arriba), np.cos(q3_arriba)), 
                      np.arctan2(np.sin(q4_arriba), np.cos(q4_arriba))]
                      
    sol_abajo  = [q1, np.arctan2(np.sin(q2_abajo), np.cos(q2_abajo)), 
                      np.arctan2(np.sin(q3_abajo), np.cos(q3_abajo)), 
                      np.arctan2(np.sin(q4_abajo), np.cos(q4_abajo))]
                      
    return sol_arriba, sol_abajo

def validar_por_cinematica_directa_exacta(q):
    """Calculo de cinematica directa para comprobar la consistencia de la IK"""
    q1, q2, q3, q4 = q
    
    phi = np.pi - psi - q3
    c2 = Lr**2 + L3**2 - 2.0 * Lr * L3 * np.cos(phi)
    c = np.sqrt(c2)
    
    alpha = np.arccos((Lr**2 + c**2 - L3**2) / (2.0 * Lr * c))
    gamma = (np.pi / 2.0) - beta - alpha - q2
    
    r = c * np.cos(gamma)
    h = c * np.sin(gamma)
    
    xw = r * np.cos(q1)
    yw = r * np.sin(q1)
    zw = h + L1
    
    theta_total = q2 + q3 + q4 + (np.pi / 2.0)
    
    x = xw + L4 * np.sin(theta_total) * np.cos(q1)
    y = yw + L4 * np.sin(theta_total) * np.sin(q1)
    z = zw + L4 * np.cos(theta_total)
    
    return x, y, z

def evaluar_limites(q):
    """Verifica si los angulos estan dentro de los limites de los motores"""
    for i in range(4):
        j = JOINTS[i]
        lo, hi = LIMITS[j]
        if not (lo <= q[i] <= hi):
            return False
    return True

def main():
    rclpy.init()
    node = PincherLab()
    node.spin_for(1.0)
    
    # Puntos de prueba cartesianos (X, Y, Z, Theta)
    puntos = [
        (0.15, 0.05, 0.15, 0.3),
        (0.20, 0.00, 0.10, 0.5),
        (0.05, 0.15, 0.20, -0.2),
        (0.12, -0.06, 0.14, 0.1),
        (0.40, 0.40, 0.40, 0.0)
    ]
    
    print("=== Evaluacion de Cinematica Inversa ===")
    
    for x, y, z, th in puntos:
        print(f"\nObjetivo: X={x}, Y={y}, Z={z} | Theta={th}")
        
        # Lectura de la posicion articular actual
        q_act = [node.current[j] for j in JOINTS[:4]]
        
        # Calculo de soluciones geometricas
        sol_arriba, sol_abajo = ik_exacto_usuario(x, y, z, th)
        
        if sol_arriba is None:
            print("  Aviso: Punto fuera del espacio de trabajo.")
            continue
            
        # Validacion de limites articulares
        valida_arriba = evaluar_limites(sol_arriba)
        valida_abajo = evaluar_limites(sol_abajo)
        
        # Seleccion de solucion por cercania angular
        q_ejecutar = None
        
        if valida_arriba and valida_abajo:
            d_arriba = np.linalg.norm(np.array(sol_arriba) - np.array(q_act))
            d_abajo = np.linalg.norm(np.array(sol_abajo) - np.array(q_act))
            if d_arriba <= d_abajo:
                q_ejecutar = sol_arriba
                print("  Seleccion: Codo Arriba (menor distancia).")
            else:
                q_ejecutar = sol_abajo
                print("  Seleccion: Codo Abajo (menor distancia).")
        elif valida_arriba:
            q_ejecutar = sol_arriba
            print("  Seleccion: Codo Arriba (Codo Abajo fuera de limites).")
        elif valida_abajo:
            q_ejecutar = sol_abajo
            print("  Seleccion: Codo Abajo (Codo Arriba fuera de limites).")
        else:
            print("  Aviso: Ambas soluciones estan fuera de los limites fisicos.")
            continue
            
        # Comprobacion interna mediante cinematica directa
        x_c, y_c, z_c = validar_por_cinematica_directa_exacta(q_ejecutar)
        error_geom = np.sqrt((x - x_c)**2 + (y - y_c)**2 + (z - z_c)**2)
        print(f"  Validacion DK: X={x_c:.4f}, Y={y_c:.4f}, Z={z_c:.4f}")
        print(f"  Error geometrico: {error_geom:.6f} m")
        
        # Envio de comandos al simulador por 2 segundos
        print("  Enviando comando a RViz...")
        comando = dict(zip(JOINTS[:4], q_ejecutar))
        t0 = time.time()
        while (time.time() - t0) < 2.0:
            node.send(comando)
            node.spin_for(0.05)
            
    # Retorno obligatorio utilizando las llaves nativas de JOINTS
    print("\nFinalizando trayectoria. Regresando a posicion Home...")
    home = dict(zip(JOINTS[:4], [0.0, 0.0, 0.0, 0.0]))
    t_home = time.time()
    while (time.time() - t_home) < 2.0:
        node.send(home)
        node.spin_for(0.05)
        
    node.destroy_node()
    rclpy.shutdown()
    print("Proceso finalizado.")

if __name__ == '__main__':
    main()