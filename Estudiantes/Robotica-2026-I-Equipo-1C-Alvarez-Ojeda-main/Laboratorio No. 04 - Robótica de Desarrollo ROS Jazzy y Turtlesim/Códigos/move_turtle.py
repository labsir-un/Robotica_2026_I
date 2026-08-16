#!/usr/bin/env python3
"""
move_turtle.py

Nodo único de ROS 2 para controlar la tortuga de turtlesim, tanto en modo
manual (teclado) como en modo automático (figuras y letras).

Arquitectura
------------
- Estado interno protegido por un lock (self._lock).
- Comunicación ROS aislada en métodos dedicados (_pose_callback, publish_twist,
  call_*).
- Primitivas de movimiento (move_distance, rotate_angle, move_arc, orientacion)
  que se apoyan en la pose real para detenerse en el punto exacto.
- run_sequence(): motor genérico que ejecuta una lista de pasos ('move'/'rotate'),
  usado por las figuras (draw_square, draw_triangulo).
- Comportamientos compuestos (draw_letter_*) construidos sobre las primitivas.
- Entrada de teclado que solo modifica estado o dispara comportamientos.

Jerarquía de llamadas típica:
    draw_square() -> run_sequence() -> move_distance()/rotate_angle() -> publish_twist() -> ROS

Teclas
------
    flechas         -> movimiento manual
    s / t           -> dibujar cuadrado / triángulo
    v/x/b/n/y/o/h   -> dibujar letras V/P/A/C/Y/O/H
    a               -> patrullaje automático (evita bordes)
    z               -> arco de prueba
    c               -> orientar la tortuga a 0 rad (Este)
    r               -> reiniciar posición (sin borrar el dibujo)
    p               -> activar/desactivar el lápiz
    espacio / q     -> detener movimiento
"""

from __future__ import annotations

import math
import random
import select
import sys
import termios
import threading
import time
import tty
from enum import Enum, auto
from typing import Callable, Optional

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_srvs.srv import Empty
from std_msgs.msg import Bool
from turtlesim.msg import Pose
from turtlesim.srv import Kill, SetPen, Spawn, TeleportAbsolute


class Mode(Enum):
    MANUAL = auto()
    DRAWING = auto()
    STOPPED = auto()


