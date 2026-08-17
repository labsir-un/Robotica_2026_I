#!/usr/bin/env python3
"""Interfaz Teach and Play para PhantomX Pincher X100 - Actividad 13.

Funciones:
- Leer posición actual desde /joint_states.
- Guardar poses actuales con nombre.
- Guardar y cargar poses desde YAML.
- Cada pose tiene:
    name: nombre
    joints: posiciones articulares en grados
    v: velocidad para llegar a esa pose
    t: tiempo de espera después de llegar a esa pose
- Reproducir rutina en orden.
- Esperar hasta que el robot llegue a cada pose antes de pasar a la siguiente.
- Detener reproducción.
"""

import math
import threading
import time
from pathlib import Path

import yaml

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import UInt32
from std_srvs.srv import SetBool, Trigger


JOINTS = ["waist", "shoulder", "elbow", "wrist", "gripper"]

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_YAML_FILE = SCRIPT_DIR / "rutina_guardada.yaml"

DEFAULT_POSE_SPEED = 80
DEFAULT_POSE_WAIT = 1.0


class TeachNode(Node):
    """Nodo ROS 2 para lectura y escritura."""

    def __init__(self):
        super().__init__("teach_and_play_node")

        self.cmd_pub = self.create_publisher(
            JointState,
            "/pincher/command",
            10,
        )

        self.speed_pub = self.create_publisher(
            UInt32,
            "/pincher/profile_velocity",
            10,
        )

        self.state_sub = self.create_subscription(
            JointState,
            "/joint_states",
            self.state_callback,
            10,
        )

        self.stop_client = self.create_client(
            Trigger,
            "/pincher/software_stop",
        )

        self.torque_client = self.create_client(
            SetBool,
            "/pincher/torque_enable",
        )

        self.home_client = self.create_client(
            Trigger,
            "/pincher/home",
        )

        self.current_positions = {joint: 0.0 for joint in JOINTS}
        self.is_ready = False

    def state_callback(self, msg):
        for i, name in enumerate(msg.name):
            if name in self.current_positions:
                self.current_positions[name] = msg.position[i]

        self.is_ready = True


