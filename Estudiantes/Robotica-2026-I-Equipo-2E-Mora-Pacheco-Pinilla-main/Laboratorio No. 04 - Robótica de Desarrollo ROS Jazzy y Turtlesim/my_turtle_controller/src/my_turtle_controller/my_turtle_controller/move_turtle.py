#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import SetPen, Spawn
from std_srvs.srv import Empty
import sys
import select
import termios
import tty
import math
import random
from HersheyFonts import HersheyFonts


PI = math.pi


class TurtleKeyboardController(Node):
    """Nodo de ROS 2 que permite controlar la tortuga en turtlesim
    mediante el teclado, incluyendo control manual, trayectorias
    automaticas, dibujo de figuras, letras personalizadas y acciones
    complementarias.
    """

    def __init__(self):
        """Inicializa el nodo ROS 2, suscriptores, publicadores,
        clientes de servicio y variables de estado."""
        super().__init__('turtle_keyboard_controller')

        self.publisher_ = self.create_publisher(
            Twist, '/turtle1/cmd_vel', 10
        )

        self.pose_subscriber_ = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10
        )

        self.cli_set_pen = self.create_client(SetPen, '/turtle1/set_pen')
        self.cli_reset = self.create_client(Empty, '/reset')
        self.cli_spawn = self.create_client(Spawn, '/spawn')

        while not self.cli_set_pen.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn('Esperando servicio /turtle1/set_pen...')
        while not self.cli_reset.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn('Esperando servicio /reset...')
        while not self.cli_spawn.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn('Esperando servicio /spawn...')

        self.current_pose = None

        self.hershey = HersheyFonts()
        self.hershey.load_default_font('futural')

        self.linear_speed = 2.5
        self.angular_speed = 2.0

        self.lin_x = 0.0
        self.ang_z = 0.0

        self.pen_down = True
        self.auto_mode = False
        self.initials_mode = False

        # --- Sistema lider-seguidor ---
        self.turtle2_pose = None
        self.follow_mode = False
        self.turtle2_spawned = False

        self.pub_turtle2 = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)

        self.sub_turtle2 = self.create_subscription(
            Pose, '/turtle2/pose', self.pose2_callback, 10
        )

        self.follower_timer = self.create_timer(0.05, self.follower_callback)

        # --- Fin sistema lider-seguidor ---

        self.print_menu()

    def print_menu(self):
        """Imprime el menu de comandos disponibles en la terminal."""
        self.get_logger().info(
            'Control de tortuga iniciado.\n'
            'Flechas: control manual\n'
            '  S : cuadrado    T : triangulo    R : reiniciar\n'
            '  P : lapiz       A : exploracion  I : modo iniciales\n'
            '  L : lider-seguidor  Q : detener     Ctrl+C : salir'
        )

    # --- Callbacks y utilidades de terminal ---

    def pose_callback(self, msg):
        """Callback del suscriptor /turtle1/pose. Almacena la pose actual."""
        self.current_pose = msg

    def pose2_callback(self, msg):
        """Callback del suscriptor /turtle2/pose. Almacena la pose de turtle2."""
        self.turtle2_pose = msg

    def spawn_turtle2(self):
        """Spawn turtle2 en (5.5, 2.0) mediante el servicio /spawn."""
        request = Spawn.Request()
        request.x = 5.5
        request.y = 2.0
        request.theta = 0.0
        request.name = 'turtle2'
        future = self.cli_spawn.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            self.turtle2_spawned = True
            self.get_logger().info('turtle2 creada en (5.5, 2.0).')
        else:
            self.get_logger().error('Error al crear turtle2.')

    def toggle_follower(self):
        """Activa o desactiva el modo lider-seguidor.
        Al activar crea turtle2 si no existe. Al desactivar
        detiene turtle2 y reimprime el menu."""
        if not self.turtle2_spawned:
            self.spawn_turtle2()
            rclpy.spin_once(self, timeout_sec=0.5)

        self.follow_mode = not self.follow_mode
        if self.follow_mode:
            self.get_logger().info(
                'MODO LIDER-SEGUIDOR activado. turtle2 sigue a turtle1.'
            )
        else:
            self.stop_turtle2()
            self.get_logger().info('MODO LIDER-SEGUIDOR desactivado.')
            self.print_menu()

    def stop_turtle2(self):
        """Publica Twist nulo en /turtle2/cmd_vel para detener turtle2."""
        msg = Twist()
        self.pub_turtle2.publish(msg)

    def follower_callback(self):
        """Timer periodico (20 Hz) del modo lider-seguidor.
        Hace que turtle2 se dirija al punto ubicado a follow_dist
        detras de turtle1 usando un controlador proporcional."""
        if not self.follow_mode:
            return
        if self.current_pose is None or self.turtle2_pose is None:
            return

        follow_dist = 1.0

        desired_x = self.current_pose.x - follow_dist * math.cos(self.current_pose.theta)
        desired_y = self.current_pose.y - follow_dist * math.sin(self.current_pose.theta)

        dx = desired_x - self.turtle2_pose.x
        dy = desired_y - self.turtle2_pose.y
        dist = math.sqrt(dx**2 + dy**2)

        ang_target = math.atan2(dy, dx)
        ang_diff = ang_target - self.turtle2_pose.theta
        ang_diff = math.atan2(math.sin(ang_diff), math.cos(ang_diff))

        kp_lin = 2.0
        kp_ang = 3.0
        max_lin_speed = 3.0
        max_ang_speed = 4.0

        lin_speed = min(kp_lin * dist, max_lin_speed)
        ang_speed = kp_ang * ang_diff
        ang_speed = max(min(ang_speed, max_ang_speed), -max_ang_speed)

        msg = Twist()
        msg.linear.x = lin_speed
        msg.angular.z = ang_speed
        self.pub_turtle2.publish(msg)

    def read_key_nonblocking(self):
        """Lee una tecla de stdin sin bloqueo.
        Reconoce secuencias de escape para flechas. Devuelve
        None si no hay tecla disponible."""
        if select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.read(1)
            if key == '\x1b':
                if select.select([sys.stdin], [], [], 0.02)[0]:
                    key += sys.stdin.read(1)
                    if select.select([sys.stdin], [], [], 0.02)[0]:
                        key += sys.stdin.read(1)
            return key
        return None

    def set_raw_mode(self):
        """Configura la terminal en modo raw para captura inmediata de teclas."""
        tty.setraw(sys.stdin.fileno())

    def restore_terminal(self, settings):
        """Restaura la configuracion original de la terminal."""
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

    def flush_stdin(self):
        """Limpia el buffer de entrada de la terminal."""
        termios.tcflush(sys.stdin, termios.TCIFLUSH)

    # --- Publicacion y control de tortuga ---

    def publish_twist(self, linear_x, angular_z):
        """Publica un comando de velocidad en /turtle1/cmd_vel."""
        msg = Twist()
        msg.linear.x = linear_x
        msg.angular.z = angular_z
        self.publisher_.publish(msg)

    def stop_turtle(self):
        """Detiene turtle1 publicando Twist nulo y resetea estados."""
        self.publish_twist(0.0, 0.0)
        self.lin_x = 0.0
        self.ang_z = 0.0
        self.auto_mode = False
        self.get_logger().info('Tortuga detenida.')

    def get_pose(self):
        """Return the latest pose, waiting briefly if none is available."""
        if self.current_pose is not None:
            return self.current_pose
        for _ in range(10):
            rclpy.spin_once(self, timeout_sec=0.05)
            if self.current_pose is not None:
                break
        return self.current_pose

    def turn_to(self, target_theta):
        """Turn to an absolute orientation using closed-loop pose feedback.

        Args:
            target_theta: Absolute orientation in radians (0=RIGHT, PI/2=UP,
                          PI=LEFT, -PI/2=DOWN).

        Returns:
            bool: True if completed, False if interrupted.
        """
        if not self.auto_mode:
            return False
        kp = 2.0
        for _ in range(300):
            pose = self.get_pose()
            if pose is None:
                rclpy.spin_once(self, timeout_sec=0.01)
                continue
            dtheta = target_theta - pose.theta
            while dtheta > math.pi:
                dtheta -= 2*math.pi
            while dtheta < -math.pi:
                dtheta += 2*math.pi
            if abs(dtheta) < 0.005:
                break
            speed = max(min(kp * dtheta, 3.0), -3.0)
            self.publish_twist(0.0, speed)
            rclpy.spin_once(self, timeout_sec=0.01)
            key = self.read_key_nonblocking()
            if key == 'q' or key == '':
                self.auto_mode = False
                self.publish_twist(0.0, 0.0)
                if key == '':
                    raise KeyboardInterrupt
                return False
        self.publish_twist(0.0, 0.0)
        return True

    def move_to(self, x, y, pen_on=True):
        """Move to absolute coordinates using closed-loop pose feedback.

        Primero gira hacia el objetivo con el lapiz levantado para
        evitar marcas de rotacion en el punto de inicio. Luego baja
        o sube el lapiz segun pen_on y avanza combinando velocidad
        lineal proporcional a la distancia restante y correccion
        angular continua para mantener el rumbo hacia el destino.
        La correccion angular evita que errores residuales de
        orientacion se traduzcan en desviaciones laterales que
        impedirian cerrar contornos de letras.

        Args:
            x: Coordenada X destino.
            y: Coordenada Y destino.
            pen_on: True si el lapiz debe dibujar durante el movimiento.

        Returns:
            bool: True si completo, False si fue interrumpido.
        """
        if not self.auto_mode:
            return False
        pose = self.get_pose()
        if pose is None:
            return False
        dx = x - pose.x
        dy = y - pose.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist < 0.002:
            return True
        target_theta = math.atan2(dy, dx)
        self.set_pen_state(False)
        if not self.turn_to(target_theta):
            return False
        self.set_pen_state(pen_on)
        kp_lin = 1.0
        kp_ang = 2.0
        for _ in range(500):
            pose = self.get_pose()
            if pose is None:
                rclpy.spin_once(self, timeout_sec=0.01)
                continue
            dx = x - pose.x
            dy = y - pose.y
            rdist = math.sqrt(dx**2 + dy**2)
            if rdist < 0.002:
                break
            lin_speed = min(kp_lin * rdist, 2.5)
            cur_target_theta = math.atan2(dy, dx)
            dtheta = cur_target_theta - pose.theta
            while dtheta > math.pi:
                dtheta -= 2*math.pi
            while dtheta < -math.pi:
                dtheta += 2*math.pi
            ang_speed = max(min(kp_ang * dtheta, 3.0), -3.0)
            self.publish_twist(lin_speed, ang_speed)
            rclpy.spin_once(self, timeout_sec=0.01)
            key = self.read_key_nonblocking()
            if key == 'q' or key == '':
                self.auto_mode = False
                self.publish_twist(0.0, 0.0)
                if key == '':
                    raise KeyboardInterrupt
                return False
        self.publish_twist(0.0, 0.0)
        return True

    def move_relative(self, dx, dy, pen_on=True):
        """Move relative to current position using closed-loop pose feedback.

        Calcula las coordenadas absolutas sumando el desplazamiento
        relativo a la posicion actual obtenida mediante el topico
        /turtle1/pose. Gira hacia el destino y avanza con velocidad
        proporcional a la distancia restante.

        Args:
            dx: Desplazamiento en el eje X.
            dy: Desplazamiento en el eje Y.
            pen_on: True si el lapiz debe dibujar durante el movimiento.

        Returns:
            bool: True si completo, False si fue interrumpido.
        """
        if not self.auto_mode:
            return False
        self.set_pen_state(pen_on)
        pose = self.get_pose()
        if pose is None:
            return False
        target_x = pose.x + dx
        target_y = pose.y + dy
        dist = math.sqrt(dx**2 + dy**2)
        if dist < 0.005:
            return True
        target_theta = math.atan2(dy, dx)
        if not self.turn_to(target_theta):
            return False
        kp = 1.0
        for _ in range(300):
            pose = self.get_pose()
            if pose is None:
                rclpy.spin_once(self, timeout_sec=0.01)
                continue
            rx = target_x - pose.x
            ry = target_y - pose.y
            rdist = math.sqrt(rx**2 + ry**2)
            if rdist < 0.005:
                break
            speed = min(kp * rdist, 2.5)
            self.publish_twist(speed, 0.0)
            rclpy.spin_once(self, timeout_sec=0.01)
            key = self.read_key_nonblocking()
            if key == 'q' or key == '':
                self.auto_mode = False
                self.publish_twist(0.0, 0.0)
                if key == '':
                    raise KeyboardInterrupt
                return False
        self.publish_twist(0.0, 0.0)
        return True

    def set_pen_state(self, on):
        """Activa o desactiva el lapiz de turtle1 mediante el servicio /turtle1/set_pen.

        Args:
            on: True para bajar el lapiz (dibujar), False para subirlo.
        """
        request = SetPen.Request()
        request.r = 255
        request.g = 255
        request.b = 255
        request.width = 3
        request.off = 0 if on else 1
        future = self.cli_set_pen.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        self.pen_down = on

    def reset_turtle(self):
        """Reinicia la simulacion mediante el servicio /reset.
        Esto elimina todas las tortugas, por lo que tambien
        resetea el estado del seguidor."""
        self.stop_turtle()
        self.flush_stdin()
        request = Empty.Request()
        future = self.cli_reset.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            self.turtle2_spawned = False
            self.turtle2_pose = None
            self.follow_mode = False
            self.get_logger().info('Posicion reiniciada.')
        else:
            self.get_logger().error('Error al reiniciar la posicion.')

    def toggle_pen(self):
        """Alterna el estado del lapiz entre activado y desactivado."""
        self.set_pen_state(not self.pen_down)
        estado = 'activado' if self.pen_down else 'desactivado'
        self.get_logger().info(f'Lapiz {estado}.')

    # --- Primitivas de movimiento ---

    def move_forward(self, speed, duration):
        """Avanza en linea recta durante un tiempo dado.

        Args:
            speed: Velocidad lineal (unidades/s).
            duration: Duracion del movimiento en segundos.

        Returns:
            bool: True si completo, False si fue interrumpido.
        """
        start = self.get_clock().now()
        while (self.get_clock().now() - start).nanoseconds / 1e9 < duration:
            if not rclpy.ok() or not self.auto_mode:
                return False
            key = self.read_key_nonblocking()
            if key == 'q':
                self.auto_mode = False
                return False
            self.publish_twist(speed, 0.0)
            rclpy.spin_once(self, timeout_sec=0.005)
        self.publish_twist(0.0, 0.0)
        return True

    def turn(self, angular_speed, duration):
        """Gira en el lugar durante un tiempo dado.

        Args:
            angular_speed: Velocidad angular (rad/s).
            duration: Duracion del giro en segundos.

        Returns:
            bool: True si completo, False si fue interrumpido.
        """
        start = self.get_clock().now()
        while (self.get_clock().now() - start).nanoseconds / 1e9 < duration:
            if not rclpy.ok() or not self.auto_mode:
                return False
            key = self.read_key_nonblocking()
            if key == 'q':
                self.auto_mode = False
                return False
            self.publish_twist(0.0, angular_speed)
            rclpy.spin_once(self, timeout_sec=0.005)
        self.publish_twist(0.0, 0.0)
        return True

    def move_arc(self, linear_speed, angular_speed, total_angle):
        """Avanza trazando un arco circular.

        La tortuga se mueve con velocidad lineal y angular simultaneas,
        trazando un arco circular. El angulo total indica cuantos
        radianes debe girar la orientacion durante el movimiento.

        Args:
            linear_speed: Velocidad lineal (unidades/s).
            angular_speed: Velocidad angular (rad/s).
            total_angle: Angulo total de giro en radianes
                        (positivo = izquierda, negativo = derecha).

        Returns:
            bool: True si completo, False si fue interrumpido.
        """
        duration = abs(total_angle / angular_speed) if angular_speed != 0 else 0
        start = self.get_clock().now()
        while (self.get_clock().now() - start).nanoseconds / 1e9 < duration:
            if not rclpy.ok() or not self.auto_mode:
                return False
            key = self.read_key_nonblocking()
            if key == 'q':
                self.auto_mode = False
                return False
            self.publish_twist(linear_speed, angular_speed)
            rclpy.spin_once(self, timeout_sec=0.005)
        self.publish_twist(0.0, 0.0)
        return True

    def draw_stroke(self, pen_on, turn_angle, distance):
        """Dibuja un trazo recto compuesto por un giro seguido de un avance.

        Args:
            pen_on: True si el lapiz debe dibujar.
            turn_angle: Angulo de giro previo (radianes).
            distance: Distancia a avanzar (unidades).

        Returns:
            bool: True si completo, False si fue interrumpido.
        """
        if not self.auto_mode:
            return False
        self.set_pen_state(pen_on)
        if abs(turn_angle) > 0.001:
            ts = 2.0 if turn_angle > 0 else -2.0
            dur = abs(turn_angle) / 2.0
            if not self.turn(ts, dur):
                return False
        if distance > 0.001:
            dur = distance / 2.0
            if not self.move_forward(2.0, dur):
                return False
        return True

    def draw_arc_stroke(self, pen_on, linear_speed, angular_speed, total_angle):
        """Traza un arco curvo con control de lapiz.

        Args:
            pen_on: True si el lapiz debe dibujar.
            linear_speed: Velocidad lineal del arco.
            angular_speed: Velocidad angular del arco.
            total_angle: Angulo total de giro (radianes).

        Returns:
            bool: True si completo, False si fue interrumpido.
        """
        if not self.auto_mode:
            return False
        self.set_pen_state(pen_on)
        return self.move_arc(linear_speed, angular_speed, total_angle)

    # --- Trayectorias geometricas ---

    def draw_square(self):
        """Dibuja un cuadrado de lado 2.0 usando la primitiva move_forward/turn."""
        self.auto_mode = True
        s = 2.0
        fs = self.linear_speed
        ts = self.angular_speed
        sd = s / fs
        td = (PI / 2.0) / ts

        self.get_logger().info('Dibujando cuadrado...')
        for i in range(4):
            if not self.auto_mode:
                break
            if not self.move_forward(fs, sd):
                break
            if i < 3:
                if not self.turn(ts, td):
                    break
        self.auto_mode = False
        self.stop_turtle()
        self.get_logger().info('Cuadrado completado.')

    def draw_triangle(self):
        """Dibuja un triangulo equilatero de lado 2.0."""
        self.auto_mode = True
        s = 2.0
        fs = self.linear_speed
        ts = self.angular_speed
        sd = s / fs
        td = (2.0 * PI / 3.0) / ts

        self.get_logger().info('Dibujando triangulo...')
        for i in range(3):
            if not self.auto_mode:
                break
            if not self.move_forward(fs, sd):
                break
            if i < 2:
                if not self.turn(ts, td):
                    break
        self.auto_mode = False
        self.stop_turtle()
        self.get_logger().info('Triangulo completado.')

    def auto_explore(self):
        """Exploracion automatica con evasion de bordes durante 60s maximo.
        Al detectar un borde, retrocede un poco y gira un angulo
        aleatorio entre 90 y 180 grados para evitar trayectorias repetitivas."""
        self.auto_mode = True
        fs = 2.0
        ts = 2.0
        max_dur = 60.0

        self.get_logger().info('Exploracion automatica (60s max)...')
        start = self.get_clock().now()
        while rclpy.ok() and self.auto_mode:
            key = self.read_key_nonblocking()
            if key == 'q':
                break
            if (self.get_clock().now() - start).nanoseconds / 1e9 > max_dur:
                self.get_logger().info('Tiempo maximo alcanzado.')
                break
            if self.current_pose is not None:
                p = self.current_pose
                if p.x < 1.0 or p.x > 10.0 or p.y < 1.0 or p.y > 10.0:
                    self.get_logger().info('Borde detectado, evadiendo...')
                    self.move_forward(-1.0, 0.3)
                    ang = PI if random.random() < 0.5 else PI / 2
                    if not self.turn(ts, ang / ts):
                        break
            if not self.auto_mode:
                break
            if not self.move_forward(fs, 0.5):
                break
        self.auto_mode = False
        self.stop_turtle()
        self.get_logger().info('Exploracion finalizada.')

    # --- Letras personalizadas con Hershey Fonts ---

    def get_letter_movements(self, char, height=3.0):
        """Genera movimientos absolutos relativos al centro de la letra
        usando la fuente vectorial Hershey (futural). A diferencia de las
        fuentes TrueType que almacenan contornos rellenos con interior y
        exterior, las fuentes Hershey son de un solo trazo (single-stroke),
        ideales para plotters y tortugas roboticas.

        Cada letra se compone de uno o mas trazos. Cada trazo comienza
        con un movimiento de lapiz arriba hasta el primer punto, seguido
        de puntos de dibujo con lapiz abajo.

        Args:
            char: Caracter a dibujar ('A', 'D', 'F', ...).
            height: Altura deseada en unidades de turtlesim.

        Returns:
            list: Lista de tuplas (x_rel, y_rel, pen_on) donde x_rel e
                  y_rel estan centradas respecto al origen de la letra y
                  escaladas a height.
        """
        strokes = list(self.hershey.strokes_for_text(char))
        if not strokes:
            return []

        all_pts = [(x, y) for s in strokes for x, y in list(s)]
        xs = [p[0] for p in all_pts]
        ys = [p[1] for p in all_pts]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        font_height = max_y - min_y
        if font_height < 0.01:
            font_height = 1.0
        scale = height / font_height
        cx = (min_x + max_x) / 2.0
        cy = (min_y + max_y) / 2.0

        movements = []
        for stroke in strokes:
            pts = list(stroke)
            for i, (fx, fy) in enumerate(pts):
                rx = (fx - cx) * scale
                ry = -(fy - cy) * scale
                pen_on = (i > 0)
                movements.append((rx, ry, pen_on))
        return movements

    def draw_letter_by_path(self, char, height=3.0):
        """Dibuja una letra usando la fuente Hershey de un solo trazo.

        Obtiene los movimientos via get_letter_movements y los ejecuta
        con move_to usando coordenadas absolutas desde la posicion
        inicial de la tortuga. Cada trazo comienza con lapiz arriba
        y dibuja con lapiz abajo en los puntos siguientes.

        Args:
            char: Caracter a dibujar.
            height: Altura en unidades de turtlesim.
        """
        self.auto_mode = True
        movements = self.get_letter_movements(char, height)
        start = self.get_pose()
        if start is None:
            self.get_logger().error('No se pudo obtener la posicion inicial.')
            self.auto_mode = False
            return

        for rx, ry, pen_on in movements:
            if not self.auto_mode:
                break
            target_x = start.x + rx
            target_y = start.y + ry
            if not self.move_to(target_x, target_y, pen_on):
                break

        self.auto_mode = False
        self.stop_turtle()

    # --- Modo Iniciales ---

    def enter_initials_mode(self):
        """Activa el modo de dibujo de iniciales.
        Bucle propio con rclpy.spin_once para no bloquear
        los callbacks de ROS. Lee teclas y dibuja la letra
        correspondiente con Hershey Fonts."""
        self.initials_mode = True
        self.flush_stdin()
        msg = (
            '\r\nMODO INICIALES activado.\r\n'
            '  D F P R : Duvan Felipe Pacheco Rodriguez\r\n'
            '  J A M H : Juan Andres Mora Henao\r\n'
            '  A G P M : Andres Gustavo Pinilla Martinez\r\n'
            '  Letras disponibles: A, D, F, G, H, J, M, P, R\r\n'
            '  Q o cualquier otra tecla: salir del modo.\r\n'
        )
        sys.stdout.write(msg)
        sys.stdout.flush()

        while rclpy.ok() and self.initials_mode:
            key = self.read_key_nonblocking()

            if key is None:
                rclpy.spin_once(self, timeout_sec=0.05)
                continue
            if key == '':
                raise KeyboardInterrupt

            if key.upper() in 'ADFGHJMPR':
                sys.stdout.write(f'  Dibujando {key.upper()}...\r\n')
                sys.stdout.flush()
                self.draw_letter_by_path(key.upper())
                self.move_to_next_letter()
            elif key == 'q':
                self.stop_turtle()
                self.initials_mode = False
            else:
                self.stop_turtle()
                self.flush_stdin()
                self.initials_mode = False

        self.initials_mode = False
        self.auto_mode = False
        sys.stdout.write(
            '\r\nMODO INICIALES desactivado. -- Menu principal --\r\n'
            '  Flechas: control manual     S: cuadrado\r\n'
            '  T: triangulo  R: reiniciar  P: lapiz\r\n'
            '  A: exploracion  I: iniciales  L: lider-seguidor  Q: detener\r\n'
        )
        sys.stdout.flush()

    def move_to_next_letter(self):
        """Desplaza la tortuga 3.5 uds a la derecha con lapiz arriba
        para preparar el dibujo de la siguiente letra."""
        self.auto_mode = True
        self.set_pen_state(False)
        self.move_relative(3.5, 0, False)
        self.auto_mode = False

    # --- Bucle principal ---

    def run(self):
        """Bucle principal del nodo.
        Configura la terminal en modo raw, lee teclas sin bloqueo,
        ejecuta comandos y publica Twist hasta Ctrl+C."""
        original_settings = termios.tcgetattr(sys.stdin)
        self.set_raw_mode()

        try:
            while rclpy.ok():
                key = self.read_key_nonblocking()

                if key is not None:
                    if key == '\x1b[A':
                        self.lin_x = self.linear_speed
                        self.ang_z = 0.0
                    elif key == '\x1b[B':
                        self.lin_x = -self.linear_speed
                        self.ang_z = 0.0
                    elif key == '\x1b[D':
                        self.lin_x = 0.0
                        self.ang_z = self.angular_speed
                    elif key == '\x1b[C':
                        self.lin_x = 0.0
                        self.ang_z = -self.angular_speed
                    elif key == 's':
                        self.draw_square()
                    elif key == 't':
                        self.draw_triangle()
                    elif key == 'r':
                        self.reset_turtle()
                    elif key == 'p':
                        self.toggle_pen()
                    elif key == 'a':
                        self.auto_explore()
                    elif key in ('i', 'I'):
                        self.enter_initials_mode()
                    elif key in ('l', 'L'):
                        self.toggle_follower()
                    elif key == 'q':
                        self.stop_turtle()
                    elif key == '':
                        raise KeyboardInterrupt
                    else:
                        self.lin_x = 0.0
                        self.ang_z = 0.0
                else:
                    self.lin_x = 0.0
                    self.ang_z = 0.0

                if not self.auto_mode and not self.initials_mode:
                    self.publish_twist(self.lin_x, self.ang_z)

                rclpy.spin_once(self, timeout_sec=0.005)

        except KeyboardInterrupt:
            self.get_logger().info('Control finalizado.')

        finally:
            self.stop_turtle2()
            self.publish_twist(0.0, 0.0)
            self.lin_x = 0.0
            self.ang_z = 0.0
            self.auto_mode = False
            self.initials_mode = False
            self.follow_mode = False
            self.restore_terminal(original_settings)


def main(args=None):
    """Punto de entrada del nodo. Inicializa ROS 2, crea el nodo
    y ejecuta el bucle principal."""
    rclpy.init(args=args)
    node = TurtleKeyboardController()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
