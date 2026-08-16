#!/usr/bin/env python3
"""
Actividad 5 - Calibración de cero y error articular.
Asistente visual para evaluar el error de cada articulación y generar gráficas.
Requiere: pip install matplotlib numpy
"""

import os
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import rclpy
import matplotlib.pyplot as plt
import numpy as np

# Import local del puente de comunicaciones
from joint_selector import JointSelector, JOINTS

# Definimos 5 posiciones seguras para cada articulación
PUNTOS_PRUEBA = {
    "base":   [-100.0, -50.0, 0.0, 50.0, 100.0],
    "hombro": [-80.0, -40.0, 0.0, 40.0,  80.0],
    "codo":   [-90.0, -45.0, 0.0, 45.0,  90.0],
    "muneca": [-70.0, -35.0, 0.0, 35.0,  70.0],
    "pinza":  [-10.0,   5.0, 20.0, 35.0, 50.0],
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRAFICAS_DIR = os.path.join(BASE_DIR, "graficas_act5")

class AsistenteCalibracionGUI:
    def __init__(self, master, node):
        self.master = master
        self.node = node
        self.master.title("Actividad 5 - Calibración de Cero y Error")
        self.master.geometry("750x750")
        self.master.minsize(700, 700)
        
        self.articulaciones = list(JOINTS.keys())
        self.var_joint = tk.StringVar(value=self.articulaciones[0])
        
        self.parada_emergencia = False
        self.detener_rutina = False
        self.rutina_activa = False
        
        # En esta actividad SÍ necesitamos torque para que se mueva solo
        self.node.habilitar_torque()
        
        self._crear_widgets()
        self._lectura_en_vivo()

    def _crear_widgets(self):
        # --- HEADER ---
        marco_header = tk.Frame(self.master, bg="#343a40", pady=10)
        marco_header.pack(fill="x")
        tk.Label(marco_header, text="ASISTENTE DE CALIBRACIÓN DE ERROR ARTICULAR", fg="white", bg="#343a40", font=("Arial", 14, "bold")).pack()

        # --- BOTONES DE SEGURIDAD ---
        frame_seguridad = tk.Frame(self.master)
        frame_seguridad.pack(padx=20, pady=10, fill="x")
        tk.Button(frame_seguridad, text="🚨 EMERGENCIA", bg="#dc3545", fg="white", font=("Arial", 10, "bold"), command=self._emergencia).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(frame_seguridad, text="🛑 DETENER RUTINA", bg="#fd7e14", fg="white", font=("Arial", 10, "bold"), command=self._detener).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(frame_seguridad, text="🏠 IR A HOME", bg="#17a2b8", fg="white", font=("Arial", 10, "bold"), command=self._ir_home).pack(side="left", expand=True, fill="x", padx=2)

        # --- PANEL DE CONTROL ---
        marco_control = ttk.LabelFrame(self.master, text="Control de Prueba", padding=10)
        marco_control.pack(padx=20, pady=5, fill="x")
        
        ttk.Label(marco_control, text="Articulación a evaluar:", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        combo_joint = ttk.Combobox(marco_control, textvariable=self.var_joint, values=self.articulaciones, state="readonly", width=12, font=("Arial", 10))
        combo_joint.pack(side="left", padx=5)
        combo_joint.bind("<<ComboboxSelected>>", self._cambio_articulacion)
        
        self.lbl_en_vivo = tk.Label(marco_control, text="Posición: --.-°", font=("Consolas", 14, "bold"), fg="#28a745")
        self.lbl_en_vivo.pack(side="left", padx=20)
        
        self.btn_iniciar = tk.Button(marco_control, text="▶️ INICIAR PRUEBA DE 5 PUNTOS", bg="#0d6efd", fg="white", font=("Arial", 10, "bold"), command=self._iniciar_rutina)
        self.btn_iniciar.pack(side="right", padx=5)

        # --- TABLA DE RESULTADOS ---
        marco_tabla = ttk.LabelFrame(self.master, text="Lecturas y Error (e_q = q_deseado - q_medido)", padding=10)
        marco_tabla.pack(padx=20, pady=5, fill="x")
        
        columnas = ("punto", "deseado", "medido", "error")
        self.tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings", height=5)
        self.tabla.heading("punto", text="Punto")
        self.tabla.heading("deseado", text="Deseado (°)")
        self.tabla.heading("medido", text="Medido (°)")
        self.tabla.heading("error", text="Error e_q (°)")
        
        self.tabla.column("punto", width=80, anchor="center")
        self.tabla.column("deseado", width=120, anchor="center")
        self.tabla.column("medido", width=120, anchor="center")
        self.tabla.column("error", width=120, anchor="center")
        self.tabla.pack(fill="x")

        # --- ESTADÍSTICAS ---
        self.marco_stats = ttk.LabelFrame(self.master, text="Resultados Estadísticos (Paso 4 y 5)", padding=10)
        self.marco_stats.pack(padx=20, pady=5, fill="x")
        
        self.lbl_err_max = tk.Label(self.marco_stats, text="Error Máximo: --.-°", font=("Arial", 11, "bold"), fg="#d63384")
        self.lbl_err_max.pack(side="left", expand=True)
        
        self.lbl_err_prom = tk.Label(self.marco_stats, text="Error Promedio: --.-°", font=("Arial", 11, "bold"), fg="#0d6efd")
        self.lbl_err_prom.pack(side="left", expand=True)
        
        self.lbl_cero = tk.Label(self.marco_stats, text="Desplaz. de Cero: --.-°", font=("Arial", 11, "bold"), fg="#198754")
        self.lbl_cero.pack(side="left", expand=True)

        # --- CONSOLA ---
        marco_inferior = tk.Frame(self.master)
        marco_inferior.pack(padx=20, pady=(5, 10), fill="both", expand=True)
        
        self.txt_consola = tk.Text(marco_inferior, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.txt_consola.pack(side="left", fill="both", expand=True)

    # ================= FUNCIONES DE UI Y LOG =================
    def _log(self, msg, color="#00ff00"):
        self.txt_consola.tag_config(color, foreground=color)
        self.txt_consola.insert(tk.END, msg + "\n", color)
        self.txt_consola.see(tk.END)

    def _emergencia(self):
        self.parada_emergencia = True
        self.node.apagar_torque_solamente()
        self._log("\n🚨 EMERGENCIA: Motores apagados. Rutina abortada.", "red")
        self._restaurar_botones()

    def _detener(self):
        self.detener_rutina = True
        self._log("\n🛑 RUTINA DETENIDA. El robot mantendrá su posición.", "orange")
        self._restaurar_botones()

    def _ir_home(self):
        if not self.rutina_activa:
            self._log("Moviendo a HOME de forma segura...", "cyan")
            self.node.mover_simultaneo({name: 0.0 for name in JOINTS}, espera_s=2.0)
        else:
            self._log("⚠️ No puedes ir a Home mientras una rutina está activa.", "orange")

    def _cambio_articulacion(self, event=None):
        self.tabla.delete(*self.tabla.get_children())
        self.lbl_err_max.config(text="Error Máximo: --.-°")
        self.lbl_err_prom.config(text="Error Promedio: --.-°")
        self.lbl_cero.config(text="Desplaz. de Cero: --.-°")
        self._log(f"Lista para evaluar: {self.var_joint.get().upper()}", "white")

    def _restaurar_botones(self):
        self.rutina_activa = False
        self.btn_iniciar.config(state="normal", text="▶️ INICIAR PRUEBA DE 5 PUNTOS", bg="#0d6efd")

    def _lectura_en_vivo(self):
        nombre = self.var_joint.get()
        val = self.node.leer_posicion(nombre)
        if val is not None:
            self.lbl_en_vivo.config(text=f"Posición: {val:+.1f}°")
        else:
            self.lbl_en_vivo.config(text="Posición: --.-°")
        self.master.after(100, self._lectura_en_vivo)

    # ================= HILO DE PRUEBA =================
    def _iniciar_rutina(self):
        nombre = self.var_joint.get()
        if self.rutina_activa: return
        
        self.tabla.delete(*self.tabla.get_children())
        self.parada_emergencia = False
        self.detener_rutina = False
        self.rutina_activa = True
        
        self.btn_iniciar.config(state="disabled", text="⏳ EVALUANDO...", bg="#6c757d")
        
        # Nos aseguramos de que el torque esté encendido por si hubo una emergencia antes
        self.node.habilitar_torque() 
        
        # Lanzamos el proceso en un hilo para no congelar la interfaz
        threading.Thread(target=self._proceso_calibracion, args=(nombre,), daemon=True).start()

    def _proceso_calibracion(self, nombre):
        self._log(f"\n--- Iniciando calibración automática para: {nombre.upper()} ---", "cyan")
        posiciones_deseadas = PUNTOS_PRUEBA[nombre]
        
        mediciones_reales = []
        errores = []
        
        for i, q_deseado in enumerate(posiciones_deseadas):
            if self.parada_emergencia or self.detener_rutina:
                return

            self._log(f"Punto {i+1}: Viajando a {q_deseado}°...", "white")
            self.node.mover_articulacion(nombre, q_deseado, espera_s=2.0)
            
            # Dejamos que estabilice 1 segundo extra
            time.sleep(1.0)
            
            if self.parada_emergencia or self.detener_rutina:
                return
                
            q_medido = self.node.leer_posicion(nombre)
            if q_medido is None: q_medido = 0.0
            
            e_q = q_deseado - q_medido
            
            mediciones_reales.append(q_medido)
            errores.append(e_q)
            
            # Actualizamos la tabla usando master.after para evitar errores de hilos en Tkinter
            self.master.after(0, self._insertar_fila, i+1, q_deseado, q_medido, e_q)
            self._log(f"   -> Medido: {q_medido:+.1f}° | Error: {e_q:+.1f}°", "yellow")

        # Regresar a Home tras terminar
        self._log("Retornando a 0.0° de forma segura...", "cyan")
        self.node.mover_articulacion(nombre, 0.0, espera_s=2.0)
        
        if not self.parada_emergencia and not self.detener_rutina:
            self._calcular_y_graficar(nombre, posiciones_deseadas, mediciones_reales, errores)

        self.master.after(0, self._restaurar_botones)

    def _insertar_fila(self, punto, deseado, medido, error):
        self.tabla.insert("", "end", values=(punto, f"{deseado:+.1f}", f"{medido:+.1f}", f"{error:+.1f}"))

    def _calcular_y_graficar(self, nombre, deseados, reales, errores):
        # 1. Cálculos matemáticos
        error_maximo = max(np.abs(errores))
        error_promedio = np.mean(np.abs(errores))
        
        # Encontrar el error donde q_deseado era 0.0
        try:
            idx_cero = deseados.index(0.0)
            desplazamiento_cero = errores[idx_cero]
        except ValueError:
            desplazamiento_cero = errores[len(errores)//2] # Fallback al centro
            
        # 2. Actualizar UI
        def actualizar_labels():
            self.lbl_err_max.config(text=f"Error Máximo: {error_maximo:.1f}°")
            self.lbl_err_prom.config(text=f"Error Promedio: {error_promedio:.1f}°")
            self.lbl_cero.config(text=f"Desplaz. de Cero: {desplazamiento_cero:.1f}°")
            self._log(f"\n✅ Análisis completado. Aplicar corrección de {-desplazamiento_cero:+.1f}° al cero.", "green")
            
        self.master.after(0, actualizar_labels)
        
        # 3. Generar Gráfica de Matplotlib
        os.makedirs(GRAFICAS_DIR, exist_ok=True)
        plt.figure(figsize=(7, 4))
        
        plt.plot(deseados, deseados, 'k--', label="Ideal (Deseado = Medido)")
        plt.plot(deseados, reales, 'o-', color='blue', label="Real (Medido)", markersize=8)
        
        plt.title(f"Calibración de Error - {nombre.capitalize()}")
        plt.xlabel("Posición Deseada ($q_{deseado}$) [Grados]")
        plt.ylabel("Posición Medida ($q_{medido}$) [Grados]")
        plt.legend()
        plt.grid(True, linestyle=':', alpha=0.7)
        
        ruta_grafica = os.path.join(GRAFICAS_DIR, f"grafica_error_{nombre}.png")
        plt.savefig(ruta_grafica)
        plt.close()
        
        self.master.after(0, self._log, f"📊 Gráfica generada: {ruta_grafica}", "cyan")

def main(args=None):
    rclpy.init(args=args)
    node = JointSelector()
    
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()
    time.sleep(1.0) 
    
    root = tk.Tk()
    app = AsistenteCalibracionGUI(root, node)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        node.apagar()
        rclpy.shutdown()

if __name__ == '__main__':
    main()