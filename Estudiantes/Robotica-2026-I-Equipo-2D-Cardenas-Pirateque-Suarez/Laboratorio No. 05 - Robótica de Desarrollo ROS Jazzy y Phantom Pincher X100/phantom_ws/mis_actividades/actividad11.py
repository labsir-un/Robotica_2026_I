#!/usr/bin/env python3
"""
Actividad 11 - Cinemática Directa (Parámetros DH).
Cálculo teórico de x, y, z, roll, pitch, yaw y movimiento físico/simulado.
"""

import math
import threading
import time
import numpy as np
import tkinter as tk
from tkinter import ttk
import rclpy

# Import local de la arquitectura del robot y límites seguros (Actividad 6)
from joint_selector import JointSelector, JOINTS, LIMITS_DEG

# =================================================================
# CONFIGURACIÓN DE MEDIDAS FÍSICAS (Valores exactos de la tabla)
# Convertidos de cm a metros para compatibilidad con ROS 2
# =================================================================
L1 = 0.0450  # 4.5 cm
L2 = 0.1070  # 10.7 cm
L3 = 0.1070  # 10.7 cm
L4 = 0.1088  # 10.88 cm

def matriz_dh(theta, d, a, alpha):
    """Calcula la matriz de transformación homogénea clásica de Denavit-Hartenberg."""
    return np.array([
        [np.cos(theta), -np.sin(theta)*np.cos(alpha),  np.sin(theta)*np.sin(alpha), a*np.cos(theta)],
        [np.sin(theta),  np.cos(theta)*np.cos(alpha), -np.cos(theta)*np.sin(alpha), a*np.sin(theta)],
        [0.0,            np.sin(alpha),                np.cos(alpha),               d],
        [0.0,            0.0,                          0.0,                         1.0]
    ])

def extraer_xyz_rpy(T):
    """Extrae posición y ángulos de Euler (Roll, Pitch, Yaw) de una matriz homogénea."""
    x = T[0, 3]
    y = T[1, 3]
    z = T[2, 3]
    
    # Extracción de RPY (Convención XYZ fija / ZYX Euler)
    pitch = math.atan2(-T[2, 0], math.sqrt(T[2, 1]**2 + T[2, 2]**2))
    
    if abs(math.cos(pitch)) > 1e-6:
        yaw = math.atan2(T[1, 0], T[0, 0])
        roll = math.atan2(T[2, 1], T[2, 2])
    else:
        # Singularidad (Gimbal Lock)
        yaw = 0.0
        roll = math.atan2(-T[1, 2], T[1, 1])
        if pitch < 0:
            roll = -roll
            
    return x, y, z, math.degrees(roll), math.degrees(pitch), math.degrees(yaw)

