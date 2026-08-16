#!/usr/bin/env python3
"""
Actividad 5 - Calibración de cero y error articular.

Para cada articulación envía 5 posiciones angulares, registra el valor
solicitado vs el reportado por el motor, calcula error máximo, error
promedio y desplazamiento de cero, y genera gráficas comparativas.
"""
import json
import math
import os
import signal
import sys
import threading
import time

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import yaml

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_srvs.srv import Trigger

DEG = math.pi / 180.0

JOINT_NAMES = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']
JOINT_LABELS = ['Base', 'Hombro', 'Codo', 'Muñeca', 'Pinza']

# 5 posiciones de prueba distribuidas en el rango seguro, paso de ~45°
TEST_POSITIONS_DEG = {
    'waist':    [-60, -30, 0, 30, 60],
    'shoulder': [0, 15, 30, 45, 60],
    'elbow':    [-60, -30, 0, 30, 60],
    'wrist':    [-60, -30, 0, 30, 60],
    'gripper':  [-30, -15, 0, 15, 30],
}

LIMITS_DEG = {
    'waist':    (-150, 150),
    'shoulder': (-150, 150),
    'elbow':    (-150, 150),
    'wrist':    (-150, 150),
    'gripper':  (-90, 90),
}

SETTLE_TIME = 1.5  # segundos entre comandos


