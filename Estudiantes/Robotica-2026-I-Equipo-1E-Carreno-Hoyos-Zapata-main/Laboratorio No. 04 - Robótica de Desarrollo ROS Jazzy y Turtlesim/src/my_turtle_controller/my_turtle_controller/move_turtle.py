#!/usr/bin/env python3
"""
move_turtle.py — Controlador de turtlesim mediante teclado.

Laboratorio 04 · Robótica de Desarrollo · 2026-I · UNAL
Equipo: Janan L. Carreño · Cristian S. Hoyos · Jose A. Zapata

Controles — FUNCIONES (teclas no usadas como iniciales del equipo):
  Flechas → Movimiento manual continuo (↑adelante ↓atrás ←izq →der)
  F       → Dibujar cuadrado
  T       → Dibujar triángulo equilátero
  M       → Trayectoria automática zigzag
  I       → Reiniciar posición al centro
  O       → Activar/desactivar lápiz
  Q       → Detener completamente

Controles — LETRAS (iniciales del equipo):
  J → letra J  · Janan · Jose
  L → letra L  · Libardo
  C → letra C  · Cristian · Carreño
  H → letra H  · Hoyos
  Z → letra Z  · Zapata
  R → letra R  · Riaño
  S → letra S  · Stiven
  A → letra A  · Andres
  P → letra P  · Peralta · Piñeros

  Ctrl+C → Salir

Diseño:
  - Nodo único 'move_turtle' con dos timers a 10 Hz (control + seguidor) y un
    hilo de teclado, de modo que las trayectorias NO bloquean el nodo.
  - Las figuras y letras se dibujan con un controlador 'goto' en lazo cerrado:
    la tortuga GIRA con velocidad angular y AVANZA con velocidad lineal hacia
    cada waypoint (no se usa teleport para girar). El teleport solo reposiciona
    con la pluma levantada entre trazos.
  - turtle2 sigue a turtle1 con un controlador proporcional saturado.
"""

import sys
import math
import threading
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import SetPen, TeleportAbsolute, Spawn

import tty
import termios

# ── Velocidades de control manual ──────────────────────────────────────────────
LIN_SPEED = 2.0    # m/s  — movimiento lineal con flechas
ANG_SPEED = 1.5    # rad/s — rotación con flechas

# ── Ganancias del controlador proporcional de seguimiento (turtle2→turtle1) ────
K_LIN          = 1.5    # ganancia lineal
K_ANG          = 4.0    # ganancia angular
MAX_FOLLOW_LIN = 2.5    # velocidad lineal máxima del seguidor
MAX_FOLLOW_ANG = 3.0    # velocidad angular máxima del seguidor
FOLLOW_STOP_DIST = 0.5  # distancia mínima; más cerca → detener turtle2

# ── Controlador "ir a punto" (goto) en lazo cerrado ─────────────────────────────
# Las figuras y letras se dibujan conduciendo la tortuga punto a punto con
# velocidad lineal y angular (NO con teleport). Esto demuestra el control de
# rotación por cmd_vel y produce un dibujo animado.
GOTO_TOL       = 0.08   # tolerancia de llegada al waypoint (u)
GOTO_ANG_TH    = 0.03   # alinear casi perfecto (~1.7°) ANTES de avanzar
GOTO_ANG_GAIN  = 6.0    # ganancia angular del goto (rotación en el sitio)
GOTO_ANG_MAX   = 2.5    # saturación angular del goto (rad/s)
GOTO_DRIVE_ANG = 1.0    # corrección de rumbo mientras avanza
GOTO_CROSS_GAIN = 2.0   # ganancia del error TRANSVERSAL (mantiene la recta)
GOTO_CROSS_MAX = 0.6    # corrección de rumbo máx por error transversal (rad)
GOTO_LIN_GAIN  = 1.6    # ganancia lineal del goto
GOTO_LIN_MAX   = 1.8    # saturación lineal del goto (m/s)
GOTO_TIMEOUT   = 200    # ticks máx por waypoint (red de seguridad, 10 s a 20 Hz;
                        # holgado para el barrido largo del zigzag de 9 u)

