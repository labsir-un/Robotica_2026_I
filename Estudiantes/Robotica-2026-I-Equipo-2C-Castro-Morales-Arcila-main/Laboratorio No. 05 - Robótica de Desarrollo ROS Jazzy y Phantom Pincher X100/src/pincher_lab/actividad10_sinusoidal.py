import rclpy
import time
import numpy as np
import matplotlib.pyplot as plt
from pincher_lab_utils import PincherLab, JOINTS

def ejecutar_prueba_sinusoidal(node, articulacion, q0, A, f):
    # Parámetros fijos de la prueba
    duracion = 10.0  # Cada prueba dura 10 segundos
    hz = 50          # Frecuencia de muestreo (50 Hz)
    periodo = 1.0 / hz
    
    # Listas vacías para almacenar los datos que pide el enunciado
    lista_tiempo = []
    lista_deseado = []
    lista_medido = []
    
    t0 = time.time()
    print(f"Ejecutando trayectoria: Amplitud = {A} rad | Frecuencia = {f} Hz")
    
    # Bucle de control basado en tiempo real
    while (time.time() - t0) < duracion:
        t = time.time() - t0  # Calcular el tiempo transcurrido
        
        # Aplicamos la ecuación exacta dada en la imagen: q(t) = q0 + A * sin(2 * pi * f * t)
        q_deseado = q0 + A * np.sin(2 * np.pi * f * t)
        
        # Leemos la posición real que mide el robot en este instante
        q_medido = node.current[articulacion]
        
        # Preparamos el comando de movimiento manteniendo estables los demás joints
        comando = node.current.copy()
        comando[articulacion] = q_deseado
        node.send(comando)
        
        # Guardamos los datos en nuestras listas para las gráficas
        lista_tiempo.append(t)
        lista_deseado.append(q_deseado)
        lista_medido.append(q_medido)
        
        # Esperamos el tiempo del periodo (1/50 Hz = 0.02 segundos)
        node.spin_for(periodo)
        
    # --- CÁLCULO DE ERRORES AL FINALIZAR LA PRUEBA ---
    # Convertimos las listas a arreglos de numpy para operar matemáticamente
    arreglo_deseado = np.array(lista_deseado)
    arreglo_medido = np.array(lista_medido)
    
    # Calculamos la diferencia (Error = Deseado - Medido)
    error = arreglo_deseado - arreglo_medido
    
    # 1. Error Máximo Absoluto
    error_maximo = np.max(np.abs(error))
    
    # 2. Error Cuadrático Medio (RMS)
    error_cuadratico_medio = np.sqrt(np.mean(error ** 2))
    
    # Mostramos los resultados en la consola de comandos
    print(f"   -> Error Máximo Calculado: {error_maximo:.4f} rad")
    print(f"   -> Error Cuadrático Medio (RMS): {error_cuadratico_medio:.4f} rad\n")
    
    # Devolvemos las listas con los datos recolectados
    return lista_tiempo, lista_deseado, lista_medido


def main():
    # Inicializar el entorno ROS2 y el robot
    rclpy.init()
    node = PincherLab()
    
    # Selección de la articulación (cumpliendo la primera frase del enunciado)
    articulacion_elegida = 'wrist'  # Controlaremos la muñeca
    posicion_inicial = 0.0
    
    # Las 4 combinaciones obligatorias combinando 2 amplitudes (0.2, 0.4) y 2 frecuencias (0.1, 0.3)
    pruebas_config = [
        (0.2, 0.1),  # Prueba 1
        (0.2, 0.3),  # Prueba 2
        (0.4, 0.1),  # Prueba 3
        (0.4, 0.3)   # Prueba 4
    ]
    
    # Ejecutamos las 4 pruebas de manera secuencial
    for A, f in pruebas_config:
        # Corremos la trayectoria y guardamos sus datos correspondientes
        tiempos, deseado, medido = ejecutar_prueba_sinusoidal(node, articulacion_elegida, posicion_inicial, A, f)
        
        # --- DISEÑO DE LAS GRÁFICAS REQUERIDAS ---
        plt.figure(figsize=(8, 4))
        plt.plot(tiempos, deseado, label='Posición Deseada (Teórica)', color='blue', linewidth=2)
        plt.plot(tiempos, medido, label='Posición Medida (Real)', color='orange', linestyle='--', linewidth=2)
        
        # Añadimos todos los elementos de identificación de la gráfica
        plt.title(f"Actividad 10: Trayectoria Sinusoidal (A={A}, f={f}Hz)")
        plt.xlabel("Tiempo (segundos)")
        plt.ylabel("Posición Angular (radianes)")
        plt.grid(True)
        plt.legend()
        
        # Guardamos la gráfica automáticamente en la carpeta del script
        nombre_imagen = f"sinusoidal_A{A}_f{f}.png"
        plt.savefig(nombre_imagen)
        print(f"   [Gráfica guardada con éxito como: {nombre_imagen}]")
        
        # --- REGRESO SEGURO A HOME ENTRE PRUEBAS ---
        print("Regresando a posición de referencia (Home)...")
        home = {}
        for j in JOINTS:
            home[j] = 0.0
        node.send(home)
        node.spin_for(2.0)  # Damos 2 segundos para que el robot se estabilice antes de la siguiente prueba
        print("-" * 50)
        
    # Desplegar todas las ventanas de las gráficas en pantalla al finalizar todo
    print("\nMostrando todas las gráficas en pantalla...")
    plt.show()
    
    # Apagar el sistema de forma limpia
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()