#!/usr/bin/env python3
"""
Actividad 10 - Trayectoria sinusoidal interactiva (GUI) con Parada de Emergencia.
Soporte para q0 variable, tiempo dinámico, torque manual y botón HOME.
"""

import time
import math
import threading
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
import rclpy

# Import local del puente de comunicaciones adaptado a nuestra estructura
from joint_selector import JointSelector, JOINTS, LIMITS_DEG

class InterfazSinusoidal:
    def __init__(self, master, node):
        self.master = master
        self.node = node
        self.master.title("Control Sinusoidal - Actividad 10")
        
        # Configuración de tamaño inicial y ventana redimensionable
        self.master.geometry("550x580")
        self.master.minsize(500, 520)
        self.master.resizable(True, True)
        
        self.dt = 0.05
        self.parada_emergencia = False
        
        self._crear_widgets()
        self._actualizar_limites() # Configurar límites iniciales

    def _crear_widgets(self):
        # --- 1. BOTÓN DE PARADA DE EMERGENCIA ---
        self.btn_emergencia = tk.Button(
            self.master, 
            text="🚨 !!! PARADA DE EMERGENCIA !!!", 
            bg="#dc3545", 
            fg="white", 
            font=("Arial", 13, "bold"), 
            activebackground="#b21f2d",
            activeforeground="white",
            command=self._parada_emergencia_accion
        )
        self.btn_emergencia.pack(padx=20, pady=10, fill="x")

        # --- 2. MARCO PRINCIPAL DE PARÁMETROS ---
        marco = ttk.LabelFrame(self.master, text="Parámetros de la Trayectoria", padding=15)
        marco.pack(padx=20, pady=5, fill="both", expand=True)

        # Selección de Articulación
        ttk.Label(marco, text="1. Articulación:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=8)
        self.combo_art = ttk.Combobox(marco, values=list(JOINTS.keys()), state="readonly", width=15)
        self.combo_art.current(0) # Selecciona 'base' por defecto
        self.combo_art.grid(row=0, column=1, sticky="w")
        self.combo_art.bind("<<ComboboxSelected>>", self._actualizar_limites)

        # Posición Inicial (q0)
        ttk.Label(marco, text="2. Posición Central q0 [°]:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=8)
        self.var_q0 = tk.DoubleVar(value=0.0)
        self.var_q0.trace_add("write", self._actualizar_limites)
        self.spin_q0 = ttk.Spinbox(marco, from_=-150.0, to=150.0, increment=5.0, textvariable=self.var_q0, width=10)
        self.spin_q0.grid(row=1, column=1, sticky="w")
        self.lbl_limite_q0 = ttk.Label(marco, text="Rango: []", foreground="gray")
        self.lbl_limite_q0.grid(row=1, column=2, sticky="w", padx=5)

        # Amplitud (A)
        ttk.Label(marco, text="3. Amplitud A [°]:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=8)
        self.var_amplitud = tk.DoubleVar(value=30.0)
        self.spin_amplitud = ttk.Spinbox(marco, from_=0.0, to=150.0, increment=5.0, textvariable=self.var_amplitud, width=10)
        self.spin_amplitud.grid(row=2, column=1, sticky="w")
        self.lbl_limite_A = ttk.Label(marco, text="(Max: )", foreground="gray")
        self.lbl_limite_A.grid(row=2, column=2, sticky="w", padx=5)

        # Frecuencia (f)
        ttk.Label(marco, text="4. Frecuencia f [Hz]:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", pady=8)
        self.var_frecuencia = tk.DoubleVar(value=0.25)
        self.spin_frecuencia = ttk.Spinbox(marco, from_=0.05, to=2.0, increment=0.05, textvariable=self.var_frecuencia, width=10)
        self.spin_frecuencia.grid(row=3, column=1, sticky="w")

        # Tiempo de prueba (t)
        ttk.Label(marco, text="5. Tiempo Total [s]:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="w", pady=8)
        self.var_tiempo = tk.DoubleVar(value=8.0)
        self.spin_tiempo = ttk.Spinbox(marco, from_=1.0, to=60.0, increment=1.0, textvariable=self.var_tiempo, width=10)
        self.spin_tiempo.grid(row=4, column=1, sticky="w")

        # --- 3. PANEL DE CONTROL DIRECTO (TORQUE Y HOME) ---
        marco_manual = ttk.LabelFrame(self.master, text="Control Manual de Hardware", padding=10)
        marco_manual.pack(padx=20, pady=5, fill="x")

        sub_grid = ttk.Frame(marco_manual)
        sub_grid.pack(fill="x")

        self.btn_torque_on = tk.Button(sub_grid, text="TORQUE ON", bg="#007bff", fg="white", font=("Arial", 9, "bold"), command=self._torque_on_accion)
        self.btn_torque_on.grid(row=0, column=0, padx=5, sticky="ew")

        self.btn_torque_off = tk.Button(sub_grid, text="TORQUE OFF", bg="#6c757d", fg="white", font=("Arial", 9, "bold"), command=self._torque_off_accion)
        self.btn_torque_off.grid(row=0, column=1, padx=5, sticky="ew")

        self.btn_home = tk.Button(sub_grid, text="IR A HOME (0°)", bg="#17a2b8", fg="white", font=("Arial", 9, "bold"), command=self._home_accion)
        self.btn_home.grid(row=0, column=2, padx=5, sticky="ew")

        sub_grid.grid_columnconfigure(0, weight=1)
        sub_grid.grid_columnconfigure(1, weight=1)
        sub_grid.grid_columnconfigure(2, weight=1)

        # --- 4. BOTÓN EJECUTAR ---
        self.btn_ejecutar = tk.Button(
            self.master, 
            text="▶ EJECUTAR TRAYECTORIA SINUSOIDAL", 
            bg="#28a745", 
            fg="white", 
            font=("Arial", 11, "bold"), 
            command=self._iniciar_prueba
        )
        self.btn_ejecutar.pack(pady=10, fill="x", padx=20)
        
        self.lbl_estado = ttk.Label(self.master, text="Estado: Listo", foreground="blue", font=("Arial", 10))
        self.lbl_estado.pack(pady=5)

    def _actualizar_limites(self, *args):
        articulacion = self.combo_art.get()
        lim_inf, lim_sup = LIMITS_DEG[articulacion]
        
        self.spin_q0.config(from_=lim_inf, to=lim_sup)
        self.lbl_limite_q0.config(text=f"Rango: [{lim_inf}°, {lim_sup}°]")
        
        try:
            q0 = self.var_q0.get()
        except tk.TclError:
            q0 = 0.0
            
        if q0 < lim_inf:
            self.var_q0.set(lim_inf)
            q0 = lim_inf
        elif q0 > lim_sup:
            self.var_q0.set(lim_sup)
            q0 = lim_sup
            
        distancia_sup = lim_sup - q0
        distancia_inf = q0 - lim_inf
        max_amp = max(0.0, min(distancia_sup, distancia_inf))
        
        self.spin_amplitud.config(to=max_amp)
        self.lbl_limite_A.config(text=f"(Max permitido: {max_amp:.1f}°)")
        
        try:
            amp_actual = self.var_amplitud.get()
            if amp_actual > max_amp:
                self.var_amplitud.set(round(max_amp, 1))
        except tk.TclError:
            pass

    def _parada_emergencia_accion(self):
        """Corta la ejecución de la trayectoria y apaga el torque de inmediato."""
        self.parada_emergencia = True
        self.node.apagar_torque_solamente()
        self.lbl_estado.config(text="!!! PARADA DE EMERGENCIA ACTIVA !!!", foreground="red", font=("Arial", 11, "bold"))

    def _torque_on_accion(self):
        self.node.habilitar_torque()
        self.lbl_estado.config(text="Torque habilitado (Motores rígidos)", foreground="green")

    def _torque_off_accion(self):
        self.node.apagar_torque_solamente()
        self.lbl_estado.config(text="Torque deshabilitado (Brazo libre)", foreground="orange")

    def _home_accion(self):
        self.lbl_estado.config(text="Enviando robot a HOME...", foreground="blue")
        hilo = threading.Thread(target=self._rutina_home)
        hilo.start()

    def _rutina_home(self):
        config_home = {name: 0.0 for name in JOINTS}
        self.node.mover_simultaneo(config_home, espera_s=2.5)
        self.master.after(0, lambda: self.lbl_estado.config(text="Robot en HOME (0°)", foreground="green"))

    def _iniciar_prueba(self):
        try:
            q0 = self.var_q0.get()
            A = self.var_amplitud.get()
            f = self.var_frecuencia.get()
            tiempo_total = self.var_tiempo.get()
        except tk.TclError:
            messagebox.showwarning("Error", "Revisa que todos los campos tengan valores numéricos válidos.")
            return

        articulacion = self.combo_art.get()

        if A < 0 or f <= 0 or tiempo_total <= 0:
            messagebox.showwarning("Error", "La amplitud debe ser ≥ 0. La frecuencia y tiempo deben ser > 0.")
            return

        # Inicializar bandera de control y bloquear interfaz para evitar ejecuciones traslapadas
        self.parada_emergencia = False
        self.btn_ejecutar.config(state="disabled", bg="gray")
        self.combo_art.config(state="disabled")
        self.lbl_estado.config(text=f"Llevando a q0 ({q0}°) y ejecutando onda...", foreground="red")
        
        # Ejecutar en un hilo paralelo para mantener viva la GUI y la Parada de Emergencia
        hilo = threading.Thread(target=self._rutina_movimiento, args=(articulacion, q0, A, f, tiempo_total))
        hilo.start()

    def _rutina_movimiento(self, articulacion, q0, A, f, tiempo_total):
        tiempos_reales = []
        q_deseados = []
        q_medidos = []
        
        # Primero llevamos de manera controlada al centro q0
        self.node.mover_articulacion(articulacion, q0, espera_s=2.5)
        
        t_inicio = time.time()
        abortado = False
        
        while True:
            if self.parada_emergencia:
                abortado = True
                break
                
            t_actual = time.time() - t_inicio
            if t_actual > tiempo_total:
                break
                
            # Ecuación q(t) = q0 + A*sin(2*pi*f*t)
            q_des = q0 + A * math.sin(2 * math.pi * f * t_actual)
            
            # Envío continuo instruyendo al controlador que complete el movimiento en dt
            self.node.mover_articulacion(articulacion, q_des, espera_s=self.dt)
            
            q_med = self.node.leer_posicion(articulacion)
            
            tiempos_reales.append(t_actual)
            q_deseados.append(q_des)
            q_medidos.append(q_med if q_med is not None else q_des)
            
        if abortado:
            self.master.after(0, self._finalizar_aborto)
        else:
            self.node.mover_articulacion(articulacion, 0.0, espera_s=2.5)
            self.master.after(0, self._mostrar_grafica, articulacion, q0, A, f, tiempo_total, tiempos_reales, q_deseados, q_medidos)

    def _finalizar_aborto(self):
        self.lbl_estado.config(text="¡TRAYECTORIA ABORTADA POR EMERGENCIA!", foreground="red", font=("Arial", 10, "bold"))
        self.btn_ejecutar.config(state="normal", bg="#28a745")
        self.combo_art.config(state="readonly")
        messagebox.showwarning("Corte de Emergencia", "Se ha abortado el bucle físico y se deshabilitó el torque del robot.")

    def _mostrar_grafica(self, articulacion, q0, A, f, t_total, t, q_des, q_med):
        t_arr = np.array(t)
        q_des_arr = np.array(q_des)
        q_med_arr = np.array(q_med)
        
        errores = np.abs(q_des_arr - q_med_arr)
        error_max = np.max(errores)
        mse = np.mean(errores**2)
        
        # Restaurar controles de la GUI
        self.lbl_estado.config(text="Prueba finalizada de manera segura.", foreground="blue")
        self.btn_ejecutar.config(state="normal", bg="#28a745")
        self.combo_art.config(state="readonly")
        
        # Desplegar gráfica de resultados
        plt.figure(figsize=(9, 6))
        plt.plot(t_arr, q_des_arr, 'k--', linewidth=2, label="Posición Deseada q(t)")
        plt.plot(t_arr, q_med_arr, 'r-', linewidth=1.5, label="Posición Medida (Real)")
        plt.title(f"Actividad 10 - {articulacion.upper()}\nCentro $q_0$: {q0}° | Amplitud: {A}° | Frecuencia: {f}Hz | Tiempo: {t_total}s\nError Máximo: {error_max:.2f}° | MSE: {mse:.2f}", fontweight='bold')
        plt.xlabel("Tiempo [s]")
        plt.ylabel("Posición [°]")
        plt.grid(True, linestyle=':', alpha=0.7)
        plt.legend(loc="upper right")
        plt.tight_layout()
        
        # Auto-guardado de la gráfica para el reporte de laboratorio
        nombre_archivo = f"grafica_act10_{articulacion}_q0_{q0}_A_{A}_f_{f}.png"
        plt.savefig(nombre_archivo)
        print(f"\n[INFO] Gráfica guardada automáticamente como: {nombre_archivo}")
        
        plt.show()

def main(args=None):
    rclpy.init(args=args)
    node = JointSelector()
    
    # Hilo vital para que el script escuche la posición real en segundo plano
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()
    time.sleep(1) # Pequeña espera para recibir el primer mensaje de ROS 2
    
    node.habilitar_torque()
    node.set_velocidad(1000)
    
    root = tk.Tk()
    app = InterfazSinusoidal(root, node)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        print("\nCerrando interfaz de manera controlada...")
        node.apagar()
        rclpy.shutdown()

if __name__ == '__main__':
    main()