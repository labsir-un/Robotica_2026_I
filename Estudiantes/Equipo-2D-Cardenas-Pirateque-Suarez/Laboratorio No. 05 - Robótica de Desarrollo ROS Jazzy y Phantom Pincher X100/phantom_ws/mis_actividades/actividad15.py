#!/usr/bin/env python3
"""
Actividad 15 - Coreografía Sincronizada (GUI)
Robot: Phantom X Pincher X100
Motor Híbrido Final: Data-Driven + Monitor en Vivo + Modo Físico/RViz
"""

import os
import csv
import time
import math
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import rclpy

from PIL import Image, ImageTk
import pygame

# Import local de tu arquitectura
from joint_selector import JointSelector, JOINTS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

IMG_CANCION_1 = os.path.join(BASE_DIR, "dubidubidu.png")
IMG_CANCION_2 = os.path.join(BASE_DIR, "pedro.png")
AUDIO_CANCION_1 = os.path.join(BASE_DIR, "dubidubidu.mp3")
AUDIO_CANCION_2 = os.path.join(BASE_DIR, "pedro.mp3")

ARCHIVO_CSV_PEDRO = os.path.join(BASE_DIR, "datos_pedro.csv")
ARCHIVO_CSV_DUBI = os.path.join(BASE_DIR, "datos_dubidubidu.csv")

