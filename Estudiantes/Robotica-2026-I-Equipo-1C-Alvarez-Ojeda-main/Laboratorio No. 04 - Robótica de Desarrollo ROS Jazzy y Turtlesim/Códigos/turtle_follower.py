#!/usr/bin/env python3

from __future__ import annotations

import math
import threading
import time
from typing import Optional

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Bool
from turtlesim.msg import Pose
from turtlesim.srv import SetPen, Spawn


class TurtleFollower(Node):
    """
    Nodo seguidor de turtle2.

    - Crea turtle2 usando /spawn.
    - Lee /turtle1/pose.
    - Lee /turtle2/pose.
    - Calcula distancia y error angular.
    - Publica velocidad en /turtle2/cmd_vel.
    - Sincroniza el lápiz de turtle2 usando /pen_enabled.
    """

    PUBLISH_RATE_HZ = 20.0

    def __init__(self):
        super().__init__('turtle_follower')

        self._lock = threading.Lock()

        self.turtle1_pose: Optional[Pose] = None
        self.turtle2_pose: Optional[Pose] = None
        self.turtle2_created = False
        self.pen_enabled = True

        self._turtle2_cmd_pub = self.create_publisher(
            Twist, '/turtle2/cmd_vel', 10
        )

        self._turtle1_pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self._turtle1_pose_callback, 10
        )

        self._turtle2_pose_sub = self.create_subscription(
            Pose, '/turtle2/pose', self._turtle2_pose_callback, 10
        )

        self._pen_state_sub = self.create_subscription(
            Bool, '/pen_enabled', self._pen_state_callback, 10
        )

        self._spawn_cli = self.create_client(Spawn, '/spawn')
        self._turtle2_set_pen_cli = self.create_client(
            SetPen, '/turtle2/set_pen'
        )

        self._spawn_cli = self.create_client(Spawn, '/spawn')
        self._turtle2_set_pen_cli = self.create_client(
            SetPen, '/turtle2/set_pen'
        )

        self._spawn_requested = False

        # Timer para intentar crear turtle2 sin bloquear el nodo
        self._startup_timer = self.create_timer(
            0.5, self._create_turtle2
        )

        # Timer principal del seguimiento
        self._timer = self.create_timer(
            1.0 / self.PUBLISH_RATE_HZ, self._follower_callback
        )

        self.get_logger().info('turtle_follower listo. turtle2 seguirá a turtle1.')

    # -------------------------------------------------------------------------
    # Callbacks de suscripción
    # -------------------------------------------------------------------------

    def _turtle1_pose_callback(self, msg: Pose):
        with self._lock:
            self.turtle1_pose = msg

    def _turtle2_pose_callback(self, msg: Pose):
        with self._lock:
            self.turtle2_pose = msg

    def _pen_state_callback(self, msg: Bool):
        self.pen_enabled = msg.data
        self._apply_turtle2_pen_state()

    # -------------------------------------------------------------------------
    # Servicios
    # -------------------------------------------------------------------------

    def _call_service_sync(self, client, request, timeout: float = 2.0):
        if not client.wait_for_service(timeout_sec=timeout):
            self.get_logger().warn(f'Servicio {client.srv_name} no disponible')
            return None

        future = client.call_async(request)

        while not future.done() and rclpy.ok():
            time.sleep(0.01)

        return future.result()

    def _create_turtle2(self):
        """
        Crea turtle2 de forma asíncrona.
        No bloquea el nodo, para que el timer de seguimiento pueda ejecutarse.
        """
        if self.turtle2_created or self._spawn_requested:
            return

        if not self._spawn_cli.service_is_ready():
            self._spawn_cli.wait_for_service(timeout_sec=0.1)
            return

        req = Spawn.Request()
        req.x = 5.0
        req.y = 5.0
        req.theta = 0.0
        req.name = 'turtle2'

        self._spawn_requested = True
        future = self._spawn_cli.call_async(req)
        future.add_done_callback(self._on_spawn_done)
    
    def _on_spawn_done(self, future):
        try:
            future.result()
            self.turtle2_created = True
            self.get_logger().info('turtle2 creada correctamente.')

            # Detener el timer de creación para que no vuelva a intentar crearla
            self._startup_timer.cancel()

            # Sincronizar lápiz inicial
            self._apply_turtle2_pen_state()

        except Exception as e:
            self.get_logger().warn(f'No se pudo crear turtle2: {e}')
            self._spawn_requested = False

    def _apply_turtle2_pen_state(self):
        """
        Aplica a turtle2 el mismo estado de lápiz recibido desde /pen_enabled.
        Se hace de forma asíncrona para no bloquear el nodo.
        """
        if not self.turtle2_created:
            return

        if not self._turtle2_set_pen_cli.service_is_ready():
            self._turtle2_set_pen_cli.wait_for_service(timeout_sec=0.1)
            return

        off_value = 0 if self.pen_enabled else 1

        req = SetPen.Request()
        req.r = 255
        req.g = 255
        req.b = 255
        req.width = 2
        req.off = off_value

        self._turtle2_set_pen_cli.call_async(req)

    # -------------------------------------------------------------------------
    # Control líder-seguidor
    # -------------------------------------------------------------------------

    def _follower_callback(self):
        if not self.turtle2_created:
            return

        with self._lock:
            turtle1_pose = self.turtle1_pose
            turtle2_pose = self.turtle2_pose

        if turtle1_pose is None or turtle2_pose is None:
            return

        dx = turtle1_pose.x - turtle2_pose.x
        dy = turtle1_pose.y - turtle2_pose.y

        distance = math.hypot(dx, dy)
        target_angle = math.atan2(dy, dx)

        angle_error = math.atan2(
            math.sin(target_angle - turtle2_pose.theta),
            math.cos(target_angle - turtle2_pose.theta)
        )

        theta_error = math.atan2(
            math.sin(turtle1_pose.theta - turtle2_pose.theta),
            math.cos(turtle1_pose.theta - turtle2_pose.theta)
        )

        msg = Twist()

        # Parámetros del controlador proporcional
        DIST_STOP = 0.07
        K_LINEAR = 2.0
        K_ANGULAR = 4.5
        K_THETA = 2.5
        V_MAX = 2.5
        W_MAX = 3.0

        if distance < DIST_STOP:
            # Si está cerca, copia orientación del líder.
            msg.linear.x = 0.0
            msg.angular.z = max(min(K_THETA * theta_error, W_MAX), -W_MAX)

            if abs(theta_error) < 0.05:
                msg.angular.z = 0.0

        elif abs(angle_error) > 1.2:
            # Si está muy desalineada, gira sobre su eje.
            msg.linear.x = 0.0
            msg.angular.z = max(min(K_ANGULAR * angle_error, W_MAX), -W_MAX)

        else:
            # Si el error angular es moderado, avanza mientras corrige.
            alignment_factor = max(0.25, math.cos(angle_error))

            msg.linear.x = min(K_LINEAR * distance * alignment_factor, V_MAX)
            msg.angular.z = max(min(K_ANGULAR * angle_error, W_MAX), -W_MAX)

        self._turtle2_cmd_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    node = TurtleFollower()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        stop_msg = Twist()
        node._turtle2_cmd_pub.publish(stop_msg)

        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()