class MoveTurtle(Node):
    """Nodo único que controla turtlesim de forma manual y automática."""

    PUBLISH_RATE_HZ = 20.0
    LINEAR_STEP = 2.0
    ANGULAR_STEP = 2.0

    # Centro de la ventana de turtlesim (usado en patrullaje y reinicio de posición)
    CENTER_X = 5.544445
    CENTER_Y = 5.544445

    def __init__(self):
        super().__init__('turtle_controller')

        # ---- Estado interno (protegido por _lock) ----
        self._lock = threading.Lock()
        self.pose = Pose()
        self.linear_speed = 0.0
        self.angular_speed = 0.0
        self.mode = Mode.MANUAL
        self.pen_enabled = True
        self._behavior_thread: Optional[threading.Thread] = None
        self._stop_behavior = threading.Event()

        # ---- Comunicación ROS ----
        self._cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self._pen_state_pub = self.create_publisher(Bool, '/pen_enabled', 10)
        self._pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self._pose_callback, 10)
        self._timer = self.create_timer(
            1.0 / self.PUBLISH_RATE_HZ, self._timer_callback)
    

        self._reset_cli = self.create_client(Empty, '/reset')
        self._teleport_cli = self.create_client(
            TeleportAbsolute, '/turtle1/teleport_absolute')
        self._set_pen_cli = self.create_client(SetPen, '/turtle1/set_pen')
        self._spawn_cli = self.create_client(Spawn, '/spawn')
        self._kill_cli = self.create_client(Kill, '/kill')

        self.get_logger().info(
            'move_turtle listo. Flechas para mover, "s" cuadrado, "q" detener.')

    # ========================================================================
    # ROS: comunicación pura
    # ========================================================================

    def _pose_callback(self, msg: Pose):
        with self._lock:
            self.pose = msg

    def _timer_callback(self):
        self.publish_twist()

    def publish_twist(self):
        # Publica en /turtle1/cmd_vel la velocidad actual del estado interno.
        with self._lock:
            v = self.linear_speed
            w = self.angular_speed
        msg = Twist()
        msg.linear.x = v
        msg.angular.z = w
        self._cmd_pub.publish(msg)

    def call_reset(self):
        return self._call_service_sync(self._reset_cli, Empty.Request())

    def call_teleport(self, x: float, y: float, theta: float = 0.0):
        req = TeleportAbsolute.Request()
        req.x, req.y, req.theta = x, y, theta
        return self._call_service_sync(self._teleport_cli, req)

    def call_set_pen(self, r=255, g=255, b=255, width=2, off=0):
        req = SetPen.Request()
        req.r, req.g, req.b, req.width, req.off = r, g, b, width, off
        return self._call_service_sync(self._set_pen_cli, req)

    def call_spawn(self, x: float, y: float, theta: float = 0.0, name: str = ''):
        req = Spawn.Request()
        req.x, req.y, req.theta, req.name = x, y, theta, name
        return self._call_service_sync(self._spawn_cli, req)

    def call_kill(self, name: str = 'turtle1'):
        req = Kill.Request()
        req.name = name
        return self._call_service_sync(self._kill_cli, req)
    
    def _call_service_sync(self, client, request, timeout: float = 2.0):
        # Llama a un servicio ROS y bloquea hasta obtener respuesta o agotar el timeout.
        if not client.wait_for_service(timeout_sec=timeout):
            self.get_logger().warn(f'Servicio {client.srv_name} no disponible')
            return None
        future = client.call_async(request)
        while not future.done():
            time.sleep(0.01)
        return future.result()

    # ========================================================================
    # Estado / modo
    # ========================================================================

    def set_mode(self, mode: Mode):
        with self._lock:
            self.mode = mode

    def get_mode(self) -> Mode:
        with self._lock:
            return self.mode

    def stop(self):
        # Detiene cualquier comportamiento en curso y frena la tortuga.
        self._stop_behavior.set()
        with self._lock:
            self.linear_speed = 0.0
            self.angular_speed = 0.0
            self.mode = Mode.STOPPED

    # ========================================================================
    # Primitivas de movimiento. Se corrigen leyendo la pose real.
    # ========================================================================

    def toggle_pen(self):
        # Alterna el lápiz activado/desactivado manteniendo el mismo color.
        self.pen_enabled = not self.pen_enabled

        off_value = 0 if self.pen_enabled else 1

        # Cambiar lápiz de turtle1
        self.call_set_pen(
            r=255, g=255, b=255, width=2,
            off=off_value
        )

        # Publicar estado del lápiz para que turtle_follower sincronice turtle2
        msg = Bool()
        msg.data = self.pen_enabled
        self._pen_state_pub.publish(msg)

        estado = "activado" if self.pen_enabled else "desactivado"
        self.get_logger().info(f"Lápiz de turtle1 {estado}")

    def auto_patrol(self):
        # Avanza en línea recta; si se acerca a un borde en esa dirección,
        # se detiene y gira hacia el centro (con una pequeña variación
        # aleatoria) antes de seguir avanzando.
        MARGIN = 0.7
        V = 1.5

        while not self._stop_behavior.is_set():
            with self._lock:
                x, y, theta = self.pose.x, self.pose.y, self.pose.theta

            dx, dy = math.cos(theta), math.sin(theta)

            # ¿Está cerca de un borde y avanzando hacia él?
            collision = (
                (x < MARGIN and dx < 0) or
                (x > 11.088 - MARGIN and dx > 0) or
                (y < MARGIN and dy < 0) or
                (y > 11.088 - MARGIN and dy > 0)
            )

            if collision:
                with self._lock:
                    self.linear_speed = 0.0
                    self.angular_speed = 0.0
                self.publish_twist()

                # Girar hacia el centro con una perturbación de hasta ±30°
                target = math.atan2(self.CENTER_Y - y, self.CENTER_X - x)
                target += random.uniform(-math.pi / 6, math.pi / 6)
                target = math.atan2(math.sin(target), math.cos(target))
                self.orientacion(target)

            with self._lock:
                self.linear_speed = V
                self.angular_speed = 0.0
            self.publish_twist()

            time.sleep(0.02)

        with self._lock:
            self.linear_speed = 0.0
            self.angular_speed = 0.0
        self.publish_twist()

    def orientacion(self, target_angle: float):
        # Controlador proporcional (P) que gira la tortuga hasta un ángulo
        # absoluto (rad), usando siempre el error angular mínimo.
        Kp = 2.0
        W_MAX = 1.0
        TOL = 0.005  # ~0.3°

        target_angle = math.atan2(math.sin(target_angle), math.cos(target_angle))

        while not self._stop_behavior.is_set():
            with self._lock:
                current_theta = self.pose.theta

            error = math.atan2(
                math.sin(target_angle - current_theta),
                math.cos(target_angle - current_theta)
            )

            if abs(error) < TOL:
                break

            omega = max(min(Kp * error, W_MAX), -W_MAX)

            with self._lock:
                self.linear_speed = 0.0
                self.angular_speed = omega
            self.publish_twist()

            time.sleep(0.01)

        with self._lock:
            self.linear_speed = 0.0
            self.angular_speed = 0.0
        self.publish_twist()

    def move_distance(self, v: float, distance: float):
        # Avanza en línea recta hasta recorrer `distance`, midiendo el
        # desplazamiento real respecto a la pose inicial.
        with self._lock:
            x0, y0 = self.pose.x, self.pose.y
            self.linear_speed = v
            self.angular_speed = 0.0
        self.publish_twist()

        traveled = 0.0
        while traveled < distance and not self._stop_behavior.is_set():
            time.sleep(0.01)
            with self._lock:
                x1, y1 = self.pose.x, self.pose.y
            traveled = math.hypot(x1 - x0, y1 - y0)

        with self._lock:
            self.linear_speed = 0.0
            self.angular_speed = 0.0
        self.publish_twist()

    def rotate_angle(self, w: float, angle: float):
        # Gira un ángulo relativo `angle` (rad) reutilizando orientacion().
        # `w` se conserva por compatibilidad con run_sequence, pero la
        # velocidad real la decide el controlador proporcional.
        with self._lock:
            theta0 = self.pose.theta

        target = theta0 + angle
        target = math.atan2(math.sin(target), math.cos(target))
        self.orientacion(target)

        with self._lock:
            self.linear_speed = 0.0
            self.angular_speed = 0.0
        self.publish_twist()

    def run_sequence(self, steps):
        # Ejecuta una lista de pasos: [('move', v, distancia), ('rotate', w, angulo), ...]
        for kind, speed, amount in steps:
            if self._stop_behavior.is_set():
                return
            if kind == 'move':
                self.move_distance(speed, amount)
            elif kind == 'rotate':
                self.rotate_angle(speed, amount)
            else:
                raise ValueError(f"Paso desconocido: '{kind}'")

    def move_arc(self, radius: float, angle: float, linear_speed: float = 1.0):
        # Recorre un arco de circunferencia de radio `radius`, girando en
        # total `angle` radianes (el signo define el sentido de giro).
        if radius <= 0:
            raise ValueError("El radio debe ser positivo.")

        omega = linear_speed / radius
        if angle < 0:
            omega = -omega

        with self._lock:
            last_theta = self.pose.theta
            self.linear_speed = linear_speed
            self.angular_speed = omega
        self.publish_twist()

        turned = 0.0
        while turned < abs(angle) and not self._stop_behavior.is_set():
            time.sleep(0.01)
            with self._lock:
                current_theta = self.pose.theta

            # Ángulo girado en este intervalo, acumulado para saber cuándo parar
            delta = math.atan2(
                math.sin(current_theta - last_theta),
                math.cos(current_theta - last_theta)
            )
            turned += abs(delta)
            last_theta = current_theta

        with self._lock:
            self.linear_speed = 0.0
            self.angular_speed = 0.0
        self.publish_twist()

    # ========================================================================
    # Comportamientos
    # ========================================================================

    def reiniciarposicion(self):
        # Reinicia solo la posición (teletransporta al centro); no borra el dibujo.
        self.stop()
        self.call_teleport(self.CENTER_X, self.CENTER_Y, 0.0)
        self.set_mode(Mode.MANUAL)

    def draw_square(self):
        # Cuadrado de 4 lados iguales, como plantilla explícita de pasos.
        v_linear = 1.0
        v_angular = 0.5
        dist = 2.0
        angle90 = math.pi / 2

        self.orientacion(0)
        steps = [
            ('move', v_linear, dist), ('rotate', v_angular, angle90),
            ('move', v_linear, dist), ('rotate', v_angular, angle90),
            ('move', v_linear, dist), ('rotate', v_angular, angle90),
            ('move', v_linear, dist), ('rotate', v_angular, angle90),
        ]
        self.run_sequence(steps)

    def draw_triangulo(self):
        # Triángulo equilátero: 3 lados iguales con giros de 120°.
        v_linear = 1.0
        v_angular = 0.5
        dist = 2.0
        angle120 = math.pi / 1.5

        self.orientacion(0)
        steps = [
            ('move', v_linear, dist), ('rotate', v_angular, angle120),
            ('move', v_linear, dist), ('rotate', v_angular, angle120),
            ('move', v_linear, dist), ('rotate', v_angular, angle120),
        ]
        self.run_sequence(steps)

    def draw_letter_v(self, scale: float = 2.0):
        # 'V': diagonal hacia abajo-derecha y luego hacia arriba-derecha.
        v_linear = 1.5
        dist = 2.0 * scale

        if not self._stop_behavior.is_set():
            self.orientacion(-math.pi / 3.0)
        if not self._stop_behavior.is_set():
            self.move_distance(v_linear, dist)

        if not self._stop_behavior.is_set():
            self.orientacion(math.pi / 2.5)
        if not self._stop_behavior.is_set():
            self.move_distance(v_linear, dist)

        if not self._stop_behavior.is_set():
            self.orientacion(0.0)

    def draw_letter_p(self, scale: float = 2.0):
        # 'P': tallo vertical seguido de un semicírculo (panza) en la mitad superior.
        v_linear = 1.5
        v_angular = 1.0

        if not self._stop_behavior.is_set():
            self.orientacion(math.pi / 2)
        if not self._stop_behavior.is_set():
            self.move_distance(v_linear, 2.0 * scale)

        if not self._stop_behavior.is_set():
            self.rotate_angle(v_angular, -math.pi / 2)
        if not self._stop_behavior.is_set():
            self.move_distance(v_linear, 0.3 * scale)

        if not self._stop_behavior.is_set():
            self.move_arc(radius=0.5 * scale, angle=-math.pi, linear_speed=v_linear)
        if not self._stop_behavior.is_set():
            self.move_distance(v_linear, 0.3 * scale)

    def draw_letter_a(self, scale: float = 2.0):
        # 'A': dos diagonales cruzadas y una barra horizontal a media altura.
        v_linear = 1.5
        dist = 2.0 * scale
        angle = math.pi / 2.5  # 72°, hace la letra más angosta
        crossbar_dist = dist * math.cos(angle)  # distancia exacta para cerrar la barra

        if not self._stop_behavior.is_set():
            self.orientacion(angle)
        if not self._stop_behavior.is_set():
            self.move_distance(v_linear, dist)

        if not self._stop_behavior.is_set():
            self.orientacion(-angle)
        if not self._stop_behavior.is_set():
            self.move_distance(v_linear, dist)

        if not self._stop_behavior.is_set():
            self.orientacion(math.pi - angle)  # vuelve a subir por el mismo lado derecho
        if not self._stop_behavior.is_set():
            self.move_distance(v_linear, dist / 2.0)

        if not self._stop_behavior.is_set():
            self.orientacion(math.pi)
        if not self._stop_behavior.is_set():
            self.move_distance(v_linear, crossbar_dist)

        if not self._stop_behavior.is_set():
            self.orientacion(0.0)

    def draw_letter_c(self, scale: float = 2.0):
        # 'C': arco de 270° dejando abierto el lado derecho.
        v_linear = 1.5
        radius = 1.0 * scale

        if not self._stop_behavior.is_set():
            self.orientacion(3.0 * math.pi / 4.0)
        if not self._stop_behavior.is_set():
            self.move_arc(radius=radius, angle=1.5 * math.pi, linear_speed=v_linear)
        if not self._stop_behavior.is_set():
            self.orientacion(0.0)

    def draw_letter_y(self, scale: float = 2.0):
        # 'Y': dos ramas superiores que bajan al centro y un tallo vertical.
        v_linear = 1.5
        branch_dist = 1.0 * scale
        stem_dist = 1.2 * scale
        angle = math.pi / 3.1  # mismo ancho que la 'A'

        if not self._stop_behavior.is_set():
            self.orientacion(-angle)
        if not self._stop_behavior.is_set():
            self.move_distance(v_linear, branch_dist)

        if not self._stop_behavior.is_set():
            self.orientacion(-math.pi / 2.0)
        if not self._stop_behavior.is_set():
            self.move_distance(v_linear, stem_dist)

        if not self._stop_behavior.is_set():
            self.orientacion(math.pi / 2.0)
        if not self._stop_behavior.is_set():
            self.move_distance(v_linear, stem_dist)  # sube por el mismo tallo

        if not self._stop_behavior.is_set():
            self.orientacion(angle)
        if not self._stop_behavior.is_set():
            self.move_distance(v_linear, branch_dist)

        if not self._stop_behavior.is_set():
            self.orientacion(0.0)

    def draw_letter_o(self, scale: float = 2.0):
        # 'O' ovalada (forma de estadio): dos lados rectos y dos semicírculos.
        v_linear = 1.5
        straight_dist = 0.2 * scale
        radius = 0.5 * scale

        if not self._stop_behavior.is_set():
            self.orientacion(math.pi / 2.0)
        if not self._stop_behavior.is_set():
            self.move_distance(v_linear, straight_dist)

        if not self._stop_behavior.is_set():
            self.move_arc(radius=radius, angle=-math.pi, linear_speed=v_linear)
        if not self._stop_behavior.is_set():
            self.move_distance(v_linear, straight_dist)

        if not self._stop_behavior.is_set():
            self.move_arc(radius=radius, angle=-math.pi, linear_speed=v_linear)
        if not self._stop_behavior.is_set():
            self.orientacion(0.0)

    def draw_letter_h(self, scale: float = 2.0):
        # 'H': dos palos verticales unidos por una barra horizontal a media altura.
        v_linear = 1.5
        height = 2.0 * scale
        half_height = 1.0 * scale
        width = 1.2 * scale

        if not self._stop_behavior.is_set():
            self.orientacion(math.pi / 2.0)
        if not self._stop_behavior.is_set():
            self.move_distance(v_linear, height)

        if not self._stop_behavior.is_set():
            self.orientacion(-math.pi / 2.0)
        if not self._stop_behavior.is_set():
            self.move_distance(v_linear, half_height)

        if not self._stop_behavior.is_set():
            self.orientacion(0.0)
        if not self._stop_behavior.is_set():
            self.move_distance(v_linear, width)

        if not self._stop_behavior.is_set():
            self.orientacion(math.pi / 2.0)
        if not self._stop_behavior.is_set():
            self.move_distance(v_linear, half_height)

        if not self._stop_behavior.is_set():
            self.orientacion(-math.pi / 2.0)
        if not self._stop_behavior.is_set():
            self.move_distance(v_linear, height)

        if not self._stop_behavior.is_set():
            self.orientacion(0.0)

    # ========================================================================
    # Lanzamiento asíncrono de comportamientos
    # ========================================================================

    def start_behavior(self, target: Callable, *args, **kwargs):
        # Ejecuta `target` en un hilo aparte para no bloquear el nodo,
        # gestionando el modo DRAWING y el evento de parada.
        if self._behavior_thread and self._behavior_thread.is_alive():
            self.get_logger().warn('Ya hay un comportamiento en ejecución')
            return

        def _wrapper():
            self.set_mode(Mode.DRAWING)
            self._stop_behavior.clear()
            try:
                target(*args, **kwargs)
            finally:
                with self._lock:
                    self.linear_speed = 0.0
                    self.angular_speed = 0.0
                    if self.mode == Mode.DRAWING:
                        self.mode = Mode.MANUAL

        self._behavior_thread = threading.Thread(target=_wrapper, daemon=True)
        self._behavior_thread.start()

    # ========================================================================
    # Movimiento manual
    # ========================================================================

    def forward(self, active: bool):
        if self.get_mode() == Mode.DRAWING:
            return
        with self._lock:
            self.linear_speed = self.LINEAR_STEP if active else 0.0

    def backward(self, active: bool):
        if self.get_mode() == Mode.DRAWING:
            return
        with self._lock:
            self.linear_speed = -self.LINEAR_STEP if active else 0.0

    def turn_left(self, active: bool):
        if self.get_mode() == Mode.DRAWING:
            return
        with self._lock:
            self.angular_speed = self.ANGULAR_STEP if active else 0.0

    def turn_right(self, active: bool):
        if self.get_mode() == Mode.DRAWING:
            return
        with self._lock:
            self.angular_speed = -self.ANGULAR_STEP if active else 0.0


