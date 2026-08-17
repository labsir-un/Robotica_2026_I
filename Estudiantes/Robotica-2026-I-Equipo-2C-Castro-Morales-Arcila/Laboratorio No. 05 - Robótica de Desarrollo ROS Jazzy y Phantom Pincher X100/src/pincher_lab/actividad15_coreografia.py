import rclpy
import yaml
import time
from pincher_lab_utils import PincherLab, JOINTS

FACTOR_VELOCIDAD = 1.0

def cargar_configuracion(archivo):
    with open(archivo, 'r') as f:
        return yaml.safe_load(f)

def main():
    rclpy.init()
    node = PincherLab()
    node.spin_for(1.0)

    poses = cargar_configuracion('poses_coreografia.yaml')
    guion = cargar_configuracion('guion.yaml')

    neutro = poses.get('neutro', {j: 0.0 for j in JOINTS})

    actual = {j: node.current[j] for j in JOINTS}
    print("Moviendo a posición segura (neutro) antes de iniciar")
    node.interp_quintica(actual, neutro, 2.0)

    print(f"Iniciando Coreografía Robótica")
    prev = neutro
    t0 = time.time()

    for ev in guion:
        # Escalar tanto el tiempo de inicio como la duración por el factor
        t_escalado = ev['t'] / FACTOR_VELOCIDAD
        dur_escalada = ev['dur'] / FACTOR_VELOCIDAD

        while (time.time() - t0) < t_escalado:
            node.spin_for(0.01)

        if ev['pose'] not in poses:
            print(f"Advertencia: La pose '{ev['pose']}' no existe.")
            continue

        target = poses[ev['pose']]
        node.interp_quintica(prev, target, dur_escalada)
        prev = target

    duracion_total = time.time() - t0
    print(f"\nCoreografía finalizada con éxito. Duración: {duracion_total:.1f} s")

    safe_home = poses.get('neutro', {j: 0.0 for j in JOINTS})
    node.interp_quintica(prev, safe_home, 2.0 / FACTOR_VELOCIDAD)

    node.destroy_node()
    rclpy.shutdown()
    print("Proceso finalizado.")

if __name__ == '__main__':
    main()