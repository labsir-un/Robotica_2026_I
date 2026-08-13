import tkinter as tk
import numpy as np
from tkinter import ttk

from .cinematica import (
    cinematica_directa,
    obtener_rpy,
    cinematica_inversa,
    elegir_solucion_cercana
)


class CinematicaGUI:


    def __init__(self, node):

        self.node = node
        self.q_actual=[0,0,0,0]
        self.window = tk.Toplevel()

        self.window.title(
            "Cinemática PhantomX Pincher"
        )

        self.crear_interfaz()



    def crear_interfaz(self):


        # --------------------------
        # Entrada de articulaciones
        # --------------------------

        ttk.Label(
            self.window,
            text="q1 Waist (°)"
        ).grid(row=0,column=0)


        self.q1 = ttk.Entry(
            self.window
        )

        self.q1.grid(
            row=0,
            column=1
        )



        ttk.Label(
            self.window,
            text="q2 Shoulder (°)"
        ).grid(row=1,column=0)


        self.q2 = ttk.Entry(
            self.window
        )

        self.q2.grid(
            row=1,
            column=1
        )



        ttk.Label(
            self.window,
            text="q3 Elbow (°)"
        ).grid(row=2,column=0)


        self.q3 = ttk.Entry(
            self.window
        )

        self.q3.grid(
            row=2,
            column=1
        )



        ttk.Label(
            self.window,
            text="q4 Wrist (°)"
        ).grid(row=3,column=0)


        self.q4 = ttk.Entry(
            self.window
        )

        self.q4.grid(
            row=3,
            column=1
        )


        ttk.Label(
            self.window,
            text="X"
        ).grid(row=0,column=5)


        self.x_entry=ttk.Entry(
            self.window
        )

        self.x_entry.grid(
            row=0,
            column=6
        )

        ttk.Label(
            self.window,
            text="Y"
        ).grid(row=1,column=5)


        self.y_entry=ttk.Entry(
            self.window
        )

        self.y_entry.grid(
            row=1,
            column=6
        )


        ttk.Label(
            self.window,
            text="Z"
        ).grid(row=2,column=5)


        self.z_entry=ttk.Entry(
            self.window
        )

        self.z_entry.grid(
            row=2,
            column=6
        )

        ttk.Label(
            self.window,
            text="Theta"
        ).grid(row=3,column=5)


        self.tita_entry=ttk.Entry(
            self.window
        )

        self.tita_entry.grid(
            row=3,
            column=6
        )



        # --------------------------
        # Botón calcular
        # --------------------------

        ttk.Button(
            self.window,
            text="Calcular",
            command=self.calcular
        ).grid(
            row=4,
            column=0,
            columnspan=2
        )

        # --------------------------
        # Botón mover robot
        # --------------------------

        ttk.Button(
            self.window,
            text="Mover robot",
            command=self.mover_robot
        ).grid(
            row=6,
            column=0,
            columnspan=2
        )

        # --------------------------
        # Botón calcular inversa
        # --------------------------

        ttk.Button(
            self.window,
            text="Calcular inversa",
            command=self.calcular_inversa
        ).grid(
            row=4,
            column=5,
            columnspan=2
        )


        # --------------------------
        # Resultado
        # --------------------------

        self.resultado = ttk.Label(
            self.window,
            text=""
        )

        self.resultado.grid(
            row=5,
            column=0,
            columnspan=2
        )

    def calcular(self):


        q=[
            float(self.q1.get()),
            float(self.q2.get()),
            float(self.q3.get()),
            float(self.q4.get())
        ]

        self.q_actual = q

        # Cinemática directa

        T = cinematica_directa(q)


        # Posición

        x=T[0,3]
        y=T[1,3]
        z=T[2,3]


        # Orientación

        roll,pitch,yaw=obtener_rpy(T)



        texto=f"""


Posición:

x = {x:.4f} m
y = {y:.4f} m
z = {z:.4f} m


Orientación:

Roll  = {roll:.2f}°
Pitch = {pitch:.2f}°
Yaw   = {yaw:.2f}°

"""


        self.resultado.config(
            text=texto
        )

    def mover_robot(self):

        if not hasattr(self,"q_actual"):
            print("Primero calcule una posición")
            return


        nombres=[
            "waist",
            "shoulder",
            "elbow",
            "wrist",
            "gripper"
        ]


        posiciones=[
            self.q_actual[0],
            self.q_actual[1],
            self.q_actual[2],
            self.q_actual[3],
            0
        ]

        self.node.publish_joint_command(
            nombres,
            posiciones
        )
    
    def calcular_inversa(self):


        x=float(self.x_entry.get())
        y=float(self.y_entry.get())
        z=float(self.z_entry.get())
        theta=float(self.tita_entry.get())


        self.soluciones=cinematica_inversa(
            x,y,z,theta
        )

        soluciones=self.soluciones

        if soluciones is None or len(soluciones)==0:

            self.resultado.config(
                text="Punto no alcanzable o sin soluciones válidas"
            )

            return

        mejor = elegir_solucion_cercana(
            self.soluciones,
            self.q_actual
        )

        self.q_actual=mejor

        texto=""


        for i, sol in enumerate(soluciones):

            texto += f"\nSolución {i+1}\n"

            texto += f"q1 = {sol[0]:.2f}°\n"
            texto += f"q2 = {sol[1]:.2f}°\n"
            texto += f"q3 = {sol[2]:.2f}°\n"
            texto += f"q4 = {sol[3]:.2f}°\n"


        texto += "\nSolución seleccionada:\n"

        texto += f"q1 = {self.q_actual[0]:.2f}°\n"
        texto += f"q2 = {self.q_actual[1]:.2f}°\n"
        texto += f"q3 = {self.q_actual[2]:.2f}°\n"
        texto += f"q4 = {self.q_actual[3]:.2f}°\n"

        self.resultado.config(
            text=texto
        )