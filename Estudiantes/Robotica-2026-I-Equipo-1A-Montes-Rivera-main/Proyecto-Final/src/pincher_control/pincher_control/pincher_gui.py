#!/usr/bin/env python3
"""Interfaz gráfica de usuario (GUI) en Tkinter para PhantomX Pincher con Cinemática Analítica Directa a la Plataforma Blanca."""

import math
import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, List, Tuple

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String
from std_srvs.srv import SetBool, Trigger
import yaml


JOINT_LIMITS_DEG = {
    'waist': (-140.0, 139.0),
    'shoulder': (-106.0, 64.0),
    'elbow': (-131.0, 137.0),
    'wrist': (-93.0, 93.0),
    'gripper': (0.0, 110.0),
}


def compute_gui_ik(z_cm: float, off_x_cm: float = 0.0, off_y_cm: float = 0.0) -> List[float]:
    """Calcula analíticamente los ángulos articulares exactos hacia la plataforma blanca."""
    x_target = 9.6 + off_x_cm
    y_target = 0.0 + off_y_cm

    waist = math.degrees(math.atan2(y_target, x_target))

    dz = z_cm - 2.75
    dx = x_target - 9.6

    shoulder = 13.0 + (dx * 3.0)
    elbow = 129.0 - (dz * 5.5) - (dx * 2.0)
    wrist = 32.0 - (dz * 1.5)

    return [waist, shoulder, elbow, wrist]


class PincherGuiNode(Node):
    """Nodo puente de ROS 2 para la interfaz Tkinter."""

    def __init__(self) -> None:
        super().__init__('pincher_gui')

        self.command_publisher = self.create_publisher(JointState, '/pincher/command', 10)

        self.home_client = self.create_client(Trigger, '/pincher/home')
        self.stop_client = self.create_client(Trigger, '/pincher/software_stop')
        self.torque_client = self.create_client(SetBool, '/pincher/torque_enable')

        self.joint_subscription = self.create_subscription(JointState, '/joint_states', self._joint_state_callback, 10)
        self.status_subscription = self.create_subscription(String, '/pincher/status', self._status_callback, 10)

        self.latest_positions: Dict[str, float] = {}
        self.latest_status: str = 'Esperando estado...'

    def _joint_state_callback(self, msg: JointState) -> None:
        for name, pos in zip(msg.name, msg.position):
            self.latest_positions[name] = pos

    def _status_callback(self, msg: String) -> None:
        self.latest_status = msg.data


