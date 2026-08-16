#!/usr/bin/env python3
"""
Actividad 12 - Cinemática Inversa.
Cálculo de configuraciones articulares a partir de (X, Y, Z, Theta).
Incluye descarte por límites, selección de codo arriba/abajo, parada de emergencia, slider y recuadro de velocidad.
"""

import time
import math
import threading
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import rclpy

# Import local de la arquitectura del robot y límites seguros (Actividad 6)
from joint_selector import JointSelector, JOINTS, LIMITS_DEG

# =================================================================
# MEDIDAS FÍSICAS EXACTAS DE LA TABLA (En metros)
# =================================================================
L1 = 0.0450
L2 = 0.1070
L3 = 0.1070
L4 = 0.1088

class InterfazCinematicaInversa:
    def __init__(self, master, node):
        self.master = master
        self.node = node
        self.master.title("Cinemática Inversa - Actividad 12")
        self.master.geometry("600x750")
        self.master.minsize(550, 700)
        self.master.resizable(True, True)
        
        self.parada_emergencia = False
        
        # 5 Pruebas Cartesianas (X[mm], Y[mm], Z[mm], Pitch Theta[°])
        self.pruebas_cartesianas = {
            "Prueba 1: Agarre Frontal (Horizontal)": [200.0, 0.0, 50.0, 0.0],
            "Prueba 2: Agarre Suelo (Vertical)": [150.0, 0.0, 10.0, -90.0],
            "Prueba 3: Reposo Alto": [120.0, 0.0, 250.0, 45.0],
            "Prueba 4: Lateral Derecha": [100.0, -150.0, 100.0, 0.0],
            "Prueba 5: Lateral Izquierda": [100.0, 150.0, 100.0, 0.0]
        }
        
        self._crear_widgets()

    def _crear_widgets(self):
        # --- BOTÓN DE PARADA DE EMERGENCIA ---
        self.btn_emergencia = tk.Button(self.master, text="🚨 !!! PARADA DE EMERGENCIA !!!", bg="#dc3545", fg="white", font=("Arial", 13, "bold"), command=self._parada_emergencia_accion)
        self.btn_emergencia.pack(padx=20, pady=10, fill="x")

        # --- PRUEBAS PREDEFINIDAS ---
        marco_rapido = ttk.LabelFrame(self.master, text="Pruebas Cartesianas Requeridas", padding=10)
        marco_rapido.pack(padx=20, pady=5, fill="x")
        
        self.combo_pruebas = ttk.Combobox(marco_rapido, values=list(self.pruebas_cartesianas.keys()), state="readonly")
        self.combo_pruebas.current(0)
        self.combo_pruebas.pack(side="left", padx=10, expand=True, fill="x")
        
        btn_cargar = tk.Button(marco_rapido, text="Cargar Coordenadas", bg="#ffc107", font=("Arial", 9, "bold"), command=self._cargar_prueba)
        btn_cargar.pack(side="right", padx=10)

        # --- ENTRADAS CARTESIANAS ---
        marco_cartesianas = ttk.LabelFrame(self.master, text="Coordenadas Objetivo (X, Y, Z, Theta)", padding=10)
        marco_cartesianas.pack(padx=20, pady=5, fill="x")
        
        self.vars_cart = {}
        etiquetas = ["X [mm]:", "Y [mm]:", "Z [mm]:", "Theta (Pitch) [°]:"]
        llaves = ["x", "y", "z", "theta"]
        valores_iniciales = [200.0, 0.0, 50.0, 0.0]
        
        for i, (etiq, llave, val) in enumerate(zip(etiquetas, llaves, valores_iniciales)):
            ttk.Label(marco_cartesianas, text=etiq, font=("Arial", 10, "bold")).grid(row=i//2, column=(i%2)*2, sticky="e", pady=5, padx=5)
            var = tk.DoubleVar(value=val)
            spin = ttk.Spinbox(marco_cartesianas, from_=-400.0, to=400.0, increment=10.0, textvariable=var, width=10)
            spin.grid(row=i//2, column=(i%2)*2+1, sticky="w", pady=5, padx=5)
            self.vars_cart[llave] = var

        # --- CONTROL MANUAL (TORQUE, HOME Y VELOCIDAD) ---
        marco_manual = ttk.LabelFrame(self.master, text="Control Manual del Robot", padding=10)
        marco_manual.pack(padx=20, pady=5, fill="x")
        
        # Botones
        frame_botones = tk.Frame(marco_manual)
        frame_botones.pack(fill="x", pady=5)
        tk.Button(frame_botones, text="TORQUE ON", bg="#007bff", fg="white", font=("Arial", 9, "bold"), command=self.node.habilitar_torque).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(frame_botones, text="TORQUE OFF", bg="#6c757d", fg="white", font=("Arial", 9, "bold"), command=self.node.apagar_torque_solamente).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(frame_botones, text="IR A HOME (0°)", bg="#17a2b8", fg="white", font=("Arial", 9, "bold"), command=self._home_accion).pack(side="left", expand=True, fill="x", padx=2)

        # Slider y Entrada numérica de velocidad
        frame_vel = tk.Frame(marco_manual)
        frame_vel.pack(fill="x", pady=10)
        ttk.Label(frame_vel, text="Velocidad (1-1023):", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        
        self.var_velocidad = tk.IntVar(value=150)
        self.var_velocidad.trace_add("write", self._cambiar_velocidad)
        
        self.spin_velocidad = ttk.Spinbox(frame_vel, from_=1, to=1023, increment=10, textvariable=self.var_velocidad, width=7)
        self.spin_velocidad.pack(side="left", padx=5)

        self.slider_velocidad = tk.Scale(frame_vel, from_=1, to=1023, orient="horizontal", variable=self.var_velocidad)
        self.slider_velocidad.pack(side="left", fill="x", expand=True, padx=5)

        # --- BOTÓN CALCULAR Y EJECUTAR ---
        self.btn_ejecutar = tk.Button(self.master, text="▶ CALCULAR INVERSA Y MOVER", bg="#28a745", fg="white", font=("Arial", 11, "bold"), command=self._iniciar_calculo)
        self.btn_ejecutar.pack(pady=10, fill="x", padx=20)
        
        # --- CONSOLA DE RESULTADOS Y ANÁLISIS ---
        marco_consola = ttk.LabelFrame(self.master, text="Análisis de Soluciones", padding=10)
        marco_consola.pack(padx=20, pady=5, fill="both", expand=True)
        
        self.txt_consola = tk.Text(marco_consola, height=10, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.txt_consola.pack(fill="both", expand=True)

    def _cambiar_velocidad(self, *args):
        try:
            val = self.var_velocidad.get()
            if 1 <= val <= 1023:
                self.node.set_velocidad(val)
        except tk.TclError:
            pass 

    def _cargar_prueba(self):
        seleccion = self.combo_pruebas.get()
        valores = self.pruebas_cartesianas[seleccion]
        self.vars_cart["x"].set(valores[0])
        self.vars_cart["y"].set(valores[1])
        self.vars_cart["z"].set(valores[2])
        self.vars_cart["theta"].set(valores[3])

    def _parada_emergencia_accion(self):
        self.parada_emergencia = True
        self.node.apagar_torque_solamente()
        self._log("!!! PARADA DE EMERGENCIA ACTIVADA !!! TORQUE APAGADO.", color="red")

    def _home_accion(self):
        self._log("Moviendo a HOME (0°)...", color="white")
        config_home = {name: 0.0 for name in JOINTS}
        threading.Thread(target=self._rutina_movimiento, args=(config_home,)).start()

    def _log(self, mensaje, color="#00ff00"):
        self.txt_consola.tag_config(color, foreground=color)
        self.txt_consola.insert(tk.END, mensaje + "\n", color)
        self.txt_consola.see(tk.END)

    def _calcular_cinematica_inversa(self, x, y, z, theta_deg):
        """Calcula el modelo geométrico inverso del Phantom X."""
        X, Y, Z = x/1000.0, y/1000.0, z/1000.0
        theta_rad = math.radians(theta_deg)
        
        # 1. Base (q1)
        q1_rad = math.atan2(Y, X)
        q1 = math.degrees(q1_rad)
        
        R = math.sqrt(X**2 + Y**2)
        
        # Angulo sigma
        sigma_q_deg = 90.0 - theta_deg
        sigma_q_rad = math.radians(sigma_q_deg)
        
        # 2. Centro de la Muñeca (Wrist Center)
        R_wc = R - L4 * math.sin(sigma_q_rad)
        Z_wc = Z - L4 * math.cos(sigma_q_rad)
        
        # 3. Vector desde el Hombro al Centro de la Muñeca
        dR = R_wc
        dZ = Z_wc - L1
        D = math.sqrt(dR**2 + dZ**2)
        
        # 4. Verificación de Alcanzabilidad
        # Agregamos una tolerancia de 0.1 mm (0.0001 metros) por errores de coma flotante en Python
        tolerancia = 0.0001
        if D > (L2 + L3 + tolerancia) or D < (abs(L2 - L3) - tolerancia):
            return [] # Inalcanzable
            
        # 5. Ecuaciones Geométricas (Teorema del Coseno)
        cos_beta = (L2**2 + L3**2 - D**2) / (2 * L2 * L3)
        cos_beta = max(-1.0, min(1.0, cos_beta))
        beta = math.acos(cos_beta)
        
        cos_alpha = (L2**2 + D**2 - L3**2) / (2 * L2 * D)
        cos_alpha = max(-1.0, min(1.0, cos_alpha))
        alpha = math.acos(cos_alpha)
        
        gamma = math.atan2(dR, dZ)
        
        soluciones = []
        
        # Solución 1: Codo Abajo (Elbow Down)
        q2_1 = math.degrees(gamma + alpha)
        q3_1 = math.degrees(-math.pi + beta)
        q4_1 = sigma_q_deg - q2_1 - q3_1
        soluciones.append({
            "tipo": "Codo Abajo", 
            "q": {"base": q1, "hombro": q2_1, "codo": q3_1, "muneca": q4_1, "pinza": 0.0}
        })
        
        # Solución 2: Codo Arriba (Elbow Up)
        q2_2 = math.degrees(gamma - alpha)
        q3_2 = math.degrees(math.pi - beta)
        q4_2 = sigma_q_deg - q2_2 - q3_2
        soluciones.append({
            "tipo": "Codo Arriba", 
            "q": {"base": q1, "hombro": q2_2, "codo": q3_2, "muneca": q4_2, "pinza": 0.0}
        })
        
        return soluciones

    def _verificar_limites(self, q_dict):
        """Descarta soluciones que incumplan los límites de seguridad."""
        for art, angulo in q_dict.items():
            if art in LIMITS_DEG:
                lim_inf, lim_sup = LIMITS_DEG[art]
                if angulo < lim_inf or angulo > lim_sup:
                    return False, art, angulo
        return True, "", 0.0

    def _iniciar_calculo(self):
        self.txt_consola.delete('1.0', tk.END)
        self.parada_emergencia = False
        
        try:
            x = self.vars_cart["x"].get()
            y = self.vars_cart["y"].get()
            z = self.vars_cart["z"].get()
            theta = self.vars_cart["theta"].get()
        except tk.TclError:
            self._log("Error: Introduce números válidos.", "red")
            return
            
        self._log(f"Objetivo: X={x}, Y={y}, Z={z}, Theta={theta}°", "white")
        
        # 1. Calcular soluciones posibles
        soluciones_crudas = self._calcular_cinematica_inversa(x, y, z, theta)
        
        if not soluciones_crudas:
            self._log("❌ ERROR: El punto solicitado es INALCANZABLE geométricamente.", "red")
            return
            
        soluciones_validas = []
        
        # 2. Identificar codo arriba/abajo y descartar incumplimientos
        for sol in soluciones_crudas:
            es_valida, art_falla, angulo_falla = self._verificar_limites(sol["q"])
            if es_valida:
                self._log(f"✅ {sol['tipo']} VÁLIDA: [q1:{sol['q']['base']:.1f}°, q2:{sol['q']['hombro']:.1f}°, q3:{sol['q']['codo']:.1f}°, q4:{sol['q']['muneca']:.1f}°]", "green")
                soluciones_validas.append(sol)
            else:
                self._log(f"⚠️ {sol['tipo']} DESCARTADA: {art_falla} ({angulo_falla:.1f}°) viola límites.", "orange")
                
        if not soluciones_validas:
            self._log("❌ ERROR: Existen soluciones, pero todas violan los límites físicos.", "red")
            return
            
        # 3. Ejecutar la solución válida más cercana a la configuración actual
        posiciones_actuales = self.node.leer_todas()
        
        mejor_solucion = None
        menor_distancia = float('inf')
        
        for sol in soluciones_validas:
            distancia = 0.0
            for art in ["base", "hombro", "codo", "muneca"]:
                pos_actual = posiciones_actuales.get(art, 0.0)
                if pos_actual is None: pos_actual = 0.0
                distancia += (sol["q"][art] - pos_actual)**2
                
            distancia = math.sqrt(distancia)
            if distancia < menor_distancia:
                menor_distancia = distancia
                mejor_solucion = sol
                
        self._log(f"\n=> Ejecutando {mejor_solucion['tipo']} por ser la trayectoria más corta.", "cyan")
        
        # Mover en hilo paralelo
        hilo = threading.Thread(target=self._rutina_movimiento, args=(mejor_solucion["q"],))
        hilo.start()

    def _rutina_movimiento(self, objetivos_q):
        self.btn_ejecutar.config(state="disabled", bg="gray")
        
        # 1. Leer el slider de velocidad
        vel_slider = self.var_velocidad.get()
        
        # 2. Mapeo matemático SEGURO (Curva de protección para el hardware físico)
        # Slider en 1 (mínimo) = Tarda 5.0 segundos
        # Slider en 1023 (máximo) = Tarda 1.5 segundos (Rápido, pero sin dañar motores)
        tiempo_total = 5.0 - ((vel_slider - 1) / 1022.0) * 3.5
        
        # 3. Delegar la fluidez al controlador interno de ROS 2
        # Al no usar un bucle 'for', ROS 2 calcula la curva perfecta sin laguearse.
        if not self.parada_emergencia:
            self.node.mover_simultaneo(objetivos_q, espera_s=tiempo_total)
            self.master.after(0, lambda: self._log(f"Movimiento completado fluidamente en {tiempo_total:.1f}s.", "cyan"))
            
        self.btn_ejecutar.config(state="normal", bg="#28a745")

def main(args=None):
    rclpy.init(args=args)
    node = JointSelector()
    
    # Hilo para lectura en segundo plano
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()
    time.sleep(1)
    
    node.habilitar_torque()
    node.set_velocidad(150)
    
    root = tk.Tk()
    app = InterfazCinematicaInversa(root, node)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        node.apagar()
        rclpy.shutdown()

if __name__ == '__main__':
    main()