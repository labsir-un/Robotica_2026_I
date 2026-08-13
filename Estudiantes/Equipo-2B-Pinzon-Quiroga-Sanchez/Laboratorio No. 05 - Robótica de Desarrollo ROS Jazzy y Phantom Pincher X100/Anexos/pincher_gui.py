"""Interfaz Tkinter para enviar comandos articulares al PhantomX Pincher."""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, List
from tkinter import simpledialog

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String, UInt32
from std_srvs.srv import SetBool, Trigger
import random
import numpy as np
import time 
import yaml
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .cinematica import (
    cinematica_inversa,
    elegir_solucion_cercana
)


JOINT_LIMITS_DEG = {
    'waist': (-150.0, 150.0),
    'shoulder': (-150.0, 150.0),
    'elbow': (-150.0, 150.0),
    'wrist': (-150.0, 150.0),
    'gripper': (-90.0, 90.0),
}


class PincherGuiNode(Node):
    """Nodo ligero usado por la ventana Tkinter."""

    def __init__(self) -> None:
        super().__init__('pincher_gui')
        self.current_positions = {}
        self.joint_state_subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )
        self.command_publisher = self.create_publisher(JointState, '/pincher/command', 10)
        self.speed_publisher = self.create_publisher(
            UInt32,
            '/pincher/profile_velocity',
            10,
        )
        self.home_client = self.create_client(Trigger, '/pincher/home')
        self.stop_client = self.create_client(Trigger, '/pincher/software_stop')
        self.torque_client = self.create_client(SetBool, '/pincher/torque_enable')
        self.latest_status = 'Esperando al controlador...'
        self.status_subscription = self.create_subscription(
            String,
            '/pincher/status',
            self._status_callback,
            10,
        )
        

    def _status_callback(self, msg: String) -> None:
        self.latest_status = msg.data

    def publish_joint_command(self, names: List[str], degrees: List[float]) -> None:
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = names
        msg.position = [math.radians(value) for value in degrees]
        self.command_publisher.publish(msg)

    def publish_speed(self, speed: int) -> None:
        msg = UInt32()
        msg.data = max(0, int(speed))
        self.speed_publisher.publish(msg)

    def joint_state_callback(self, msg):
        for name, position in zip(msg.name, msg.position):
            self.current_positions[name] = math.degrees(position)


