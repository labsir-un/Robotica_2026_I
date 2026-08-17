#!/usr/bin/env python3
"""Interfaz punto 4 laboratorio - Movimiento individual PhantomX Pincher."""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk, messagebox

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState
from std_msgs.msg import UInt32, String
from std_srvs.srv import Trigger, SetBool


JOINT_LIMITS = {
    "waist": (-150, 150),
    "shoulder": (-150, 150),
    "elbow": (-150, 150),
    "wrist": (-150, 150),
    "gripper": (-90, 90),
}


class PincherNode(Node):

    def __init__(self):

        super().__init__("punto4_gui")

        self.pub_command = self.create_publisher(
            JointState,
            "/pincher/command",
            10
        )

        self.pub_speed = self.create_publisher(
            UInt32,
            "/pincher/profile_velocity",
            10
        )


        self.home = self.create_client(
            Trigger,
            "/pincher/home"
        )

        self.stop = self.create_client(
            Trigger,
            "/pincher/software_stop"
        )

        self.torque = self.create_client(
            SetBool,
            "/pincher/torque_enable"
        )


        self.status = ""

        self.create_subscription(
            String,
            "/pincher/status",
            self.status_callback,
            10
        )


    def status_callback(self,msg):

        self.status = msg.data



    def send_joint(self,joint,angle):

        msg = JointState()

        msg.header.stamp = self.get_clock().now().to_msg()

        msg.name = [joint]

        msg.position = [
            math.radians(angle)
        ]

        self.pub_command.publish(msg)



    def send_speed(self,value):

        msg = UInt32()

        msg.data = int(value)

        self.pub_speed.publish(msg)




class Interface:


    def __init__(self,node):

        self.node=node

        self.root=tk.Tk()

        self.root.title(
            "Punto 4 laboratorio - Movimiento individual PhantomX Pincher"
        )

        self.root.geometry("600x450")


        self.joint=tk.StringVar(
            value="waist"
        )

        self.position=tk.DoubleVar(
            value=0
        )

        self.speed=tk.IntVar(
            value=100
        )


        self.build()


        self.root.after(
            20,
            self.spin
        )


    def build(self):


        title=ttk.Label(
            self.root,
            text="Movimiento individual de articulaciones",
            font=("Arial",16,"bold")
        )

        title.pack(pady=10)



        frame=ttk.LabelFrame(
            self.root,
            text="Selección de articulación",
            padding=10
        )

        frame.pack(
            fill="x",
            padx=15
        )


        ttk.Label(
            frame,
            text="Articulación:"
        ).grid(
            row=0,
            column=0
        )


        combo=ttk.Combobox(
            frame,
            textvariable=self.joint,
            values=list(JOINT_LIMITS.keys()),
            state="readonly"
        )

        combo.grid(
            row=0,
            column=1,
            padx=10
        )



        ttk.Label(
            frame,
            text="Posición (grados):"
        ).grid(
            row=1,
            column=0,
            pady=10
        )


        ttk.Entry(
            frame,
            textvariable=self.position
        ).grid(
            row=1,
            column=1
        )



        ttk.Button(
            frame,
            text="Enviar posición",
            command=self.send
        ).grid(
            row=2,
            column=0,
            columnspan=2,
            pady=10
        )



        speed_frame=ttk.LabelFrame(
            self.root,
            text="Velocidad",
            padding=10
        )

        speed_frame.pack(
            fill="x",
            padx=15,
            pady=10
        )



        ttk.Spinbox(
            speed_frame,
            from_=0,
            to=1023,
            textvariable=self.speed,
            width=10
        ).pack(
            side="left",
            padx=10
        )


        ttk.Button(
            speed_frame,
            text="Aplicar velocidad",
            command=self.apply_speed
        ).pack(
            side="left"
        )




        special=ttk.LabelFrame(
            self.root,
            text="Funciones especiales",
            padding=10
        )


        special.pack(
            fill="x",
            padx=15
        )



        ttk.Button(
            special,
            text="HOME",
            command=self.home
        ).pack(
            side="left",
            padx=5
        )


        ttk.Button(
            special,
            text="Torque ON",
            command=lambda:self.torque(True)
        ).pack(
            side="left",
            padx=5
        )


        ttk.Button(
            special,
            text="Torque OFF",
            command=lambda:self.torque(False)
        ).pack(
            side="left",
            padx=5
        )


        ttk.Button(
            special,
            text="PARADA SOFTWARE",
            command=self.stop
        ).pack(
            side="left",
            padx=5
        )



        self.label=ttk.Label(
            self.root,
            text="Listo"
        )

        self.label.pack(
            pady=20
        )



    def send(self):

        joint=self.joint.get()

        value=self.position.get()


        low,high=JOINT_LIMITS[joint]


        if value < low or value > high:

            messagebox.showwarning(
                "Límite",
                f"{joint} debe estar entre {low} y {high}"
            )

            return


        self.node.send_joint(
            joint,
            value
        )


        self.label.config(
            text=f"{joint} enviado a {value} grados"
        )




    def apply_speed(self):

        self.node.send_speed(
            self.speed.get()
        )


    def home(self):

        if self.node.home.service_is_ready():

            self.node.home.call_async(
                Trigger.Request()
            )


    def stop(self):

        if self.node.stop.service_is_ready():

            self.node.stop.call_async(
                Trigger.Request()
            )



    def torque(self,state):

        if self.node.torque.service_is_ready():

            req=SetBool.Request()

            req.data=state

            self.node.torque.call_async(req)




    def spin(self):

        rclpy.spin_once(
            self.node,
            timeout_sec=0
        )

        self.root.after(
            20,
            self.spin
        )



    def run(self):

        self.root.mainloop()




def main():

    rclpy.init()

    node=PincherNode()

    gui=Interface(node)


    gui.run()


    node.destroy_node()

    rclpy.shutdown()



if __name__=="__main__":

    main()