class CalibrationNode(Node):
    def __init__(self):
        super().__init__('calibration')
        self.cmd_pub = self.create_publisher(JointState, '/pincher/command', 10)
        self.state_sub = self.create_subscription(
            JointState, '/joint_states', self.state_cb, 10)
        self.home_cli = self.create_client(Trigger, '/pincher/home')

        self.latest_positions = {name: 0.0 for name in JOINT_NAMES}
        self.data_lock = threading.Lock()

        self.output_dir = os.path.expanduser('~/ros2_jazzy/phantom_ws/calibration_results')
        self.pkg_results_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results')
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.pkg_results_dir, exist_ok=True)

        self.get_logger().info('Nodo de calibración iniciado')

    def state_cb(self, msg):
        with self.data_lock:
            for n, p in zip(msg.name, msg.position):
                self.latest_positions[n] = p

    def get_measured(self, joint):
        with self.data_lock:
            return self.latest_positions.get(joint, 0.0)

    def send_command(self, joint, position_rad):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = [joint]
        msg.position = [position_rad]
        self.cmd_pub.publish(msg)
        self.get_logger().info(f'  → {joint}: {position_rad/DEG:.1f}°')

    def wait_settle(self, joint, target_deg, timeout=3.0):
        target_rad = target_deg * DEG
        tol = 2.0 * DEG  # ±2° de tolerancia
        start = time.time()
        while time.time() - start < timeout:
            with self.data_lock:
                measured = self.latest_positions.get(joint, 0.0)
            if abs(measured - target_rad) < tol:
                return measured
            rclpy.spin_once(self, timeout_sec=0.1)
        with self.data_lock:
            return self.latest_positions.get(joint, 0.0)

    def run(self):
        results = {}

        for idx, joint in enumerate(JOINT_NAMES):
            label = JOINT_LABELS[idx]
            test_deg = TEST_POSITIONS_DEG[joint]
            lim = LIMITS_DEG[joint]

            self.get_logger().info(f'\n{"="*50}')
            self.get_logger().info(f'Articulación: {label} ({joint})')
            self.get_logger().info(f'Posiciones de prueba: {test_deg}')
            self.get_logger().info(f'Límites: {lim}')
            self.get_logger().info(f'{"="*50}')

            desired = []
            measured = []

            for deg_val in test_deg:
                if deg_val < lim[0] or deg_val > lim[1]:
                    self.get_logger().warn(f'  ⚠ {deg_val}° fuera de límites, saltando')
                    continue

                self.send_command(joint, deg_val * DEG)

                # Esperar que alcance la posición (spin durante la espera)
                meas_rad = self.wait_settle(joint, deg_val)
                meas_deg = meas_rad / DEG

                desired.append(deg_val)
                measured.append(meas_deg)

                self.get_logger().info(f'  Deseado: {deg_val:+.1f}° → Medido: {meas_deg:+.1f}°')

            if not desired:
                continue

            # Cálculos de error
            desired_arr = np.array(desired)
            measured_arr = np.array(measured)
            error_arr = desired_arr - measured_arr

            max_error = float(np.max(np.abs(error_arr)))
            avg_error = float(np.mean(error_arr))
            zero_offset = float(np.mean(error_arr))  # offset = error promedio

            results[joint] = {
                'label': label,
                'desired': desired,
                'measured': [round(v, 2) for v in measured],
                'errors': [round(v, 2) for v in error_arr.tolist()],
                'max_error_deg': round(max_error, 2),
                'avg_error_deg': round(avg_error, 2),
                'zero_offset_deg': round(zero_offset, 2),
            }

            self.get_logger().info(f'  ─────────────────────────────')
            self.get_logger().info(f'  Error máximo:  {max_error:.2f}°')
            self.get_logger().info(f'  Error promedio: {avg_error:.2f}°')
            self.get_logger().info(f'  Offset de cero: {zero_offset:.2f}°')
            self.get_logger().info(f'')

            # Gráfica individual
            self._plot_joint(joint, results[joint])

            # Volver a home
            self.send_command(joint, 0.0)
            time.sleep(SETTLE_TIME)

        # Gráfica general
        self._plot_summary(results)

        # Guardar resultados
        self._save_results(results)

        self.get_logger().info(f'\n{"="*50}')
        self.get_logger().info('CALIBRACIÓN COMPLETADA')
        self.get_logger().info(f'Resultados guardados en: {self.output_dir}')
        self.get_logger().info(f'{"="*50}\n')

        return results

    def _plot_joint(self, joint, data):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
        fig.suptitle(f'{data["label"]} ({joint}) — Calibración', fontweight='bold')

        x = range(len(data['desired']))
        labels = [f'{v:+.0f}°' for v in data['desired']]

        ax1.plot(x, data['desired'], 'o-', color='#1a365d', linewidth=2, label='Deseado')
        ax1.plot(x, data['measured'], 's--', color='#2b6cb0', linewidth=2, label='Medido')
        ax1.set_ylabel('Posición (°)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks(x)
        ax1.set_xticklabels(labels)

        ax2.bar(x, data['errors'], color='#e53e3e', alpha=0.7, label=f'Error (max: {data["max_error_deg"]}°)')
        ax2.axhline(y=data['avg_error_deg'], color='#2f855a', linestyle='--',
                    label=f'Promedio: {data["avg_error_deg"]:+.2f}°')
        ax2.axhline(y=0, color='#718096', linewidth=0.8)
        ax2.set_xlabel('Posición deseada')
        ax2.set_ylabel('Error (°)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xticks(x)
        ax2.set_xticklabels(labels)

        plt.tight_layout()
        path = os.path.join(self.output_dir, f'calibracion_{joint}.png')
        fig.savefig(path, dpi=150)
        plt.close(fig)
        self.get_logger().info(f'  📊 Gráfica guardada: {path}')

    def _plot_summary(self, results):
        n = len(results)
        fig, axes = plt.subplots(2, n, figsize=(4 * n, 7))
        if n == 1:
            axes = axes.reshape(2, 1)
        fig.suptitle('Resumen de Calibración — Todas las Articulaciones', fontweight='bold', fontsize=13)

        colors = ['#1a365d', '#2b6cb0', '#2f855a', '#d69e2e', '#e53e3e']

        for i, (joint, data) in enumerate(results.items()):
            x = range(len(data['desired']))
            labels = [f'{v:+.0f}°' for v in data['desired']]

            ax1 = axes[0, i]
            ax1.plot(x, data['desired'], 'o-', color=colors[i], linewidth=2, label='Deseado')
            ax1.plot(x, data['measured'], 's--', color=colors[min(i + 1, len(colors) - 1)],
                     linewidth=2, label='Medido')
            ax1.set_title(data['label'])
            ax1.set_ylabel('Pos (°)')
            ax1.legend(fontsize=6)
            ax1.grid(True, alpha=0.3)
            ax1.set_xticks(x)
            ax1.set_xticklabels(labels, fontsize=7)

            ax2 = axes[1, i]
            ax2.bar(x, data['errors'], color=colors[i], alpha=0.6)
            ax2.axhline(y=data['avg_error_deg'], color='#2f855a', linestyle='--',
                        label=f'Ø {data["avg_error_deg"]:+.2f}°')
            ax2.axhline(y=0, color='#718096', linewidth=0.8)
            ax2.set_xlabel('Deseado')
            ax2.set_ylabel('Error (°)')
            ax2.legend(fontsize=6)
            ax2.grid(True, alpha=0.3)
            ax2.set_xticks(x)
            ax2.set_xticklabels(labels, fontsize=7)

        plt.tight_layout()
        path = os.path.join(self.output_dir, 'calibracion_resumen.png')
        fig.savefig(path, dpi=150)
        plt.close(fig)
        self.get_logger().info(f'  📊 Gráfica resumen guardada: {path}')

    def _copy_to_pkg(self, filename):
        src = os.path.join(self.output_dir, filename)
        dst = os.path.join(self.pkg_results_dir, filename)
        if os.path.exists(src):
            import shutil
            shutil.copy2(src, dst)

    def _save_results(self, results):
        path = os.path.join(self.output_dir, 'calibracion_resultados.yaml')
        with open(path, 'w') as f:
            yaml.dump({'fecha': time.strftime('%Y-%m-%d %H:%M:%S'),
                       'articulaciones': results}, f, allow_unicode=True, default_flow_style=False)
        self.get_logger().info(f'  📄 Resultados guardados: {path}')

        # Guardar también un resumen de offsets recomendados
        offsets = {}
        for joint, data in results.items():
            offsets[joint] = {
                'zero_offset_deg': data['zero_offset_deg'],
                'max_error_deg': data['max_error_deg'],
                'avg_error_deg': data['avg_error_deg'],
            }

        summary_path = os.path.join(self.output_dir, 'offsets_recomendados.yaml')
        recommended = {
            'fecha': time.strftime('%Y-%m-%d %H:%M:%S'),
            'nota': 'Sumar estos offsets a home_positions en ax12a.yaml para corregir el cero.',
            'offsets_grados': offsets,
        }
        with open(summary_path, 'w') as f:
            yaml.dump(recommended, f, allow_unicode=True, default_flow_style=False)
        self.get_logger().info(f'  📄 Offsets recomendados: {summary_path}')

        # Copiar todos los resultados al package para el README
        self._copy_to_pkg('calibracion_resultados.yaml')
        self._copy_to_pkg('offsets_recomendados.yaml')
        self._copy_to_pkg('README_calibracion.md')
        for joint in JOINT_NAMES:
            self._copy_to_pkg(f'calibracion_{joint}.png')
        self._copy_to_pkg('calibracion_resumen.png')
        self.get_logger().info(f'  📋 Resultados copiados a: {self.pkg_results_dir}')


def print_header(results):
    print(f'\n')
    print(f'  ╔══════════════════════════════════════════════════════╗')
    print(f'  ║         CALIBRACIÓN DE CERO Y ERROR ARTICULAR       ║')
    print(f'  ╚══════════════════════════════════════════════════════╝')
    print(f'')

    for joint, data in results.items():
        print(f'  {data["label"]:10s} ({joint:10s})  '
              f'Error máx: {data["max_error_deg"]:6.2f}°  '
              f'Error prom: {data["avg_error_deg"]:+.2f}°  '
              f'Offset cero: {data["zero_offset_deg"]:+.2f}°')

    print(f'')
    print(f'  Resultados guardados en: ~/ros2_jazzy/phantom_ws/calibration_results/')
    print(f'  Gráficas: calibracion_{"{articulacion}"}.png  +  calibracion_resumen.png')
    print(f'  Datos: calibracion_resultados.yaml  +  offsets_recomendados.yaml')
    print(f'')


def generate_readme(results):
    path = os.path.expanduser('~/ros2_jazzy/phantom_ws/calibration_results/README_calibracion.md')
    lines = []
    lines.append('# Calibración de Cero y Error Articular')
    lines.append('')
    lines.append('## Laboratorio No. 05 — Phantom X Pincher X100 — ROS 2 Jazzy')
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('## 1. Objetivo')
    lines.append('')
    lines.append('Determinar el error sistemático de cada articulación del robot Phantom X Pincher')
    lines.append('X100 enviando posiciones angulares conocidas y comparándolas con la posición')
    lines.append('reportada por los servomotores DYNAMIXEL. A partir de los errores medidos se')
    lines.append('calcula el desplazamiento de cero (offset) necesario para corregir la')
    lines.append('calibración del manipulador.')
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('## 2. Metodología')
    lines.append('')
    lines.append('### 2.1. Posiciones de prueba')
    lines.append('')
    lines.append('Para cada articulación se seleccionaron 5 posiciones angulares distribuidas')
    lines.append('dentro del rango seguro, evitando colisiones con la mesa y respetando los')
    lines.append('límites mecánicos del robot. El paso angular es de aproximadamente 45°.')
    lines.append('')
    lines.append('| Articulación | ID  | Rango seguro (°) | Posiciones de prueba (°) |')
    lines.append('|-------------|:---:|:----------------:|:------------------------:|')
    for i, joint in enumerate(JOINT_NAMES):
        lim = LIMITS_DEG[joint]
        deg_str = ', '.join(f'{v:+.0f}' for v in TEST_POSITIONS_DEG[joint])
        lines.append(f'| {JOINT_LABELS[i]:12s} | {i+1:3d} | {lim[0]:5.0f} a {lim[1]:4.0f} | {deg_str} |')
    lines.append('')
    lines.append('### 2.2. Procedimiento')
    lines.append('')
    lines.append('1. Se verificó que el robot esté en una posición segura y el controlador')
    lines.append('   `pincher_controller` esté ejecutándose con `use_hardware:=true`.')
    lines.append('2. Para cada articulación, en orden (Base → Hombro → Codo → Muñeca → Pinza):')
    lines.append('   a. Se envía la primera posición angular vía el tópico `/pincher/command`.')
    lines.append('   b. Se espera 1.5 segundos para que el motor alcance la posición.')
    lines.append('   c. Se lee la posición reportada por el motor desde `/joint_states`.')
    lines.append('   d. Se repite para las 5 posiciones.')
    lines.append('   e. Se retorna la articulación a 0° (home).')
    lines.append('3. Se calcula el error para cada punto: `e_q = q_deseado - q_medido`.')
    lines.append('4. Se determina: error máximo, error promedio y desplazamiento de cero.')
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('## 3. Resultados')
    lines.append('')
    lines.append('### 3.1. Tabla de resultados')
    lines.append('')
    lines.append('| Articulación | Error máx (°) | Error prom (°) | Offset cero (°) |')
    lines.append('|-------------|:------------:|:--------------:|:---------------:|')
    for joint, data in results.items():
        lines.append(f'| {data["label"]:12s} | {data["max_error_deg"]:11.2f} | {data["avg_error_deg"]:13.2f} | {data["zero_offset_deg"]:14.2f} |')
    lines.append('')
    lines.append('### 3.2. Datos detallados por articulación')
    lines.append('')
    for joint, data in results.items():
        lines.append(f'**{data["label"]}** (`{joint}`)')
        lines.append('')
        lines.append('| Prueba | Deseado (°) | Medido (°) | Error (°) |')
        lines.append('|:-----:|:----------:|:---------:|:--------:|')
        for i in range(len(data['desired'])):
            d = data['desired'][i]
            m = data['measured'][i]
            e = data['errors'][i]
            lines.append(f'| {i+1:5d} | {d:10.1f} | {m:9.2f} | {e:8.2f} |')
        lines.append(f'|       | **Error máx:** | | **{data["max_error_deg"]:.2f}°** |')
        lines.append(f'|       | **Error prom:** | | **{data["avg_error_deg"]:+.2f}°** |')
        lines.append(f'|       | **Offset cero:** | | **{data["zero_offset_deg"]:+.2f}°** |')
        lines.append('')
    lines.append('')
    lines.append('### 3.3. Interpretación de resultados')
    lines.append('')
    lines.append('- **Error máximo:** La mayor desviación absoluta entre lo deseado y lo medido.')
    lines.append('  Indica la precisión máxima del servo en todo su rango.')
    lines.append('- **Error promedio:** El sesgo sistemático de la articulación. Si es positivo,')
    lines.append('  el motor tiende a quedarse por debajo de la posición deseada.')
    lines.append('- **Offset de cero:** Es el error promedio. Representa cuánto hay que desplazar')
    lines.append('  la referencia de la articulación para que 0° real corresponda a 0° medido.')
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('## 4. Gráficas')
    lines.append('')
    lines.append('Se generaron dos tipos de gráficas:')
    lines.append('')
    lines.append('### 4.1. Gráficas individuales')
    lines.append('')
    lines.append('Archivo: `calibracion_{articulación}.png`')
    lines.append('')
    lines.append('Cada gráfica contiene dos subgráficas:')
    lines.append('')
    lines.append('1. **Posición deseada vs. medida** (superior): Compara visualmente el')
    lines.append('   comportamiento real del servo frente a lo solicitado.')
    lines.append('2. **Error** (inferior): Muestra la magnitud del error en cada punto.')
    lines.append('   La línea verde punteada indica el error promedio.')
    lines.append('')
    lines.append('### 4.2. Gráfica de resumen')
    lines.append('')
    lines.append('Archivo: `calibracion_resumen.png`')
    lines.append('')
    lines.append('Compara todas las articulaciones en una sola figura para facilitar la')
    lines.append('identificación de cuáles articulaciones presentan mayor error.')
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('## 5. Corrección de cero')
    lines.append('')
    lines.append('### 5.1. Cálculo de la corrección')
    lines.append('')
    lines.append('El offset de cero calculado debe aplicarse al parámetro `home_positions`')
    lines.append('en el archivo de configuración del controlador. Para los servomotores')
    lines.append('AX-12A, el rango raw es de 0 a 1023, correspondiente a 300° de giro.')
    lines.append('La conversión de grados a unidades raw es:')
    lines.append('')
    lines.append('    raw_offset = offset_grados × (1024 / 300)')
    lines.append('')
    lines.append('### 5.2. Offsets recomendados')
    lines.append('')
    lines.append('| Articulación | Offset (°) | Offset (raw) | home actual | home corregido |')
    lines.append('|-------------|:----------:|:------------:|:----------:|:--------------:|')
    for joint, data in results.items():
        raw_offset = data['zero_offset_deg'] * (1024 / 300)
        new_home = 512 + raw_offset
        lines.append(f'| {data["label"]:12s} | {data["zero_offset_deg"]:10.2f} | {raw_offset:11.0f} | {512:10d} | {int(round(new_home)):13d} |')
    lines.append('')
    lines.append('### 5.3. Aplicación de la corrección')
    lines.append('')
    lines.append('1. Abrir el archivo `pincher_control/config/ax12a.yaml`')
    lines.append('2. Modificar el parámetro `home_positions` con los valores de la columna')
    lines.append('   "home corregido":')
    lines.append('')
    lines.append('```yaml')
    offset_list = []
    for joint in JOINT_NAMES:
        data = results.get(joint)
        if data:
            raw_offset = data['zero_offset_deg'] * (1024 / 300)
            offset_list.append(int(round(512 + raw_offset)))
        else:
            offset_list.append(512)
    lines.append(f'home_positions: {offset_list}')
    lines.append('```')
    lines.append('')
    lines.append('3. Guardar el archivo y reiniciar el controlador.')
    lines.append('4. Verificar que en home (0° para todas las articulaciones) el robot esté en la')
    lines.append('   posición de referencia definida en la Actividad 2.')
    lines.append('')
    lines.append('### 5.4. Verificación')
    lines.append('')
    lines.append('Después de aplicar los offsets, repetir la calibración para confirmar que el')
    lines.append('error promedio se ha reducido (idealmente a menos de ±1°).')
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('## 6. Archivos generados')
    lines.append('')
    lines.append('| Archivo | Contenido |')
    lines.append('|---------|----------|')
    lines.append('| `calibracion_resultados.yaml` | Datos completos de todas las mediciones |')
    lines.append('| `offsets_recomendados.yaml` | Offsets calculados por articulación |')
    lines.append('| `calibracion_{articulación}.png` | Gráfica individual por articulación |')
    lines.append('| `calibracion_resumen.png` | Gráfica comparativa de todas las articulaciones |')
    lines.append('| `README_calibracion.md` | Este documento |')
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('## 7. Conclusiones')
    lines.append('')
    lines.append('La calibración permitió cuantificar el error sistemático de cada articulación')
    lines.append('del Phantom X Pincher X100. Los principales hallazgos fueron:')
    lines.append('')
    for joint, data in results.items():
        lines.append(f'- **{data["label"]}:** error máximo de {data["max_error_deg"]:.2f}°, '
                     f'offset de {data["zero_offset_deg"]:+.2f}°.')
    lines.append('')
    lines.append('Se recomienda aplicar los offsets calculados en el archivo `ax12a.yaml`')
    lines.append('para mejorar la precisión del robot en tareas que requieran repetibilidad.')
    lines.append('')

    with open(path, 'w') as f:
        f.write('\n'.join(lines))
    print(f'  📄 README generado: {path}')


def main():
    import threading

    rclpy.init()
    node = CalibrationNode()

    running = True
    def shutdown(sig, frame):
        nonlocal running
        running = False
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print(f'')
    print(f'  ╔══════════════════════════════════════════════════════╗')
    print(f'  ║   Iniciando calibración de cero y error articular   ║')
    print(f'  ║   Asegúrate de que el robot esté conectado y        ║')
    print(f'  ║   el controlador pincher_controller esté corriendo   ║')
    print(f'  ╚══════════════════════════════════════════════════════╝')
    print(f'')

    spinner = ['|', '/', '-', '\\']
    spin_idx = [0]
    spin_thread = [True]

    def spin_worker():
        while spin_thread[0] and running:
            print(f'\r  Calibrando... {spinner[spin_idx[0] % 4]}', end='', flush=True)
            spin_idx[0] += 1
            time.sleep(0.2)

    t = threading.Thread(target=spin_worker, daemon=True)
    t.start()

    try:
        results = node.run()
        spin_thread[0] = False
        time.sleep(0.3)
        print('\r' + ' ' * 40 + '\r', end='')

        if results:
            print_header(results)
            generate_readme(results)
        else:
            print('  No se obtuvieron resultados.')

    except KeyboardInterrupt:
        print('\n  Calibración interrumpida por el usuario.')
    finally:
        spin_thread[0] = False
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