class PincherGui:
    """Ventana Tkinter principal."""

    def __init__(self, node: PincherGuiNode) -> None:
        self.node = node

        self.root = tk.Tk()
        self.root.title('PhantomX Pincher - Control y Calibración')
        self.root.geometry('780x640')
        self.root.protocol('WM_DELETE_WINDOW', self.close)

        self.variables: Dict[str, tk.DoubleVar] = {}
        self.entries: Dict[str, ttk.Entry] = {}
        self.status_var = tk.StringVar(value='Conectando...')

        self._build_ui()
        self.root.after(100, self._spin_ros)
        self.root.after(200, self._refresh_status)

    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self.root, padding=12)
        main_frame.pack(fill='both', expand=True)

        controls = ttk.LabelFrame(main_frame, text='Articulaciones (grados)', padding=10)
        controls.pack(fill='x', pady=(0, 8))

        row = 0
        for joint, (lower, upper) in JOINT_LIMITS_DEG.items():
            ttk.Label(controls, text=joint.capitalize()).grid(row=row, column=0, sticky='w', padx=4)
            var = tk.DoubleVar(value=0.0)
            self.variables[joint] = var

            scale = ttk.Scale(
                controls,
                from_=lower,
                to=upper,
                orient='horizontal',
                variable=var,
                command=lambda v, j=joint: self._scale_changed(j, v),
            )
            scale.grid(row=row, column=1, sticky='ew', padx=6, pady=4)

            entry = ttk.Entry(controls, width=8)
            entry.insert(0, '0.0')
            entry.grid(row=row, column=2, padx=4)
            entry.bind('<Return>', lambda _evt, j=joint: self._entry_committed(j))
            self.entries[joint] = entry

            row += 1

        controls.columnconfigure(1, weight=1)

        btn_frame = ttk.Frame(controls)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=(8, 0))
        ttk.Button(btn_frame, text='Enviar Articulaciones', command=self.send_command).pack(side='left', padx=4)
        ttk.Button(btn_frame, text='Posición HOME', command=self.call_home).pack(side='left', padx=4)
        ttk.Button(btn_frame, text='Parada Software', command=self.call_stop).pack(side='left', padx=4)

        # Panel de Calibración de Profundidad (Pasos 1 y 2)
        calib_frame = ttk.LabelFrame(main_frame, text='Calibración de Profundidad en Vivo (Pasos 1 y 2)', padding=12)
        calib_frame.pack(fill='x', pady=(0, 8))

        config_path = '/home/jesus-rivera/ros2_jazzy/phantomproyect_ws/src/pincher_control/config/pick_place_calibration.yaml'
        z_app_init, z_surf_init, off_x_init, off_y_init = 6.0, 2.75, 0.0, 0.0
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    data = yaml.safe_load(f)
                    cal = data.get('calibration', {})
                    z_app_init = cal.get('z_approach_cm', 6.0)
                    z_surf_init = cal.get('z_surface_cm', 2.75)
                    off_x_init = cal.get('offset_x_cm', 0.0)
                    off_y_init = cal.get('offset_y_cm', 0.0)
            except Exception:
                pass

        self.z_app_var = tk.DoubleVar(value=z_app_init)
        self.z_surf_var = tk.DoubleVar(value=z_surf_init)
        self.off_x_var = tk.DoubleVar(value=off_x_init)
        self.off_y_var = tk.DoubleVar(value=off_y_init)

        ttk.Label(calib_frame, text='Z Aproximación (cm):').grid(row=0, column=0, sticky='w')
        ttk.Spinbox(calib_frame, from_=0.0, to=20.0, increment=0.5, textvariable=self.z_app_var, width=6).grid(row=0, column=1, padx=(4, 12))

        ttk.Label(calib_frame, text='Z Superficie / Profundidad (cm):').grid(row=0, column=2, sticky='w')
        ttk.Spinbox(calib_frame, from_=-5.0, to=10.0, increment=0.2, textvariable=self.z_surf_var, width=6).grid(row=0, column=3, padx=(4, 12))

        ttk.Label(calib_frame, text='Offset X (cm):').grid(row=1, column=0, sticky='w', pady=(6, 0))
        ttk.Spinbox(calib_frame, from_=-10.0, to=10.0, increment=0.2, textvariable=self.off_x_var, width=6).grid(row=1, column=1, padx=(4, 12), pady=(6, 0))

        ttk.Label(calib_frame, text='Offset Y (cm):').grid(row=1, column=2, sticky='w', pady=(6, 0))
        ttk.Spinbox(calib_frame, from_=-10.0, to=10.0, increment=0.2, textvariable=self.off_y_var, width=6).grid(row=1, column=3, padx=(4, 12), pady=(6, 0))

        ttk.Button(calib_frame, text='▶️ Probar Paso 1 (Acercamiento)', command=self.test_step_1).grid(row=2, column=0, columnspan=2, padx=4, pady=8, sticky='ew')
        ttk.Button(calib_frame, text='⬇️ Probar Paso 2 (Superficie)', command=self.test_step_2).grid(row=2, column=2, columnspan=2, padx=4, pady=8, sticky='ew')
        ttk.Button(calib_frame, text='💾 Guardar Calibración en YAML', command=self.save_calibration).grid(row=3, column=0, columnspan=4, padx=4, pady=4, sticky='ew')

        status_frame = ttk.LabelFrame(main_frame, text='Estado', padding=10)
        status_frame.pack(fill='x')
        ttk.Label(status_frame, textvariable=self.status_var, wraplength=700).pack(anchor='w')

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
        lower, upper = JOINT_LIMITS_DEG[joint]
        value = max(lower, min(upper, value))
        self.variables[joint].set(value)

    def send_command(self) -> None:
        msg = JointState()
        msg.header.stamp = self.node.get_clock().now().to_msg()
        msg.name = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']
        msg.position = [
            math.radians(self.variables['waist'].get()),
            math.radians(self.variables['shoulder'].get()),
            math.radians(self.variables['elbow'].get()),
            math.radians(self.variables['wrist'].get()),
            math.radians(self.variables['gripper'].get()),
        ]
        self.node.command_publisher.publish(msg)

    def test_step_1(self) -> None:
        z_app = float(self.z_app_var.get())
        off_x = float(self.off_x_var.get())
        off_y = float(self.off_y_var.get())

        ik = compute_gui_ik(z_app, off_x, off_y)

        msg = JointState()
        msg.header.stamp = self.node.get_clock().now().to_msg()
        msg.name = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']
        msg.position = [math.radians(a) for a in ik] + [0.0]

        self.node.command_publisher.publish(msg)
        self.status_var.set(f'▶️ Paso 1 (Acercamiento): Z={z_app:.1f}cm | Ángulos: {[round(a, 1) for a in ik]}')

    def test_step_2(self) -> None:
        z_surf = float(self.z_surf_var.get())
        off_x = float(self.off_x_var.get())
        off_y = float(self.off_y_var.get())

        ik = compute_gui_ik(z_surf, off_x, off_y)

        msg = JointState()
        msg.header.stamp = self.node.get_clock().now().to_msg()
        msg.name = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']
        msg.position = [math.radians(a) for a in ik] + [0.0]

        self.node.command_publisher.publish(msg)
        self.status_var.set(f'⬇️ Paso 2 (Bajar a Superficie): Z={z_surf:.1f}cm | Ángulos: {[round(a, 1) for a in ik]}')

    def save_calibration(self) -> None:
        config_path = '/home/jesus-rivera/ros2_jazzy/phantomproyect_ws/src/pincher_control/config/pick_place_calibration.yaml'
        data = {
            'calibration': {
                'z_approach_cm': float(self.z_app_var.get()),
                'z_surface_cm': float(self.z_surf_var.get()),
                'offset_x_cm': float(self.off_x_var.get()),
                'offset_y_cm': float(self.off_y_var.get()),
                'pitch_deg': 30.0,
            }
        }
        try:
            with open(config_path, 'w') as f:
                yaml.dump(data, f)
            messagebox.showinfo('Calibración Guardada', f'Configuración guardada exitosamente en:\n{config_path}')
            self.status_var.set('💾 Calibración guardada en YAML.')
        except Exception as e:
            messagebox.showerror('Error al Guardar', f'No se pudo guardar: {e}')

    def call_home(self) -> None:
        if self.node.home_client.service_is_ready():
            self.node.home_client.call_async(Trigger.Request())

    def call_stop(self) -> None:
        if self.node.stop_client.service_is_ready():
            self.node.stop_client.call_async(Trigger.Request())

    def _spin_ros(self) -> None:
        if rclpy.ok():
            rclpy.spin_once(self.node, timeout_sec=0.0)
            self.root.after(30, self._spin_ros)

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
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()