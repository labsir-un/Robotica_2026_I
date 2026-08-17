#!/usr/bin/env python3

import rclpy
import yaml
import os
import time
import threading
import math
from rclpy.node import Node
from sensor_msgs.msg import JointState


JOINT_NAMES = [
    "waist",
    "shoulder",
    "elbow",
    "wrist",
    "gripper"
]

YAML_FILE = "poses.yaml"


class TeachRepeat(Node):

    def __init__(self):

        super().__init__("teach_repeat")

        self.publisher = self.create_publisher(
            JointState,
            "/pincher/command",
            10
        )

        self.subscription = self.create_subscription(
            JointState,
            "/joint_states",
            self.joint_callback,
            10
        )

        self.current = [0.0] * 5

        self.duration = 3.0

        self.stop_requested = False

        self.playing = False

        self.poses = {}

        self.load_yaml()


    ###########################################################
    # CALLBACK
    ###########################################################

    def joint_callback(self, msg):

        self.current = list(msg.position)

    
    ###########################################################
    # PUBLICAR
    ###########################################################

    def publish(self, q):

        msg = JointState()

        msg.header.stamp = self.get_clock().now().to_msg()

        msg.name = JOINT_NAMES

        msg.position = q

        self.publisher.publish(msg)


    ###########################################################
    # YAML
    ###########################################################

    def load_yaml(self):

        if not os.path.exists(YAML_FILE):

            self.poses = {}

            return

        with open(YAML_FILE, "r") as f:

            data = yaml.safe_load(f)

        if data is None:

            self.poses = {}

        else:

            self.poses = data.get("poses", {})


    def save_yaml(self):

        data = {

            "poses": self.poses

        }

        with open(YAML_FILE, "w") as f:

            yaml.dump(
                data,
                f,
                default_flow_style=False,
                sort_keys=False
            )


    ###########################################################
    # GUARDAR
    ###########################################################

    def save_pose(self, name):

        rclpy.spin_once(self, timeout_sec=0.1)

        q_rad = self.current.copy()
        q_deg = [math.degrees(q) for q in q_rad]

        print("\nEstado actual:")
        print("Radianes:")
        print([round(q, 4) for q in q_rad])

        print("Grados:")
        print([round(q, 2) for q in q_deg])

        self.poses[name] = {

            "joints": q_rad

        }

        self.save_yaml()

        print()

        print(f"Pose '{name}' guardada.")


    ###########################################################
    # LISTAR
    ###########################################################

    def list_poses(self):

        print()

        if len(self.poses) == 0:

            print("No existen poses.")

            return

        print("Poses registradas:\n")

        for i, (name, data) in enumerate(self.poses.items(), start=1):

            q_rad = data["joints"]

            q_deg = [round(math.degrees(q), 2) for q in q_rad]

            print(f"{i}. {name}")
            print(f"   Rad: {['{:.4f}'.format(q) for q in q_rad]}")
            print(f"   Deg: {q_deg}\n")

    ###########################################################
    # ELIMINAR
    ###########################################################

    def delete_pose(self, name):

        if name not in self.poses:

            print()

            print("La pose no existe.")

            return

        del self.poses[name]

        self.save_yaml()

        print()

        print(f"Pose '{name}' eliminada.")


    ###########################################################
    # MOVIMIENTO SUAVE
    ###########################################################

    def move_to(self, target):

        start = self.current.copy()

        frequency = 200

        steps = int(self.duration * frequency)

        for i in range(steps + 1):

            if self.stop_requested:

                print("\nMovimiento detenido.")

                return False

            alpha = i / steps

            q = [

                start[j] + alpha * (target[j] - start[j])

                for j in range(5)

            ]

            self.publish(q)

            rclpy.spin_once(self, timeout_sec=0)

            time.sleep(1 / frequency)

        return True


    ###########################################################
    # IR A UNA POSE
    ###########################################################

    def go_pose(self, name):

        if name not in self.poses:

            print()

            print("La pose no existe.")

            return

        target = self.poses[name]["joints"]

        print()

        print(f"Moviendo a '{name}'...")

        self.move_to(target)

        print("Movimiento terminado.")


    ###########################################################
    # REPRODUCCION
    ###########################################################

    def play_sequence(self):

        if len(self.poses) == 0:

            print()

            print("No existen poses registradas.")

            return

        self.stop_requested = False

        self.playing = True

        print()

        print("Iniciando reproduccion...")

        for name in self.poses.keys():

            if self.stop_requested:

                break

            print(f"\nPose: {name}")

            target = self.poses[name]["joints"]

            ok = self.move_to(target)

            if not ok:

                break

        self.playing = False

        self.stop_requested = False

        print()

        print("Reproduccion finalizada.")


    ###########################################################
    # HILO DE REPRODUCCION
    ###########################################################

    def play_thread(self):

        hilo = threading.Thread(

            target=self.play_sequence,

            daemon=True

        )

        hilo.start()


    ###########################################################
    # DETENER
    ###########################################################

    def stop(self):

        if self.playing:

            self.stop_requested = True

        else:

            print()

            print("No hay ninguna reproducción en curso.")

    ###########################################################
    # EVALUAR POSE
    ###########################################################

    def current_pose(self):

        rclpy.spin_once(self, timeout_sec=0.1)

        print("\nPosición articular actual:")

        print("Radianes:")
        print([round(q, 4) for q in self.current])

        print("Grados:")
        print([round(math.degrees(q), 2) for q in self.current])


