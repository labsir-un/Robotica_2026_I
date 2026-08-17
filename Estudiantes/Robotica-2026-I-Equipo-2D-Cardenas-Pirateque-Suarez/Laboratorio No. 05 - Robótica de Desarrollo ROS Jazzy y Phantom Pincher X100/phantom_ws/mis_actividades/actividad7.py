#!/usr/bin/env python3
"""
Actividad 7 - Movimiento Simultáneo (GUI).
Ejecución y validación de 5 configuraciones articulares específicas.
Incluye protección de límites (con justificación automática), control de velocidad seguro y parada de emergencia.
"""

import time
import threading
import tkinter as tk
from tkinter import ttk
import rclpy

# Import local de la arquitectura del robot y límites seguros
from joint_selector import JointSelector, JOINTS, LIMITS_DEG

# Configuraciones extraídas EXACTAMENTE de la guía del laboratorio
CONFIGURACIONES_ACT7 = {
    "Configuración 1": [0.0, 0.0, 0.0, 0.0, 0.0],
    "Configuración 2": [25.0, 25.0, 20.0, -20.0, 0.0],
    "Configuración 3": [-35.0, 35.0, -30.0, 30.0, 0.0],
    "Configuración 4": [85.0, -20.0, 55.0, 25.0, 0.0],
    "Configuración 5": [80.0, -35.0, 55.0, -45.0, 0.0]
}

