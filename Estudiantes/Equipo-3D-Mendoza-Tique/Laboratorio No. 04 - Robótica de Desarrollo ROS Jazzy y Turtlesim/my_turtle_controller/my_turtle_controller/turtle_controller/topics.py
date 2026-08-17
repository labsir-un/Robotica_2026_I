# topics.py — publicadores y suscriptores ROS 2
#
# Contiene TopicsManager, mixin que el nodo principal hereda.
# Gestiona de forma thread-safe la lectura de pose1 y pose2,
# y expone métodos para publicar velocidades.

import math
import threading
import time

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from rclpy.qos import QoSProfile, ReliabilityPolicy


class TopicsManager:
    """
    Mixin con publicadores, suscriptores y lógica del seguidor.
    La clase heredante debe ser un rclpy.Node.
    """

    def init_topics(self):
        """
        Registra publicadores y suscriptores.
        Llamar desde __init__ del nodo.
        """
        # QoS compatible con turtlesim (publica pose con BEST_EFFORT)
        qos_pose = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)

        # Publicadores
        self.pub1 = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pub2 = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)

        # Suscriptores con lock para acceso thread-safe
        self._pose1_lock     = threading.Lock()
        self._pose2_lock     = threading.Lock()
        self._pose1          = Pose()
        self._pose2          = Pose()
        self._pose1_received = False
        self._pose2_received = False

        self.create_subscription(Pose, '/turtle1/pose', self._cb_pose1, qos_pose)
        self.create_subscription(Pose, '/turtle2/pose', self._cb_pose2, qos_pose)

    # ── Propiedades thread-safe ─────────────────────────────────────────

    @property
    def pose1(self) -> Pose:
        """Copia atómica de la pose de turtle1."""
        with self._pose1_lock:
            return self._pose1

    @property
    def pose2(self) -> Pose:
        """Copia atómica de la pose de turtle2."""
        with self._pose2_lock:
            return self._pose2

    # ── Callbacks de suscripción (ejecutados por el executor) ───────────

    def _cb_pose1(self, msg: Pose):
        with self._pose1_lock:
            self._pose1          = msg
            self._pose1_received = True

    def _cb_pose2(self, msg: Pose):
        with self._pose2_lock:
            self._pose2          = msg
            self._pose2_received = True

    # ── Publicación de velocidad (solo desde hilos secundarios) ─────────

    def publish_vel1(self, linear: float, angular: float, duration: float):
        """
        Publica velocidad en turtle1 durante 'duration' segundos y para.
        Usa bucle con sleep corto para que self.running pueda interrumpirlo.
        Solo llamar desde hilos secundarios, nunca desde callbacks.
        """
        twist = Twist()
        twist.linear.x  = linear
        twist.angular.z = angular
        t_end = time.time() + duration
        while time.time() < t_end and self.running:
            self.pub1.publish(twist)
            time.sleep(0.05)
        self.pub1.publish(Twist())   # stop

    def stop_all(self):
        """Publica Twist vacío en ambas tortugas."""
        self.pub1.publish(Twist())
        self.pub2.publish(Twist())

    # ── Sistema líder-seguidor (Timer callback 10 Hz) ───────────────────

    def follower_callback(self):
        """
        Publicado por un Timer de 10 Hz en el nodo principal.
        Lee pose1 y pose2 de forma thread-safe y publica en /turtle2/cmd_vel.
        Control proporcional: linear ∝ distancia, angular ∝ error de ángulo.
        """
        if not (self._pose1_received and self._pose2_received):
            return

        p1 = self.pose1
        p2 = self.pose2

        kl = self.get_parameter('follower_gain_lin').value
        ka = self.get_parameter('follower_gain_ang').value

        dx   = p1.x - p2.x
        dy   = p1.y - p2.y
        dist = math.hypot(dx, dy)

        if dist < 0.5:
            self.pub2.publish(Twist())
            return

        angle_goal = math.atan2(dy, dx)
        err = math.atan2(
            math.sin(angle_goal - p2.theta),
            math.cos(angle_goal - p2.theta)
        )

        twist = Twist()
        twist.linear.x  = min(kl * dist, 2.0)
        twist.angular.z = ka * err
        self.pub2.publish(twist)
