#!/usr/bin/env python3
"""Interfaz Tkinter para enviar comandos articulares al PhantomX Pincher."""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, List

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String, UInt32
from std_srvs.srv import SetBool, Trigger

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

class PincherGui:
    """Ventana principal con sliders, entradas y controles de seguridad."""

    def __init__(self, node: PincherGuiNode) -> None:
        self.node = node
        self.root = tk.Tk()
        self.root.title('PhantomX Pincher X100 - ROS 2 Jazzy')
        self.root.minsize(760, 520)
        self.root.protocol('WM_DELETE_WINDOW', self.close)

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
        except Exception as exc:
            self.status_var.set(f'Error llamando al servicio: {exc}')

    def _spin_ros(self) -> None:
        if rclpy.ok():
            rclpy.spin_once(self.node, timeout_sec=0.0)
            self.root.after(20, self._spin_ros)

    def _refresh_status(self) -> None:
        if self.node.latest_status:
            self.status_var.set(self.node.latest_status)
        if rclpy.ok():
            self.root.after(200, self._refresh_status)

    def run(self) -> None:
        self.root.mainloop()

    def close(self) -> None:
        self.root.destroy()

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