# ============================================================================
# Bucle de teclado
# ============================================================================

def _read_key(settings, timeout: float = 0.1) -> str:
    # Lee una tecla (o secuencia de escape de flecha) sin bloquear más de `timeout`.
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], timeout)
    if not rlist:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        return ''
    ch = sys.stdin.read(1)
    if ch == '\x1b':
        ch += sys.stdin.read(2)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return ch


# Teclas que disparan un comportamiento directo sobre el nodo. Las flechas y
# ' '/'q' se manejan aparte en keyboard_loop porque dependen de si la tecla
# sigue presionada.
_BEHAVIOR_KEYS: dict[str, Callable[['MoveTurtle'], None]] = {
    's': lambda n: n.start_behavior(n.draw_square),
    't': lambda n: n.start_behavior(n.draw_triangulo),
    'a': lambda n: n.start_behavior(n.auto_patrol),
    'v': lambda n: n.start_behavior(n.draw_letter_v, scale=0.8),
    'x': lambda n: n.start_behavior(n.draw_letter_p, scale=0.8),
    'b': lambda n: n.start_behavior(n.draw_letter_a, scale=0.8),
    'c': lambda n: n.start_behavior(n.draw_letter_c, scale=0.7),
    'y': lambda n: n.start_behavior(n.draw_letter_y, scale=0.8),
    'o': lambda n: n.start_behavior(n.draw_letter_o, scale=0.8),
    'h': lambda n: n.start_behavior(n.draw_letter_h, scale=0.8),
    'z': lambda n: n.start_behavior(n.move_arc, radius=1.0, angle=math.pi),
    'r': lambda n: n.reiniciarposicion(),
    'p': lambda n: n.toggle_pen(),
}


