import rclpy
import yaml
import time
from pincher_lab_utils import PincherLab, JOINTS

ARCHIVO = 'poses.yaml'

def guardar_pose(node, nombre):
    # Procesa los mensajes acumulados de los sliders antes de leer la posicion
    node.spin_for(0.5)
    
    try:
        with open(ARCHIVO, 'r') as f:
            data = yaml.safe_load(f) or {}
    except FileNotFoundError:
        data = {}
    
    data[nombre] = {j: node.current[j] for j in JOINTS}
    with open(ARCHIVO, 'w') as f:
        yaml.dump(data, f)
    print(f"Pose '{nombre}' guardada.")

def reproducir(node, orden, dur):
    try:
        with open(ARCHIVO, 'r') as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print("Error: No se encontro el archivo YAML.")
        return

    prev = {j: node.current[j] for j in JOINTS}
    for nombre in orden:
        print(f"Moviendo a: {nombre} ({dur}s)")
        node.interp_quintica(prev, data[nombre], dur)
        prev = data[nombre]

def main():
    rclpy.init()
    node = PincherLab()
    orden_registro = []
    
    print("=== MODO ENSEÑANZA ===")
    while True:
        nombre = input("Mueva el robot y asigne un nombre (o ENTER para reproducir): ").strip()
        
        if not nombre:
            if len(orden_registro) < 8:
                print(f"Faltan poses. Debe registrar al menos 8 (Lleva: {len(orden_registro)})")
                continue
            break
            
        guardar_pose(node, nombre)
        orden_registro.append(nombre)
        
    print("\n=== MODO REPETICION ===")
    try:
        t_transicion = float(input("Ingrese el tiempo de transicion entre poses (segundos): "))
        print("Iniciando secuencia. Presione Ctrl+C para detener.")
        reproducir(node, orden_registro, t_transicion)
    except KeyboardInterrupt:
        print("\nReproduccion detenida por el usuario.")
    except ValueError:
        print("Tiempo invalido. Entrada cancelada.")

    # Retorno obligatorio a la posicion Home usando la nomenclatura nativa
    print("\nFinalizando secuencia. Regresando a posicion Home...")
    home = {j: 0.0 for j in JOINTS}
    t_home = time.time()
    while (time.time() - t_home) < 2.0:
        node.send(home)
        node.spin_for(0.05)

    node.destroy_node()
    rclpy.shutdown()
    print("Proceso finalizado.")

if __name__ == '__main__':
    main()