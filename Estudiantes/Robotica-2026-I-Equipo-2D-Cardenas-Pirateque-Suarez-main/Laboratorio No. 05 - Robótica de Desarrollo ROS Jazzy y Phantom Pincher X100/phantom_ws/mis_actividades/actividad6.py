#!/usr/bin/env python3
"""
Actividad 6 - Determinación de limites seguros (VERSIÓN GUI COMPACTA).
Asistente visual interactivo de libre elección para calibrar límites seguros.
Robot: Phantom X Pincher X100
"""

import os
import csv
import json
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import rclpy

# Import local de la arquitectura del robot
from joint_selector import JointSelector, JOINTS

# Rutas de almacenamiento
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIMITES_DIR = os.path.join(BASE_DIR, "limites_act6")
LIMITES_JSON = os.path.join(LIMITES_DIR, "limites_seguros.json")
LIMITES_CSV = os.path.join(LIMITES_DIR, "limites_seguros.csv")

class AsistenteLimitesGUI:
    def __init__(self, master, node):
        self.master = master
        self.node = node
        self.master.title("Actividad 6 - Determinación de Límites Seguros")
        self.master.geometry("700x600")
        
        self.articulaciones = list(JOINTS.keys())
        self.lecturas_temp = []
        self.resultados = {}
        self.nodos_tabla = {} # Para actualizar filas existentes
        
        self.margen_var = tk.DoubleVar(value=5.0)
        self.var_joint = tk.StringVar(value=self.articulaciones[0])
        
        # Apagar torque para permitir movimiento manual
        self.node.apagar_torque_solamente()
        
        self._crear_widgets()
        self._lectura_en_vivo()

    def _crear_widgets(self):
        # --- HEADER ---
        marco_header = tk.Frame(self.master, bg="#343a40", pady=10)
        marco_header.pack(fill="x")
        tk.Label(marco_header, text="ASISTENTE DE CALIBRACIÓN MANUAL", fg="white", bg="#343a40", font=("Arial", 14, "bold")).pack()

        # --- CONFIGURACIÓN GLOBAL ---
        marco_config = ttk.LabelFrame(self.master, text="Configuración Global", padding=10)
        marco_config.pack(padx=20, pady=5, fill="x")
        
        ttk.Label(marco_config, text="Margen de seguridad por defecto [grados]:", font=("Arial", 10)).pack(side="left", padx=5)
        ttk.Spinbox(marco_config, from_=1.0, to=20.0, increment=1.0, textvariable=self.margen_var, width=8, font=("Arial", 10)).pack(side="left", padx=5)
        tk.Button(marco_config, text="🔄 REINICIAR MOTORES (Torque OFF)", bg="#6c757d", fg="white", font=("Arial", 9, "bold"), command=self.node.apagar_torque_solamente).pack(side="right", padx=10)

        # --- CAPTURA POR ARTICULACIÓN ---
        marco_accion = ttk.LabelFrame(self.master, text="Calibración por Articulación", padding=10)
        marco_accion.pack(padx=20, pady=5, fill="x")
        
        frame_controles = tk.Frame(marco_accion)
        frame_controles.pack(fill="x", pady=5)
        
        ttk.Label(frame_controles, text="Articulación:", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        combo_joint = ttk.Combobox(frame_controles, textvariable=self.var_joint, values=self.articulaciones, state="readonly", width=12, font=("Arial", 10))
        combo_joint.pack(side="left", padx=5)
        combo_joint.bind("<<ComboboxSelected>>", self._cambio_articulacion)
        
        self.lbl_en_vivo = tk.Label(frame_controles, text="Posición: --.-°", font=("Consolas", 14, "bold"), fg="#28a745")
        self.lbl_en_vivo.pack(side="left", padx=20)
        
        self.btn_registrar = tk.Button(frame_controles, text="📸 REGISTRAR EXTREMO 1", bg="#0d6efd", fg="white", font=("Arial", 10, "bold"), command=self._registrar_lectura)
        self.btn_registrar.pack(side="right", padx=5)

        self.lbl_instruccion = tk.Label(marco_accion, text="Selecciona una articulación, llévala a un tope y registra.", font=("Arial", 10), fg="#0056b3")
        self.lbl_instruccion.pack(pady=2)

        # --- TABLA DE RESULTADOS (Ajustada a 5 filas exactas) ---
        marco_tabla = ttk.LabelFrame(self.master, text="Tabla de Límites Seguros", padding=10)
        marco_tabla.pack(padx=20, pady=5, fill="x") 
        
        columnas = ("art", "lim_inf", "lim_sup", "margen")
        self.tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings", height=5)
        self.tabla.heading("art", text="Articulación")
        self.tabla.heading("lim_inf", text="Límite Inferior")
        self.tabla.heading("lim_sup", text="Límite Superior")
        self.tabla.heading("margen", text="Margen Seguridad")
        
        self.tabla.column("art", width=120, anchor="center")
        self.tabla.column("lim_inf", width=120, anchor="center")
        self.tabla.column("lim_sup", width=120, anchor="center")
        self.tabla.column("margen", width=120, anchor="center")
        self.tabla.pack(fill="x")

        # --- BOTÓN EXPORTAR (Aislado entre la tabla y la consola) ---
        marco_medio = tk.Frame(self.master)
        marco_medio.pack(padx=20, pady=(5, 0), fill="x")
        
        self.btn_guardar = tk.Button(marco_medio, text="💾 EXPORTAR JSON Y CSV", bg="#198754", fg="white", font=("Arial", 10, "bold"), state="disabled", command=self._guardar_datos)
        self.btn_guardar.pack(side="right")

        # --- PANEL INFERIOR (Consola expandida libremente) ---
        marco_inferior = tk.Frame(self.master)
        marco_inferior.pack(padx=20, pady=(5, 10), fill="both", expand=True)
        
        self.txt_consola = tk.Text(marco_inferior, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.txt_consola.pack(side="left", fill="both", expand=True)

    def _log(self, msg, color="#00ff00"):
        self.txt_consola.tag_config(color, foreground=color)
        self.txt_consola.insert(tk.END, msg + "\n", color)
        self.txt_consola.see(tk.END)

    def _cambio_articulacion(self, event=None):
        """Resetea las lecturas temporales al cambiar de articulación"""
        self.lecturas_temp = []
        self.btn_registrar.config(text="📸 REGISTRAR EXTREMO 1", bg="#0d6efd")
        self.lbl_instruccion.config(text="Mueve la articulación cerca de un tope mecánico y registra.", fg="#0056b3")

    def _lectura_en_vivo(self):
        nombre = self.var_joint.get()
        val = self.node.leer_posicion(nombre)
        if val is not None:
            self.lbl_en_vivo.config(text=f"Posición: {val:+.1f}°")
        else:
            self.lbl_en_vivo.config(text="Posición: --.-°")
            
        self.master.after(100, self._lectura_en_vivo)

    def _registrar_lectura(self):
        nombre = self.var_joint.get()
        val = self.node.leer_posicion(nombre)
        if val is None:
            val = 0.0 
            
        self.lecturas_temp.append(val)
        num_lectura = len(self.lecturas_temp)
        self._log(f"[{nombre.upper()}] Extremo {num_lectura}: {val:+.1f}°", "cyan")
        
        if num_lectura == 1:
            self.btn_registrar.config(text="📸 REGISTRAR EXTREMO 2", bg="#198754")
            self.lbl_instruccion.config(text="Mueve la articulación hacia el tope OPUESTO y registra.", fg="#d63384")
        elif num_lectura == 2:
            self._procesar_articulacion(nombre)
            self._cambio_articulacion() # Resetea la interfaz para la siguiente articulación

    def _procesar_articulacion(self, nombre):
        ext_inf = min(self.lecturas_temp)
        ext_sup = max(self.lecturas_temp)
        margen = self.margen_var.get()
        
        lim_inf = ext_inf + margen
        lim_sup = ext_sup - margen
        margen_efectivo = margen
        
        if lim_inf >= lim_sup:
            margen_efectivo = max(0.0, (ext_sup - ext_inf) / 2 - 0.5)
            lim_inf = ext_inf + margen_efectivo
            lim_sup = ext_sup - margen_efectivo
            self._log(f"⚠️ Margen ajustado en '{nombre}' a {margen_efectivo:.1f}° por poco espacio.", "orange")
            
        self.resultados[nombre] = {
            "extremo_inferior": round(ext_inf, 1),
            "extremo_superior": round(ext_sup, 1),
            "limite_inferior": round(lim_inf, 1),
            "limite_superior": round(lim_sup, 1),
            "margen_seguridad": round(margen_efectivo, 1),
        }
        
        # Insertar o actualizar la fila en la tabla
        valores = (nombre.capitalize(), f"{lim_inf:+.1f}°", f"{lim_sup:+.1f}°", f"{margen_efectivo:.1f}°")
        
        if nombre in self.nodos_tabla:
            self.tabla.item(self.nodos_tabla[nombre], values=valores)
            self._log(f"🔄 '{nombre.upper()}' recalibrada y actualizada.", "yellow")
        else:
            item_id = self.tabla.insert("", "end", values=valores)
            self.nodos_tabla[nombre] = item_id
            self._log(f"✅ '{nombre.upper()}' calibrada.", "green")
            
        # Habilitar el botón de guardado solo cuando estén todas las articulaciones
        if len(self.resultados) >= len(self.articulaciones):
            self.btn_guardar.config(state="normal")
            self.lbl_instruccion.config(text="¡Todas las articulaciones calibradas! Puedes exportar.", fg="#198754")

    def _guardar_datos(self):
        os.makedirs(LIMITES_DIR, exist_ok=True)
        
        filas_csv = [("articulacion", "extremo_inferior_deg", "extremo_superior_deg", 
                      "limite_inferior_deg", "limite_superior_deg", "margen_seguridad_deg")]
        for nombre, d in self.resultados.items():
            filas_csv.append((
                nombre, f"{d['extremo_inferior']:.1f}", f"{d['extremo_superior']:.1f}",
                f"{d['limite_inferior']:.1f}", f"{d['limite_superior']:.1f}", f"{d['margen_seguridad']:.1f}"
            ))
            
        with open(LIMITES_CSV, "w", newline="") as f:
            csv.writer(f).writerows(filas_csv)
            
        with open(LIMITES_JSON, "w") as f:
            json.dump(self.resultados, f, indent=2)
            
        self._log(f"\n✅ DATOS EXPORTADOS CORRECTAMENTE.", "green")
        messagebox.showinfo("Proceso Terminado", f"Límites guardados en:\n{LIMITES_DIR}")


def main(args=None):
    rclpy.init(args=args)
    node = JointSelector()
    
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()
    time.sleep(1.0) 
    
    root = tk.Tk()
    app = AsistenteLimitesGUI(root, node)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        node.apagar()
        rclpy.shutdown()

if __name__ == "__main__":
    main()