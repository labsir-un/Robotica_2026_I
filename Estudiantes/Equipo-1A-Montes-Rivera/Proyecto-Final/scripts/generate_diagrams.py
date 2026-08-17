#!/usr/bin/env python3
"""
Script para generar los diagramas de flujo, arquitectura ROS 2 y plano de planta de la celda.
Guarda las imágenes PNG de alta resolución en la carpeta doc/.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs('doc', exist_ok=True)
plt.style.use('dark_background')

# ==============================================================================
# 1. DIAGRAMA DE FLUJO: PROCESO GLOBAL DE CLASIFICACIÓN PICK & PLACE POR VACÍO
# ==============================================================================
def create_flowchart():
    fig, ax = plt.subplots(figsize=(14, 18), dpi=300)
    ax.set_facecolor('#0d1117')
    fig.patch.set_facecolor('#0d1117')

    nodes = [
        ("INICIO\nLanzar master_autonomous.launch", 0.5, 0.96, '#27ae60', 'start'),
        ("Inicialización ROS 2 & Carga Params\n(control_servo, vacuum_relay, vision, sorting, hmi)", 0.5, 0.90, '#1f2937', 'proc'),
        ("Movimiento a Pose HOME\n[0°, 0°, 0°, 0°, 0°]", 0.5, 0.84, '#1f2937', 'proc'),
        ("Movimiento a Pose SCAN\n[0°, -90°, 90°, 90°, 0°]", 0.5, 0.78, '#1f2937', 'proc'),
        ("Captura Cenital & YOLOv8 Inferencia\nFiltro Área Circular Plato (r <= 140 px)", 0.5, 0.71, '#1e1b4b', 'proc'),
        ("¿Pieza Detectada\nen Plato?", 0.5, 0.63, '#374151', 'dec'),
        ("Transformación Homografía Píxel -> cm\nCoordenadas (X, Y) en Marco 'world'", 0.5, 0.55, '#1e1b4b', 'proc'),
        ("Cálculo Cinemática Inversa 3D\n(TCP Ventosa: Z_approach=8cm, Z_surface=5cm)", 0.5, 0.48, '#1f2937', 'proc'),
        ("¿IK 3D Válida\n& Segura?", 0.5, 0.41, '#374151', 'dec'),
        ("Aproximación PRE_PICK (Z = 8.0 cm)\nDescenso a PICK (Z = 5.0 cm)", 0.5, 0.33, '#1f2937', 'proc'),
        ("Activación Succión: VACUUM_ON\nRelé GPIO 17 HIGH (Bomba 12V Active)", 0.5, 0.26, '#065f46', 'proc'),
        ("Elevación LIFT (Z = 8.0 cm) & Traslado PRE_DROP\nhacia Caneca de Color (Roja, Verde, Azul, Amarilla)", 0.5, 0.19, '#1f2937', 'proc'),
        ("Posicionamiento sobre Caneca & Descarga\nDesactivación Succión: VACUUM_OFF (GPIO 17 LOW)", 0.5, 0.12, '#065f46', 'proc'),
        ("Actualizar Conteo HMI (12 Cubos)\n¿Quedan Cubos por Clasificar?", 0.5, 0.05, '#374151', 'dec'),
        ("FIN / Estado DONE\nRetorno a HOME Segura", 0.88, 0.05, '#27ae60', 'end'),
        ("Rutina RECOVERY / FAULT\nVACUUM_OFF & Elevación a SCAN", 0.12, 0.41, '#7f1d1d', 'proc'),
    ]

    for text, x, y, color, ntype in nodes:
        ax.text(x, y, text, ha='center', va='center', color='white', weight='bold', fontsize=9,
                bbox=dict(boxstyle='round,pad=0.5', facecolor=color, edgecolor='white', alpha=0.9, lw=1.5))

    arrow_props = dict(arrowstyle='->', lw=2, color='#60a5fa', mutation_scale=15)
    
    ax.annotate('', xy=(0.5, 0.925), xytext=(0.5, 0.94), arrowprops=arrow_props)
    ax.annotate('', xy=(0.5, 0.865), xytext=(0.5, 0.88), arrowprops=arrow_props)
    ax.annotate('', xy=(0.5, 0.805), xytext=(0.5, 0.82), arrowprops=arrow_props)
    ax.annotate('', xy=(0.5, 0.745), xytext=(0.5, 0.765), arrowprops=arrow_props)
    ax.annotate('', xy=(0.5, 0.67), xytext=(0.5, 0.68), arrowprops=arrow_props)
    
    ax.annotate('', xy=(0.5, 0.58), xytext=(0.5, 0.60), arrowprops=arrow_props)
    ax.text(0.52, 0.59, 'Sí', color='#34d399', weight='bold', fontsize=9)
    
    ax.annotate('', xy=(0.5, 0.51), xytext=(0.5, 0.53), arrowprops=arrow_props)
    ax.annotate('', xy=(0.5, 0.44), xytext=(0.5, 0.46), arrowprops=arrow_props)
    
    ax.annotate('', xy=(0.5, 0.36), xytext=(0.5, 0.38), arrowprops=arrow_props)
    ax.text(0.52, 0.37, 'Sí', color='#34d399', weight='bold', fontsize=9)
    
    ax.annotate('', xy=(0.22, 0.41), xytext=(0.38, 0.41), arrowprops=dict(arrowstyle='->', lw=2, color='#f87171', mutation_scale=15))
    ax.text(0.30, 0.42, 'No (Fallo IK)', color='#f87171', weight='bold', fontsize=8)
    
    ax.annotate('', xy=(0.12, 0.78), xytext=(0.12, 0.44), arrowprops=dict(arrowstyle='->', lw=1.5, color='#f87171', ls='--'))
    ax.annotate('', xy=(0.35, 0.78), xytext=(0.12, 0.78), arrowprops=dict(arrowstyle='->', lw=1.5, color='#f87171', ls='--'))

    ax.annotate('', xy=(0.5, 0.29), xytext=(0.5, 0.305), arrowprops=arrow_props)
    ax.annotate('', xy=(0.5, 0.22), xytext=(0.5, 0.235), arrowprops=arrow_props)
    ax.annotate('', xy=(0.5, 0.15), xytext=(0.5, 0.165), arrowprops=arrow_props)
    ax.annotate('', xy=(0.5, 0.08), xytext=(0.5, 0.095), arrowprops=arrow_props)
    
    ax.annotate('', xy=(0.76, 0.05), xytext=(0.62, 0.05), arrowprops=arrow_props)
    ax.text(0.68, 0.06, 'No (12 Clasificados)', color='#34d399', weight='bold', fontsize=8)
    
    ax.annotate('', xy=(0.88, 0.78), xytext=(0.5, 0.02), arrowprops=dict(arrowstyle='->', lw=1.5, color='#fbbf24', ls='--'))
    ax.annotate('', xy=(0.65, 0.78), xytext=(0.88, 0.78), arrowprops=dict(arrowstyle='->', lw=1.5, color='#fbbf24', ls='--'))
    ax.text(0.89, 0.40, 'Sí (Siguiente Cubo)', color='#fbbf24', weight='bold', fontsize=8, rotation=90)

    ax.set_title("DIAGRAMA DE FLUJO: PROCESO GLOBAL DE CLASIFICACIÓN PICK & PLACE POR VACÍO",
                 color='#60a5fa', weight='bold', fontsize=14, pad=15)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('doc/diagrama_de_flujo.png', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print("✅ Creado doc/diagrama_de_flujo.png")


# ==============================================================================
# 2. DIAGRAMA DE ARQUITECTURA DE NODOS Y TÓPICOS ROS 2
# ==============================================================================
def create_ros2_architecture():
    fig, ax = plt.subplots(figsize=(15, 10), dpi=300)
    ax.set_facecolor('#0d1117')
    fig.patch.set_facecolor('#0d1117')

    node_box = dict(boxstyle='round,pad=0.6', facecolor='#1e293b', edgecolor='#38bdf8', lw=2)
    hw_box = dict(boxstyle='round,pad=0.6', facecolor='#312e81', edgecolor='#818cf8', lw=2)

    ax.text(0.15, 0.75, "NODO ROS 2\nvision_node\n(YOLOv8 + Filter)", ha='center', va='center', color='white', weight='bold', bbox=node_box)
    ax.text(0.50, 0.75, "NODO PRINCIPAL\nsorting_node\n(Máquina de Estados & IK)", ha='center', va='center', color='white', weight='bold', bbox=node_box)
    ax.text(0.85, 0.75, "NODO INTERFAZ\npincher_hmi\n(PyQt5 HMI)", ha='center', va='center', color='white', weight='bold', bbox=node_box)
    
    ax.text(0.30, 0.30, "NODO CONTROL\ncontrol_servo\n(DynamixelSDK)", ha='center', va='center', color='white', weight='bold', bbox=node_box)
    ax.text(0.70, 0.30, "NODO VACÍO\nvacuum_relay_node\n(GPIO 17)", ha='center', va='center', color='white', weight='bold', bbox=node_box)

    ax.text(0.15, 0.92, "Cámara HD USB\n(Visión Cenital)", ha='center', va='center', color='white', weight='bold', bbox=hw_box)
    ax.text(0.30, 0.08, "PhantomX Pincher\n(AX-12A / XL430)", ha='center', va='center', color='white', weight='bold', bbox=hw_box)
    ax.text(0.70, 0.08, "Relé GPIO 17 &\nBomba Vacío Micro 370A", ha='center', va='center', color='white', weight='bold', bbox=hw_box)

    arrow_props = dict(arrowstyle='->', lw=2, color='#38bdf8', mutation_scale=12)

    ax.annotate('', xy=(0.15, 0.81), xytext=(0.15, 0.87), arrowprops=arrow_props)
    ax.text(0.325, 0.80, "vision/coordenada_pieza (Point)\nvision/color_pieza (String)", ha='center', color='#a7f3d0', fontsize=8, weight='bold')
    ax.annotate('', xy=(0.40, 0.75), xytext=(0.25, 0.75), arrowprops=arrow_props)

    ax.text(0.35, 0.55, "/pincher/command\n(sensor_msgs/JointState)", ha='center', color='#fef08a', fontsize=8, weight='bold')
    ax.annotate('', xy=(0.32, 0.36), xytext=(0.45, 0.69), arrowprops=arrow_props)

    ax.text(0.65, 0.55, "/pincher/vacuum\n(std_msgs/String: ON/OFF)", ha='center', color='#6ee7b7', fontsize=8, weight='bold')
    ax.annotate('', xy=(0.68, 0.36), xytext=(0.55, 0.69), arrowprops=arrow_props)

    ax.annotate('', xy=(0.30, 0.14), xytext=(0.30, 0.24), arrowprops=arrow_props)
    ax.annotate('', xy=(0.70, 0.14), xytext=(0.70, 0.24), arrowprops=arrow_props)

    ax.text(0.50, 0.40, "/joint_states (JointState)", ha='center', color='#38bdf8', fontsize=8, weight='bold')
    ax.annotate('', xy=(0.48, 0.69), xytext=(0.35, 0.35), arrowprops=dict(arrowstyle='->', lw=1.5, color='#38bdf8', ls='--'))
    ax.annotate('', xy=(0.80, 0.69), xytext=(0.35, 0.35), arrowprops=dict(arrowstyle='->', lw=1.5, color='#38bdf8', ls='--'))

    ax.set_title("ARQUITECTURA DE NODOS, TÓPICOS Y HARDWARE DE LA CELDA EN ROS 2 JAZZY",
                 color='#38bdf8', weight='bold', fontsize=13, pad=15)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig('doc/arquitectura_ros2.png', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print("✅ Creado doc/arquitectura_ros2.png")


# ==============================================================================
# 3. PLANO DE PLANTA Y DISPOSICIÓN ESPACIAL DE LA CELDA DE TRABAJO (2D TOP VIEW)
# ==============================================================================
def create_floorplan():
    fig, ax = plt.subplots(figsize=(12, 10), dpi=300)
    ax.set_facecolor('#0f172a')
    fig.patch.set_facecolor('#0f172a')

    mdf = patches.Rectangle((-0.12, -0.18), 0.554, 0.360, linewidth=2, edgecolor='#64748b', facecolor='#1e293b', alpha=0.6)
    ax.add_patch(mdf)
    ax.text(0.15, -0.16, "Plataforma Base MDF (554 mm x 360 mm)", color='#94a3b8', weight='bold', fontsize=9)

    reach = patches.Circle((0, 0), 0.30, linewidth=1.5, edgecolor='#38bdf8', facecolor='none', linestyle='--')
    ax.add_patch(reach)
    ax.text(0.0, 0.31, "Espacio Alcanzable Máximo (R = 300 mm)", color='#38bdf8', weight='bold', fontsize=8, ha='center')

    robot_base = patches.Circle((0, 0), 0.04, linewidth=2, edgecolor='#ef4444', facecolor='#b91c1c')
    ax.add_patch(robot_base)
    ax.text(0.0, 0.0, "ROBOT\n(0, 0)", color='white', weight='bold', fontsize=8, ha='center', va='center')

    tray = patches.Circle((0.099, 0), 0.073, linewidth=2, edgecolor='#f8fafc', facecolor='#e2e8f0', alpha=0.8)
    ax.add_patch(tray)
    ax.text(0.099, 0, "Bandeja Recolección\nDia 146 mm\n(9.9 cm, 0 cm)", color='#0f172a', weight='bold', fontsize=8, ha='center', va='center')

    bins = [
        ("Caneca ROJA\n(-0.9 cm, 11.7 cm)", -0.009, 0.117, '#ef4444'),
        ("Caneca VERDE\n(19.6 cm, 9.1 cm)", 0.196, 0.091, '#2ecc71'),
        ("Caneca AZUL\n(19.2 cm, -8.8 cm)", 0.192, -0.088, '#3b82f6'),
        ("Caneca AMARILLA\n(-1.0 cm, -11.0 cm)", -0.010, -0.110, '#f59e0b'),
    ]

    for name, x, y, color in bins:
        b = patches.Circle((x, y), 0.035, linewidth=2, edgecolor='white', facecolor=color, alpha=0.9)
        ax.add_patch(b)
        ax.text(x, y, name, color='white' if color != '#f59e0b' else 'black', weight='bold', fontsize=7, ha='center', va='center')

    cam = patches.Rectangle((0.24, -0.02), 0.04, 0.04, linewidth=1.5, edgecolor='#a855f7', facecolor='#6b21a8')
    ax.add_patch(cam)
    ax.text(0.26, 0.03, "Cámara Cenital\n(26.0 cm, 0 cm)", color='#c084fc', weight='bold', fontsize=8, ha='center')

    ax.annotate('', xy=(0.08, 0), xytext=(0, 0), arrowprops=dict(arrowstyle='->', lw=2, color='#ef4444'))
    ax.text(0.08, 0.01, "+X (Frente)", color='#ef4444', weight='bold', fontsize=8)

    ax.annotate('', xy=(0, 0.08), xytext=(0, 0), arrowprops=dict(arrowstyle='->', lw=2, color='#22c55e'))
    ax.text(0.01, 0.08, "+Y (Izquierda)", color='#22c55e', weight='bold', fontsize=8)

    ax.set_title("PLANO DE PLANTA Y DISPOSICIÓN DE LA CELDA DE TRABAJO (VISTA CENITAL 2D)",
                 color='#f8fafc', weight='bold', fontsize=13, pad=15)
    ax.set_xlim(-0.15, 0.45)
    ax.set_ylim(-0.20, 0.35)
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', color='#334155', alpha=0.5)

    plt.tight_layout()
    plt.savefig('doc/plano_de_planta.png', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print("✅ Creado doc/plano_de_planta.png")


if __name__ == '__main__':
    create_flowchart()
    create_ros2_architecture()
    create_floorplan()