###########################################################
# MAIN
###########################################################

def main():

    rclpy.init()

    node = TeachRepeat()

    print("\nEsperando estado actual del robot...")

    while rclpy.ok():

        rclpy.spin_once(node, timeout_sec=0.1)

        if len(node.current) == 5:
            break

    print("\n========================================")
    print(" MODO TEACH & REPEAT")
    print("========================================")
    print("Comandos disponibles:\n")
    print("guardar <nombre>     Guarda la pose actual")
    print("listar               Lista las poses")
    print("ir <nombre>          Va a una pose")
    print("reproducir           Reproduce todas las poses")
    print("tiempo <segundos>    Cambia el tiempo entre poses")
    print("eliminar <nombre>    Elimina una pose")
    print("actual               Imprime la pose articular actual")
    print("stop                 Detiene la reproducción")
    print("salir                Finaliza el programa\n")

    while rclpy.ok():

        rclpy.spin_once(node, timeout_sec=0)

        try:

            comando = input(">> ").strip()

        except (KeyboardInterrupt, EOFError):

            break

        if comando == "":

            continue

        partes = comando.split()

        cmd = partes[0].lower()

        ###################################################

        if cmd == "guardar":

            if len(partes) != 2:

                print("Uso: guardar nombre")

                continue

            node.save_pose(partes[1])

        ###################################################

        elif cmd == "listar":

            node.list_poses()

        ###################################################

        elif cmd == "ir":

            if len(partes) != 2:

                print("Uso: ir nombre")

                continue

            node.go_pose(partes[1])

        ###################################################

        elif cmd == "reproducir":

            if node.playing:

                print("Ya existe una reproducción en curso.")

            else:

                node.play_thread()

        ###################################################

        elif cmd == "tiempo":

            if len(partes) != 2:

                print("Uso: tiempo segundos")

                continue

            try:

                t = float(partes[1])

                if t <= 0:

                    raise ValueError

                node.duration = t

                print(f"Tiempo de transición = {t:.2f} s")

            except ValueError:

                print("Tiempo inválido.")

        ###################################################

        elif cmd == "stop":

            node.stop()

        ###################################################

        elif cmd == "eliminar":

            if len(partes) != 2:

                print("Uso: eliminar nombre")

                continue

            node.delete_pose(partes[1])

        ###################################################

        elif cmd == "salir":

            break

        ###################################################

        elif cmd == "actual":

            node.current_pose() 

        ###################################################


        else:

            print("Comando no reconocido.")

    print("\nFinalizando...")

    node.destroy_node()

    rclpy.shutdown()


###########################################################

if __name__ == "__main__":

    main()