# ── Geometría compartida (FUENTE ÚNICA usada por el dibujo y las evidencias) ─────
LETTER_BOX = (4.0, 4.0, 2.0, 3.0)   # caja de letras: bx, by, ancho, alto


def square_waypoints():
    """Esquinas del cuadrado de 3 u de lado (inicio en (3.5, 4.0))."""
    return [(6.5, 4.0), (6.5, 7.0), (3.5, 7.0), (3.5, 4.0)]


def triangle_waypoints():
    """Vértices del triángulo equilátero de 3 u de lado (inicio en (3.5, 4.0))."""
    bx, by, s = 3.5, 4.0, 3.0
    h = s * math.sqrt(3) / 2
    return [(bx + s, by), (bx + s / 2, by + h), (bx, by)]


def zigzag_waypoints():
    """Trayectoria automática en zigzag (serpiente conectada) dentro de la ventana."""
    rows = [9.0, 7.5, 6.0, 4.5, 3.0, 1.5]
    pts, go = [], True
    for i, y in enumerate(rows):
        x1 = 10.0 if go else 1.0
        pts.append((x1, y))                       # barrido horizontal
        if i < len(rows) - 1:
            pts.append((x1, rows[i + 1]))         # conector vertical
        go = not go
    return pts


def letter_strokes(letter):
    """Devuelve los trazos de una letra como listas de puntos (x, y).
    Cada trazo se dibuja con la pluma abajo; entre trazos se levanta."""
    bx, by, w, h = LETTER_BOX
    lx, ly, rx, ty = bx, by, bx + w, by + h
    mx, my = bx + w / 2, by + h / 2
    strokes = {
        'J': [[(mx + 0.3, ty), (rx, ty)],
              [(rx, ty), (rx, ly + 0.9), (mx, ly + 0.1), (lx + 0.2, ly + 0.7)]],
        'L': [[(lx, ty), (lx, ly), (rx, ly)]],
        'C': [[(rx, ty), (lx, ty), (lx, ly), (rx, ly)]],
        'H': [[(lx, ly), (lx, ty)], [(lx, my), (rx, my)], [(rx, ly), (rx, ty)]],
        'Z': [[(lx, ty), (rx, ty), (lx, ly), (rx, ly)]],
        'R': [[(lx, ly), (lx, ty), (rx, ty - 0.5), (rx, my + 0.5), (lx, my)],
              [(lx + 0.4, my), (rx, ly)]],
        'S': [[(rx, ty), (lx, ty), (lx, my), (rx, my), (rx, ly), (lx, ly)]],
        'A': [[(lx, ly), (mx, ty)], [(mx, ty), (rx, ly)],
              [(lx + 0.45, ly + h / 3), (rx - 0.45, ly + h / 3)]],
        'P': [[(lx, ly), (lx, ty), (rx, ty - 0.5), (rx, my + 0.5), (lx, my)]],
    }
    return strokes.get(letter, [])