class TeachGUI:
    def __init__(self, node: TeachNode):
        self.node = node

        self.root = tk.Tk()
        self.root.title("Actividad 13 - Teach & Play - PhantomX Pincher X100")
        self.root.geometry("1050x650")

        self.yaml_path = DEFAULT_YAML_FILE
        self.poses_data = []

        self.is_playing = False
        self.stop_playback = False

        self.cargar_yaml(self.yaml_path, show_message=False)
        self._build_ui()

        self.root.after(20, self._spin_ros)
        self.root.after(100, self._update_realtime)

    # =========================================================
    # YAML
    # =========================================================

    def normalizar_poses_yaml(self, data):
        """
        Acepta dos formatos:

        Formato nuevo:
        joints_order:
        - waist
        - shoulder
        - elbow
        - wrist
        - gripper
        poses:
        - name: pose_1
          joints: [0, 0, 0, 0, 0]
          v: 80
          t: 1.0

        Formato viejo:
        - name: pose_1
          joints: [0, 0, 0, 0, 0]
        """
        if data is None:
            return []

        if isinstance(data, dict):
            poses = data.get("poses", [])
        elif isinstance(data, list):
            poses = data
        else:
            raise ValueError(
                "El YAML debe ser una lista de poses o un diccionario con clave 'poses'."
            )

        normalizadas = []

        for idx, pose in enumerate(poses, start=1):
            if not isinstance(pose, dict):
                raise ValueError(f"La pose {idx} no tiene formato de diccionario.")

            name = pose.get("name", f"pose_{idx}")
            joints = pose.get("joints", None)

            if joints is None:
                raise ValueError(f"La pose '{name}' no tiene la clave 'joints'.")

            if len(joints) != len(JOINTS):
                raise ValueError(
                    f"La pose '{name}' debe tener {len(JOINTS)} valores articulares."
                )

            joints_float = [float(value) for value in joints]

            # Compatibilidad:
            # v: velocidad de la pose
            # t: tiempo de espera después de llegar
            # Si el YAML viejo no los tiene, se asignan valores por defecto.
            v = pose.get("v", pose.get("velocity", DEFAULT_POSE_SPEED))
            t = pose.get("t", pose.get("wait_time", DEFAULT_POSE_WAIT))

            normalizadas.append({
                "name": str(name),
                "joints": joints_float,
                "v": int(float(v)),
                "t": float(t),
            })

        return normalizadas

    def cargar_yaml(self, path=None, show_message=True):
        if path is None:
            path = self.yaml_path

        path = Path(path)

        if not path.exists():
            self.poses_data = []
            if show_message:
                messagebox.showwarning(
                    "YAML no encontrado",
                    f"No existe el archivo:\n{path}",
                )
            return

        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f)

            self.poses_data = self.normalizar_poses_yaml(data)
            self.yaml_path = path

            if hasattr(self, "listbox"):
                self.actualizar_listbox()

            if hasattr(self, "status_bar"):
                self.status_bar.config(
                    text=f"YAML cargado: {self.yaml_path} | Poses: {len(self.poses_data)}"
                )

            if show_message:
                messagebox.showinfo(
                    "YAML cargado",
                    f"Se cargaron {len(self.poses_data)} poses desde:\n{self.yaml_path}",
                )

        except Exception as e:
            self.poses_data = []

            if hasattr(self, "status_bar"):
                self.status_bar.config(text=f"Error cargando YAML: {e}")

            if show_message:
                messagebox.showerror("Error cargando YAML", str(e))

    def cargar_yaml_dialogo(self):
        path = filedialog.askopenfilename(
            title="Seleccionar archivo YAML de poses",
            filetypes=[
                ("YAML files", "*.yaml *.yml"),
                ("Todos los archivos", "*.*"),
            ],
        )

        if not path:
            return

        self.cargar_yaml(path, show_message=True)

    def guardar_yaml(self):
        try:
            self.yaml_path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "joints_order": JOINTS,
                "poses": self.poses_data,
            }

            with open(self.yaml_path, "w") as f:
                yaml.dump(
                    data,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                )

            self.status_bar.config(text=f"YAML guardado: {self.yaml_path}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

    def guardar_yaml_como(self):
        path = filedialog.asksaveasfilename(
            title="Guardar rutina como YAML",
            defaultextension=".yaml",
            filetypes=[
                ("YAML files", "*.yaml *.yml"),
                ("Todos los archivos", "*.*"),
            ],
            initialfile="rutina_guardada.yaml",
        )

        if not path:
            return

        self.yaml_path = Path(path)
        self.guardar_yaml()

    # =========================================================
    # UI
    # =========================================================

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="y", expand=False, padx=(0, 10))

        realtime_group = ttk.LabelFrame(
            left_frame,
            text="Lectura en tiempo real [°]",
            padding=10,
        )
        realtime_group.pack(fill="x", pady=(0, 10))

        self.lbl_realtime = {}

        for i, joint in enumerate(JOINTS):
            ttk.Label(
                realtime_group,
                text=f"{joint.capitalize()}:",
                font=("Arial", 10, "bold"),
            ).grid(row=i, column=0, sticky="w", padx=3, pady=2)

            var = tk.StringVar(value="0.0")
            ttk.Label(
                realtime_group,
                textvariable=var,
                width=10,
            ).grid(row=i, column=1, sticky="e", padx=3, pady=2)

            self.lbl_realtime[joint] = var

        hw_group = ttk.LabelFrame(
            left_frame,
            text="Control físico",
            padding=10,
        )
        hw_group.pack(fill="x", pady=10)

        tk.Button(
            hw_group,
            text="Torque OFF\n(para mover a mano)",
            bg="orange",
            command=lambda: self.set_torque(False),
        ).pack(fill="x", pady=2)

        tk.Button(
            hw_group,
            text="Torque ON\n(bloquear)",
            bg="lightgreen",
            command=lambda: self.set_torque(True),
        ).pack(fill="x", pady=2)

        ttk.Button(
            hw_group,
            text="Ir a HOME",
            command=self.go_home,
        ).pack(fill="x", pady=2)

        tk.Button(
            hw_group,
            text="EMERGENCIA / STOP",
            bg="red",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.stop_all,
        ).pack(fill="x", pady=10)

        speed_frame = ttk.Frame(hw_group)
        speed_frame.pack(fill="x", pady=5)

        ttk.Label(speed_frame, text="Velocidad manual:").pack(side="left")
        self.speed_var = tk.IntVar(value=DEFAULT_POSE_SPEED)

        ttk.Spinbox(
            speed_frame,
            from_=0,
            to=1023,
            textvariable=self.speed_var,
            width=7,
        ).pack(side="left", padx=5)

        ttk.Button(
            speed_frame,
            text="Aplicar",
            command=self.apply_speed,
        ).pack(side="left")

        pose_defaults_group = ttk.LabelFrame(
            left_frame,
            text="Valores por defecto al guardar pose",
            padding=10,
        )
        pose_defaults_group.pack(fill="x", pady=10)

        ttk.Label(pose_defaults_group, text="v velocidad:").grid(
            row=0,
            column=0,
            sticky="w",
            pady=2,
        )
        self.default_pose_speed_var = tk.StringVar(value=str(DEFAULT_POSE_SPEED))
        ttk.Entry(
            pose_defaults_group,
            textvariable=self.default_pose_speed_var,
            width=8,
        ).grid(row=0, column=1, pady=2)

        ttk.Label(pose_defaults_group, text="t espera [s]:").grid(
            row=1,
            column=0,
            sticky="w",
            pady=2,
        )
        self.default_pose_wait_var = tk.StringVar(value=str(DEFAULT_POSE_WAIT))
        ttk.Entry(
            pose_defaults_group,
            textvariable=self.default_pose_wait_var,
            width=8,
        ).grid(row=1, column=1, pady=2)

        arrival_group = ttk.LabelFrame(
            left_frame,
            text="Detección de llegada",
            padding=10,
        )
        arrival_group.pack(fill="x", pady=10)

        ttk.Label(arrival_group, text="Tolerancia [°]:").grid(
            row=0,
            column=0,
            sticky="w",
            pady=2,
        )
        self.tolerance_var = tk.StringVar(value="3.0")
        ttk.Entry(
            arrival_group,
            textvariable=self.tolerance_var,
            width=8,
        ).grid(row=0, column=1, pady=2)

        ttk.Label(arrival_group, text="Timeout por pose [s]:").grid(
            row=1,
            column=0,
            sticky="w",
            pady=2,
        )
        self.timeout_var = tk.StringVar(value="12.0")
        ttk.Entry(
            arrival_group,
            textvariable=self.timeout_var,
            width=8,
        ).grid(row=1, column=1, pady=2)

        ttk.Label(arrival_group, text="Estabilidad lecturas:").grid(
            row=2,
            column=0,
            sticky="w",
            pady=2,
        )
        self.stable_count_var = tk.StringVar(value="5")
        ttk.Entry(
            arrival_group,
            textvariable=self.stable_count_var,
            width=8,
        ).grid(row=2, column=1, pady=2)

        right_frame = ttk.LabelFrame(
            main_frame,
            text="Gestor de poses - Teach & Play",
            padding=10,
        )
        right_frame.pack(side="left", fill="both", expand=True)

        yaml_frame = ttk.LabelFrame(
            right_frame,
            text="Archivo YAML",
            padding=8,
        )
        yaml_frame.pack(fill="x", pady=(0, 8))

        self.yaml_var = tk.StringVar(value=str(self.yaml_path))

        ttk.Label(
            yaml_frame,
            textvariable=self.yaml_var,
            wraplength=720,
        ).pack(fill="x", pady=2)

        yaml_buttons = ttk.Frame(yaml_frame)
        yaml_buttons.pack(fill="x", pady=4)

        ttk.Button(
            yaml_buttons,
            text="Cargar YAML...",
            command=self.cargar_yaml_dialogo,
        ).pack(side="left", padx=2)

        ttk.Button(
            yaml_buttons,
            text="Recargar YAML actual",
            command=lambda: self.cargar_yaml(self.yaml_path, show_message=True),
        ).pack(side="left", padx=2)

        ttk.Button(
            yaml_buttons,
            text="Guardar YAML",
            command=self.guardar_yaml,
        ).pack(side="left", padx=2)

        ttk.Button(
            yaml_buttons,
            text="Guardar como...",
            command=self.guardar_yaml_como,
        ).pack(side="left", padx=2)

        list_controls = ttk.Frame(right_frame)
        list_controls.pack(fill="x", pady=(0, 5))

        ttk.Button(
            list_controls,
            text="Guardar pose actual",
            command=self.save_current_pose,
        ).pack(side="left", padx=2)

        ttk.Button(
            list_controls,
            text="Editar v/t seleccionada",
            command=self.edit_selected_pose_params,
        ).pack(side="left", padx=2)

        ttk.Button(
            list_controls,
            text="Borrar seleccionada",
            command=self.delete_pose,
        ).pack(side="left", padx=2)

        ttk.Button(
            list_controls,
            text="Actualizar lista",
            command=self.actualizar_listbox,
        ).pack(side="left", padx=2)

        self.listbox = tk.Listbox(
            right_frame,
            height=14,
            font=("Courier", 10),
        )
        self.listbox.pack(fill="both", expand=True, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.on_pose_select)

        self.info_var = tk.StringVar(
            value="Selecciona una pose para ver sus valores."
        )

        ttk.Label(
            right_frame,
            textvariable=self.info_var,
            background="#e6e6e6",
            padding=5,
        ).pack(fill="x", pady=5)

        ttk.Button(
            right_frame,
            text="Mover robot a pose seleccionada",
            command=self.go_to_selected_pose,
        ).pack(fill="x", pady=5)

        play_group = ttk.LabelFrame(
            right_frame,
            text="Reproducción de rutina",
            padding=10,
        )
        play_group.pack(fill="x", pady=10)

        ttk.Label(
            play_group,
            text="La rutina usa v y t propios de cada pose.",
        ).grid(row=0, column=0, padx=4, pady=4, sticky="w")

        tk.Button(
            play_group,
            text="▶ REPRODUCIR RUTINA",
            bg="lightblue",
            font=("Arial", 10, "bold"),
            command=self.play_sequence,
        ).grid(row=0, column=1, padx=10, pady=4)

        tk.Button(
            play_group,
            text="DETENER REPRODUCCIÓN",
            bg="tomato",
            fg="white",
            command=self.stop_play_sequence,
        ).grid(row=0, column=2, padx=4, pady=4)

        self.status_bar = ttk.Label(
            self.root,
            text="Listo.",
            relief="sunken",
            anchor="w",
        )
        self.status_bar.pack(side="bottom", fill="x")

        self.actualizar_listbox()

    # =========================================================
    # ROS + UI
    # =========================================================

    def _spin_ros(self):
        if rclpy.ok():
            rclpy.spin_once(self.node, timeout_sec=0.0)
            self.root.after(20, self._spin_ros)

    def _update_realtime(self):
        if self.node.is_ready:
            for joint in JOINTS:
                grados = math.degrees(self.node.current_positions[joint])
                self.lbl_realtime[joint].set(f"{grados:6.2f}")

        self.yaml_var.set(str(self.yaml_path))
        self.root.after(100, self._update_realtime)

    # =========================================================
    # Control hardware
    # =========================================================

    def set_torque(self, state: bool):
        if self.node.torque_client.service_is_ready():
            req = SetBool.Request()
            req.data = bool(state)
            self.node.torque_client.call_async(req)
            self.status_bar.config(text=f"Torque {'ON' if state else 'OFF'}")
        else:
            self.status_bar.config(
                text="Servicio /pincher/torque_enable no disponible."
            )

    def stop_all(self):
        self.stop_playback = True

        if self.node.stop_client.service_is_ready():
            self.node.stop_client.call_async(Trigger.Request())

        self.set_torque(False)

        self.status_bar.config(
            text="¡STOP! Reproducción detenida y solicitud de Torque OFF enviada."
        )

    def stop_play_sequence(self):
        self.stop_playback = True
        self.status_bar.config(text="Solicitud de detener reproducción enviada.")

    def go_home(self):
        if self.node.home_client.service_is_ready():
            self.node.home_client.call_async(Trigger.Request())
            self.status_bar.config(text="Comando HOME enviado.")
        else:
            self.status_bar.config(text="Servicio /pincher/home no disponible.")

    def set_speed_value(self, value):
        try:
            val = int(float(value))
            val = max(0, min(1023, val))
        except ValueError:
            val = DEFAULT_POSE_SPEED

        msg = UInt32()
        msg.data = val

        for _ in range(3):
            self.node.speed_pub.publish(msg)
            time.sleep(0.05)

        return val

    def apply_speed(self):
        try:
            val = int(self.speed_var.get())
            val = max(0, min(1023, val))
            self.speed_var.set(val)

            self.set_speed_value(val)
            self.status_bar.config(text=f"Velocidad manual ajustada a {val}")

        except ValueError:
            messagebox.showerror("Error", "Velocidad inválida.")

    # =========================================================
    # Poses
    # =========================================================

    def actualizar_listbox(self):
        self.listbox.delete(0, tk.END)

        for idx, pose in enumerate(self.poses_data):
            name = pose.get("name", f"pose_{idx + 1}")
            joints = pose.get("joints", [0, 0, 0, 0, 0])
            v = pose.get("v", DEFAULT_POSE_SPEED)
            t = pose.get("t", DEFAULT_POSE_WAIT)

            joints_txt = "[" + ", ".join([f"{q:.1f}" for q in joints]) + "]"

            self.listbox.insert(
                tk.END,
                f"{idx + 1:02d}. {name:<18} v={v:<4} t={t:<5} joints={joints_txt}",
            )

        if hasattr(self, "status_bar"):
            self.status_bar.config(
                text=f"Lista actualizada. Poses cargadas: {len(self.poses_data)}"
            )

    def pedir_velocidad_y_tiempo(self, initial_v=None, initial_t=None):
        if initial_v is None:
            try:
                initial_v = int(float(self.default_pose_speed_var.get()))
            except ValueError:
                initial_v = DEFAULT_POSE_SPEED

        if initial_t is None:
            try:
                initial_t = float(self.default_pose_wait_var.get())
            except ValueError:
                initial_t = DEFAULT_POSE_WAIT

        v = simpledialog.askinteger(
            "Velocidad de la pose",
            "v = velocidad para llegar a esta pose:",
            initialvalue=int(initial_v),
            minvalue=0,
            maxvalue=1023,
        )

        if v is None:
            return None, None

        t = simpledialog.askfloat(
            "Tiempo de espera",
            "t = tiempo de espera después de llegar a esta pose [s]:",
            initialvalue=float(initial_t),
            minvalue=0.0,
        )

        if t is None:
            return None, None

        return int(v), float(t)

    def save_current_pose(self):
        if not self.node.is_ready:
            messagebox.showwarning(
                "Aviso",
                "No se han recibido datos del robot todavía.",
            )
            return

        nombre = simpledialog.askstring(
            "Guardar pose",
            "Nombre de la pose:",
        )

        if not nombre:
            return

        v, t = self.pedir_velocidad_y_tiempo()

        if v is None or t is None:
            return

        grados = [
            round(math.degrees(self.node.current_positions[joint]), 2)
            for joint in JOINTS
        ]

        nueva_pose = {
            "name": nombre,
            "joints": grados,
            "v": v,
            "t": t,
        }

        self.poses_data.append(nueva_pose)
        self.guardar_yaml()
        self.actualizar_listbox()

        self.status_bar.config(
            text=f"Pose '{nombre}' guardada: joints={grados}, v={v}, t={t}s"
        )

    def edit_selected_pose_params(self):
        seleccion = self.listbox.curselection()

        if not seleccion:
            messagebox.showwarning(
                "Aviso",
                "Selecciona una pose para editar.",
            )
            return

        idx = seleccion[0]
        pose = self.poses_data[idx]

        current_v = pose.get("v", DEFAULT_POSE_SPEED)
        current_t = pose.get("t", DEFAULT_POSE_WAIT)

        v, t = self.pedir_velocidad_y_tiempo(
            initial_v=current_v,
            initial_t=current_t,
        )

        if v is None or t is None:
            return

        pose["v"] = v
        pose["t"] = t

        self.guardar_yaml()
        self.actualizar_listbox()

        self.status_bar.config(
            text=f"Pose '{pose['name']}' actualizada: v={v}, t={t}s"
        )

    def delete_pose(self):
        seleccion = self.listbox.curselection()

        if not seleccion:
            messagebox.showwarning(
                "Aviso",
                "Selecciona una pose para borrar.",
            )
            return

        idx = seleccion[0]
        nombre = self.poses_data[idx]["name"]

        if messagebox.askyesno(
            "Confirmar",
            f"¿Borrar la pose '{nombre}'?",
        ):
            self.poses_data.pop(idx)
            self.guardar_yaml()
            self.actualizar_listbox()
            self.info_var.set("Selecciona una pose para ver sus valores.")

    def on_pose_select(self, event=None):
        seleccion = self.listbox.curselection()

        if not seleccion:
            return

        idx = seleccion[0]
        pose = self.poses_data[idx]

        joints = pose["joints"]
        v = pose.get("v", DEFAULT_POSE_SPEED)
        t = pose.get("t", DEFAULT_POSE_WAIT)

        j_str = ", ".join(
            [
                f"{joint}: {value:.2f}°"
                for joint, value in zip(JOINTS, joints)
            ]
        )

        self.info_var.set(
            f"{pose['name']} -> {j_str} | v={v} | t={t:.2f}s"
        )

    def go_to_selected_pose(self):
        seleccion = self.listbox.curselection()

        if not seleccion:
            messagebox.showwarning(
                "Aviso",
                "Selecciona una pose de la lista primero.",
            )
            return

        idx = seleccion[0]
        pose = self.poses_data[idx]

        v = pose.get("v", DEFAULT_POSE_SPEED)
        self.set_speed_value(v)
        self._enviar_comando(pose["joints"])

        self.status_bar.config(
            text=f"Moviendo a pose: {pose['name']} con v={v}"
        )

    def _enviar_comando(self, grados_list):
        msg = JointState()
        msg.header.stamp = self.node.get_clock().now().to_msg()
        msg.name = JOINTS
        msg.position = [math.radians(float(g)) for g in grados_list]

        for _ in range(5):
            self.node.cmd_pub.publish(msg)
            time.sleep(0.04)

    # =========================================================
    # Detección de llegada
    # =========================================================

    def get_current_positions_deg(self):
        return {
            joint: math.degrees(self.node.current_positions[joint])
            for joint in JOINTS
        }

    def pose_error_deg(self, target_deg):
        current = self.get_current_positions_deg()

        errors = {}

        for joint, target in zip(JOINTS, target_deg):
            errors[joint] = abs(float(target) - current[joint])

        max_error = max(errors.values())

        return errors, max_error

    def wait_until_pose_reached(self, target_deg, pose_name):
        try:
            tolerance = float(self.tolerance_var.get())
        except ValueError:
            tolerance = 3.0

        try:
            timeout = float(self.timeout_var.get())
        except ValueError:
            timeout = 12.0

        try:
            required_stable_count = int(float(self.stable_count_var.get()))
        except ValueError:
            required_stable_count = 5

        required_stable_count = max(1, required_stable_count)

        t0 = time.time()
        stable_count = 0
        last_max_error = None

        while time.time() - t0 < timeout:
            if self.stop_playback:
                return False, time.time() - t0, last_max_error

            if not self.node.is_ready:
                time.sleep(0.05)
                continue

            errors, max_error = self.pose_error_deg(target_deg)
            last_max_error = max_error

            if max_error <= tolerance:
                stable_count += 1
            else:
                stable_count = 0

            elapsed = time.time() - t0

            self.root.after(
                0,
                lambda p=pose_name, e=max_error, t=elapsed: self.status_bar.config(
                    text=f"Esperando llegada a '{p}' | error máx={e:.2f}° | t={t:.1f}s"
                ),
            )

            if stable_count >= required_stable_count:
                return True, elapsed, max_error

            time.sleep(0.1)

        return False, timeout, last_max_error

    # =========================================================
    # Reproducción
    # =========================================================

    def play_sequence(self):
        if len(self.poses_data) < 2:
            messagebox.showwarning(
                "Aviso",
                "Necesitas al menos 2 poses guardadas para reproducir una rutina.",
            )
            return

        if self.is_playing:
            messagebox.showinfo(
                "Reproducción activa",
                "La rutina ya se está reproduciendo.",
            )
            return

        self.is_playing = True
        self.stop_playback = False

        thread = threading.Thread(
            target=self._play_loop,
            daemon=True,
        )
        thread.start()

    def _play_loop(self):
        self.root.after(
            0,
            lambda: self.status_bar.config(text="Reproducción INICIADA..."),
        )

        for idx, pose in enumerate(self.poses_data):
            if self.stop_playback:
                self.root.after(
                    0,
                    lambda: self.status_bar.config(text="Reproducción ABORTADA."),
                )
                break

            pose_name = pose["name"]
            joints = pose["joints"]
            v = pose.get("v", DEFAULT_POSE_SPEED)
            t_wait = pose.get("t", DEFAULT_POSE_WAIT)

            self.root.after(
                0,
                lambda i=idx: self.listbox.selection_clear(0, tk.END),
            )
            self.root.after(
                0,
                lambda i=idx: self.listbox.selection_set(i),
            )
            self.root.after(
                0,
                lambda i=idx: self.listbox.see(i),
            )
            self.root.after(
                0,
                lambda p=pose_name, v=v, t=t_wait: self.status_bar.config(
                    text=f"Enviando pose: {p} | v={v} | t={t:.2f}s"
                ),
            )

            self.set_speed_value(v)
            self._enviar_comando(joints)

            reached, elapsed, max_error = self.wait_until_pose_reached(
                target_deg=joints,
                pose_name=pose_name,
            )

            if self.stop_playback:
                break

            if reached:
                self.root.after(
                    0,
                    lambda p=pose_name, elapsed=elapsed, max_error=max_error: self.status_bar.config(
                        text=f"Pose '{p}' alcanzada en {elapsed:.2f}s | error máx={max_error:.2f}°"
                    ),
                )
            else:
                self.root.after(
                    0,
                    lambda p=pose_name, max_error=max_error: self.status_bar.config(
                        text=f"Timeout en pose '{p}' | error máx={max_error if max_error is not None else -1:.2f}°"
                    ),
                )

            # t_wait: espera propia de la pose después de llegar.
            t_pause = 0.0
            while t_pause < t_wait:
                if self.stop_playback:
                    break

                self.root.after(
                    0,
                    lambda p=pose_name, t=t_pause, total=t_wait: self.status_bar.config(
                        text=f"Pose alcanzada: '{p}' | espera {t:.1f}/{total:.1f}s"
                    ),
                )

                time.sleep(0.1)
                t_pause += 0.1

        self.is_playing = False

        if not self.stop_playback:
            self.root.after(
                0,
                lambda: self.status_bar.config(text="Reproducción FINALIZADA."),
            )
        else:
            self.root.after(
                0,
                lambda: self.status_bar.config(text="Reproducción DETENIDA."),
            )


def main(args=None):
    rclpy.init(args=args)

    node = TeachNode()
    app = TeachGUI(node)

    try:
        app.root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