class PincherGui:
    """Ventana principal con sliders, entradas y controles de seguridad."""
    
    def __init__(self, node: PincherGuiNode) -> None:
        self.node = node
        self.root = tk.Tk()
        self.root.title('PhantomX Pincher X100 - ROS 2 Jazzy')
        self.root.minsize(760, 520)
        self.root.protocol('WM_DELETE_WINDOW', self.close)
        self.yaml_file = "/home/kovoz/ros2_jazzy_jalisco/phantom_ws/src/pincher_control/config/poses.yaml"

        self.joint_names = list(JOINT_LIMITS_DEG)
        self.variables: Dict[str, tk.DoubleVar] = {
            name: tk.DoubleVar(value=0.0) for name in self.joint_names
        }
        self.entries: Dict[str, ttk.Entry] = {}
        self.status_var = tk.StringVar(value=self.node.latest_status)
        self.speed_var = tk.IntVar(value=100)

        self._build_layout()
        self.root.after(20, self._spin_ros)
        self.root.after(200, self._refresh_status)
        self.errores = {
            name: [0]*5
            for name in self.joint_names
        }
        self.deseadas = {
            name: [0]*5
            for name in self.joint_names
        }
        self.medidas = {
            name: [0]*5
            for name in self.joint_names
        }

    def _build_layout(self) -> None:
        style = ttk.Style(self.root)
        style.configure('Title.TLabel', font=('TkDefaultFont', 16, 'bold'))
        style.configure('Danger.TButton', font=('TkDefaultFont', 11, 'bold'))

        header = ttk.Frame(self.root, padding=12)
        header.pack(fill='x')
        ttk.Label(
            header,
            text='Control del PhantomX Pincher X100',
            style='Title.TLabel',
        ).pack(anchor='w')
        ttk.Label(
            header,
            text='Comandos articulares en grados; ROS 2 transmite radianes.',
        ).pack(anchor='w', pady=(4, 0))

        joints_frame = ttk.LabelFrame(self.root, text='Articulaciones', padding=12)
        joints_frame.pack(fill='both', expand=True, padx=12, pady=(0, 8))
        joints_frame.columnconfigure(1, weight=1)

        for row, name in enumerate(self.joint_names):
            lower, upper = JOINT_LIMITS_DEG[name]
            ttk.Label(joints_frame, text=name.capitalize(), width=12).grid(
                row=row,
                column=0,
                sticky='w',
                padx=(0, 8),
                pady=5,
            )
            scale = ttk.Scale(
                joints_frame,
                from_=lower,
                to=upper,
                variable=self.variables[name],
                orient='horizontal',
                command=lambda value, joint=name: self._scale_changed(joint, value),
            )
            scale.grid(row=row, column=1, sticky='ew', pady=5)
            scale.bind('<ButtonRelease-1>', lambda event: self.send_all())

            entry = ttk.Entry(joints_frame, width=10)
            entry.insert(0, '0.0')
            entry.grid(row=row, column=2, padx=(10, 4), pady=5)
            entry.bind('<Return>', lambda event, joint=name: self._entry_committed(joint))
            entry.bind('<FocusOut>', lambda event, joint=name: self._entry_committed(joint))
            self.entries[name] = entry
            ttk.Label(joints_frame, text='°').grid(row=row, column=3, sticky='w')

        controls = ttk.LabelFrame(self.root, text='Control general', padding=12)
        controls.pack(fill='x', padx=12, pady=(0, 8))

        ttk.Label(controls, text='Velocidad/Profile Velocity:').grid(
            row=0,
            column=0,
            sticky='w',
        )
        speed_spin = ttk.Spinbox(
            controls,
            from_=0,
            to=1023,
            textvariable=self.speed_var,
            width=9,
        )
        speed_spin.grid(row=0, column=1, padx=(6, 12))
        ttk.Button(controls, text='Aplicar velocidad', command=self.apply_speed).grid(
            row=0,
            column=2,
            padx=4,
        )
        ttk.Button(controls, text='Enviar posiciones', command=self.send_all).grid(
            row=0,
            column=3,
            padx=4,
        )
        ttk.Button(controls, text='HOME', command=self.call_home).grid(
            row=0,
            column=4,
            padx=4,
        )
        ttk.Button(controls, text='Torque ON', command=lambda: self.call_torque(True)).grid(
            row=1,
            column=0,
            padx=4,
            pady=(10, 0),
        )
        ttk.Button(controls, text='Torque OFF', command=lambda: self.call_torque(False)).grid(
            row=1,
            column=1,
            padx=4,
            pady=(10, 0),
        )
        ttk.Button(
            controls,
            text='PARADA DE SOFTWARE',
            command=self.call_stop,
            style='Danger.TButton',
        ).grid(row=1, column=2, columnspan=3, sticky='ew', padx=4, pady=(10, 0))

        # =====================================================
        # Actividad 7. Movimiento simultàneo y Actividad 8. Movimiento secuencial
        # =====================================================

        movement_frame = ttk.Frame(self.root)
        movement_frame.pack(fill='x', padx=12, pady=(0, 8))

        simultaneous = ttk.LabelFrame(
            movement_frame,
            text='Movimiento simultáneo',
            padding=12,
        )

        simultaneous.pack(
            side='left',
            fill='y',
            padx=(0, 6),
        )

        sequential = ttk.LabelFrame(
            movement_frame,
            text='Movimiento secuencial',
            padding=12,
        )

        sequential.pack(
            side='left',
            fill='both',
            expand=True,
        )

        ttk.Button(
            simultaneous,
            text='POSE 1',
            command=self.pose1,
            width=6,
        ).grid(row=0, column=0, padx=4)

        ttk.Button(
            simultaneous,
            text='POSE 2',
            command=self.pose2,
            width=6,
        ).grid(row=0,column=1,padx=4)

        ttk.Button(
            simultaneous,
            text='POSE 3',
            command=self.pose3,
            width=6,
        ).grid(row=0,column=2,padx=4)

        ttk.Button(
            simultaneous,
            text='POSE 4',
            command=self.pose4,
            width=6,
        ).grid(row=0,column=3,padx=4)

        ttk.Button(
            simultaneous,
            text='POSE 5',
            command=self.pose5,
            width=6,
        ).grid(row=0,column=4,padx=4)

        ttk.Button(
            sequential,
            text='SECUENCIA POSE 3',
            command=self.secuencia_pose1,
        ).pack(fill='x', pady=2)

        kinematics = ttk.LabelFrame(
            movement_frame,
            text='Cinemática',
            padding=12,
        )

        kinematics.pack(
            side='left',
            fill='both',
            expand=True,
            padx=(6,0),
        )

        ttk.Button(
            kinematics,
            text='Directa e inversa',
            command=self.forward_kinematics,
        ).pack(fill='x', pady=2)

        # =====================================================
        # Actividad 9. Interpolaciòn de trayectorias y Actividad 10. Trayectoria sinusoidal de una articulaciòn
        # =====================================================

        trajectory_frame = ttk.Frame(self.root)
        trajectory_frame.pack(fill='x', padx=12, pady=(0,8))

        interpolation = ttk.LabelFrame(
            trajectory_frame,
            text="Controles",
            padding=12,
        )

        interpolation.pack(
            fill="x",
            padx=12,
            pady=(0,8),
        )

        for i in range(6):
            interpolation.columnconfigure(i, weight=1)

        ttk.Button(
            interpolation,
            text="Interpolación lineal",
            command=self.linear_interpolation,
        ).grid(row=0, column=0, padx=4, pady=4, sticky="ew")

        ttk.Button(
            interpolation,
            text="Interpolación cúbica",
            command=self.cubic_interpolation,
        ).grid(row=0, column=1, padx=4, pady=4, sticky="ew")

        ttk.Button(
            interpolation,
            text="Mov. senoidal",
            command=self.sinusoidal_motion,
        ).grid(row=0, column=2, padx=4, pady=4, sticky="ew")

        ttk.Button(
            interpolation,
            text="Enseñanza",
            command=self.abrir_ensenanza,
        ).grid(row=0, column=3, padx=4, pady=4, sticky="ew")

        ttk.Button(
            interpolation,
            text="Dibujo",
            command=self.dibujar_cuadrado, 
        ).grid(row=0, column=4, padx=4, pady=4, sticky="ew")

        ttk.Button(
            interpolation,
            text="Baile",
            command=self.baile,
        ).grid(row=0, column=5, padx=4, pady=4, sticky="ew")

        status_frame = ttk.LabelFrame(self.root, text='Estado', padding=10)
        status_frame.pack(fill='x', padx=12, pady=(0, 12))
        ttk.Label(
            status_frame,
            textvariable=self.status_var,
            wraplength=700,
        ).pack(anchor='w')
        ttk.Label(
            status_frame,
            text=(
                'La parada de la GUI no sustituye un circuito físico de emergencia. '
                'Mantén disponible el corte de alimentación.'
            ),
        ).pack(anchor='w', pady=(6, 0))

    def _scale_changed(self, joint: str, value: str) -> None:
        numeric = float(value)
        entry = self.entries[joint]
        entry.delete(0, tk.END)
        entry.insert(0, f'{numeric:.1f}')

    def _entry_committed(self, joint: str) -> None:
        entry = self.entries[joint]
        try:
            value = float(entry.get())
        except ValueError:
            value = self.variables[joint].get()
            messagebox.showwarning('Valor inválido', f'La entrada de {joint} no es numérica.')
        lower, upper = JOINT_LIMITS_DEG[joint]
        value = max(lower, min(upper, value))
        self.variables[joint].set(value)
        entry.delete(0, tk.END)
        entry.insert(0, f'{value:.1f}')

    def send_all(self) -> None:
        for name in self.joint_names:
            self._entry_committed(name)
        values = [self.variables[name].get() for name in self.joint_names]
        self.node.publish_joint_command(self.joint_names, values)
        self.status_var.set('Comando articular publicado en /pincher/command.')

    def apply_speed(self) -> None:
        try:
            speed = int(self.speed_var.get())
        except (ValueError, tk.TclError):
            messagebox.showwarning('Valor inválido', 'La velocidad debe ser un número entero.')
            return
        speed = max(0, min(1023, speed))
        self.speed_var.set(speed)
        self.node.publish_speed(speed)
        self.status_var.set(f'Velocidad {speed} publicada.')

    def _service_available(self, client, name: str) -> bool:
        if client.service_is_ready():
            return True
        self.status_var.set(f'El servicio {name} todavía no está disponible.')
        return False

    def call_home(self) -> None:
        if not self._service_available(self.node.home_client, '/pincher/home'):
            return
        future = self.node.home_client.call_async(Trigger.Request())
        future.add_done_callback(self._service_done)
        for name in self.joint_names:
            self.variables[name].set(0.0)
            self._scale_changed(name, '0.0')

    def call_stop(self) -> None:
        if not self._service_available(self.node.stop_client, '/pincher/software_stop'):
            return
        future = self.node.stop_client.call_async(Trigger.Request())
        future.add_done_callback(self._service_done)

    def call_torque(self, enabled: bool) -> None:
        if not self._service_available(self.node.torque_client, '/pincher/torque_enable'):
            return
        request = SetBool.Request()
        request.data = enabled
        future = self.node.torque_client.call_async(request)
        future.add_done_callback(self._service_done)

    def _service_done(self, future) -> None:
        try:
            response = future.result()
            self.status_var.set(response.message)
        except Exception as exc:  # noqa: BLE001
            self.status_var.set(f'Error llamando al servicio: {exc}')

    def _spin_ros(self) -> None:
        if rclpy.ok():
            rclpy.spin_once(self.node, timeout_sec=0.0)
            self.root.after(20, self._spin_ros)

    def _refresh_status(self) -> None:
        self.status_var.set(self.node.latest_status)
        if hasattr(self, "position_table"):
            self.call_pos()
        if rclpy.ok():
            self.root.after(200, self._refresh_status)

    def run(self) -> None:
        self.root.mainloop()

    def close(self) -> None:
        self.root.destroy()
    
    def call_pos(self) -> None:
        # Limpiar la tabla
        for fila in self.position_table.get_children():
            self.position_table.delete(fila)

        # Rellenar la tabla
        for name in self.joint_names:
            posicion = self.node.current_positions.get(name, 0.0)

            self.position_table.insert(
                "",
                "end",
                values=(
                    name,
                    f"{posicion:.2f}"
                )
            )
    
    # =====================================================
    # Funciones Actividad 7
    # =====================================================

    def move_pose(self, pose):

        for joint, value in pose.items():
            self.variables[joint].set(value)
            self._scale_changed(joint, str(value))

        self.send_all()


    def pose1(self) -> None:
        """Envía una configuración predefinida."""

        pose = {
            "waist": 0.0,
            "shoulder": 0.0,
            "elbow": 0.0,
            "wrist": 0.0,
            "gripper": 0.0,
        }

        for joint, value in pose.items():
            self.variables[joint].set(value)
            self._scale_changed(joint, str(value))

        self.send_all()

        self.status_var.set("Pose 1 enviada.")

    def pose2(self) -> None:
        """Envía una configuración predefinida."""

        pose = {
            "waist": 25.0,
            "shoulder": 25.0,
            "elbow": 20.0,
            "wrist": -20.0,
            "gripper": 0.0,
        }

        for joint, value in pose.items():
            self.variables[joint].set(value)
            self._scale_changed(joint, str(value))

        self.send_all()

        self.status_var.set("Pose 2 enviada.")

    def pose3(self) -> None:
        """Envía una configuración predefinida."""

        pose = {
            "waist": -35.0,
            "shoulder": 35.0,
            "elbow": -30.0,
            "wrist": 30.0,
            "gripper": 0.0,
        }

        for joint, value in pose.items():
            self.variables[joint].set(value)
            self._scale_changed(joint, str(value))

        self.send_all()

        self.status_var.set("Pose 3 enviada.")

    def pose4(self) -> None:
        """Envía una configuración predefinida."""

        pose = {
            "waist": 85.0,
            "shoulder": -20.0,
            "elbow": 55.0,
            "wrist": 25.0,
            "gripper": 0.0,
        }

        for joint, value in pose.items():
            self.variables[joint].set(value)
            self._scale_changed(joint, str(value))

        self.send_all()

        self.status_var.set("Pose 4 enviada.")

    def pose5(self) -> None:
        """Envía una configuración predefinida."""

        pose = {
            "waist": 80.0,
            "shoulder": -35.0,
            "elbow": 55.0,
            "wrist": -45.0,
            "gripper": 0.0,
        }

        for joint, value in pose.items():
            self.variables[joint].set(value)
            self._scale_changed(joint, str(value))

        self.send_all()

        self.status_var.set("Pose 5 enviada.")

    # =====================================================
    # Funciones Actividad 8
    # =====================================================


    def secuencia_pose1(self) -> None:

        self.pose_secuencial = {
            "waist": -35.0,
            "shoulder": 35.0,
            "elbow": -30.0,
            "wrist": 30.0,
            "gripper": 0.0,
        }

        self.orden = [
            "waist",
            "shoulder",
            "elbow",
            "wrist",
            "gripper",
        ]

        self.paso_actual = 0

        self.mover_siguiente()

    def mover_siguiente(self):

        if self.paso_actual >= len(self.orden):
            self.status_var.set("Secuencia terminada.")
            return

        joint = self.orden[self.paso_actual]

        valor = self.pose_secuencial[joint]

        self.variables[joint].set(valor)

        self._scale_changed(joint, str(valor))

        self.send_all()

        self.paso_actual += 1

        self.root.after(1000, self.mover_siguiente)

    # =====================================================
    # Funciones Actividad 9
    # =====================================================

    def linear_interpolation(self):

        self.status_var.set(
            "Interpolación lineal seleccionada."
        )
        ventana = tk.Toplevel(self.root)
        ventana.title("Interpolación lineal")
        ventana.geometry("700x350")

        self.x1 = tk.DoubleVar(value=0)
        self.y1 = tk.DoubleVar(value=0)
        self.z1 = tk.DoubleVar(value=0.25)

        self.x2 = tk.DoubleVar(value=0.06)
        self.y2 = tk.DoubleVar(value=0)
        self.z2 = tk.DoubleVar(value=0.3)

        frame = ttk.LabelFrame(ventana,text="Punto inicial",padding=10)
        frame.pack(side="left",fill="both", padx=12, pady=(0,8))

        ttk.Label(frame, text="x1").grid(row=0,column=0)
        ttk.Entry(frame,textvariable=self.x1,width=8).grid(row=0,column=1)
        ttk.Label(frame, text="y1").grid(row=1,column=0)
        ttk.Entry(frame,textvariable=self.y1,width=8).grid(row=1,column=1)
        ttk.Label(frame, text="z1").grid(row=2,column=0)
        ttk.Entry(frame,textvariable=self.z1,width=8).grid(row=2,column=1)

        frame2 = ttk.LabelFrame(ventana,text="Punto final",padding=10)
        frame2.pack(side="left", fill="both", padx=12, pady=(0,8))

        ttk.Label(frame2, text="x2").grid(row=0,column=0)
        ttk.Entry(frame2,textvariable=self.x2,width=8).grid(row=0,column=1)
        ttk.Label(frame2, text="y2").grid(row=1,column=0)
        ttk.Entry(frame2,textvariable=self.y2,width=8).grid(row=1,column=1)
        ttk.Label(frame2, text="z2").grid(row=2,column=0)
        ttk.Entry(frame2,textvariable=self.z2,width=8).grid(row=2,column=1)

        graficas = ttk.LabelFrame(ventana,text="Gráficas",padding=10)
        graficas.pack(side="right", fill="both", padx=12, pady=(0,8), expand=True)

        ttk.Button(
            frame2,
            text='INICIAR',
            command=lambda: self.ir_inter_lin(self.x1.get(),self.y1.get(),self.z1.get(),self.x2.get(),self.y2.get(),self.z2.get())
        ).grid(row=3, column=1, padx=4)

        self.fig, self.axs = plt.subplots(4, 1, figsize=(6,5), sharex=True)
        self.fig.subplots_adjust(left=0.12, right=0.98,top=0.96,bottom=0.06,hspace=0.35)
        self.fig.tight_layout(rect=[0,0,1,0.98])
        self.lineas = []
        nombres = [
            "Waist",
            "Shoulder",
            "Elbow",
            "Wrist"
        ]
        for ax, nombre in zip(self.axs, nombres):
            ax.set_title(nombre)
            ax.set_ylabel("Ángulo [°]")
            ax.grid(True)

            linea, = ax.plot([],[],lw=2)
            self.lineas.append(linea)
        self.axs[-1].set_xlabel("Tiempo [s]")
        ventana.update()
        self.canvas = FigureCanvasTkAgg(self.fig, master=graficas)
        self.canvas.get_tk_widget().grid(row=4, column=0, columnspan=4, sticky="nsew", padx=5)
        self.canvas.draw()

        self.ang_ref = [
            [],[],[],[],[]
        ]


    def ir_inter_lin(self, x1, y1, z1, x2, y2, z2):

        pasos = 50          # cantidad de puntos
        dt = 0.1            # segundos entre puntos (100 ms)

        self.t_data = []

        self.ang_data = [
            [],
            [],
            [],
            [],
        ]

        self.status_var.set("Interpolación lineal comenzando.")
        
        self.call_home
        time.sleep(5)

        for i in range(pasos + 1):

            # Permite que ROS procese mensajes
            rclpy.spin_once(self.node, timeout_sec=0)

            # Parámetro de interpolación
            s = i / pasos

            # Punto cartesiano
            x = x1 + s * (x2 - x1)
            y = y1 + s * (y2 - y1)
            z = z1 + s * (z2 - z1)

            print(f"Punto {i}: ({x:.1f}, {y:.1f}, {z:.1f})")

            soluciones = cinematica_inversa(x, y, z, 0)

            if not soluciones:
                print("Sin solución")
                continue

            q = soluciones[0]

            print("q =", q)

            valores = [
                q[0],
                q[1],
                q[2],
                q[3],
                1
            ]

            self.node.publish_joint_command(
                self.joint_names,
                valores
            )

            # Graficar
            self.t_data.append(i * dt)

            for n in range(4):
                self.ang_data[n].append(q[n])
                self.lineas[n].set_data(
                    self.t_data,
                    self.ang_data[n]
                )

            for ax in self.axs:
                ax.relim()
                ax.autoscale_view()

            self.canvas.draw_idle()
            self.root.update()

            # Esperar antes del siguiente punto
            time.sleep(dt)

            self.status_var.set("Interpolación finalizada.")
        
        self.call_home
        time.sleep(5)

    def cubic_interpolation(self):

        self.status_var.set(
            "Interpolación cúbica seleccionada."
        )
        ventana = tk.Toplevel(self.root)
        ventana.title("Interpolación cúbica")
        ventana.geometry("700x350")

        self.x1 = tk.DoubleVar(value=0)
        self.y1 = tk.DoubleVar(value=0)
        self.z1 = tk.DoubleVar(value=0.25)

        self.x2 = tk.DoubleVar(value=0.06)
        self.y2 = tk.DoubleVar(value=0)
        self.z2 = tk.DoubleVar(value=0.3)

        frame = ttk.LabelFrame(ventana,text="Punto inicial",padding=10)
        frame.pack(side="left",fill="both", padx=12, pady=(0,8))

        ttk.Label(frame, text="x1").grid(row=0,column=0)
        ttk.Entry(frame,textvariable=self.x1,width=8).grid(row=0,column=1)
        ttk.Label(frame, text="y1").grid(row=1,column=0)
        ttk.Entry(frame,textvariable=self.y1,width=8).grid(row=1,column=1)
        ttk.Label(frame, text="z1").grid(row=2,column=0)
        ttk.Entry(frame,textvariable=self.z1,width=8).grid(row=2,column=1)

        frame2 = ttk.LabelFrame(ventana,text="Punto final",padding=10)
        frame2.pack(side="left", fill="both", padx=12, pady=(0,8))

        ttk.Label(frame2, text="x2").grid(row=0,column=0)
        ttk.Entry(frame2,textvariable=self.x2,width=8).grid(row=0,column=1)
        ttk.Label(frame2, text="y2").grid(row=1,column=0)
        ttk.Entry(frame2,textvariable=self.y2,width=8).grid(row=1,column=1)
        ttk.Label(frame2, text="z2").grid(row=2,column=0)
        ttk.Entry(frame2,textvariable=self.z2,width=8).grid(row=2,column=1)
        
        graficas = ttk.LabelFrame(ventana,text="Gráficas",padding=10)
        graficas.pack(side="right", fill="both", padx=12, pady=(0,8), expand=True)

        ttk.Button(
            frame2,
            text='INICIAR',
            command=lambda: self.ir_inter_cub(self.x1.get(),self.y1.get(),self.z1.get(),self.x2.get(),self.y2.get(),self.z2.get())
        ).grid(row=3, column=1, padx=4)

        self.fig, self.axs = plt.subplots(4, 1, figsize=(6,5), sharex=True)
        self.fig.subplots_adjust(left=0.12, right=0.98,top=0.96,bottom=0.06,hspace=0.35)
        self.fig.tight_layout(rect=[0,0,1,0.98])
        self.lineas = []
        nombres = [
            "Waist",
            "Shoulder",
            "Elbow",
            "Wrist"
        ]
        for ax, nombre in zip(self.axs, nombres):
            ax.set_title(nombre)
            ax.set_ylabel("Ángulo [°]")
            ax.grid(True)

            linea, = ax.plot([],[],lw=2)
            self.lineas.append(linea)
        self.axs[-1].set_xlabel("Tiempo [s]")
        ventana.update()
        self.canvas = FigureCanvasTkAgg(self.fig, master=graficas)
        self.canvas.get_tk_widget().grid(row=4, column=0, columnspan=4, sticky="nsew", padx=5)
        self.canvas.draw()

        self.ang_ref = [
            [],[],[],[]
        ]


    def ir_inter_cub(self, x1, y1, z1, x4, y4, z4):

        pasos = 50          # Número de puntos
        dt = 0.1            # Tiempo entre puntos (100 ms)

        self.t_data = []

        self.ang_data = [
            [],
            [],
            [],
            [],
        ]

        self.status_var.set("Interpolación cúbica comenzando.")

        self.call_home

        # Parámetro de diseño: altura máxima del arco
        altura_arco = 0.02 

        # Cómputo automático de los puntos de control (P2 y P3)
        # Dividimos la distancia en X e Y en tercios, y elevamos el eje Z
        x2, y2, z2 = x1 + (x4 - x1)/3, y1 + (y4 - y1)/3, max(z1, z4) + altura_arco
        x3, y3, z3 = x1 + 2*(x4 - x1)/3, y1 + 2*(y4 - y1)/3, max(z1, z4) + altura_arco

        time.sleep(5)

        for i in range(pasos + 1):

            # Permitir que ROS procese mensajes
            rclpy.spin_once(self.node, timeout_sec=0)

            # Parámetro normalizado
            u = i / pasos

            # Interpolación cúbica
            s = 3*u**2 - 2*u**3

            # Ecuaciones de Bézier Cúbico 3D
            x = (1-s)**3 * x1 + 3*(1-s)**2 * s * x2 + 3*(1-s) * s**2 * x3 + s**3 * x4
            y = (1-s)**3 * y1 + 3*(1-s)**2 * s * y2 + 3*(1-s) * s**2 * y3 + s**3 * y4
            z = (1-s)**3 * z1 + 3*(1-s)**2 * s * z2 + 3*(1-s) * s**2 * z3 + s**3 * z4

            # Punto cartesiano
            #x = x1 + s * (x2 - x1)
            #y = y1 + s * (y2 - y1)
            #z = z1 + s * (z2 - z1)

            # Cinemática inversa
            soluciones = cinematica_inversa(x, y, z, 0)

            if not soluciones:
                print(f"Sin solución para el punto {i}")
                continue

            q = soluciones[0]

            # Publicar al robot
            valores = [
                q[0],
                q[1],
                q[2],
                q[3],
                1
            ]

            self.node.publish_joint_command(
                self.joint_names,
                valores
            )

            # -------- Graficar --------

            self.t_data.append(i * dt)

            for n in range(4):
                self.ang_data[n].append(q[n])
                self.lineas[n].set_data(
                    self.t_data,
                    self.ang_data[n]
                )

            for ax in self.axs:
                ax.relim()
                ax.autoscale_view()

            self.canvas.draw_idle()
            self.root.update_idletasks()
            self.root.update()
 
            # --------------------------

            time.sleep(dt)

            self.status_var.set("Interpolación cúbica finalizada.")
        
        self.call_home
        time.sleep(5)

    # =====================================================
    # Trayectoria sinusoidal de una articulación
    # ===================================================== 

    def sinusoidal_motion(self):

        self.status_var.set(
            "Movimiento senoidal seleccionado."
        )
        ventana = tk.Toplevel(self.root)
        ventana.title("Trayectoria sinusoidal")
        ventana.geometry("700x350")

        self.amplitud = tk.DoubleVar(value=10.0)
        self.frecuencia = tk.DoubleVar(value=0.5)

        frame = ttk.LabelFrame(ventana,text="Movimiento Senoidal",padding=10)
        frame.pack(fill="x", padx=12, pady=(0,8))

        ttk.Label(frame, text="Amplitud").grid(row=0,column=0)

        ttk.Entry(
            frame,
            textvariable=self.amplitud,
            width=8
        ).grid(row=1,column=0)

        ttk.Label(frame, text="Frecuencia").grid(row=0,column=1)

        ttk.Entry(
            frame,
            textvariable=self.frecuencia,
            width=8
        ).grid(row=1,column=1)

        ttk.Button(
            frame,
            text='INICIAR',
            command=lambda: self.call_SINU(self.amplitud.get(),self.frecuencia.get())
        ).grid(row=3, column=0, padx=4)

        self.t_data = []
        self.ang_data = []
        self.ang_data_real = []

        self.fig, self.ax = plt.subplots(figsize=(5,3))
        self.line, = self.ax.plot([], [], lw=2)
        self.line_real, = self.ax.plot([], [], lw=2)

        self.ax.set_title("Ángulo vs Tiempo")
        self.ax.set_xlabel("Tiempo [s]")
        self.ax.set_ylabel("Ángulo [°]")
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=ventana)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.error_max_var = tk.StringVar(value="0.00 °")   
        self.mse_var = tk.StringVar(value="0.00 (°)²")

        ttk.Label(frame, text="Error máximo:").grid(row=0, column=4, sticky="w")
        ttk.Label(frame, textvariable=self.error_max_var).grid(row=1, column=4, sticky="w")

        ttk.Label(frame, text="MSE:").grid(row=0, column=5, sticky="w")
        ttk.Label(frame, textvariable=self.mse_var).grid(row=1, column=5, sticky="w")
    
    def call_SINU(self, amplitud, frecuencia):
        # Reiniciar datos
        self.t_data.clear()
        self.ang_data.clear()
        self.ang_data_real.clear()

        # Limpiar la línea
        self.line.set_data([], [])
        self.line_real.set_data([], [])

        # Reiniciar ejes
        self.ax.relim()
        self.ax.autoscale_view()

        self.canvas.draw()

        dt = 0.02          # 20 ms
        duracion = 5.0

        inicio = time.perf_counter()
        proximo = inicio

        while True:

            ahora = time.perf_counter()
            if ahora - inicio >= duracion:
                break
            # Procesar mensajes ROS
            rclpy.spin_once(self.node, timeout_sec=0)
            t = ahora - inicio
            # Tu trayectoria
            angulo = 0 + amplitud*math.sin(2*math.pi*frecuencia*t)
            #Crea el mensaje a enviar
            valores = [
                0,
                angulo,
                0,
                0,
                0
            ]
            #Envia la pose al robot
            self.node.publish_joint_command(
                self.joint_names,
                valores
            )
            # Guardar valores
            self.t_data.append(t)
            self.ang_data.append(angulo)
            self.ang_data_real.append(self.node.current_positions.get("shoulder", 0.0))
            # Actualiza la grafica
            self.line.set_data(self.t_data, self.ang_data)
            self.line_real.set_data(self.t_data, self.ang_data_real)

            self.ax.relim()
            self.ax.autoscale_view()

            self.canvas.draw_idle()
            proximo += dt
            while time.perf_counter() < proximo:
                pass
        # Calcular el error en cada muestra
        errores = [
            ref - real
            for ref, real in zip(self.ang_data, self.ang_data_real)
        ]

        # Error máximo absoluto
        error_max = max(abs(e) for e in errores)

        # Error cuadrático medio (RMSE)
        mse = sum(e**2 for e in errores) / len(errores)
        self.error_max_var.set(f"{error_max:.2f} °")
        self.mse_var.set(f"{mse:.2f} (°)²")


    # =====================================================
    # Cinemática
    # ===================================================== 

    def forward_kinematics(self):

        from .cinematica_gui import CinematicaGUI

        self.cinematica_window = CinematicaGUI(
            self.node
        )

    # =====================================================
    #  Enseñanza y repetición de poses
    # ===================================================== 

    def abrir_ensenanza(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Modo Enseñanza")
        ventana.geometry("700x350")

        teach_frame = ttk.LabelFrame(ventana,text="Controles",padding=10)
        teach_frame.pack(fill="x", padx=12, pady=(0,8))
        ttk.Button(
            teach_frame,
            text='GUARDAR',
            command=self.call_enseñ
        ).grid(row=0, column=0, padx=4)
        ttk.Button(
            teach_frame,
            text='REPRODUCIR',
            command=self.call_reproducir
        ).grid(row=1, column=0, padx=4)
        ttk.Button(
            teach_frame,
            text='DETENER',
            command=self.call_detener
        ).grid(row=2, column=0, padx=4)

        results_frame = ttk.LabelFrame(ventana,text="Resultados de calibración",padding=10)
        results_frame.pack(fill="x", padx=12, pady=(0,8))

        self.position_table = ttk.Treeview(
            teach_frame,
            columns=("joint", "actual"),
            show="headings",
            height=5
        )
        self.position_table.grid(row=0, column=3,rowspan=3, sticky="nsew", pady=5)
        self.position_table.heading("joint", text="Articulación")
        self.position_table.heading("actual", text="Posición actual (°)")

        self.poses_table = ttk.Treeview(
            teach_frame,
            columns=("poses"),
            show="headings",
            height=5
        )
        self.poses_table.grid(row=0,column=1, rowspan=3,columnspan=1,sticky="ew",pady=5)
        self.poses_table.heading("poses", text="Poses")
        self.actualizar_tabla_poses()

    def call_enseñ(self) -> None:
        for name in self.joint_names:
            self._entry_committed(name)
        nombre = simpledialog.askstring(
            "Guardar pose",
            "Ingrese el nombre de la pose:"
        )
        if nombre is None:
            return  
        if nombre.strip() == "":
            messagebox.showwarning(
                "Nombre inválido",
                "Debe ingresar un nombre."
            )
            return
        with open(self.yaml_file,"r") as f:
            datos = yaml.safe_load(f)
        if datos is None:
            datos = {"poses": []}
            with open(self.yaml_file, "w") as f:
                yaml.dump(datos, f, sort_keys=False)
        nueva_pose = {
            "nombre": nombre,
            "waist": self.node.current_positions["waist"],
            "shoulder": self.node.current_positions["shoulder"],
            "elbow": self.node.current_positions["elbow"],
            "wrist": self.node.current_positions["wrist"],
            "gripper": self.node.current_positions["gripper"],
        }
        datos["poses"].insert(0, nueva_pose)
        datos["poses"] = datos["poses"][:8]
        with open(self.yaml_file, "w") as f:
            yaml.dump(datos, f, sort_keys=False)
        self.actualizar_tabla_poses()
    
    def actualizar_tabla_poses(self):
        # Borra todas las filas
        for fila in self.poses_table.get_children():
            self.poses_table.delete(fila)
        # Lee el archivo YAML
        with open(self.yaml_file, "r") as f:
            datos = yaml.safe_load(f)
        if datos is None:
            return
        # Inserta las poses
        for pose in datos["poses"]:
            self.poses_table.insert(
                "",
                "end",
                values=(pose["nombre"],)
        )
    
    def call_reproducir(self):
        self.reproduciendo = True
        with open(self.yaml_file, "r") as f:
            datos = yaml.safe_load(f)
        if datos is None or "poses" not in datos:
            messagebox.showwarning(
                "Sin poses",
                "No hay poses almacenadas."
            )
            return
            # Recorre desde la última hasta la primera
        for pose in reversed(datos["poses"]):
             # Si se presionó detener, salir inmediatamente
            if not self.reproduciendo:
                break
            valores = [
                pose["waist"],
                pose["shoulder"],
                pose["elbow"],
                pose["wrist"],
                pose["gripper"]
            ]
            #Envia la pose al robot
            self.node.publish_joint_command(
                self.joint_names,
                valores
            )
            # tiempo entre poses
            espera = 5
            inicio = time.time()
            while time.time() - inicio < espera:
                if not self.reproduciendo:
                    return
                self.root.update()
                time.sleep(0.05)
        self.reproduciendo = False
        self.status_var.set("Reproducción finalizada.")

    def call_detener(self):
        self.reproduciendo = False
        self.status_var.set("Reproducción detenida.")
    
    # =====================================================
    #  Dibujo
    # ===================================================== 

    def dibujar_cuadrado(self):

        # -------------------------
        # Parámetros
        # -------------------------

        lado = 0.05            # 5 cm
        puntos_lado = 50       # cantidad de puntos por lado
        theta = -90            # orientación constante
        dt = 0.1                 # tiempo entre puntos

        # Primera esquina (la que ya verificaste)

        p1 = np.array([
            0.0000,
            0.1996,
            0.1100
        ])

        # Esquinas del cuadrado

        p2 = p1 + np.array([0.00, lado, 0.00])
        p3 = p2 + np.array([-lado, 0.00, 0.00])
        p4 = p1 + np.array([-lado, 0.00, 0.00])

        lados = [
            (p1,p2),
            (p2,p3),
            (p3,p4),
            (p4,p1)
        ]

        # configuración inicial

        q_inicio = [90, -17.01, -117.96, 44.97, 0]

        # Actualizar sliders
        for nombre, valor in zip(self.joint_names, q_inicio):
            self.variables[nombre].set(valor)
            self._scale_changed(nombre, str(valor))

        # Enviar al robot
        self.node.publish_joint_command(
            self.joint_names,
            q_inicio
        )

        # Esperar 2 segundos
        self.root.update()
        time.sleep(5)

        # La configuración actual será la inicial
        q_actual = q_inicio[:4]

        # ----------------------------------------
        # Recorrer los cuatro lados
        # ----------------------------------------

        for inicio, fin in lados:

            for alpha in np.linspace(0,1,puntos_lado):

                punto = inicio + alpha*(fin-inicio)

                x = punto[0]
                y = punto[1]
                z = punto[2]

                soluciones = cinematica_inversa(
                    x,
                    y,
                    z,
                    theta
                )

                if soluciones is None or len(soluciones)==0:
                    print(f"Punto no alcanzable: {x:.3f} {y:.3f} {z:.3f}")
                    continue

                q = elegir_solucion_cercana(
                    soluciones,
                    q_actual
                )

                if q is None:
                    continue

                q_actual = q

                posiciones = [
                    float(q[0]),
                    float(q[1]),
                    float(q[2]),
                    float(q[3]),
                    0.0
                ]

                # Actualizar sliders

                for nombre,valor in zip(
                    self.joint_names,
                    posiciones
                ):
                    self.variables[nombre].set(valor)
                    self._scale_changed(nombre,str(valor))

                # Enviar al robot

                self.node.publish_joint_command(
                    self.joint_names,
                    posiciones
                )

                self.root.update()

                time.sleep(dt)

        print("Cuadrado terminado.")

        time.sleep(2)

        valores = [
                    0,
                    0,
                    0,
                    0,
                    0
                ]
        
        self.node.publish_joint_command(
            self.joint_names,
            valores
        )
        
    # =====================================================
    #  Baile
    # ===================================================== 

    def baile(self):

        valores = [
            0,
            0,
            0,
            0,
            0
        ]

        self.node.publish_joint_command(
            self.joint_names,
            valores
        )

        time.sleep(1)

        valores = [
            90,
            0,
            0,
            0,
            0
        ]

        self.node.publish_joint_command(
            self.joint_names,
            valores
        )
        
        time.sleep(1)

        valores = [
           -90,
            0,
            0,
            0,
            0
        ]

        self.node.publish_joint_command(
            self.joint_names,
            valores
        )

        time.sleep(1)


        duracion = 4
        dt = 0.01
        periodo_base = 6.0      # segundos para ir de 150 a -150 y volver

        t = 0.0


        # -------------------------------
        # Rutina principal
        # -------------------------------

        while t <= duracion:

            base = -90

            f = 0.5

            shoulder = 10 * math.sin(2 * math.pi * 2 * f * t)

            elbow = 15 * math.sin(2 * math.pi * 2 * f * t + math.pi/4)

            wrist = 15 * math.sin(2 * math.pi * f * t + math.pi/2)

            gripper = 0

            valores = [
                base,
                shoulder,
                elbow,
                wrist,
                gripper
            ]

            # Actualiza sliders
            for nombre, valor in zip(self.joint_names, valores):
                self.variables[nombre].set(valor)
                self._scale_changed(nombre, str(valor))

            # Envía al robot
            self.node.publish_joint_command(
                self.joint_names,
                valores
            )

            self.root.update()

            time.sleep(dt)

            t += dt

        # -------------------------------
        # Regreso suave a HOME
        # -------------------------------

        pasos = 40

        base_ini = base
        shoulder_ini = shoulder
        elbow_ini = elbow
        wrist_ini = wrist
        gripper_ini = gripper

        for i in range(pasos):

            alpha = (i + 1) / pasos

            valores = [

                base_ini * (1-alpha),

                shoulder_ini * (1-alpha),

                elbow_ini * (1-alpha),

                wrist_ini * (1-alpha),

                gripper_ini * (1-alpha)

            ]

            for nombre, valor in zip(self.joint_names, valores):
                self.variables[nombre].set(valor)
                self._scale_changed(nombre, str(valor))

            self.node.publish_joint_command(
                self.joint_names,
                valores
            )

            self.root.update()


            time.sleep(dt)

        duracion = 9.0
        dt = 0.01
        periodo_base = 6.0      # segundos para ir de 150 a -150 y volver

        t = 0.0


        # -------------------------------
        # Rutina principal
        # -------------------------------

        while t <= duracion:

            # ---------- BASE ----------
            fase = (t % periodo_base) / periodo_base

            if fase < 0.5:
                base = 150 - 600*fase
            else:
                base = -150 + 600*(fase-0.5)

            # ---------- OTRAS ARTICULACIONES ----------

            shoulder = 0

            elbow = 20 * math.sin(2 * math.pi * 1 * t)

            wrist = 0

            gripper = 30 * math.sin(2 * math.pi * 1 * t)

            valores = [
                base,
                shoulder,
                elbow,
                wrist,
                gripper
            ]

            # Actualiza sliders
            for nombre, valor in zip(self.joint_names, valores):
                self.variables[nombre].set(valor)
                self._scale_changed(nombre, str(valor))

            # Envía al robot
            self.node.publish_joint_command(
                self.joint_names,
                valores
            )

            self.root.update()

            time.sleep(dt)

            t += dt

        # -------------------------------
        # Regreso suave a HOME
        # -------------------------------

        pasos = 40

        base_ini = base
        shoulder_ini = shoulder
        elbow_ini = elbow
        wrist_ini = wrist
        gripper_ini = gripper

        for i in range(pasos):

            alpha = (i + 1) / pasos

            valores = [

                base_ini * (1-alpha),

                shoulder_ini * (1-alpha),

                elbow_ini * (1-alpha),

                wrist_ini * (1-alpha),

                gripper_ini * (1-alpha)

            ]

            for nombre, valor in zip(self.joint_names, valores):
                self.variables[nombre].set(valor)
                self._scale_changed(nombre, str(valor))

            self.node.publish_joint_command(
                self.joint_names,
                valores
            )

            self.root.update()


            time.sleep(dt)

        duracion = 9.0
        dt = 0.01
        periodo_base = 6.0      # segundos para ir de 150 a -150 y volver

        t = 0.0


        # -------------------------------
        # Rutina principal
        # -------------------------------

        while t <= duracion:

            # ---------- BASE ----------
            fase = (t % periodo_base) / periodo_base

            if fase < 0.5:
                base = 150 - 600*fase
            else:
                base = -150 + 600*(fase-0.5)
            # ---------- OTRAS ARTICULACIONES ----------

            shoulder = 0

            elbow = -30

            wrist = 45 + 20 * math.sin(2 * math.pi * 2 * t)

            gripper = 30* math.sin(2 * math.pi * 1 * t)

            valores = [
                base,
                shoulder,
                elbow,
                wrist,
                gripper
            ]

            # Actualiza sliders
            for nombre, valor in zip(self.joint_names, valores):
                self.variables[nombre].set(valor)
                self._scale_changed(nombre, str(valor))

            # Envía al robot
            self.node.publish_joint_command(
                self.joint_names,
                valores
            )

            self.root.update()

            time.sleep(dt)

            t += dt

        # -------------------------------
        # Regreso suave a HOME
        # -------------------------------

        pasos = 40

        base_ini = base
        shoulder_ini = shoulder
        elbow_ini = elbow
        wrist_ini = wrist
        gripper_ini = gripper

        for i in range(pasos):

            alpha = (i + 1) / pasos

            valores = [

                base_ini * (1-alpha),

                shoulder_ini * (1-alpha),

                elbow_ini * (1-alpha),

                wrist_ini * (1-alpha),

                gripper_ini * (1-alpha)

            ]

            for nombre, valor in zip(self.joint_names, valores):
                self.variables[nombre].set(valor)
                self._scale_changed(nombre, str(valor))

            self.node.publish_joint_command(
                self.joint_names,
                valores
            )

            self.root.update()


            time.sleep(dt)

        duracion = 4
        dt = 0.01
        periodo_base = 3.0      # segundos para ir de 150 a -150 y volver

        t = 0.0


        # -------------------------------
        # Rutina principal
        # -------------------------------

        while t <= duracion:


            f = 2

            base = 20 * math.cos(2*math.pi*f*t)

            # ---------- OTRAS ARTICULACIONES -

            shoulder = 0

            elbow = 0

            wrist = 90

            gripper = 0

            valores = [
                base,
                shoulder,
                elbow,
                wrist,
                gripper
            ]

            # Actualiza sliders
            for nombre, valor in zip(self.joint_names, valores):
                self.variables[nombre].set(valor)
                self._scale_changed(nombre, str(valor))

            # Envía al robot
            self.node.publish_joint_command(
                self.joint_names,
                valores
            )

            self.root.update()

            time.sleep(dt)

            t += dt

        # -------------------------------
        # Regreso suave a HOME
        # -------------------------------

        pasos = 40

        base_ini = base
        shoulder_ini = shoulder
        elbow_ini = elbow
        wrist_ini = wrist
        gripper_ini = gripper

        for i in range(pasos):

            alpha = (i + 1) / pasos

            valores = [

                base_ini * (1-alpha),

                shoulder_ini * (1-alpha),

                elbow_ini * (1-alpha),

                wrist_ini * (1-alpha),

                gripper_ini * (1-alpha)

            ]

            for nombre, valor in zip(self.joint_names, valores):
                self.variables[nombre].set(valor)
                self._scale_changed(nombre, str(valor))

            self.node.publish_joint_command(
                self.joint_names,
                valores
            )

            self.root.update()


            time.sleep(dt)

    

        self.status_var.set("Baile finalizado.")
   


def main(args=None) -> None:
    rclpy.init(args=args)
    node = PincherGuiNode()
    gui = PincherGui(node)
    try:
        gui.run()
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()