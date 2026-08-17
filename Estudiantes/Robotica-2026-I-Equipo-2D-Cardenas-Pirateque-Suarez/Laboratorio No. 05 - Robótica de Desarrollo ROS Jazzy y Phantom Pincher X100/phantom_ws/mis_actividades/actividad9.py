#!/usr/bin/env python3
"""
Actividad 9 - Interpolación Lineal vs Cúbica (GUI).
Torque permanente y pausas exactas de 3 segundos.
REGLA ESTRICTA: El movimiento físico/simulado ocurre PRIMERO. 
Las gráficas solo se generan y muestran al finalizar toda la rutina.
"""

import time
import csv
import os
import threading
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
import rclpy

# IMPORTACIÓN CORREGIDA PARA EL MODELO NUEVO
from joint_selector import JointSelector, JOINTS, LIMITS_DEG

def calcular_trayectorias_multiples(config_A, config_B, tiempo_total, dt):
    tiempos = np.arange(0, tiempo_total + dt, dt)
    trayectoria_lineal = {nombre: [] for nombre in JOINTS}
    trayectoria_cubica = {nombre: [] for nombre in JOINTS}
    
    for t in tiempos:
        for nombre in JOINTS:
            qi = config_A[nombre]
            qf = config_B[nombre]
            
            # Lineal
            q_lin = qi + (qf - qi) * (t / tiempo_total)
            trayectoria_lineal[nombre].append(q_lin)
            
            # Cúbica
            a0 = qi
            a2 = 3.0 * (qf - qi) / (tiempo_total ** 2)
            a3 = -2.0 * (qf - qi) / (tiempo_total ** 3)
            q_cub = a0 + a2*(t**2) + a3*(t**3)
            trayectoria_cubica[nombre].append(q_cub)
            
    return tiempos, trayectoria_lineal, trayectoria_cubica

def esperar_llegada_real(node, configuracion_objetivo, margen_error_deg=4.0, timeout_s=5.0):
    inicio = time.time()
    while (time.time() - inicio) < timeout_s:
        posiciones_reales = node.leer_todas()
        llegaron_todos = True
        
        for nombre in JOINTS:
            val_real = posiciones_reales.get(nombre)
            if val_real is not None:
                error = abs(val_real - configuracion_objetivo[nombre])
                if error > margen_error_deg:
                    llegaron_todos = False
                    break
            else:
                llegaron_todos = False
                break
                
        if llegaron_todos:
            break
            
        time.sleep(0.1)