class MoveTurtle(Node):
    """
    Nodo principal que:
      1. Lee el teclado en un hilo separado (sin bloquear el event loop).
      2. Controla turtle1 con flechas o ejecuta trayectorias automáticas.
      3. Hace que turtle2 siga a turtle1 con un controlador proporcional.

    Las trayectorias se almacenan como listas de 'pasos' y se ejecutan paso
    a paso en el timer de control (10 Hz), sin bloquear el nodo.

    Formato de cada paso de trayectoria:
      {'type': 'vel',      'lin': float, 'ang': float, 'ticks': int}
      {'type': 'goto',     'x': float,   'y': float}                # lazo cerrado
      {'type': 'teleport', 'x': float,   'y': float,   'theta': float}
      {'type': 'pen',      'on': bool}
    """

    TICK_HZ = 20  # frecuencia de los timers (Hz) → 1 tick = 0.05 s
                  # (20 Hz da un dibujo 'goto' suave sin sobrepaso en las esquinas)

    def __init__(self):
        super().__init__('move_turtle')

        # ── Publishers ─────────────────────────────────────────────────────────
        self.pub1 = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pub2 = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)

        # ── Subscribers ────────────────────────────────────────────────────────
        self.pose1 = Pose()
        self.pose2 = Pose()
        self.create_subscription(
            Pose, '/turtle1/pose', lambda m: setattr(self, 'pose1', m), 10)
        self.create_subscription(
            Pose, '/turtle2/pose', lambda m: setattr(self, 'pose2', m), 10)

        # ── Service clients ────────────────────────────────────────────────────
        self.cli_pen      = self.create_client(SetPen,            '/turtle1/set_pen')
        self.cli_teleport = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        self.cli_spawn    = self.create_client(Spawn,             '/spawn')

        # ── Estado interno ─────────────────────────────────────────────────────
        self._key        = None   # última tecla capturada por el hilo
        self._pen_on     = True   # estado actual del lápiz
        self._traj_steps = []     # cola de pasos de la trayectoria activa
        self._traj_tick  = 0      # ticks consumidos en el paso actual
        self._seg_start  = (0.0, 0.0)  # inicio del segmento 'goto' (para seguir la recta)
        self._manual_lin = 0.0    # velocidad manual activa (persiste entre ticks)
        self._manual_ang = 0.0

        # ── Inicialización ─────────────────────────────────────────────────────
        self._wait_for_services()
        self._spawn_turtle2()

        # ── Timers ─────────────────────────────────────────────────────────────
        period = 1.0 / self.TICK_HZ
        self.create_timer(period, self._control_loop)   # control + trayectorias
        self.create_timer(period, self._follower_loop)  # seguimiento turtle2

        # ── Hilo de teclado ────────────────────────────────────────────────────
        self._running = True
        self._kb_thread = threading.Thread(
            target=self._keyboard_loop, daemon=True)
        self._kb_thread.start()

        self.get_logger().info(
            '\n'
            '══════════════════════════════════════════════\n'
            '  MoveTurtle listo\n'
            '  — Funciones —\n'
            '  ↑↓←→ : manual  F: cuadrado  T: triángulo\n'
            '  M: automática  I: inicio  O: lápiz  Q: stop\n'
            '  — Letras del equipo —\n'
            '  J L C H Z R S A P\n'
            '  Ctrl+C : salir\n'
            '══════════════════════════════════════════════'
        )

    # ══════════════════════════════════════════════════════════════════════════
    # INICIALIZACIÓN
    # ══════════════════════════════════════════════════════════════════════════

    def _wait_for_services(self):
        """Espera a que los servicios de turtlesim estén disponibles."""
        for cli, name in [
            (self.cli_pen,      '/turtle1/set_pen'),
            (self.cli_teleport, '/turtle1/teleport_absolute'),
            (self.cli_spawn,    '/spawn'),
        ]:
            self.get_logger().info(f'Esperando {name} ...')
            cli.wait_for_service(timeout_sec=10.0)

    def _spawn_turtle2(self):
        """Crea turtle2 en la esquina inferior izquierda."""
        req = Spawn.Request()
        req.x, req.y, req.theta, req.name = 2.0, 2.0, 0.0, 'turtle2'
        future = self.cli_spawn.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        self.get_logger().info('turtle2 creada en (2.0, 2.0).')

    # ══════════════════════════════════════════════════════════════════════════
    # SERVICIOS AUXILIARES (llamadas asíncronas — no bloquean el nodo)
    # ══════════════════════════════════════════════════════════════════════════

    def _set_pen(self, on: bool):
        """Activa o desactiva el lápiz de turtle1."""
        req = SetPen.Request()
        req.r, req.g, req.b, req.width = 255, 255, 255, 3
        req.off = 0 if on else 1
        self.cli_pen.call_async(req)
        self._pen_on = on

    def _teleport(self, x: float, y: float, theta: float):
        """Teleporta turtle1 a la posición (x, y, theta) sin trazar línea."""
        req = TeleportAbsolute.Request()
        req.x, req.y, req.theta = float(x), float(y), float(theta)
        self.cli_teleport.call_async(req)

    # ══════════════════════════════════════════════════════════════════════════
    # LECTURA DE TECLADO (hilo separado)
    # ══════════════════════════════════════════════════════════════════════════

    def _keyboard_loop(self):
        """
        Lee teclas en modo raw de forma no bloqueante.
        Las secuencias de escape de las flechas requieren leer 3 bytes.
        Escribe la tecla detectada en self._key para que el timer la consuma.
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while self._running:
                ch = sys.stdin.read(1)

                if ch == '\x1b':                      # inicio de secuencia de escape
                    ch2 = sys.stdin.read(1)
                    ch3 = sys.stdin.read(1)
                    if ch2 == '[':
                        self._key = {
                            'A': 'UP', 'B': 'DOWN',
                            'C': 'RIGHT', 'D': 'LEFT',
                        }.get(ch3)

                elif ch.upper() in 'FTMIOQJLCHZRSAP':  # teclas de función y letras
                    self._key = ch.upper()

                elif ch == '\x03':                    # Ctrl+C → salir
                    self._running = False
                    rclpy.shutdown()
                    break

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    # ══════════════════════════════════════════════════════════════════════════
    # LOOP PRINCIPAL DE CONTROL (10 Hz)
    # ══════════════════════════════════════════════════════════════════════════

    def _control_loop(self):
        """
        Se ejecuta 10 veces por segundo.
        Prioridades:
          1. Comandos instantáneos (I, O, Q) — interrumpen cualquier trayectoria.
          2. Inicio de trayectorias (F, T, M) y letras (J,L,C,H,Z,R,S,A,P).
          3. Ejecución paso a paso de la trayectoria activa.
          4. Control manual con flechas — velocidad persiste hasta nueva tecla o Q.
        """
        key = self._key
        self._key = None

        # ── 1. Comandos instantáneos ───────────────────────────────────────────
        if key == 'I':                          # Inicio / reset al centro
            self._stop_trajectory()
            self._manual_lin = 0.0
            self._manual_ang = 0.0
            self._teleport(5.5, 5.5, 0.0)
            return

        if key == 'O':                          # On/Off lápiz
            self._set_pen(not self._pen_on)
            return

        if key == 'Q':
            self._stop_trajectory()
            self._manual_lin = 0.0
            self._manual_ang = 0.0
            self._publish_vel1(0.0, 0.0)
            return

        # ── 2. Inicio de trayectorias ──────────────────────────────────────────
        if key == 'F':                          # Figura cuadrado
            self._start_trajectory(self._build_square())
        elif key == 'T':                        # Triángulo
            self._start_trajectory(self._build_triangle())
        elif key == 'M':                        # Movimiento automático
            self._start_trajectory(self._build_auto())
        # Letras del equipo (R,S,A,P libres porque las funciones usan F,M,I,O)
        elif key in ('J', 'L', 'C', 'H', 'Z', 'R', 'S', 'A', 'P'):
            self._start_trajectory(self._build_letter(key))

        # ── 3. Ejecutar trayectoria activa ─────────────────────────────────────
        if self._traj_steps:
            self._tick_trajectory()
            return

        # ── 4. Control manual con velocidad persistente ────────────────────────
        # La velocidad se mantiene entre ticks; se detiene con Q o flecha contraria.
        if key == 'UP':
            self._manual_lin =  LIN_SPEED
            self._manual_ang =  0.0
        elif key == 'DOWN':
            self._manual_lin = -LIN_SPEED
            self._manual_ang =  0.0
        elif key == 'LEFT':
            self._manual_ang =  ANG_SPEED
            self._manual_lin =  0.0
        elif key == 'RIGHT':
            self._manual_ang = -ANG_SPEED
            self._manual_lin =  0.0

        self._publish_vel1(self._manual_lin, self._manual_ang)

    # ══════════════════════════════════════════════════════════════════════════
    # MOTOR DE TRAYECTORIAS
    # ══════════════════════════════════════════════════════════════════════════

    def _start_trajectory(self, steps: list):
        self._traj_steps = steps
        self._traj_tick  = 0
        self.get_logger().info(f'Trayectoria iniciada ({len(steps)} pasos).')

    def _stop_trajectory(self):
        self._traj_steps = []
        self._traj_tick  = 0

    def _tick_trajectory(self):
        """Avanza un tick (0.1 s) en la trayectoria activa."""
        if not self._traj_steps:
            return

        step = self._traj_steps[0]

        if step['type'] == 'vel':
            # Publicar velocidad y contar ticks
            self._publish_vel1(step['lin'], step['ang'])
            self._traj_tick += 1
            if self._traj_tick >= step['ticks']:
                self._traj_steps.pop(0)
                self._traj_tick = 0

        elif step['type'] == 'goto':
            # Controlador 'ir a punto' que SIGUE LA RECTA del segmento: primero rota
            # en el sitio para alinearse y luego avanza corrigiendo el error
            # transversal (distancia perpendicular a la recta) → lados rectos.
            if self._traj_tick == 0:                           # inicio del segmento
                self._seg_start = (self.pose1.x, self.pose1.y)
            sx, sy = self._seg_start
            bx, by = step['x'], step['y']
            dist = math.hypot(bx - self.pose1.x, by - self.pose1.y)
            if dist < GOTO_TOL:
                self._publish_vel1(0.0, 0.0)
                self._traj_steps.pop(0)
                self._traj_tick = 0
            else:
                line_ang = math.atan2(by - sy, bx - sx)        # dirección de la recta
                cross = (-(self.pose1.x - sx) * math.sin(line_ang)
                         + (self.pose1.y - sy) * math.cos(line_ang))   # error transversal
                desired = line_ang - max(-GOTO_CROSS_MAX,
                                         min(GOTO_CROSS_MAX, GOTO_CROSS_GAIN * cross))
                ang_err = desired - self.pose1.theta
                while ang_err >  math.pi: ang_err -= 2.0 * math.pi
                while ang_err < -math.pi: ang_err += 2.0 * math.pi
                if abs(ang_err) > GOTO_ANG_TH:                 # desalineado → rotar
                    ang = max(-GOTO_ANG_MAX, min(GOTO_ANG_MAX, GOTO_ANG_GAIN * ang_err))
                    self._publish_vel1(0.0, ang)
                else:                                          # avanzar siguiendo la recta
                    lin = min(GOTO_LIN_MAX, GOTO_LIN_GAIN * dist)
                    self._publish_vel1(lin, GOTO_DRIVE_ANG * ang_err)
                self._traj_tick += 1
                if self._traj_tick > GOTO_TIMEOUT:             # red de seguridad
                    self._traj_steps.pop(0)
                    self._traj_tick = 0

        elif step['type'] == 'teleport':
            # Teleport es instantáneo — ejecutar y avanzar
            self._teleport(step['x'], step['y'], step['theta'])
            self._traj_steps.pop(0)

        elif step['type'] == 'pen':
            self._set_pen(step['on'])
            self._traj_steps.pop(0)

        # Fin de trayectoria
        if not self._traj_steps:
            self._publish_vel1(0.0, 0.0)
            self.get_logger().info('Trayectoria completada.')

    # ── Helpers para construir pasos ───────────────────────────────────────────

    def _vel(self, lin, ang, ticks):
        """Paso de velocidad: lin m/s, ang rad/s durante 'ticks' ticks (×0.1 s)."""
        return {'type': 'vel', 'lin': float(lin), 'ang': float(ang), 'ticks': int(ticks)}

    def _tp(self, x, y, theta=0.0):
        """Paso de teleport (solo para reposicionar con la pluma levantada)."""
        return {'type': 'teleport', 'x': float(x), 'y': float(y), 'theta': float(theta)}

    def _goto(self, x, y):
        """Paso 'ir a punto' en lazo cerrado (dibuja con velocidad lineal y angular)."""
        return {'type': 'goto', 'x': float(x), 'y': float(y)}

    def _pen(self, on):
        """Paso de control del lápiz."""
        return {'type': 'pen', 'on': bool(on)}

    # ══════════════════════════════════════════════════════════════════════════
    # DEFINICIÓN DE TRAYECTORIAS
    # ══════════════════════════════════════════════════════════════════════════

    def _build_square(self):
        """
        Cuadrado de 3 u de lado dibujado conduciendo la tortuga esquina a esquina
        con el controlador 'goto': avanza con velocidad lineal y GIRA con velocidad
        ANGULAR en cada esquina (no se usa teleport para girar). Lazo cerrado sobre
        la pose → la figura cierra sin acumular error.
        """
        steps = [self._pen(False), self._tp(3.5, 4.0, 0.0), self._pen(True)]
        for x, y in square_waypoints():
            steps.append(self._goto(x, y))
        steps.append(self._pen(False))
        return steps

    def _build_triangle(self):
        """
        Triángulo equilátero de 3 u de lado dibujado vértice a vértice con 'goto'.
        En cada vértice la tortuga gira ~120° con velocidad angular antes de avanzar
        el siguiente lado con velocidad lineal.
        """
        steps = [self._pen(False), self._tp(3.5, 4.0, 0.0), self._pen(True)]
        for x, y in triangle_waypoints():
            steps.append(self._goto(x, y))
        steps.append(self._pen(False))
        return steps

    def _build_auto(self):
        """
        Trayectoria automática en zigzag (serpiente conectada) recorrida con 'goto'.
        La tortuga avanza y gira con velocidad lineal/angular dentro de los límites
        de la ventana (1–10), sin salirse de los bordes y sin usar teleport.
        """
        wps = zigzag_waypoints()
        steps = [self._pen(False), self._tp(wps[0][0], wps[0][1], 0.0), self._pen(True)]
        for x, y in wps[1:]:
            steps.append(self._goto(x, y))
        steps.append(self._pen(False))
        return steps

    def _build_letter(self, letter: str):
        """
        Dibuja una letra del equipo conduciendo la tortuga con el controlador
        'goto' (velocidad lineal + angular). La geometría proviene de
        letter_strokes() — la MISMA fuente que generan las evidencias.

        Cada letra es una lista de trazos; por trazo: se levanta la pluma y se
        reposiciona al inicio (teleport instantáneo, sin línea), se baja la pluma
        y se recorre el trazo con 'goto', que anima el dibujo.

          J → Janan · Jose        L → Libardo        C → Cristian · Carreño
          H → Hoyos               Z → Zapata         R → Riaño
          S → Stiven              A → Andres         P → Peralta · Piñeros
        """
        steps = []
        for stroke in letter_strokes(letter):
            steps.append(self._pen(False))
            steps.append(self._tp(stroke[0][0], stroke[0][1]))   # ir al inicio sin trazar
            steps.append(self._pen(True))
            for x, y in stroke[1:]:
                steps.append(self._goto(x, y))                   # trazo animado por velocidad
            steps.append(self._pen(False))
        return steps

    # ══════════════════════════════════════════════════════════════════════════
    # CONTROLADOR DE SEGUIMIENTO turtle2 → turtle1  (10 Hz)
    # ══════════════════════════════════════════════════════════════════════════

    def _follower_loop(self):
        """
        Controlador proporcional (P) que hace que turtle2 persiga a turtle1.

        Algoritmo:
          1. Calcular vector de error (dx, dy) desde turtle2 hacia turtle1.
          2. Calcular distancia y ángulo objetivo.
          3. Calcular error angular (diferencia entre ángulo objetivo y heading actual).
          4. Aplicar control proporcional saturado.
        """
        dx   = self.pose1.x - self.pose2.x
        dy   = self.pose1.y - self.pose2.y
        dist = math.hypot(dx, dy)

        if dist < FOLLOW_STOP_DIST:
            # Muy cerca: detener turtle2
            self.pub2.publish(Twist())
            return

        angle_to_target = math.atan2(dy, dx)
        angle_err       = angle_to_target - self.pose2.theta

        # Normalizar a [-π, π]
        while angle_err >  math.pi: angle_err -= 2.0 * math.pi
        while angle_err < -math.pi: angle_err += 2.0 * math.pi

        msg = Twist()
        msg.linear.x  = min(K_LIN * dist,      MAX_FOLLOW_LIN)
        msg.angular.z = max(-MAX_FOLLOW_ANG,
                        min(K_ANG * angle_err,  MAX_FOLLOW_ANG))
        self.pub2.publish(msg)

    # ══════════════════════════════════════════════════════════════════════════
    # UTILIDADES
    # ══════════════════════════════════════════════════════════════════════════

    def _publish_vel1(self, lin: float, ang: float):
        msg = Twist()
        msg.linear.x  = lin
        msg.angular.z = ang
        self.pub1.publish(msg)


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    rclpy.init()
    node = MoveTurtle()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node._running = False
        node._publish_vel1(0.0, 0.0)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