class InterfazCinematica:
    def __init__(self, master, node):
        self.master = master
        self.node = node
        self.master.title("Cinemática Directa - Actividad 11")
        self.master.geometry("550x650")
        self.master.resizable(True, True)
        
        # Diccionario para guardar las 5 configuraciones de tu Actividad 7
        # Orden: [base, hombro, codo, muneca, pinza] en grados
        self.configuraciones_act7 = {
            "Configuración 1 (HOME)": [0.0, 0.0, 0.0, 0.0, 0.0],
            "Configuración 2": [25.0, 25.0, 20.0, -20.0, 0.0],
            "Configuración 3": [-35.0, 35.0, -30.0, 30.0, 0.0],
            "Configuración 4": [85.0, -20.0, 55.0, 25.0, 0.0],
            "Configuración 5": [80.0, -35.0, 55.0, -45.0, 0.0]
        }
        
        self._crear_widgets()

    def _crear_widgets(self):
        # 1. Menú de Configuración Rápida
        marco_rapido = ttk.LabelFrame(self.master, text="Configuraciones Guardadas (Actividad 7)", padding=10)
        marco_rapido.pack(padx=20, pady=10, fill="x")
        
        self.combo_configs = ttk.Combobox(marco_rapido, values=list(self.configuraciones_act7.keys()), state="readonly")
        self.combo_configs.current(0)
        self.combo_configs.pack(side="left", padx=10, expand=True, fill="x")
        
        btn_cargar = tk.Button(marco_rapido, text="Cargar Configuración", bg="#ffc107", font=("Arial", 9, "bold"), command=self._cargar_config)
        btn_cargar.pack(side="right", padx=10)

        # 2. Controles Manuales de Articulaciones
        marco_articulaciones = ttk.LabelFrame(self.master, text="Entrada de Articulaciones (q1, q2, q3, q4)", padding=10)
        marco_articulaciones.pack(padx=20, pady=10, fill="x")
        
        self.vars_q = {}
        nombres = ["Base (q1)", "Hombro (q2)", "Codo (q3)", "Muñeca (q4)", "Pinza (Gripper)"]
        llaves_reales = ["base", "hombro", "codo", "muneca", "pinza"]
        
        for i, (nombre, llave) in enumerate(zip(nombres, llaves_reales)):
            ttk.Label(marco_articulaciones, text=nombre, font=("Arial", 10, "bold")).grid(row=i, column=0, sticky="w", pady=5)
            var = tk.DoubleVar(value=0.0)
            
            # Extraemos los límites seguros para esta articulación
            lim_inf, lim_sup = LIMITS_DEG[llave]
            
            spin = ttk.Spinbox(marco_articulaciones, from_=lim_inf, to=lim_sup, increment=5.0, textvariable=var, width=15)
            spin.grid(row=i, column=1, padx=20, sticky="w")
            
            # Indicador visual de los límites al lado del spinbox
            ttk.Label(marco_articulaciones, text=f"[{lim_inf}°, {lim_sup}°]", foreground="gray").grid(row=i, column=2, sticky="w")
            
            self.vars_q[llave] = var

        # 3. Botones de Acción
        marco_acciones = tk.Frame(self.master)
        marco_acciones.pack(padx=20, pady=10, fill="x")
        
        btn_ejecutar = tk.Button(marco_acciones, text="▶ MOVER Y CALCULAR CINEMÁTICA", bg="#28a745", fg="white", font=("Arial", 12, "bold"), command=self._ejecutar_cinematica)
        btn_ejecutar.pack(fill="x", pady=5)
        
        # El botón de Home ahora apunta a su propia función dedicada
        btn_home = tk.Button(marco_acciones, text="IR A HOME", bg="#17a2b8", fg="white", font=("Arial", 10, "bold"), command=self._ir_a_home)
        btn_home.pack(fill="x", pady=5)

        # 4. Panel de Resultados Matemáticos (Cinemática Directa)
        marco_resultados = ttk.LabelFrame(self.master, text="Resultados Teóricos (Denavit-Hartenberg)", padding=15)
        marco_resultados.pack(padx=20, pady=10, fill="both", expand=True)

        self.lbl_x = ttk.Label(marco_resultados, text="X: 0.000 mm", font=("Courier", 12, "bold"), foreground="#d63384")
        self.lbl_x.pack(anchor="w", pady=2)
        self.lbl_y = ttk.Label(marco_resultados, text="Y: 0.000 mm", font=("Courier", 12, "bold"), foreground="#d63384")
        self.lbl_y.pack(anchor="w", pady=2)
        self.lbl_z = ttk.Label(marco_resultados, text="Z: 0.000 mm", font=("Courier", 12, "bold"), foreground="#d63384")
        self.lbl_z.pack(anchor="w", pady=2)
        
        ttk.Separator(marco_resultados, orient='horizontal').pack(fill='x', pady=8)
        
        self.lbl_roll = ttk.Label(marco_resultados, text="Roll:  0.00°", font=("Courier", 12, "bold"), foreground="#0d6efd")
        self.lbl_roll.pack(anchor="w", pady=2)
        self.lbl_pitch = ttk.Label(marco_resultados, text="Pitch: 0.00°", font=("Courier", 12, "bold"), foreground="#0d6efd")
        self.lbl_pitch.pack(anchor="w", pady=2)
        self.lbl_yaw = ttk.Label(marco_resultados, text="Yaw:   0.00°", font=("Courier", 12, "bold"), foreground="#0d6efd")
        self.lbl_yaw.pack(anchor="w", pady=2)

    def _cargar_config(self):
        seleccion = self.combo_configs.get()
        valores = self.configuraciones_act7[seleccion]
        self._cargar_manual(valores)
        
    def _cargar_manual(self, valores):
        llaves = ["base", "hombro", "codo", "muneca", "pinza"]
        for llave, val in zip(llaves, valores):
            self.vars_q[llave].set(val)
        self._calcular_dh() # Solo calcula, NO mueve

    def _ir_a_home(self):
        """Lleva todos los campos a 0.0 y envía el comando de movimiento real."""
        self._cargar_manual([0.0, 0.0, 0.0, 0.0, 0.0])
        self._ejecutar_cinematica()

    def _calcular_dh(self):
        # 1. Obtener ángulos en radianes
        q1 = math.radians(self.vars_q["base"].get())
        q2 = math.radians(self.vars_q["hombro"].get())
        q3 = math.radians(self.vars_q["codo"].get())
        q4 = math.radians(self.vars_q["muneca"].get())
        
        # ⚠️ CORRECCIÓN CLAVE: Offset Geométrico vs DH 
        # Geométricamente 0° es ARRIBA, pero en DH 0° es ADELANTE.
        q2_dh = q2 - (math.pi / 2.0)
        
        # 2. Construir matrices T según la tabla DH oficial
        T01 = matriz_dh(q1, L1, 0.0, -math.pi/2) # alpha_1 = -90°
        
        # Inyectamos el ángulo corregido SOLO al hombro
        T12 = matriz_dh(q2_dh, 0.0, L2, 0.0)
        
        T23 = matriz_dh(q3, 0.0, L3, 0.0)
        T34 = matriz_dh(q4, 0.0, L4, 0.0)
        
        # 3. Multiplicar matrices (T_final = T01 * T12 * T23 * T34)
        T02 = np.dot(T01, T12)
        T03 = np.dot(T02, T23)
        T04 = np.dot(T03, T34)
        
        # 4. Extraer datos y mostrar en la UI
        x, y, z, roll, pitch, yaw = extraer_xyz_rpy(T04)
        
        self.lbl_x.config(text=f"X: {x*1000:>8.2f} mm")
        self.lbl_y.config(text=f"Y: {y*1000:>8.2f} mm")
        self.lbl_z.config(text=f"Z: {z*1000:>8.2f} mm")
        
        self.lbl_roll.config(text=f"Roll:  {roll:>8.2f}°")
        self.lbl_pitch.config(text=f"Pitch: {pitch:>8.2f}°")
        self.lbl_yaw.config(text=f"Yaw:   {yaw:>8.2f}°")

    def _ejecutar_cinematica(self):
        # 1. Reflejar cálculo en pantalla de forma instantánea
        self._calcular_dh()
        
        # 2. Mover el robot real/simulado en un hilo aparte
        objetivos = {llave: var.get() for llave, var in self.vars_q.items()}
        hilo = threading.Thread(target=lambda: self.node.mover_simultaneo(objetivos, espera_s=1.5))
        hilo.start()

def main(args=None):
    rclpy.init(args=args)
    node = JointSelector()
    
    # Hilo vital para que el script escuche y envíe comandos a ROS 2
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()
    time.sleep(1)
    
    node.habilitar_torque()
    node.set_velocidad(150)
    
    root = tk.Tk()
    app = InterfazCinematica(root, node)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        node.apagar()
        rclpy.shutdown()

if __name__ == '__main__':
    main()