class InterfazActividad9:
    def __init__(self, master, node):
        self.master = master
        self.node = node
        self.master.title("Actividad 9 - Interpolación de Trayectorias")
        self.master.geometry("700x750")
        self.master.minsize(650, 700)
        
        self.parada_emergencia = False
        
        # Almacenamiento temporal para graficar después de mover
        self.datos_tiempos = []
        self.datos_lineal = {}
        self.datos_cubica = {}
        
        # Poses por defecto de la guía
        self.val_pose_a = {"base": -62.0, "hombro": 28.0, "codo": -66.0, "muneca": 34.0, "pinza": 44.0}
        self.val_pose_b = {"base": 123.0, "hombro": -36.0, "codo": -36.0, "muneca": 46.0, "pinza": 12.0}
        
        self._crear_widgets()

    def _crear_widgets(self):
        # --- BOTÓN PARADA EMERGENCIA ---
        tk.Button(self.master, text="🚨 !!! PARADA DE EMERGENCIA !!!", bg="#dc3545", fg="white", font=("Arial", 12, "bold"), command=self._emergencia).pack(padx=20, pady=10, fill="x")

        # --- ENTRADAS DE POSES ---
        marco_poses = ttk.LabelFrame(self.master, text="Configuraciones de Extremos (Pose A -> Pose B)", padding=10)
        marco_poses.pack(padx=20, pady=5, fill="x")
        
        self.vars_pose_a = {}
        self.vars_pose_b = {}
        
        ttk.Label(marco_poses, text="Articulación", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(marco_poses, text="Pose A (Inicio)", font=("Arial", 9, "bold"), foreground="blue").grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(marco_poses, text="Pose B (Destino)", font=("Arial", 9, "bold"), foreground="green").grid(row=0, column=2, padx=5, pady=2)
        
        for i, art in enumerate(JOINTS.keys()):
            ttk.Label(marco_poses, text=art.capitalize(), font=("Arial", 9, "bold")).grid(row=i+1, column=0, sticky="w", padx=5, pady=2)
            lim_inf, lim_sup = LIMITS_DEG[art]
            
            var_a = tk.DoubleVar(value=self.val_pose_a[art])
            ttk.Spinbox(marco_poses, from_=lim_inf, to=lim_sup, increment=5.0, textvariable=var_a, width=10).grid(row=i+1, column=1, padx=10, pady=2)
            self.vars_pose_a[art] = var_a
            
            var_b = tk.DoubleVar(value=self.val_pose_b[art])
            ttk.Spinbox(marco_poses, from_=lim_inf, to=lim_sup, increment=5.0, textvariable=var_b, width=10).grid(row=i+1, column=2, padx=10, pady=2)
            self.vars_pose_b[art] = var_b

        # --- PARÁMETROS Y HARDWARE ---
        marco_params = ttk.LabelFrame(self.master, text="Parámetros de Tiempo y Hardware", padding=10)
        marco_params.pack(padx=20, pady=5, fill="x")
        
        frame_t = tk.Frame(marco_params)
        frame_t.pack(fill="x", pady=5)
        ttk.Label(frame_t, text="Tiempo Total [s]:", font=("Arial", 9, "bold")).pack(side="left")
        self.var_tiempo = tk.DoubleVar(value=5.0)
        ttk.Spinbox(frame_t, from_=1.0, to=20.0, increment=1.0, textvariable=self.var_tiempo, width=8).pack(side="left", padx=5)
        
        ttk.Label(frame_t, text="Paso (dt) [s]:", font=("Arial", 9, "bold")).pack(side="left", padx=(20, 0))
        self.var_dt = tk.DoubleVar(value=0.02) # 50 FPS por defecto
        ttk.Spinbox(frame_t, from_=0.01, to=0.5, increment=0.01, textvariable=self.var_dt, width=8).pack(side="left", padx=5)

        frame_hw = tk.Frame(marco_params)
        frame_hw.pack(fill="x", pady=10)
        tk.Button(frame_hw, text="TORQUE ON", bg="#007bff", fg="white", font=("Arial", 8, "bold"), command=self.node.habilitar_torque).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(frame_hw, text="TORQUE OFF", bg="#6c757d", fg="white", font=("Arial", 8, "bold"), command=self.node.apagar_torque_solamente).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(frame_hw, text="IR A HOME", bg="#17a2b8", fg="white", font=("Arial", 8, "bold"), command=lambda: threading.Thread(target=self._ir_home).start()).pack(side="left", expand=True, fill="x", padx=2)

        # --- BOTÓN MAESTRO DE EJECUCIÓN ---
        self.btn_ejecutar = tk.Button(self.master, text="▶ CALCULAR, MOVER ROBOT Y LUEGO GRAFICAR", bg="#28a745", fg="white", font=("Arial", 11, "bold"), command=self._iniciar_hilo_principal)
        self.btn_ejecutar.pack(padx=20, pady=10, fill="x")

        # --- CONSOLA ---
        marco_consola = ttk.LabelFrame(self.master, text="Consola de Operaciones", padding=10)
        marco_consola.pack(padx=20, pady=5, fill="both", expand=True)
        self.txt_consola = tk.Text(marco_consola, height=10, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.txt_consola.pack(fill="both", expand=True)

    def _log(self, msg, color="#00ff00"):
        self.txt_consola.tag_config(color, foreground=color)
        self.txt_consola.insert(tk.END, msg + "\n", color)
        self.txt_consola.see(tk.END)

    def _emergencia(self):
        self.parada_emergencia = True
        self.node.apagar_torque_solamente()
        self._log("\n🚨 EMERGENCIA: Torque apagado. Rutina abortada.", "red")
        self.btn_ejecutar.config(state="normal", bg="#28a745")

    def _ir_home(self):
        self._log("Moviendo a HOME...", "white")
        self.node.mover_simultaneo({name: 0.0 for name in JOINTS}, espera_s=2.5)

    def _iniciar_hilo_principal(self):
        self.btn_ejecutar.config(state="disabled", bg="gray")
        self.parada_emergencia = False
        self.txt_consola.delete('1.0', tk.END)
        threading.Thread(target=self._rutina_completa, daemon=True).start()

    def _rutina_completa(self):
        """
        Ejecuta el orden estricto: 
        1. Matemáticas -> 2. Mover Robot Físico/RViz -> 3. Graficar
        """
        conf_A = {art: self.vars_pose_a[art].get() for art in JOINTS}
        conf_B = {art: self.vars_pose_b[art].get() for art in JOINTS}
        tiempo_total = self.var_tiempo.get()
        dt = self.var_dt.get()
        config_home = {name: 0.0 for name in JOINTS}

        # ---------------------------------------------------------
        # PASO 1: MATEMÁTICAS (Sin tocar Matplotlib)
        # ---------------------------------------------------------
        self._log(f"Calculando trayectorias (T={tiempo_total}s, dt={dt}s)...", "cyan")
        self.datos_tiempos, self.datos_lineal, self.datos_cubica = calcular_trayectorias_multiples(conf_A, conf_B, tiempo_total, dt)

        # Exportar CSV de una vez
        ruta_guardado = os.path.dirname(os.path.abspath(__file__))
        nombre_csv = os.path.join(ruta_guardado, "trayectorias_act9.csv")
        try:
            with open(nombre_csv, mode='w', newline='') as archivo_csv:
                escritor = csv.writer(archivo_csv)
                encabezados = ["Tiempo_s"] + [f"{n.capitalize()}_Lin" for n in JOINTS] + [f"{n.capitalize()}_Cub" for n in JOINTS]
                escritor.writerow(encabezados)
                for i in range(len(self.datos_tiempos)):
                    fila = [round(self.datos_tiempos[i], 3)]
                    for n in JOINTS: fila.append(round(self.datos_lineal[n][i], 3))
                    for n in JOINTS: fila.append(round(self.datos_cubica[n][i], 3))
                    escritor.writerow(fila)
            self._log("Datos exportados a CSV exitosamente.", "green")
        except Exception as e:
            self._log(f"Error guardando CSV: {e}", "red")

        # ---------------------------------------------------------
        # PASO 2: MOVIMIENTO DEL ROBOT (Streaming en tiempo real)
        # ---------------------------------------------------------
        self._log("\n[ FASE 1: INICIO EN HOME ]", "yellow")
        self.node.mover_simultaneo(config_home, espera_s=2.5)
        time.sleep(3.0) 
        
        # --- PRUEBA LINEAL ---
        if self.parada_emergencia: return
        self._log("\n[ PRUEBA LINEAL ]", "cyan")
        self._log("-> Yendo a Pose A (Inicio)...", "white")
        self.node.mover_simultaneo(conf_A, espera_s=2.5)
        time.sleep(3.0) 
        
        self._log("-> Ejecutando interpolación paso a paso...", "cyan")
        for i in range(len(self.datos_tiempos)):
            if self.parada_emergencia: break
            objetivos = {nombre: self.datos_lineal[nombre][i] for nombre in JOINTS}
            self.node.mover_simultaneo(objetivos, espera_s=0.0)
            time.sleep(dt)
            
        if self.parada_emergencia: return
        esperar_llegada_real(self.node, conf_B)
        self._log("-> ¡Llegada confirmada! Esperando 3s en Pose B...", "white")
        time.sleep(3.0) 
        
        self._log("-> Regresando a HOME...", "yellow")
        self.node.mover_simultaneo(config_home, espera_s=2.5)
        time.sleep(3.0) 

        # --- PRUEBA CÚBICA ---
        if self.parada_emergencia: return
        self._log("\n[ PRUEBA CÚBICA ]", "cyan")
        self._log("-> Yendo a Pose A (Inicio)...", "white")
        self.node.mover_simultaneo(conf_A, espera_s=2.5)
        time.sleep(3.0) 

        self._log("-> Ejecutando interpolación paso a paso...", "cyan")
        for i in range(len(self.datos_tiempos)):
            if self.parada_emergencia: break
            objetivos = {nombre: self.datos_cubica[nombre][i] for nombre in JOINTS}
            self.node.mover_simultaneo(objetivos, espera_s=0.0)
            time.sleep(dt)
            
        if self.parada_emergencia: return
        esperar_llegada_real(self.node, conf_B)
        self._log("-> ¡Llegada confirmada! Esperando 3s en Pose B...", "white")
        time.sleep(3.0) 
            
        self._log("-> Regresando a HOME...", "yellow")
        self.node.mover_simultaneo(config_home, espera_s=2.5)
        time.sleep(3.0)

        # ---------------------------------------------------------
        # PASO 3: DIBUJAR Y MOSTRAR GRÁFICA AL FINALIZAR TODO
        # ---------------------------------------------------------
        if not self.parada_emergencia:
            self._log("\nRutina física finalizada con éxito. Generando gráficas...", "green")
            # Delegar la interfaz gráfica de Matplotlib al hilo principal para evitar crasheos de GUI
            self.master.after(0, self._dibujar_graficas_finales)

    def _dibujar_graficas_finales(self):
        ruta_guardado = os.path.dirname(os.path.abspath(__file__))
        nombre_grafica = os.path.join(ruta_guardado, "grafica_act9_todas_articulaciones.png")
        
        fig, axs = plt.subplots(5, 1, figsize=(10, 14), sharex=True)
        articulaciones_lista = ["base", "hombro", "codo", "muneca", "pinza"]
        colores = {"base": "red", "hombro": "blue", "codo": "green", "muneca": "orange", "pinza": "purple"}
        
        for idx, nombre in enumerate(articulaciones_lista):
            axs[idx].plot(self.datos_tiempos, self.datos_lineal[nombre], color=colores[nombre], linestyle='--', alpha=0.6, label="Lineal")
            axs[idx].plot(self.datos_tiempos, self.datos_cubica[nombre], color=colores[nombre], linestyle='-', linewidth=2.5, label="Cúbica")
            axs[idx].set_title(f"Articulación: {nombre.upper()}", fontsize=11, fontweight='bold')
            axs[idx].set_ylabel("Posición [°]", fontsize=9)
            axs[idx].grid(True, linestyle=':', alpha=0.6)
            axs[idx].legend(loc="upper left", fontsize=8)
            
        axs[-1].set_xlabel("Tiempo [s]", fontsize=10, fontweight='bold')
        plt.tight_layout()
        plt.savefig(nombre_grafica)
        self._log(f"Gráfica guardada en:\n{nombre_grafica}", "green")
        
        self.btn_ejecutar.config(state="normal", bg="#28a745")
        
        # Esto abrirá la ventana emergente con la imagen
        plt.show()

def main(args=None):
    rclpy.init(args=args)
    node = JointSelector()
    
    # Hilo en segundo plano obligatorio
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()
    time.sleep(1.0) 
    
    node.habilitar_torque()
    node.set_velocidad(180)
    
    root = tk.Tk()
    app = InterfazActividad9(root, node)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        node.apagar()
        rclpy.shutdown()

if __name__ == '__main__':
    main()