class InterfazActividad7:
    def __init__(self, master, node):
        self.master = master
        self.node = node
        self.master.title("Movimiento Simultáneo - Actividad 7")
        self.master.geometry("600x650")
        self.master.minsize(550, 600)
        self.master.resizable(True, True)
        
        self.parada_emergencia = False
        self._crear_widgets()

    def _crear_widgets(self):
        # --- 1. BOTÓN DE PARADA DE EMERGENCIA ---
        self.btn_emergencia = tk.Button(self.master, text="🚨 !!! PARADA DE EMERGENCIA !!!", bg="#dc3545", fg="white", font=("Arial", 13, "bold"), command=self._parada_emergencia_accion)
        self.btn_emergencia.pack(padx=20, pady=10, fill="x")

        # --- 2. SELECCIÓN DE CONFIGURACIONES ---
        marco_rapido = ttk.LabelFrame(self.master, text="Configuraciones del Laboratorio", padding=10)
        marco_rapido.pack(padx=20, pady=5, fill="x")
        
        self.combo_pruebas = ttk.Combobox(marco_rapido, values=list(CONFIGURACIONES_ACT7.keys()), state="readonly", font=("Arial", 11))
        self.combo_pruebas.current(0)
        self.combo_pruebas.pack(side="left", padx=10, expand=True, fill="x")
        
        btn_cargar = tk.Button(marco_rapido, text="▶ EJECUTAR CONFIGURACIÓN", bg="#28a745", fg="white", font=("Arial", 10, "bold"), command=self._ejecutar_configuracion)
        btn_cargar.pack(side="right", padx=10)

        # --- 3. CONTROL MANUAL DEL HARDWARE ---
        marco_manual = ttk.LabelFrame(self.master, text="Control y Seguridad del Robot", padding=10)
        marco_manual.pack(padx=20, pady=5, fill="x")
        
        frame_botones = tk.Frame(marco_manual)
        frame_botones.pack(fill="x", pady=5)
        tk.Button(frame_botones, text="TORQUE ON", bg="#007bff", fg="white", font=("Arial", 9, "bold"), command=self.node.habilitar_torque).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(frame_botones, text="TORQUE OFF", bg="#6c757d", fg="white", font=("Arial", 9, "bold"), command=self.node.apagar_torque_solamente).pack(side="left", expand=True, fill="x", padx=2)
        self.btn_home = tk.Button(frame_botones, text="IR A HOME (0°)", bg="#17a2b8", fg="white", font=("Arial", 9, "bold"), command=self._home_accion)
        self.btn_home.pack(side="left", expand=True, fill="x", padx=2)

        # Slider de velocidad con mapeo seguro
        frame_vel = tk.Frame(marco_manual)
        frame_vel.pack(fill="x", pady=10)
        ttk.Label(frame_vel, text="Velocidad (1-1023):", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        
        self.var_velocidad = tk.IntVar(value=150)
        self.var_velocidad.trace_add("write", self._cambiar_velocidad)
        
        ttk.Spinbox(frame_vel, from_=1, to=1023, increment=10, textvariable=self.var_velocidad, width=7).pack(side="left", padx=5)
        tk.Scale(frame_vel, from_=1, to=1023, orient="horizontal", variable=self.var_velocidad).pack(side="left", fill="x", expand=True, padx=5)

        # --- 4. CONSOLA DE DIAGNÓSTICO Y JUSTIFICACIÓN ---
        marco_consola = ttk.LabelFrame(self.master, text="Análisis de Restricciones y Resultados", padding=10)
        marco_consola.pack(padx=20, pady=5, fill="both", expand=True)
        
        self.txt_consola = tk.Text(marco_consola, height=12, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.txt_consola.pack(fill="both", expand=True)

    def _cambiar_velocidad(self, *args):
        try:
            val = self.var_velocidad.get()
            if 1 <= val <= 1023:
                self.node.set_velocidad(val)
        except tk.TclError:
            pass

    def _parada_emergencia_accion(self):
        self.parada_emergencia = True
        self.node.apagar_torque_solamente()
        self._log("\n🚨 PARADA DE EMERGENCIA ACTIVADA. Torque apagado.", color="red")

    def _home_accion(self):
        self._log("\nRegresando a HOME (0°)...", color="white")
        config_home = {name: 0.0 for name in JOINTS}
        threading.Thread(target=self._rutina_movimiento, args=(config_home,)).start()

    def _log(self, mensaje, color="#00ff00"):
        self.txt_consola.tag_config(color, foreground=color)
        self.txt_consola.insert(tk.END, mensaje + "\n", color)
        self.txt_consola.see(tk.END)

    def _validar_justificar_limites(self, config_valores):
        """Revisa la configuración contra los topes y genera la justificación si es insegura."""
        llaves = ["base", "hombro", "codo", "muneca", "pinza"]
        config_segura = {}
        es_segura = True
        
        for llave, valor_teorico in zip(llaves, config_valores):
            lim_inf, lim_sup = LIMITS_DEG[llave]
            
            if valor_teorico < lim_inf:
                self._log(f"⚠️ MODIFICACIÓN REQUERIDA en {llave.upper()}:", "orange")
                self._log(f"   Justificación: El ángulo solicitado ({valor_teorico}°) es menor al límite seguro ({lim_inf}°). Podría causar colisión mecánica.", "yellow")
                config_segura[llave] = lim_inf
                es_segura = False
            elif valor_teorico > lim_sup:
                self._log(f"⚠️ MODIFICACIÓN REQUERIDA en {llave.upper()}:", "orange")
                self._log(f"   Justificación: El ángulo solicitado ({valor_teorico}°) supera el límite seguro ({lim_sup}°). Riesgo de daño en servomotor.", "yellow")
                config_segura[llave] = lim_sup
                es_segura = False
            else:
                config_segura[llave] = valor_teorico
                
        return es_segura, config_segura

    def _ejecutar_configuracion(self):
        seleccion = self.combo_pruebas.get()
        valores_teoricos = CONFIGURACIONES_ACT7[seleccion]
        
        self.txt_consola.delete('1.0', tk.END)
        self.parada_emergencia = False
        
        self._log(f"--- Evaluando {seleccion} ---", "cyan")
        self._log(f"Valores teóricos: {valores_teoricos}", "white")
        
        es_segura, config_segura = self._validar_justificar_limites(valores_teoricos)
        
        if es_segura:
            self._log("✅ Configuración evaluada como SEGURA.", "green")
        else:
            self._log("⚠️ Configuración truncada a márgenes seguros antes del envío.", "orange")
            
        # Ejecutar en hilo para no bloquear la interfaz
        hilo = threading.Thread(target=self._rutina_movimiento, args=(config_segura,))
        hilo.start()

    def _rutina_movimiento(self, objetivos_q):
        self.master.after(0, lambda: self.btn_home.config(state="disabled"))

        # Ahora permitimos velocidades mucho más rápidas (0.2s) para la Actividad 7
        vel_slider = self.var_velocidad.get()
        tiempo_total = 5.0 - ((vel_slider - 1) / 1022.0) * 4.8

        if not self.parada_emergencia:
            self.master.after(0, lambda: self._log(f"Enviando trayectoria simultánea ({tiempo_total:.1f}s)...", "cyan"))

            # mover_simultaneo YA duerme espera_s internamente antes de retornar,
            # así que aquí solo esperamos un pequeño margen extra, no tiempo_total otra vez
            self.node.mover_simultaneo(objetivos_q, espera_s=tiempo_total)
            time.sleep(0.2)

            if not self.parada_emergencia:
                pos_reales = self.node.leer_todas()

                def _mostrar_reporte():
                    self._log("\n--- Reporte de Posición Final ---", "white")
                    for art, obj in objetivos_q.items():
                        real = pos_reales.get(art, 0.0)
                        if real is None:
                            real = 0.0
                        self._log(f" * {art.capitalize()}: Deseado = {obj:.1f}° | Real = {real:.1f}°", "green")

                self.master.after(0, _mostrar_reporte)

        self.master.after(0, lambda: self.btn_home.config(state="normal"))

def main(args=None):
    rclpy.init(args=args)
    node = JointSelector()
    
    # Hilo vital para escuchar posiciones
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()
    time.sleep(1)
    
    node.habilitar_torque()
    node.set_velocidad(150)
    
    root = tk.Tk()
    app = InterfazActividad7(root, node)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        node.apagar()
        rclpy.shutdown()

if __name__ == '__main__':
    main()