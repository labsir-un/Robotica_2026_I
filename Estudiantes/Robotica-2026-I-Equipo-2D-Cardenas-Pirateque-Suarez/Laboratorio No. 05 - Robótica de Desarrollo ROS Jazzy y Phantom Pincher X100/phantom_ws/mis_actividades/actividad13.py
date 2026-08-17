#!/usr/bin/env python3
"""
Actividad 13 - Enseñanza y repetición de poses (Teach & Play).
Integra control manual de articulaciones, captura de poses (físicas o simuladas),
parada de emergencia, torque manual, reproducción fluida delegada a ROS 2 y persistencia YAML.
"""

import os
import time
import yaml
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import rclpy
from joint_selector import JointSelector, JOINTS, LIMITS_DEG

# =================================================================
# RUTA ABSOLUTA PARA ARCHIVOS YAML (Adaptada a tu espacio de trabajo)
# =================================================================
RUTA_YAMLS = os.path.join(os.path.expanduser("~"), "ros2_jazzy", "Lab5", "Codigos", "phantom_ws", "mis_actividades", "yamls")

class InterfazEnsenanzaCompleta:
    def __init__(self, master, node):
        self.master = master
        self.node = node
        self.master.title("Consola de Aprendizaje (Teach Pendant) - Actividad 13")
        self.master.geometry("1000x700")
        self.master.minsize(950, 650)
        self.master.resizable(True, True)
        
        self.parada_emergencia = False
        self.reproduciendo = False
        self.lista_poses = []  # Almacena diccionarios: {"nombre": str, "q": dict}
        
        self.vars_joints = {}
        self.traces = {}
        
        self._crear_interfaz()

    def _crear_interfaz(self):
        # --- COLUMNA IZQUIERDA (CONTROL MANUAL ESTILO ACTIVIDAD 4) ---
        marco_izq = ttk.LabelFrame(self.master, text=" Control Manual de Articulaciones (Simulación / Físico) ", padding=15)
        marco_izq.pack(side="left", fill="both", expand=True, padx=15, pady=15)

        for art, (lim_inf, lim_sup) in LIMITS_DEG.items():
            frame_art = tk.Frame(marco_izq)
            frame_art.pack(fill="x", pady=10)
            
            lbl_nombre = ttk.Label(frame_art, text=f"{art.upper()} [{lim_inf}° a {lim_sup}°]:", font=("Arial", 10, "bold"))
            lbl_nombre.pack(anchor="w")
            
            # Variable doble para sincronizar Slider y Spinbox
            var = tk.DoubleVar(value=0.0)
            self.vars_joints[art] = var
            
            # Contenedor para alinear los controles en la misma fila
            row_cont = tk.Frame(frame_art)
            row_cont.pack(fill="x")
            
            spin = ttk.Spinbox(row_cont, from_=lim_inf, to=lim_sup, increment=5.0, textvariable=var, width=8, font=("Arial", 10))
            spin.pack(side="left", padx=5)
            
            slider = tk.Scale(row_cont, from_=lim_inf, to=lim_sup, orient="horizontal", variable=var, resolution=0.5, showvalue=False)
            slider.pack(side="left", fill="x", expand=True, padx=5)
            
            # Vincular cambio de variable con movimiento en tiempo real (Trace)
            trace_id = var.trace_add("write", lambda *args, a=art: self._on_joint_gui_change(a))
            self.traces[art] = trace_id

        # Panel de Control de Velocidad (Slider + Teclado)
        frame_vel_cont = ttk.LabelFrame(marco_izq, text=" Configuración de Velocidad de Hardware ", padding=10)
        frame_vel_cont.pack(fill="x", pady=20)
        
        self.var_velocidad = tk.IntVar(value=150)
        self.var_velocidad.trace_add("write", self._cambiar_velocidad)
        
        spin_vel = ttk.Spinbox(frame_vel_cont, from_=1, to=1023, increment=10, textvariable=self.var_velocidad, width=7, font=("Arial", 10))
        spin_vel.pack(side="left", padx=5)
        
        slider_vel = tk.Scale(frame_vel_cont, from_=1, to=1023, orient="horizontal", variable=self.var_velocidad, showvalue=False)
        slider_vel.pack(side="left", fill="x", expand=True, padx=5)

        # --- COLUMNA DERECHA (GESTIÓN DE ENSEÑANZA Y SECUENCIAS) ---
        marco_der = ttk.Frame(self.master)
        marco_der.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        # 1. Parada de Emergencia
        self.btn_emergencia = tk.Button(
            marco_der, 
            text="🚨 !!! PARADA DE EMERGENCIA !!!", 
            bg="#dc3545", 
            fg="white", 
            font=("Arial", 12, "bold"), 
            command=self._parada_emergencia_accion
        )
        self.btn_emergencia.pack(fill="x", pady=(0, 10))

        # 2. Control de Hardware (Torque y Home)
        marco_hardware = ttk.LabelFrame(marco_der, text=" Controles del Robot ", padding=10)
        marco_hardware.pack(fill="x", pady=5)
        
        btn_grid = tk.Frame(marco_hardware)
        btn_grid.pack(fill="x")
        tk.Button(btn_grid, text="TORQUE ON", bg="#007bff", fg="white", font=("Arial", 8, "bold"), command=self._torque_on_accion).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(btn_grid, text="TORQUE OFF", bg="#6c757d", fg="white", font=("Arial", 8, "bold"), command=self._torque_off_accion).pack(side="left", expand=True, fill="x", padx=2)
        self.btn_home = tk.Button(btn_grid, text="IR A HOME (0°)", bg="#17a2b8", fg="white", font=("Arial", 8, "bold"), command=self._home_accion)
        self.btn_home.pack(side="left", expand=True, fill="x", padx=2)

        # 3. Guardado de Posiciones
        marco_guardado = ttk.LabelFrame(marco_der, text=" Registro de Poses (Teach) ", padding=10)
        marco_guardado.pack(fill="x", pady=5)
        
        name_grid = tk.Frame(marco_guardado)
        name_grid.pack(fill="x", pady=5)
        ttk.Label(name_grid, text="Nombre Pose:", font=("Arial", 9, "bold")).pack(side="left")
        self.var_nombre_pose = tk.StringVar(value="Pose 1")
        tk.Entry(name_grid, textvariable=self.var_nombre_pose, font=("Arial", 10), width=15).pack(side="left", padx=10)
        
        self.btn_guardar_pose = tk.Button(
            marco_guardado, 
            text="📸 CAPTURAR Y GUARDAR POSE ACTUAL", 
            bg="#28a745", 
            fg="white", 
            font=("Arial", 9, "bold"), 
            command=self._guardar_pose_actual
        )
        self.btn_guardar_pose.pack(fill="x", pady=5)

        # 4. Lista de Secuencia y Persistencia YAML
        marco_secuencia = ttk.LabelFrame(marco_der, text=" Secuencia de Poses Registradas ", padding=10)
        marco_secuencia.pack(fill="both", expand=True, pady=5)
        
        frame_scroll = tk.Frame(marco_secuencia)
        frame_scroll.pack(fill="both", expand=True, pady=5)
        self.listbox_poses = tk.Listbox(frame_scroll, font=("Consolas", 9), height=6, selectmode=tk.SINGLE)
        scrollbar = tk.Scrollbar(frame_scroll, orient="vertical", command=self.listbox_poses.yview)
        self.listbox_poses.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.listbox_poses.pack(side="left", fill="both", expand=True)
        
        frame_sec_btns = tk.Frame(marco_secuencia)
        frame_sec_btns.pack(fill="x", pady=5)
        tk.Button(frame_sec_btns, text="Eliminar", bg="#ffc107", font=("Arial", 8), command=self._eliminar_pose).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(frame_sec_btns, text="Limpiar Todo", bg="#dc3545", fg="white", font=("Arial", 8), command=self._limpiar_lista).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(frame_sec_btns, text="💾 Guardar YAML", bg="#17a2b8", fg="white", font=("Arial", 8), command=self._guardar_yaml).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(frame_sec_btns, text="📂 Cargar YAML", bg="#6c757d", fg="white", font=("Arial", 8), command=self._cargar_yaml).pack(side="left", expand=True, fill="x", padx=2)

        # 5. Control de Reproducción (Playback)
        marco_playback = ttk.LabelFrame(marco_der, text=" Reproducción (Playback) ", padding=10)
        marco_playback.pack(fill="x", pady=5)
        
        frame_t_reprod = tk.Frame(marco_playback)
        frame_t_reprod.pack(fill="x", pady=5)
        ttk.Label(frame_t_reprod, text="Tiempo de transición entre poses [s]:", font=("Arial", 9, "bold")).pack(side="left")
        self.var_tiempo = tk.DoubleVar(value=3.0)
        ttk.Spinbox(frame_t_reprod, from_=0.5, to=20.0, increment=0.5, textvariable=self.var_tiempo, width=6, font=("Arial", 9)).pack(side="left", padx=10)
        
        frame_play = tk.Frame(marco_playback)
        frame_play.pack(fill="x", pady=5)
        self.btn_play = tk.Button(frame_play, text="▶ REPRODUCIR SECUENCIA", bg="#28a745", fg="white", font=("Arial", 10, "bold"), command=self._iniciar_reproduccion)
        self.btn_play.pack(side="left", expand=True, fill="x", padx=2)
        self.btn_stop = tk.Button(frame_play, text="⏹ DETENER REPRODUCCIÓN", bg="#dc3545", fg="white", font=("Arial", 10, "bold"), state="disabled", command=self._detener_reproduccion)
        self.btn_stop.pack(side="left", expand=True, fill="x", padx=2)

        # Consola de diagnóstico integrada
        self.txt_consola = tk.Text(marco_der, height=5, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 9))
        self.txt_consola.pack(fill="x", pady=5)

    def _log(self, mensaje, color="#00ff00"):
        self.txt_consola.tag_config(color, foreground=color)
        self.txt_consola.insert(tk.END, mensaje + "\n", color)
        self.txt_consola.see(tk.END)

    def _on_joint_gui_change(self, art):
        if self.reproduciendo:
            return
        try:
            val = self.vars_joints[art].get()
            # Enviar con un dt de 0.2s para fluidez sin bloqueos
            self.node.mover_articulacion(art, val, espera_s=0.2)
        except tk.TclError:
            pass

    def _cambiar_velocidad(self, *args):
        try:
            val = self.var_velocidad.get()
            if 1 <= val <= 1023:
                self.node.set_velocidad(val)
        except tk.TclError:
            pass

    def _parada_emergencia_accion(self):
        self.parada_emergencia = True
        self.reproduciendo = False
        self.node.apagar_torque_solamente()
        self._log("!!! PARADA DE EMERGENCIA ACTIVADA !!! TORQUE APAGADO.", "red")
        self._restaurar_ui()

    def _torque_on_accion(self):
        self.node.habilitar_torque()
        self._log("Torque ON habilitado (Motores bloqueados y listos para comandos).", "white")

    def _torque_off_accion(self):
        self.node.apagar_torque_solamente()
        self._log("Torque OFF (Robot libre para enseñanza manual).", "orange")

    def _home_accion(self):
        self._log("Regresando a HOME (0°) de forma suave...", "white")
        config_home = {name: 0.0 for name in JOINTS}
        threading.Thread(target=self._rutina_movimiento, args=(config_home, 2.5, False)).start()

    def _guardar_pose_actual(self):
        posiciones_finales = {}
        # Leer la posición real desde el tópico de ROS (Crucial para cuando el torque está OFF)
        posiciones_reales = self.node.leer_todas()
        
        for art in JOINTS.keys():
            val_real = posiciones_reales.get(art)
            if val_real is not None:
                posiciones_finales[art] = float(val_real)
            else:
                posiciones_finales[art] = float(self.vars_joints[art].get())
                
        nombre = self.var_nombre_pose.get().strip()
        if not nombre:
            nombre = f"Pose {len(self.lista_poses) + 1}"
            
        nueva_pose = {"nombre": nombre, "q": posiciones_finales}
        self.lista_poses.append(nueva_pose)
        
        self._actualizar_listbox()
        self._log(f"✅ Pose '{nombre}' guardada con éxito.", "green")
        self.var_nombre_pose.set(f"Pose {len(self.lista_poses) + 1}")

    def _actualizar_listbox(self):
        self.listbox_poses.delete(0, tk.END)
        for i, pose in enumerate(self.lista_poses):
            q_str = f"[b:{pose['q']['base']:.1f}° h:{pose['q']['hombro']:.1f}° c:{pose['q']['codo']:.1f}° m:{pose['q']['muneca']:.1f}°]"
            self.listbox_poses.insert(tk.END, f"{i+1}. {pose['nombre']} {q_str}")

    def _eliminar_pose(self):
        seleccion = self.listbox_poses.curselection()
        if seleccion:
            idx = seleccion[0]
            eliminada = self.lista_poses.pop(idx)
            self._actualizar_listbox()
            self._log(f"Pose '{eliminada['nombre']}' eliminada.", "yellow")

    def _limpiar_lista(self):
        if messagebox.askyesno("Confirmar", "¿Eliminar todas las poses registradas?"):
            self.lista_poses.clear()
            self._actualizar_listbox()
            self._log("Secuencia de poses limpiada.", "yellow")

    def _guardar_yaml(self):
        if not self.lista_poses:
            messagebox.showinfo("Vacío", "No hay poses para exportar.")
            return
            
        os.makedirs(RUTA_YAMLS, exist_ok=True)
        
        archivo = filedialog.asksaveasfilename(
            defaultextension=".yaml",
            initialfile="poses_act13.yaml",
            initialdir=RUTA_YAMLS,
            title="Guardar Poses como YAML",
            filetypes=[("Archivos YAML", "*.yaml")]
        )
        
        if archivo:
            try:
                with open(archivo, 'w') as file:
                    yaml.dump(self.lista_poses, file, default_flow_style=False, sort_keys=False)
                self._log(f"💾 Secuencia guardada en: {os.path.basename(archivo)}", "cyan")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")

    def _cargar_yaml(self):
        os.makedirs(RUTA_YAMLS, exist_ok=True)
        
        archivo = filedialog.askopenfilename(
            initialdir=RUTA_YAMLS,
            title="Cargar Poses desde YAML",
            filetypes=[("Archivos YAML", "*.yaml")]
        )
        if archivo:
            try:
                with open(archivo, 'r') as file:
                    datos = yaml.safe_load(file)
                    if isinstance(datos, list):
                        self.lista_poses = datos
                        self._actualizar_listbox()
                        self._log(f"📂 Secuencia cargada de: {os.path.basename(archivo)}", "cyan")
                    else:
                        messagebox.showerror("Formato Inválido", "El archivo YAML no contiene un formato de lista válido.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar: {str(e)}")

    def _iniciar_reproduccion(self):
        if not self.lista_poses:
            messagebox.showwarning("Lista Vacía", "Agregue o cargue poses antes de reproducir.")
            return
            
        try:
            tiempo_transicion = self.var_tiempo.get()
            if tiempo_transicion <= 0: raise ValueError
        except (tk.TclError, ValueError):
            messagebox.showerror("Error", "El tiempo de transición debe ser un número positivo.")
            return

        self.reproduciendo = True
        self.parada_emergencia = False
        
        self.node.habilitar_torque()
        
        self.btn_play.config(state="disabled")
        self.btn_guardar_pose.config(state="disabled")
        self.btn_home.config(state="disabled")
        self.btn_stop.config(state="normal")
        
        self._log(f"▶ INICIANDO PLAYBACK ({len(self.lista_poses)} poses)...", "green")
        
        hilo = threading.Thread(target=self._hilo_reproduccion, args=(tiempo_transicion,))
        hilo.start()

    def _detener_reproduccion(self):
        self.reproduciendo = False
        self._log("⏹ Detención solicitada. El robot frenará de manera controlada al completar la transición actual.", "orange")

    def _hilo_reproduccion(self, tiempo_transicion):
        for i, pose in enumerate(self.lista_poses):
            if not self.reproduciendo or self.parada_emergencia:
                break
                
            self._log(f"  -> Ejecutando [{i+1}/{len(self.lista_poses)}]: {pose['nombre']}")
            
            self.master.after(0, self.listbox_poses.selection_clear, 0, tk.END)
            self.master.after(0, self.listbox_poses.selection_set, i)
            self.master.after(0, self.listbox_poses.see, i)
            
            # Ejecutar movimiento fluido delegando a ROS 2
            self._rutina_movimiento(pose["q"], tiempo_transicion, es_playback=True)
            
        if self.reproduciendo and not self.parada_emergencia:
            self._log("✅ Secuencia de reproducción finalizada con éxito.", "green")
            
        self.reproduciendo = False
        self.master.after(0, self._restaurar_ui)

    def _rutina_movimiento(self, objetivos_q, tiempo_total, es_playback=False):
        self.btn_home.config(state="disabled", bg="gray")
        self.btn_play.config(state="disabled", bg="gray")

        # Delega el cálculo de la curva y fluidez por completo al controlador de ROS 2
        if not self.parada_emergencia:
            if es_playback and not self.reproduciendo:
                pass
            else:
                self.node.mover_simultaneo(objetivos_q, espera_s=tiempo_total)
                
                # Actualiza los Sliders visualmente para mantener sincronizada la GUI
                for art, val in objetivos_q.items():
                    self.master.after(0, self.vars_joints[art].set, val)
                
                # Esperamos estrictamente a que el movimiento físico termine
                time.sleep(tiempo_total)

        self.btn_home.config(state="normal", bg="#17a2b8")
        self.btn_play.config(state="normal", bg="#28a745")

    def _restaurar_ui(self):
        self.btn_play.config(state="normal")
        self.btn_guardar_pose.config(state="normal")
        self.btn_home.config(state="normal")
        self.btn_stop.config(state="disabled")

def main(args=None):
    rclpy.init(args=args)
    node = JointSelector()
    
    # Hilo fundamental para escuchar las posiciones en segundo plano al usar "Teach" manual
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()
    time.sleep(1)
    
    node.habilitar_torque()
    node.set_velocidad(150)
    
    root = tk.Tk()
    app = InterfazEnsenanzaCompleta(root, node)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        node.apagar()
        rclpy.shutdown()

if __name__ == '__main__':
    main()