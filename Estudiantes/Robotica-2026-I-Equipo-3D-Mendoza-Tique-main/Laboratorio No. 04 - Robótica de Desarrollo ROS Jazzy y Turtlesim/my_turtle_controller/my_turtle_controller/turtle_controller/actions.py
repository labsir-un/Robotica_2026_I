# actions.py — trayectorias automáticas, letras y control manual
#
# Contiene ActionsManager, mixin que el nodo principal hereda.
# Todas las funciones que duran más de un tick se ejecutan en
# hilos daemon secundarios para no bloquear el executor de ROS 2.

import math
import random
import threading
import time

from geometry_msgs.msg import Twist

from .constants import WIN_MIN, WIN_MAX   # ← importación explícita


class ActionsManager:
    """
    Mixin con todas las acciones del laboratorio.
    Depende de TopicsManager y ServiceManager (via herencia múltiple en el nodo).
    """

    # ══════════════════════════════════════════════════════════
    # Control manual
    # ══════════════════════════════════════════════════════════

    def move_forward(self):
        """Flecha ↑: publica velocidad lineal positiva en turtle1."""
        t = Twist()
        t.linear.x = self.get_parameter('linear_speed').value
        self.pub1.publish(t)

    def move_backward(self):
        """Flecha ↓: publica velocidad lineal negativa en turtle1."""
        t = Twist()
        t.linear.x = -self.get_parameter('linear_speed').value
        self.pub1.publish(t)

    def turn_left(self):
        """Flecha ←: publica velocidad angular positiva en turtle1."""
        t = Twist()
        t.angular.z = self.get_parameter('angular_speed').value
        self.pub1.publish(t)

    def turn_right(self):
        """Flecha →: publica velocidad angular negativa en turtle1."""
        t = Twist()
        t.angular.z = -self.get_parameter('angular_speed').value
        self.pub1.publish(t)

    def stop_turtle1(self):
        """Tecla Q: detiene turtle1 y cancela la trayectoria automática."""
        self.pub1.publish(Twist())
        self.auto_running = False
        self.get_logger().info('Tortuga detenida.')

    # ══════════════════════════════════════════════════════════
    # Helpers internos (solo hilos secundarios)
    # ══════════════════════════════════════════════════════════

    def _draw_with_pen(self, draw_func):
        """
        Activa el lápiz si estaba apagado, ejecuta draw_func y restaura
        el estado original. Garantiza que el lápiz quede como estaba.
        """
        was_on = self.pen_active
        if not was_on:
            self.svc_set_pen1(255, 255, 255, 2, 0)
            self.pen_active = True
        draw_func()
        if not was_on:
            self.svc_set_pen1(0, 0, 0, 2, 1)
            self.pen_active = False

    def _draw_segment(self, x0, y0, x1, y1, color=(255, 200, 0), width=3):
        """
        Teletransporta turtle1 a (x0,y0) apuntando hacia (x1,y1),
        luego avanza la distancia exacta.
        Apaga el lápiz durante el salto y lo enciende solo durante el trazo.
        """
        angle = math.atan2(y1 - y0, x1 - x0)
        self.svc_set_pen1(0, 0, 0, width, 1)      # OFF para saltar
        self.svc_teleport(x0, y0, angle)
        self.svc_set_pen1(*color, width, 0)        # ON para trazar
        dist  = math.hypot(x1 - x0, y1 - y0)
        speed = self.get_parameter('linear_speed').value * 0.6
        self.publish_vel1(speed, 0.0, dist / speed)
        self.svc_set_pen1(0, 0, 0, width, 1)       # OFF al terminar

    # ══════════════════════════════════════════════════════════
    # Trayectorias geométricas
    # ══════════════════════════════════════════════════════════

    def draw_square(self):
        """Tecla s: cuadrado de 4 lados girando 90° en cada esquina."""
        self.get_logger().info('Dibujando cuadrado...')
        lin = self.get_parameter('linear_speed').value
        ang = self.get_parameter('angular_speed').value
        def _draw():
            for _ in range(4):
                if not self.running: break
                self.publish_vel1(lin, 0.0, 1.0)
                self.publish_vel1(0.0, ang, (math.pi / 2) / ang)
        self._draw_with_pen(_draw)
        self.get_logger().info('Cuadrado listo.')

    def draw_triangle(self):
        """Tecla t: triángulo equilátero girando 120° en cada vértice."""
        self.get_logger().info('Dibujando triángulo...')
        lin = self.get_parameter('linear_speed').value
        ang = self.get_parameter('angular_speed').value
        def _draw():
            for _ in range(3):
                if not self.running: break
                self.publish_vel1(lin, 0.0, 1.2)
                self.publish_vel1(0.0, ang, (2 * math.pi / 3) / ang)
        self._draw_with_pen(_draw)
        self.get_logger().info('Triángulo listo.')

    # ══════════════════════════════════════════════════════════
    # Letras personalizadas
    # ══════════════════════════════════════════════════════════

    def draw_letter_D(self):
        """Tecla d: letra D — palo vertical + semicírculo a la derecha."""
        self.get_logger().info('Dibujando letra D...')
        def _draw():
            self._draw_segment(2.0, 2.5, 2.0, 4.5, color=(255, 200, 0))
            self.svc_set_pen1(0, 0, 0, 3, 1)
            self.svc_teleport(2.0, 4.5, 0.0)
            self.svc_set_pen1(255, 200, 0, 3, 0)
            v = 1.0; r = 1.0; omega = -v / r
            steps = 20
            dt = math.pi / (abs(omega) * steps)
            for _ in range(steps):
                if not self.running: break
                t = Twist(); t.linear.x = v; t.angular.z = omega
                self.pub1.publish(t)
                time.sleep(dt)
            self.pub1.publish(Twist())
            self.svc_set_pen1(0, 0, 0, 3, 1)
        self._draw_with_pen(_draw)
        self.get_logger().info('Letra D lista.')

    def draw_letter_T(self):
        """Tecla T: letra T — barra horizontal superior + palo vertical."""
        self.get_logger().info('Dibujando letra T...')
        def _draw():
            self._draw_segment(5.0, 4.5, 7.0, 4.5, color=(0, 200, 255))
            self._draw_segment(6.0, 4.5, 6.0, 2.5, color=(0, 200, 255))
        self._draw_with_pen(_draw)
        self.get_logger().info('Letra T lista.')

    def draw_letter_L(self):
        """Tecla l: letra L — palo vertical + base horizontal."""
        self.get_logger().info('Dibujando letra L...')
        def _draw():
            self._draw_segment(7.0, 4.5, 7.0, 2.5, color=(255, 100, 100))
            self._draw_segment(7.0, 2.5, 9.0, 2.5, color=(255, 100, 100))
        self._draw_with_pen(_draw)
        self.get_logger().info('Letra L lista.')

    def draw_letter_M(self):
        """Tecla m: letra M — cinco puntos conectados con giro explícito."""
        self.get_logger().info('Dibujando letra M...')
        pts = [(2.0, 5.5), (2.0, 7.5), (3.5, 6.5), (5.0, 7.5), (5.0, 5.5)]

        def _draw():
            ang   = self.get_parameter('angular_speed').value
            speed = self.get_parameter('linear_speed').value * 0.6
            self.svc_set_pen1(0, 0, 0, 3, 1)
            self.svc_teleport(pts[0][0], pts[0][1], math.pi / 2)
            self.svc_set_pen1(100, 255, 100, 3, 0)
            for i in range(len(pts) - 1):
                x0, y0 = pts[i]
                x1, y1 = pts[i + 1]
                angle = math.atan2(y1 - y0, x1 - x0)
                cur   = self.pose1.theta
                diff  = math.atan2(math.sin(angle - cur), math.cos(angle - cur))
                if abs(diff) > 0.05:
                    self.publish_vel1(0.0, math.copysign(ang, diff), abs(diff) / ang)
                dist = math.hypot(x1 - x0, y1 - y0)
                self.publish_vel1(speed, 0.0, dist / speed)
            self.svc_set_pen1(0, 0, 0, 3, 1)

        self._draw_with_pen(_draw)
        self.get_logger().info('Letra M lista.')

    # ══════════════════════════════════════════════════════════
    # Reinicio y lápiz
    # ══════════════════════════════════════════════════════════

    def reset_turtle(self):
        """Tecla r: centra turtle1, limpia pantalla y restaura estado."""
        self.get_logger().info('Reiniciando...')
        was_on = self.pen_active
        self.svc_clear()
        self.svc_set_pen1(0, 0, 0, 2, 1)
        self.svc_teleport(5.54, 5.54, 0.0)
        if was_on:
            self.svc_set_pen1(255, 255, 255, 2, 0)
            self.pen_active = True
        else:
            self.pen_active = False
        self.svc_disable_pen2()
        self.get_logger().info('Reiniciado.')

    def toggle_pen(self):
        """Tecla p: activa o desactiva el lápiz de turtle1."""
        self.pen_active = not self.pen_active
        off = 0 if self.pen_active else 1
        self.svc_set_pen1(255, 255, 255, 2, off)
        self.get_logger().info(f'Lápiz {"ON" if self.pen_active else "OFF"}.')

    # ══════════════════════════════════════════════════════════
    # Trayectoria automática con evasión de bordes
    # ══════════════════════════════════════════════════════════

    def auto_trajectory(self):
        """
        Tecla a: avanza en línea recta; al detectar borde gira completamente
        hacia el centro antes de retomar el avance.
        Corre en hilo daemon para no bloquear el executor.
        """
        if self.auto_running:
            self.get_logger().info('Trayectoria ya en curso.')
            return
        self.auto_running = True
        self.get_logger().info('Auto-trayectoria iniciada. Presiona Q para detener.')

        def _run():
            # Esperar primer mensaje de pose
            while not self._pose1_received and self.running:
                time.sleep(0.05)

            # Leer parámetros en el momento de inicio
            border = self.get_parameter('border_margin').value
            lin    = self.get_parameter('linear_speed').value
            THRESH = 0.10   # rad — tolerancia para considerar alineado

            while self.auto_running and self.running:
                p = self.pose1   # copia atómica thread-safe

                near = (
                    p.x < WIN_MIN + border or p.x > WIN_MAX - border or
                    p.y < WIN_MIN + border or p.y > WIN_MAX - border
                )

                if near:
                    # ── Fase giro: girar hasta apuntar al centro ──────────
                    while self.auto_running and self.running:
                        p      = self.pose1
                        target = math.atan2(5.54 - p.y, 5.54 - p.x)
                        diff   = math.atan2(
                            math.sin(target - p.theta),
                            math.cos(target - p.theta)
                        )
                        if abs(diff) <= THRESH:
                            break
                        w = math.copysign(max(abs(diff) * 2.0, 0.8), diff)
                        twist = Twist()
                        twist.angular.z = w
                        self.pub1.publish(twist)
                        time.sleep(0.05)

                    self.pub1.publish(Twist())   # detener giro
                    time.sleep(0.05)

                else:
                    # ── Fase avance: ir recto con leve variación ──────────
                    twist = Twist()
                    twist.linear.x  = lin
                    twist.angular.z = random.uniform(-0.1, 0.1)
                    self.pub1.publish(twist)
                    time.sleep(0.05)

            self.pub1.publish(Twist())
            self.auto_running = False
            self.get_logger().info('Auto-trayectoria detenida.')

        threading.Thread(target=_run, daemon=True).start()