def keyboard_loop(node: MoveTurtle):
    settings = termios.tcgetattr(sys.stdin)

    # Tiempo sin recibir tecla antes de soltar el movimiento manual (flechas).
    KEY_TIMEOUT = 0.5
    last_key_time = time.time()

    try:
        while rclpy.ok():
            key = _read_key(settings, timeout=0.05)

            if key != '':
                last_key_time = time.time()

            if key == '\x1b[A':
                node.forward(True)
            elif key == '\x1b[B':
                node.backward(True)
            elif key == '\x1b[D':
                node.turn_left(True)
            elif key == '\x1b[C':
                node.turn_right(True)
            elif key in (' ', 'q'):
                node.stop()
            elif key in _BEHAVIOR_KEYS:
                _BEHAVIOR_KEYS[key](node)
            elif key == '':
                # Sin tecla nueva: si pasó KEY_TIMEOUT, soltamos el movimiento manual.
                if (time.time() - last_key_time) > KEY_TIMEOUT:
                    if node.get_mode() != Mode.DRAWING:
                        node.forward(False)
                        node.backward(False)
                        node.turn_left(False)
                        node.turn_right(False)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)


def main(args=None):
    rclpy.init(args=args)
    node = MoveTurtle()

    executor_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    executor_thread.start()

    try:
        keyboard_loop(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()
        executor_thread.join(timeout=1.0)


if __name__ == '__main__':
    main()
