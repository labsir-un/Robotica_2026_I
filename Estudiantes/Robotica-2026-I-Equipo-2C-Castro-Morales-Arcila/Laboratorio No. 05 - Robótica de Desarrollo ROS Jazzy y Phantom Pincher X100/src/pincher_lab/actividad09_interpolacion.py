import rclpy
import numpy as np
import matplotlib.pyplot as plt  # <--- Librería para graficar
from pincher_lab_utils import PincherLab, JOINTS

def main():
    # 1. Inicializar ROS2 y crear el nodo del robot
    rclpy.init()
    node = PincherLab()
    
    # Definimos la posición HOME (0.0)
    home = {}
    for j in JOINTS:
        home[j] = 0.0
        
    # Definimos la posición lejana (qf) en radianes
    valores_finales = [1.2, -0.8, 0.9, 0.5, 0.3]
    posicion_final = {}
    for i in range(len(JOINTS)):
        posicion_final[JOINTS[i]] = valores_finales[i]
        
    tiempo_trayectoria = 3.0  # Duración de cada tramo (3 segundos)
    
    # 2. EJECUCIÓN EN EL ROBOT
    print("1. Moviendo hacia adelante con Interpolación Lineal...")
    node.interp_lineal(home, posicion_final, tiempo_trayectoria)
    node.spin_for(1.0) # Pausa de 1 segundo
    
    print("2. Regresando a HOME con Interpolación Quíntica...")
    node.interp_quintica(posicion_final, home, tiempo_trayectoria)
    
    # Comando de seguridad para asegurar que quede en HOME antes de apagar
    node.send(home)
    node.spin_for(1.0)
    
    # 3. GENERACIÓN DE LAS GRÁFICAS PARA EL REPORTE
    print("\nCalculando datos matemáticos para generar la gráfica...")
    
    # Creamos un eje de tiempo simulado de 100 puntos para cada tramo
    t_tramo1 = np.linspace(0, tiempo_trayectoria, 100)
    t_tramo2 = np.linspace(0, tiempo_trayectoria, 100)
    
    # Para que la gráfica no sea un caos de líneas, graficaremos la articulación 'base'
    # como muestra representativa (va de 0.0 a 1.2 radianes y regresa)
    qi_base = 0.0
    qf_base = 1.2
    
    # Tramo 1: Ecuación matemática de la Interpolación Lineal
    pos_lineal = qi_base + ((qf_base - qi_base) / tiempo_trayectoria) * t_tramo1
    
    # Tramo 2: Ecuación matemática de la Interpolación Quíntica (Polinomio de 5to grado)
    # Fórmula estandarizada: s(t) = 10t^3 - 15t^4 + 6t^5
    tau = t_tramo2 / tiempo_trayectoria
    polinomio_s = 10 * (tau**3) - 15 * (tau**4) + 6 * (tau**5)
    pos_quintica = qf_base + (qi_base - qf_base) * polinomio_s
    
    # Unimos ambos tramos para crear una trayectoria continua de 6 segundos en total
   # Desplazamos el tiempo del segundo tramo para que empiece en 3.0 segundos
    t_tramo2_ajustado = t_tramo2 + tiempo_trayectoria
    
    # Unimos ambos tramos de tiempo y posición en trayectorias continuas
    tiempo_total = np.concatenate((t_tramo1, t_tramo2_ajustado))
    posicion_total = np.concatenate((pos_lineal, pos_quintica))
    
    # Configuración de la ventana de Matplotlib
    plt.figure(figsize=(9, 5))
    plt.plot(tiempo_total, posicion_total, label="Articulación Base", color="blue", linewidth=2.5)
    
    # Dibujamos una línea roja discontinua para marcar justo dónde cambia el método
    plt.axvline(x=tiempo_trayectoria, color="red", linestyle="--", label="Cambio de Método (t = 3s)")
    
    # Títulos y nombres de los ejes
    plt.title("Actividad 9: Posición Angular vs Tiempo")
    plt.xlabel("Tiempo (segundos)")
    plt.ylabel("Posición (radianes)")
    plt.grid(True)
    plt.legend()
    
    # Desplegar la gráfica en la pantalla
    print("Mostrando gráfica en pantalla. Ciérrala para finalizar el script.")
    plt.show()
    
    # 4. Cerrar todo limpiamente
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()