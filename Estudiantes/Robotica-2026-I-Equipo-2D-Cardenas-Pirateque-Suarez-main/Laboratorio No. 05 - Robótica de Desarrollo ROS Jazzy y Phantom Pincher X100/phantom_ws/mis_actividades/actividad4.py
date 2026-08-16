import threading
import queue
import time
import tkinter as tk
from tkinter import ttk, simpledialog
import rclpy

# Cambio crucial 1: Importar del archivo local directamente
from joint_selector import (
    JointSelector, JOINTS, LIMITS_DEG, DEMO_POSICIONES,
)

NOMBRES_BONITOS = {
    "base": "Base", "hombro": "Hombro", "codo": "Codo",
    "muneca": "Mu\u00f1eca", "pinza": "Pinza",
}

class JointControlApp:
    def __init__(self, root: tk.Tk, node: JointSelector):
        self.root = root
        self.node = node
        self.log_q: "queue.Queue[str]" = queue.Queue()
        self.busy = False

        self.sliders = {}
        self.entries = {}
        self.medido_labels = {}
        self.velocidad_actual = getattr(node, "speed", 80)
        self.monitor_var = tk.BooleanVar(value=False)

        root.title("Control Phantom X Pincher X100 \u2013 Actividad 4")
        root.geometry("620x860")
        root.resizable(True, True)

        menubar = tk.Menu(root)
        opciones_menu = tk.Menu(menubar, tearoff=0)
        opciones_menu.add_command(
            label="\u25b6 Demo (3 posiciones \u00d7 articulaci\u00f3n)...",
            command=self.demo,
        )
        menubar.add_cascade(label="Opciones", menu=opciones_menu)
        root.config(menu=menubar)

        main = ttk.Frame(root, padding=14)
        main.pack(fill="both", expand=True)

        estop_btn = tk.Button(
            main, text="!!! PARADA DE EMERGENCIA !!!",
            bg="#b71c1c", fg="white", font=("Sans", 14, "bold"),
            activebackground="#ff5252", command=self.parada_emergencia
        )
        estop_btn.pack(fill="x", pady=(0, 15), ipady=8)

        ttk.Label(main, text="Control individual de articulaciones", font=("Sans", 13, "bold")).pack(pady=(0, 10))

        cabecera = ttk.Frame(main)
        cabecera.pack(fill="x")
        ttk.Label(cabecera, text="", width=9).pack(side="left")
        ttk.Label(cabecera, text="Slider (\u00b0)").pack(side="left", padx=(0, 0))
        ttk.Label(cabecera, text="Medido").pack(side="right", padx=(0, 4))

        monitor_frame = ttk.Frame(main)
        monitor_frame.pack(fill="x", pady=(2, 8))

        monitor_chk = ttk.Checkbutton(
            monitor_frame, text="\U0001F4CD Monitor de posici\u00f3n en vivo (con torque OFF)",
            variable=self.monitor_var, command=self._toggle_monitor,
        )
        monitor_chk.pack(side="left")

        log_pos_btn = tk.Button(
            monitor_frame, text="\U0001F4DD Anotar posiciones",
            command=self._anotar_posiciones_log, font=("Sans", 9)
        )
        log_pos_btn.pack(side="right")

        for nombre in JOINTS:
            self._build_joint_row(main, nombre)

        ir_todas_btn = tk.Button(
            main, text="\u25b6 EJECUTAR TODAS (Simult\u00e1neo)",
            bg="#f57c00", fg="white", font=("Sans", 10, "bold"),
            activebackground="#e65100", command=self.ir_a_todas_posiciones,
        )
        ir_todas_btn.pack(fill="x", pady=(10, 5))

        ttk.Separator(main, orient="horizontal").pack(fill="x", pady=(10, 10))
        ttk.Label(main, text="Velocidad de movimiento (1\u20131023, mayor = m\u00e1s r\u00e1pido)", font=("Sans", 10, "bold")).pack(anchor="w")

        vel_row = ttk.Frame(main)
        vel_row.pack(fill="x", pady=(4, 0))

        self.vel_slider = tk.Scale(
            vel_row, from_=1, to=1023, orient="horizontal",
            resolution=1, length=380, showvalue=True,
        )
        self.vel_slider.set(self.velocidad_actual)
        self.vel_slider.pack(side="left", padx=(0, 8))
        self.vel_slider.bind("<ButtonRelease-1>", lambda e: self._enviar_velocidad(self.vel_slider.get()))

        self.vel_entry_var = tk.StringVar(value=str(self.velocidad_actual))
        vel_entry = ttk.Entry(vel_row, textvariable=self.vel_entry_var, width=6, justify="center")
        vel_entry.pack(side="left")
        vel_entry.bind("<Return>", lambda e: self._enviar_velocidad_desde_entry())

        vel_ir_btn = tk.Button(vel_row, text="Ir", width=3, command=self._enviar_velocidad_desde_entry)
        vel_ir_btn.pack(side="left", padx=(4, 0))

        botones = ttk.Frame(main)
        botones.pack(fill="x", pady=(16, 6))

        home_btn = tk.Button(
            botones, text="\u2b24 HOME (0\u00b0 en todas simult\u00e1neo)",
            bg="#2e7d32", fg="white", font=("Sans", 11, "bold"),
            activebackground="#1b5e20", command=self.ir_a_home,
        )
        home_btn.pack(fill="x", ipady=6)

        torque_row = ttk.Frame(main)
        torque_row.pack(fill="x", pady=(8, 6))

        torque_on_btn = tk.Button(
            torque_row, text="\u26a1 TORQUE ON", bg="#1565c0", fg="white", font=("Sans", 11, "bold"),
            activebackground="#0d47a1", command=self.torque_on,
        )
        torque_on_btn.pack(side="left", fill="x", expand=True, padx=(0, 6), ipady=6)

        torque_off_btn = tk.Button(
            torque_row, text="\u26a0 TORQUE OFF", bg="#c62828", fg="white", font=("Sans", 11, "bold"),
            activebackground="#8e0000", command=self.torque_off,
        )
        torque_off_btn.pack(side="left", fill="x", expand=True, padx=(6, 0), ipady=6)

        ttk.Label(main, text="Registro:").pack(anchor="w", pady=(12, 2))
        self.log_text = tk.Text(main, height=9, state="disabled", font=("Consolas", 9), bg="#f4f4f4")
        self.log_text.pack(fill="both", expand=True)

        self._log(f"Conectado a ros2_control. Torque simulado activo.")
        self.root.after(100, self._poll_log_queue)

    def _build_joint_row(self, parent, nombre):
        lo, hi = LIMITS_DEG[nombre]
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=5)

        ttk.Label(frame, text=NOMBRES_BONITOS[nombre], width=9).pack(side="left")

        slider = tk.Scale(frame, from_=lo, to=hi, orient="horizontal", resolution=1, length=300, showvalue=True)
        slider.set(0)
        slider.pack(side="left", padx=(4, 8))
        slider.bind("<ButtonRelease-1>", lambda e, n=nombre, s=slider: self._enviar(n, s.get()))
        self.sliders[nombre] = slider

        entry_var = tk.StringVar(value="0")
        entry = ttk.Entry(frame, textvariable=entry_var, width=6, justify="center")
        entry.pack(side="left", padx=(0, 20))
        entry.bind("<Return>", lambda e: self.ir_a_todas_posiciones())
        self.entries[nombre] = entry_var

        medido_lbl = ttk.Label(frame, text="\u2014", width=8, anchor="e")
        medido_lbl.pack(side="right")
        self.medido_labels[nombre] = medido_lbl

    def _enviar(self, nombre, valor):
        if self.busy:
            self._log("Ocupado terminando un movimiento...")
            return
        angulo = float(valor)
        self._run_en_hilo(lambda: self._mover_individual(nombre, angulo))

    def parada_emergencia(self):
        def tarea():
            self.node.apagar_torque_solamente()
            self.log_q.put("!!! PARADA DE EMERGENCIA: Torque apagado inmediatamente !!!")
        threading.Thread(target=tarea, daemon=True).start()

    def _toggle_monitor(self):
        if self.monitor_var.get():
            self._log("Monitor de posici\u00f3n: ACTIVADO.")
            threading.Thread(target=self._monitor_loop, daemon=True).start()
        else:
            self._log("Monitor de posici\u00f3n: DESACTIVADO.")

    def _monitor_loop(self):
        while self.monitor_var.get():
            lecturas = self.node.leer_todas()
            self.root.after(0, self._aplicar_lecturas, lecturas)
            time.sleep(0.3) 

    def _aplicar_lecturas(self, lecturas: dict):
        for nombre, medido in lecturas.items():
            if medido is not None:
                self.medido_labels[nombre].config(text=f"{medido:.1f}\u00b0")
                if not self.node.torque_habilitado:
                    self.sliders[nombre].set(medido)
                    self.entries[nombre].set(f"{medido:.0f}")

    def _anotar_posiciones_log(self):
        lecturas = self.node.leer_todas()
        partes = []
        for nombre in JOINTS:
            val = lecturas.get(nombre)
            val_str = f"{val:.1f}\u00b0" if val is not None else "?"
            partes.append(f"{nombre.capitalize()}={val_str}")
        self.log_q.put("POSICIONES ACTUALES: " + " | ".join(partes))

    def ir_a_todas_posiciones(self):
        if self.busy:
            self._log("Ocupado terminando un movimiento, espera un momento...")
            return

        angulos_objetivo = {}
        for nombre in JOINTS:
            val_str = self.entries[nombre].get()
            try:
                angulos_objetivo[nombre] = float(val_str)
            except ValueError:
                self._log(f"Valor inv\u00e1lido en {nombre}: '{val_str}'. Cancelado.")
                return

        def tarea():
            self.log_q.put("Enviando comando simult\u00e1neo a las 5 articulaciones...")
            resultados = self.node.mover_simultaneo(angulos_objetivo, espera_s=0.7)

            for nombre, (ok, medido) in resultados.items():
                self.root.after(0, self._sync_widgets, nombre, angulos_objetivo[nombre], medido, ok)
                est = "OK" if ok else "RECHAZADO"
                val = f"{medido:.1f}\u00b0" if medido is not None else "?"
                self.log_q.put(f"{nombre} -> {angulos_objetivo[nombre]:.0f}\u00b0 [{est}] medido={val}")

            self.log_q.put("Movimiento simult\u00e1neo completado.")
        self._run_en_hilo(tarea)

    def ir_a_home(self):
        if self.busy: return
        def tarea():
            self.log_q.put("Enviando robot a HOME (0\u00b0)...")
            objetivos = {nombre: 0.0 for nombre in JOINTS}
            resultados = self.node.mover_simultaneo(objetivos, espera_s=0.7)

            for nombre, (ok, medido) in resultados.items():
                self.root.after(0, self._sync_widgets, nombre, 0.0, medido, ok)
        self._run_en_hilo(tarea)

    def demo(self):
        if self.busy: return
        segundos = simpledialog.askfloat(
            "Demo", "Segundos de espera en cada posici\u00f3n:",
            initialvalue=2.5, minvalue=0.5, maxvalue=10.0, parent=self.root,
        )
        if segundos is None: return

        def tarea():
            self.log_q.put(f"--- Iniciando DEMO ({segundos:.1f} s por posici\u00f3n) ---")
            for nombre, posiciones in DEMO_POSICIONES.items():
                self.log_q.put(f"--- Articulaci\u00f3n: {nombre} ---")
                for angulo in posiciones:
                    self._mover_individual(nombre, angulo, espera_s=segundos)
                self._mover_individual(nombre, 0.0, espera_s=segundos)
            self.log_q.put("--- DEMO finalizada ---")

        self._run_en_hilo(tarea)

    def _mover_individual(self, nombre, angulo, espera_s=0.6):
        ok = self.node.mover_articulacion(nombre, angulo, espera_s=espera_s)
        medido = self.node.last_measured_deg
        self.root.after(0, self._sync_widgets, nombre, angulo, medido, ok)
        est = "OK" if ok else "RECHAZADO"
        val = f"{medido:.1f}\u00b0" if medido is not None else "?"
        self.log_q.put(f"{nombre} -> {angulo:.0f}\u00b0 [{est}] medido={val}")

    def torque_off(self):
        self._run_en_hilo(lambda: (self.node.apagar_torque_solamente(), self.log_q.put("Torque desactivado.")))

    def torque_on(self):
        self._run_en_hilo(lambda: (self.node.habilitar_torque(), self.log_q.put("Torque habilitado.")))

    def _enviar_velocidad(self, valor):
        try: velocidad = int(float(valor))
        except ValueError: return
        if self.busy: return
        def tarea():
            if self.node.set_velocidad(velocidad):
                self.root.after(0, self._sync_velocidad_widgets, velocidad)
                self.log_q.put(f"Velocidad simulada: {velocidad}")
        self._run_en_hilo(tarea)

    def _enviar_velocidad_desde_entry(self):
        self._enviar_velocidad(self.vel_entry_var.get())

    def _sync_velocidad_widgets(self, velocidad):
        self.velocidad_actual = velocidad
        self.vel_slider.set(velocidad)
        self.vel_entry_var.set(str(velocidad))

    def _sync_widgets(self, nombre, angulo, medido, ok):
        if ok:
            self.sliders[nombre].set(angulo)
            self.entries[nombre].set(f"{angulo:.0f}")
        if medido is not None:
            self.medido_labels[nombre].config(text=f"{medido:.1f}\u00b0")

    def _run_en_hilo(self, fn):
        self.busy = True
        def wrapper():
            try: fn()
            finally: self.busy = False
        threading.Thread(target=wrapper, daemon=True).start()

    def _poll_log_queue(self):
        while not self.log_q.empty():
            msg = self.log_q.get_nowait()
            self._log(msg)
        self.root.after(100, self._poll_log_queue)

    def _log(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

def main(args=None):
    rclpy.init(args=args)
    node = JointSelector()
    
    # Cambio crucial 2: Hilo dedicado para recibir información de ROS 2
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()

    root = tk.Tk()
    app = JointControlApp(root, node)

    def on_close():
        try: node.apagar()
        finally:
            rclpy.shutdown()
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

if __name__ == "__main__":
    main()