class AsistenteCoreografia:
    def __init__(self, master, node):
        self.master = master
        self.node = node
        self.master.title("Actividad 15 - Suite de Coreografía Data-Driven")
        self.master.geometry("750x980") # Ventana más alta para el monitor
        
        self.rutina_activa = False
        self.parada_emergencia = False
        self.is_paused = False
        
        # Banderas de sliders
        self.is_dragging_audio = False
        self.flag_seek_audio = False
        self.is_dragging_robot = False
        self.flag_seek_robot = False
        
        # Memoria de las canciones (CSVs)
        self.datos_pedro = []
        self.datos_dubi = []
        self._cargar_csv(ARCHIVO_CSV_PEDRO, self.datos_pedro)
        self._cargar_csv(ARCHIVO_CSV_DUBI, self.datos_dubi)
        
        pygame.mixer.init()
        self.node.habilitar_torque()
        self._crear_widgets()

    def _cargar_csv(self, ruta, destino):
        if os.path.exists(ruta):
            with open(ruta, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    destino.append({
                        'Energia': float(row['Energia']),
                        'Frecuencia': float(row['Frecuencia']),
                        'Es_Beat': int(row['Es_Beat'])
                    })
            print(f"✅ CSV Cargado en memoria: {os.path.basename(ruta)} ({len(destino)} frames a 10Hz).")
        else:
            print(f"⚠️ Advertencia: No se encontró {os.path.basename(ruta)}.")

    def _crear_widgets(self):
        marco_header = tk.Frame(self.master, bg="#212529", pady=15)
        marco_header.pack(fill="x")
        tk.Label(marco_header, text="CENTRO DE CONTROL COREOGRÁFICO (ACT 15)", fg="white", bg="#212529", font=("Arial", 16, "bold")).pack()

        # --- PANEL DE LÍNEA DE TIEMPO ---
        marco_tiempo = ttk.LabelFrame(self.master, text="Línea de Tiempo (Buscar / Seek Independiente)", padding=10)
        marco_tiempo.pack(padx=20, pady=5, fill="x")

        tk.Label(marco_tiempo, text="🎵 Música [s]:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="e", padx=5)
        self.var_slider_audio = tk.DoubleVar(value=0.0)
        self.scale_audio = ttk.Scale(marco_tiempo, from_=0.0, to=230.0, orient="horizontal", variable=self.var_slider_audio, length=400)
        self.scale_audio.grid(row=0, column=1, padx=5, pady=5)
        self.lbl_audio_time = tk.Label(marco_tiempo, text="0.0 s", width=6, font=("Consolas", 10, "bold"), fg="#198754")
        self.lbl_audio_time.grid(row=0, column=2, padx=5)

        tk.Label(marco_tiempo, text="🤖 Robot [s]:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky="e", padx=5)
        self.var_slider_robot = tk.DoubleVar(value=0.0)
        self.scale_robot = ttk.Scale(marco_tiempo, from_=0.0, to=230.0, orient="horizontal", variable=self.var_slider_robot, length=400)
        self.scale_robot.grid(row=1, column=1, padx=5, pady=5)
        self.lbl_robot_time = tk.Label(marco_tiempo, text="0.0 s", width=6, font=("Consolas", 10, "bold"), fg="#0d6efd")
        self.lbl_robot_time.grid(row=1, column=2, padx=5)

        self.scale_audio.bind("<ButtonPress-1>", lambda e: setattr(self, 'is_dragging_audio', True))
        self.scale_audio.bind("<ButtonRelease-1>", self._on_release_audio)
        self.scale_robot.bind("<ButtonPress-1>", lambda e: setattr(self, 'is_dragging_robot', True))
        self.scale_robot.bind("<ButtonRelease-1>", self._on_release_robot)

        # --- PANEL DE AJUSTE MANUAL Y ENTORNO ---
        marco_tuning = ttk.LabelFrame(self.master, text="Entorno, Sincronía y Hardware", padding=10)
        marco_tuning.pack(padx=20, pady=5, fill="x")

        # Modo RViz vs Físico
        self.var_modo = tk.StringVar(value="rviz")
        marco_modos = tk.Frame(marco_tuning)
        marco_modos.grid(row=0, column=0, columnspan=3, pady=5)
        tk.Label(marco_modos, text="Entorno de Ejecución:", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        tk.Radiobutton(marco_modos, text="Simulación (RViz)", variable=self.var_modo, value="rviz", font=("Arial", 9)).pack(side="left", padx=10)
        tk.Radiobutton(marco_modos, text="Robot Físico (Dynamixel)", variable=self.var_modo, value="fisico", font=("Arial", 9)).pack(side="left", padx=10)

        tk.Label(marco_tuning, text="Desfase Fino [s]:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.var_offset = tk.DoubleVar(value=0.0)
        ttk.Scale(marco_tuning, from_=-2.0, to=2.0, orient="horizontal", variable=self.var_offset, length=300).grid(row=1, column=1, padx=5, pady=5)
        ttk.Spinbox(marco_tuning, from_=-2.0, to=2.0, increment=0.05, textvariable=self.var_offset, width=8, font=("Consolas", 10, "bold")).grid(row=1, column=2, padx=5, pady=5)

        tk.Label(marco_tuning, text="Vel. Física (0-1023):", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.var_velocidad = tk.IntVar(value=378)
        ttk.Scale(marco_tuning, from_=10, to=1023, orient="horizontal", variable=self.var_velocidad, length=300).grid(row=2, column=1, padx=5, pady=5)
        ttk.Spinbox(marco_tuning, from_=0, to=1023, increment=10, textvariable=self.var_velocidad, width=8, font=("Consolas", 10, "bold")).grid(row=2, column=2, padx=5, pady=5)

        # --- BOTONES DE SEGURIDAD Y CONTROL ---
        frame_seguridad = tk.Frame(self.master)
        frame_seguridad.pack(padx=20, pady=5, fill="x")
        tk.Button(frame_seguridad, text="🚨 EMERGENCIA", bg="#dc3545", fg="white", font=("Arial", 11, "bold"), command=self._emergencia).pack(side="left", expand=True, fill="x", padx=2)
        
        self.btn_pausa = tk.Button(frame_seguridad, text="⏸️ PAUSAR", bg="#ffc107", fg="black", font=("Arial", 11, "bold"), command=self._toggle_pausa, state="disabled")
        self.btn_pausa.pack(side="left", expand=True, fill="x", padx=2)
        
        tk.Button(frame_seguridad, text="🛑 DETENER", bg="#fd7e14", fg="white", font=("Arial", 11, "bold"), command=self._detener).pack(side="left", expand=True, fill="x", padx=2)
        
        # AGREGADO: Botón IR A HOME
        tk.Button(frame_seguridad, text="🏠 IR A HOME", bg="#17a2b8", fg="white", font=("Arial", 11, "bold"), command=self._ir_home).pack(side="left", expand=True, fill="x", padx=2)

        # --- CONTENEDOR DE CANCIONES ---
        marco_canciones = tk.Frame(self.master)
        marco_canciones.pack(padx=20, pady=5, fill="x")

        frame_c1 = tk.Frame(marco_canciones)
        frame_c1.pack(side="left", expand=True, fill="both")
        try:
            img1 = Image.open(IMG_CANCION_1).resize((260, 160))
            self.foto1 = ImageTk.PhotoImage(img1)
            tk.Label(frame_c1, image=self.foto1, bd=3, relief="groove").pack(pady=5)
        except Exception:
            tk.Label(frame_c1, text=f"[Falta {IMG_CANCION_1}]", width=30, height=10, bg="grey").pack(pady=5)
        self.btn_c1 = tk.Button(frame_c1, text="▶️ 1. Dubidubidu", bg="#0d6efd", fg="white", font=("Arial", 12, "bold"), pady=5, command=lambda: self._iniciar_baile(1))
        self.btn_c1.pack(fill="x", padx=20)

        frame_c2 = tk.Frame(marco_canciones)
        frame_c2.pack(side="right", expand=True, fill="both")
        try:
            img2 = Image.open(IMG_CANCION_2).resize((260, 160))
            self.foto2 = ImageTk.PhotoImage(img2)
            tk.Label(frame_c2, image=self.foto2, bd=3, relief="groove").pack(pady=5)
        except Exception:
            tk.Label(frame_c2, text=f"[Falta {IMG_CANCION_2}]", width=30, height=10, bg="grey").pack(pady=5)
        self.btn_c2 = tk.Button(frame_c2, text="▶️ 2. Pedro (Mapache)", bg="#198754", fg="white", font=("Arial", 12, "bold"), pady=5, command=lambda: self._iniciar_baile(2))
        self.btn_c2.pack(fill="x", padx=20)

        # --- MONITOR DE ARTICULACIONES (NUEVO) ---
        self.marco_monitor = ttk.LabelFrame(self.master, text="Monitor Cinemático (En Vivo)", padding=5)
        self.marco_monitor.pack(padx=20, pady=5, fill="x")
        
        self.lbls_set = {}
        self.lbls_read = {}
        
        for j in JOINTS:
            frame_j = tk.Frame(self.marco_monitor)
            frame_j.pack(side="left", expand=True, fill="both")
            tk.Label(frame_j, text=j.upper(), font=("Arial", 9, "bold")).pack()
            self.lbls_set[j] = tk.Label(frame_j, text="Set:   0.0°", fg="blue", font=("Consolas", 10, "bold"))
            self.lbls_set[j].pack()
            self.lbls_read[j] = tk.Label(frame_j, text="Read:  0.0°", fg="#198754", font=("Consolas", 10, "bold"))
            self.lbls_read[j].pack()

        # --- CONSOLA ---
        self.txt_consola = tk.Text(self.master, height=6, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.txt_consola.pack(padx=20, pady=10, fill="both", expand=True)

    def _on_release_audio(self, event):
        self.is_dragging_audio = False
        self.flag_seek_audio = True

    def _on_release_robot(self, event):
        self.is_dragging_robot = False
        self.flag_seek_robot = True

    def _log_safe(self, msg, color="#00ff00"):
        def _insertar():
            self.txt_consola.tag_config(color, foreground=color)
            self.txt_consola.insert(tk.END, msg + "\n", color)
            self.txt_consola.see(tk.END)
        self.master.after(0, _insertar)

    def _actualizar_monitor(self, b, h, c, m, p):
        """ Actualiza la interfaz con los valores deseados (Set) y los valores físicos reales (Read) """
        setpoints = {'base': b, 'hombro': h, 'codo': c, 'muneca': m, 'pinza': p}
        leidas = {}
        
        # Intentamos obtener las lecturas físicas del nodo
        if hasattr(self.node, 'angulos_actuales') and isinstance(self.node.angulos_actuales, dict):
            leidas = self.node.angulos_actuales
        elif hasattr(self.node, 'posiciones_actuales') and isinstance(self.node.posiciones_actuales, dict):
            leidas = self.node.posiciones_actuales
        elif hasattr(self.node, 'leer_articulaciones') and callable(self.node.leer_articulaciones):
            try: leidas = self.node.leer_articulaciones()
            except: pass
            
        def _update_ui():
            for j in JOINTS:
                val_set = setpoints.get(j, 0.0)
                # Si estamos en RViz o no hay hardware para leer, igualamos la lectura al Setpoint
                val_read = leidas.get(j, val_set) if self.var_modo.get() == "fisico" else val_set
                
                self.lbls_set[j].config(text=f"Set: {val_set:6.1f}°")
                self.lbls_read[j].config(text=f"Read:{val_read:6.1f}°")
                
        self.master.after(0, _update_ui)

    def _toggle_pausa(self):
        if not self.rutina_activa: return
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            pygame.mixer.music.pause()
            self.btn_pausa.config(text="▶️ REANUDAR", bg="#28a745", fg="white")
            self._log_safe("⏸️ COREOGRAFÍA PAUSADA.", "yellow")
        else:
            pygame.mixer.music.unpause()
            self.btn_pausa.config(text="⏸️ PAUSAR", bg="#ffc107", fg="black")
            self._log_safe("▶️ COREOGRAFÍA REANUDADA.", "green")

    def _emergencia(self):
        self.parada_emergencia = True
        self.is_paused = False
        pygame.mixer.music.stop()
        self.node.apagar_torque_solamente()
        self._log_safe("\n🚨 EMERGENCIA DETENIDA.", "red")
        self._restaurar_interfaz()

    def _detener(self):
        self.parada_emergencia = True
        self.is_paused = False
        pygame.mixer.music.stop()
        self._log_safe("\n🛑 Coreografía abortada.", "orange")
        self.node.mover_simultaneo({name: 0.0 for name in JOINTS}, espera_s=1.5)
        self._restaurar_interfaz()

    def _ir_home(self):
        if self.rutina_activa and not self.parada_emergencia:
            self._log_safe("⚠️ Detén la coreografía antes de forzar el retorno a Home.", "orange")
            return
        self._log_safe("\n🏠 Regresando a HOME (0°)...", "cyan")
        # Enviar el comando en un hilo para mantener la GUI responsiva
        threading.Thread(target=lambda: self.node.mover_simultaneo({name: 0.0 for name in JOINTS}, espera_s=2.0), daemon=True).start()

    def _restaurar_interfaz(self):
        self.rutina_activa = False
        self.btn_c1.config(state="normal")
        self.btn_c2.config(state="normal")
        self.btn_pausa.config(state="disabled", text="⏸️ PAUSAR", bg="#ffc107", fg="black")

    def _iniciar_baile(self, num_cancion):
        if self.rutina_activa: return
        archivo_audio = AUDIO_CANCION_1 if num_cancion == 1 else AUDIO_CANCION_2
        if not os.path.exists(archivo_audio):
            messagebox.showerror("Error", f"No se encontró el audio:\n{archivo_audio}")
            return
            
        self.rutina_activa = True
        self.parada_emergencia = False
        self.is_paused = False
        self.btn_c1.config(state="disabled")
        self.btn_c2.config(state="disabled")
        self.btn_pausa.config(state="normal")
        
        # --- LÓGICA DE VELOCIDAD POR DEFECTO ---
        modo_actual = self.var_modo.get()
        if modo_actual == "fisico":
            self.var_velocidad.set(150)
        else: # modo rviz
            if num_cancion == 1: # Dubidubidu
                self.var_velocidad.set(378)
            else: # Pedro
                self.var_velocidad.set(360)
                
        self.node.habilitar_torque()
        
        # Enviar modo de ejecución al nodo si este tiene la propiedad
        if hasattr(self.node, 'modo'):
            self.node.modo = self.var_modo.get()
        
        max_time = 227.0 if num_cancion == 1 else 130.0
        self.scale_audio.config(to=max_time)
        self.scale_robot.config(to=max_time)
        
        self.txt_consola.delete('1.0', tk.END)
        threading.Thread(target=self._hilo_coreografia, args=(num_cancion, archivo_audio), daemon=True).start()

    # ================= 1. LETRAS EXACTAS =================
    def _obtener_letras_pedro(self):
        return [
            (0.0,  "🎵 (Intro) Preparando...", "gray"),
            (16.0, "🎵 Passeggio tutta sola per le strade", "white"),
            (19.5, "🎵 Guardando attentamente i monumenti", "white"),
            (23.0, "🎵 La classica straniera con un'aria strana", "white"),
            (27.0, "🎵 Che gira stanca tutta la città", "white"),
            (31.0, "🎵 A un certo punto della passeggiata...", "white"),
            (34.0, "🎵 Mi chiama da una parte un ragazzino...", "white"),
            (37.0, "🎵 Sembrava a prima vista tanto per benino...", "white"),
            (39.5, "🎵 Si offre a far da guida per la città...", "white"),
            (41.0, "🎵 Pedro, pedro,", "yellow"),
            (41.8, "🎵 Pedro, pedro,", "yellow"),
            (42.6, "🎵 Pè!", "yellow"),
            (43.0, "🦝 ¡DROP MAPACHE! (Posiciones Exactas)", "red"),
            (43.5, "🎵 Praticamente il meglio di Santa Fe", "cyan"),
            (62.5, "🎵 Altro che ragazzino che per benino", "white"),
            (66.0, "🎵 Sapeva molte cose più di me", "white"),
            (69.5, "🎵 Mi ha portato tante volte a veder le stelle", "white"),
            (73.0, "🎵 Ma non ho visto niente di Santa Fe", "white"),
            (76.5, "🎵 Pedro, pedro,", "yellow"),
            (77.3, "🎵 Pedro, pedro,", "yellow"),
            (78.1, "🎵 Pè!", "yellow"),
            (79.0, "🎵 Praticamente il meglio di Santa Fe", "cyan"),
            (84.0, "🤖 (Acurrucándose poco a poco para el salto...)", "gray"),
            (95.0, "🦝 ¡DROP MAPACHE 2!", "red"),
            (107.0,"🎵 Pedro, pedro... (Tercer Coro)", "yellow"),
            (113.0,"🦝 ¡DROP MAPACHE FINAL!", "red"),
            (120.8,"⏹️ (Fade-Out paulatino a Home activado...)", "gray")
        ]

    def _obtener_letras_dubidubidu(self):
        return [
            (0.0,  "🎵 (Intro)", "gray"),
            (19.0, "🎵 Si tú quieres bailar, jugar, pintar, cantar", "white"),
            (23.0, "🎵 Tú puedes venir a mi casa", "white"),
            (25.0, "🎵 La idea es compartir, te vas a divertir", "white"),
            (28.0, "🎵 Si quieres venir a mi casa", "white"),
            (30.0, "🎵 Quiero invitar a jugar a mi casa", "white"),
            (34.0, "🎵 A todas mis amigas y amigos", "white"),
            (37.0, "🎵 Quiero saltar y bailar", "white"),
            (40.0, "🎵 Y lo que tengo compartir contigo", "white"),
            
            (44.0, "🐱 ¡Chipi chipi chapa chapa dubi dubi daba daba!", "yellow"),
            (47.0, "🐱 Mágico mi dubi dubi boom boom boom boom boom!", "yellow"),
            (51.0, "🐱 ¡Chipi chipi chapa chapa dubi dubi daba daba!", "yellow"),
            (54.0, "🐱 Mágico mi dubi dubi boooooooooooooooom!", "cyan"),

            (58.0, "🎵 Si tú quieres cantar yo te voy a enseñar", "white"),
            (62.0, "🎵 Si quieres venir a mi casa", "white"),
            (64.0, "🎵 Le digo a mi mamá que diga a tu mamá", "white"),
            (68.0, "🎵 Que deje venirte a mi casa", "white"),
            (70.0, "🎵 Tengo un muñeco regalón que si le das un biberón", "white"),
            (74.0, "🎵 No llora (no llora)", "white"),
            (76.0, "🎵 Y en mi libreta una canción", "white"),
            (80.0, "🎵 Que todos vamos a cantar ahora!", "cyan"),

            (84.0, "🐱 ¡Chipi chipi chapa chapa dubi dubi daba daba!", "yellow"),
            (87.0, "🐱 Mágico mi dubi dubi boom boom boom boom boom!", "yellow"),
            (91.0, "🐱 ¡Chipi chipi chapa chapa dubi dubi daba daba!", "yellow"),
            (94.0, "🐱 Mágico mi dubi dubi boooooom!", "cyan"),
            (98.0, "🐱 ¡Chipi chipi chapa chapa dubi dubi daba daba!", "yellow"),
            (102.0, "🐱 Mágico mi dubi dubi boom boom boom boom boom!", "yellow"),
            (105.0, "🐱 ¡Chipi chipi chapa chapa dubi dubi daba daba!", "yellow"),
            (109.0, "🐱 Mágico mi dubi dubi boooooooooooooooom!", "cyan"),
            
            (126.0, "🎵 Si tú quieres bailar, jugar, pintar, cantar", "white"),
            (130.0, "🎵 Tú puedes venir a mi casa", "white"),
            (132.0, "🎵 La idea es compartir, te vas a divertir", "white"),
            (136.0, "🎵 Si quieres venir a mi casa", "white"),
            (138.0, "🎵 Quiero invitar a jugar a mi casa", "white"),
            (142.0, "🎵 A todas mis amigas y amigos", "white"),
            (145.0, "🎵 Quiero saltar y bailar", "white"),
            (148.0, "🎵 Y lo que tengo compartir contigo", "white"),

            (151.0, "🎵 Si tú quieres cantar yo te voy a enseñar", "white"),
            (155.0, "🎵 Si puedes venir a mi casa", "white"),
            (157.0, "🎵 Le digo a mi mamá que diga a tu mamá", "white"),
            (161.0, "🎵 Que deje de venirte a mi casa", "white"),
            (163.0, "🎵 Tengo un muñeco regalón que si le das un biberón", "white"),
            (167.0, "🎵 No llora (no llora)", "white"),
            (169.0, "🎵 Y en mi libreta una canción", "white"),
            (173.0, "🎵 Que todos vamos a cantar ahora!", "cyan"),

            (177.0, "🐱 ¡Chipi chipi chapa chapa dubi dubi daba daba!", "yellow"),
            (180.0, "🐱 Mágico mi dubi dubi boom boom boom boom boom!", "yellow"),
            (184.0, "🐱 ¡Chipi chipi chapa chapa dubi dubi daba daba!", "yellow"),
            (188.0, "🐱 Mágico mi dubi dubi boooooom!", "cyan"),
            (191.0, "🐱 ¡Chipi chipi chapa chapa dubi dubi daba daba!", "yellow"),
            (195.0, "🐱 Mágico mi dubi dubi boom boom boom boom boom!", "yellow"),
            (199.0, "🐱 ¡Chipi chipi chapa chapa dubi dubi daba daba!", "yellow"),
            (203.0, "🐱 Mágico mi dubi dubi boooooooooooooooom!", "cyan"),
            (206.0, "🐱 ¡Chipi chipi chapa chapa dubi dubi daba daba!", "yellow"),
            (210.0, "🐱 Mágico mi dubi dubi boom boom boom boom boom!", "yellow"),
            (214.0, "🐱 ¡Chipi chipi chapa chapa dubi dubi daba daba!", "yellow"),
            (218.0, "🐱 Mágico mi dubi dubi boooooooooooooooom!", "cyan"),
            (223.0, "⏹️ (Fade-Out paulatino a Home activado...)", "gray")
        ]

    # ================= 2. GENERADOR DE POSES (CON INTERPOLACIÓN A HOME) =================
    def _calcular_pose(self, num_cancion, t):
        # 🦝 CANCIÓN 2: PEDRO
        if num_cancion == 2 and self.datos_pedro:
            idx = int(t * 10.0)
            if idx < 0: idx = 0
            if idx >= len(self.datos_pedro): idx = len(self.datos_pedro) - 1
            
            row = self.datos_pedro[idx]
            energia = row['Energia']       
            freq = row['Frecuencia']       
            beat = row['Es_Beat']          
            
            onda_base = math.sin(2 * math.pi * 1.15 * t)
            onda_rapida = math.sin(2 * math.pi * 2.3 * t)
            
            es_coro = (41.0 <= t < 43.0) or (76.5 <= t < 84.0) or (107.0 <= t < 113.0)
            es_drop = (43.0 <= t < 62.5) or (95.0 <= t < 107.0) or (113.0 <= t <= 121.0)
            es_acurrucado = (84.0 <= t < 95.0)
            
            if es_drop:
                b = 45.0 * onda_base
                h = -15.0 + (15.0 * onda_base)
                c = -6.0 + (6.0 * onda_base)
                m = -45.0 + (45.0 * onda_rapida)
                if beat == 1:
                    p = 30.0 
                else:
                    p = 15.0 + (15.0 * onda_rapida)
                    
            elif es_acurrucado:
                progreso = (t - 84.0) / 11.0
                progreso = max(0.0, min(1.0, progreso))
                
                b = 25.0 * onda_base 
                h = 0.0 + (96.0 * progreso)
                c = 0.0 + (-138.0 * progreso)
                m = 0.0 + (50.0 * progreso)
                p = 0.0 + (-18.0 * progreso)
                
            elif es_coro:
                b = 30.0 * onda_base
                h = -20.0 + (20.0 * onda_rapida)
                c = 20.0 - (20.0 * onda_rapida)
                
                if beat == 1:
                    m = 45.0
                    p = 30.0
                else:
                    m = -45.0 + (energia * 45.0)
                    p = -30.0 + (energia * 30.0)
                
            else:
                b = onda_base * (10.0 + energia * 50.0)
                h = -60.0 + (freq * 120.0)
                c = 60.0 - (freq * 120.0)
                
                if beat == 1:
                    m = 60.0 * onda_rapida
                    p = 30.0
                else:
                    m = onda_rapida * (energia * 60.0)
                    p = -30.0 + (energia * 60.0)

            # Fade-Out matemático al final de la canción (Pedro)
            if t >= 120.8:
                progreso_fade = (t - 120.8) / 4.0
                factor_fade = max(0.0, 1.0 - progreso_fade)
                b *= factor_fade
                h *= factor_fade
                c *= factor_fade
                m *= factor_fade
                p *= factor_fade

        # 🐱 CANCIÓN 1: DUBIDUBIDU
        elif num_cancion == 1 and self.datos_dubi:
            idx = int(t * 10.0)
            if idx < 0: idx = 0
            if idx >= len(self.datos_dubi): idx = len(self.datos_dubi) - 1
            
            row = self.datos_dubi[idx]
            energia = row['Energia']       
            freq = row['Frecuencia']       
            beat = row['Es_Beat']          
            
            onda_base = math.sin(2 * math.pi * 1.3 * t)  
            onda_rapida = math.sin(2 * math.pi * 2.6 * t)
            
            es_chipi = (44.0 <= t < 58.0) or (84.0 <= t < 115.0) or (177.0 <= t < 225.0)
            
            if es_chipi:
                b = 40.0 * onda_base * (0.5 + energia)
                h = -30.0 + (freq * 120.0)
                c = 30.0 - (freq * 120.0)
                m = -30.0 + (60.0 * onda_rapida)
                
                if beat == 1:
                    p = 30.0 
                else:
                    p = 15.0 * onda_rapida
            else:
                b = onda_base * (15.0 + energia * 30.0)
                h = -40.0 + (freq * 80.0)
                c = 40.0 - (freq * 80.0)
                
                if beat == 1:
                    m = 30.0
                    p = 20.0
                else:
                    m = onda_base * 20.0
                    p = -10.0 + (energia * 30.0)
            
            # Fade-Out matemático al final de la canción (Dubidubidu)
            if t >= 223.0:
                progreso_fade = (t - 223.0) / 4.0
                factor_fade = max(0.0, 1.0 - progreso_fade)
                b *= factor_fade
                h *= factor_fade
                c *= factor_fade
                m *= factor_fade
                p *= factor_fade

        # FALLBACK MATEMÁTICO
        else:
            onda_base = math.sin(2 * math.pi * 1.15 * t)
            onda_suave = math.sin(2 * math.pi * (1.15 * 0.5) * t)
            onda_rapida = math.sin(2 * math.pi * 2.3 * t)
            
            if t < 19.0:
                b = 60.0 * onda_suave
                h, c, m, p = 10.0, -10.0, 0.0, 0.0
            elif (19.0 <= t < 44.0) or (58.0 <= t < 84.0):
                b = 60.0 * onda_suave
                h = 60.0 * onda_base
                c = -60.0 * onda_base
                m = 60.0 * onda_base
                p = 0.0
            else: 
                b = 60.0 * onda_base
                h, c, m = -60.0 * onda_suave, 60.0 * onda_suave, 60.0 * onda_rapida
                p = 30.0 if onda_rapida > 0 else -30.0

        # === CLAMPS DE SEGURIDAD ABSOLUTOS ===
        b = max(-90.0, min(90.0, b))
        h = max(-100.0, min(100.0, h))   
        c = max(-150.0, min(150.0, c))   
        m = max(-90.0, min(90.0, m)) 
        p = max(-30.0, min(30.0, p))     
                
        return b, h, c, m, p

    # ================= 3. BUCLE DE CONTROL AVANZADO =================
    def _hilo_coreografia(self, num, audio):
        self.node.mover_simultaneo({"base":0.0, "hombro":20.0, "codo":-20.0, "muneca":0.0, "pinza":0.0}, espera_s=2.0)
        time.sleep(2.0)
        
        letras = self._obtener_letras_dubidubidu() if num == 1 else self._obtener_letras_pedro()
        idx_letra = 0
        dt = 0.1 
        
        pygame.mixer.music.load(audio)
        pygame.mixer.music.play()
        
        t_audio = 0.0
        t_robot = 0.0
        t_ultimo_reloj = time.time()
        
        modo_actual = self.var_modo.get()
        self._log_safe(f"▶️ MODO ACTIVO: DATA-DRIVEN [{modo_actual.upper()}]", "cyan")
        
        while (pygame.mixer.music.get_busy() or self.is_paused) and not self.parada_emergencia:
            t_ahora = time.time()
            dt_reloj = t_ahora - t_ultimo_reloj
            t_ultimo_reloj = t_ahora
            
            # ⚙️ CONTROL DINÁMICO DE VELOCIDAD DE RETORNO (HARDWARE)
            if num == 2 and t_audio >= 120.8:
                if self.var_velocidad.get() > 180:
                    self.var_velocidad.set(180)
            elif num == 1 and t_audio >= 223.0:
                if self.var_velocidad.get() > 180:
                    self.var_velocidad.set(180)

            ajuste_offset = self.var_offset.get() 
            vel_dynamixel = self.var_velocidad.get()

            # --- MANEJO DE SALTOS ---
            if self.flag_seek_audio:
                t_audio = self.var_slider_audio.get()
                pygame.mixer.music.play(start=t_audio)
                if self.is_paused:
                    pygame.mixer.music.pause()
                
                idx_letra = 0
                while idx_letra < len(letras) and letras[idx_letra][0] < t_audio:
                    idx_letra += 1
                self.flag_seek_audio = False

            if self.flag_seek_robot:
                t_robot = self.var_slider_robot.get()
                self.flag_seek_robot = False
                if self.is_paused:
                    b, h, c, m, p = self._calcular_pose(num, t_robot + ajuste_offset)
                    self.node.mover_simultaneo({"base":b, "hombro":h, "codo":c, "muneca":m, "pinza":p}, espera_s=0.5)
                    self._actualizar_monitor(b, h, c, m, p)

            if not self.is_paused:
                t_audio += dt_reloj
                t_robot += dt_reloj

            # --- ACTUALIZACIÓN VISUAL ---
            if not self.is_dragging_audio:
                self.var_slider_audio.set(t_audio)
                self.master.after(0, self.lbl_audio_time.config, {'text': f"{t_audio:.1f} s"})
            else:
                self.master.after(0, self.lbl_audio_time.config, {'text': f"{self.var_slider_audio.get():.1f} s"})

            if not self.is_dragging_robot:
                self.var_slider_robot.set(t_robot)
                self.master.after(0, self.lbl_robot_time.config, {'text': f"{t_robot:.1f} s"})
            else:
                self.master.after(0, self.lbl_robot_time.config, {'text': f"{self.var_slider_robot.get():.1f} s"})

            if self.is_paused:
                time.sleep(0.05) 
                continue

            # --- EJECUCIÓN NORMAL ---
            if idx_letra < len(letras) and t_audio >= letras[idx_letra][0]:
                self._log_safe(f"[{letras[idx_letra][0]:05.1f}s] {letras[idx_letra][1]}", letras[idx_letra][2])
                idx_letra += 1
                
            b, h, c, m, p = self._calcular_pose(num, t_robot + ajuste_offset)
            factor_tiempo = 1023.0 / max(1, vel_dynamixel)
            duracion_efectiva = dt * factor_tiempo
            
            # Actualiza el monitor UI (Set vs Read)
            self._actualizar_monitor(b, h, c, m, p)
            
            self.node.mover_simultaneo({"base":b, "hombro":h, "codo":c, "muneca":m, "pinza":p}, espera_s=duracion_efectiva)
            
            # Mantenimiento exacto a 10Hz
            t_siguiente_tick = t_ahora + dt
            espera = t_siguiente_tick - time.time()
            if espera > 0:
                time.sleep(espera)

        if not self.parada_emergencia:
            self.node.mover_simultaneo({name: 0.0 for name in JOINTS}, espera_s=1.5)
            
        self.master.after(0, self._restaurar_interfaz)

def main(args=None):
    rclpy.init(args=args)
    node = JointSelector()
    
    threading.Thread(target=rclpy.spin, args=(node,), daemon=True).start()
    time.sleep(1.0)
    
    root = tk.Tk()
    app = AsistenteCoreografia(root, node)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        node.apagar()
        rclpy.shutdown()

if __name__ == "__main__":
    main()