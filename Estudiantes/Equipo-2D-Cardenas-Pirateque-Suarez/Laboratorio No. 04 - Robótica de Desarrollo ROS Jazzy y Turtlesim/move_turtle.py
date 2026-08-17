#!/usr/bin/env python3
"""
move_turtle.py

Laboratorio No. 04 - 2026-I - Robotica de Desarrollo
Introduccion a ROS 2 Jazzy Jalisco - Turtlesim
Universidad Nacional de Colombia

"""

import sys
import math
import time
import threading
import termios
import tty
import select

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import TeleportAbsolute, SetPen, Spawn, Kill
from std_srvs.srv import Empty


# Secuencias de escape que envia la terminal al presionar las flechas
KEY_UP = '\x1b[A'
KEY_DOWN = '\x1b[B'
KEY_RIGHT = '\x1b[C'
KEY_LEFT = '\x1b[D'
CTRL_C = '\x03'

# Velocidades por defecto para el control manual
LINEAR_SPEED = 2.0    # m/s
ANGULAR_SPEED = 1.2   # rad/s (Reducido para giros suaves y no exagerados)

# Velocidades usadas en las trayectorias automaticas
AUTO_LINEAR_SPEED = 2.0            # m/s, velocidad al dibujar figuras
AUTO_ANGULAR_SPEED = math.pi / 2   # rad/s, velocidad al girar en las figuras
SHAPE_SIDE_LENGTH = 4.0            # metros de cada lado del cuadrado y el triangulo
POSE_DISTANCE_TOLERANCE = 0.02     # metros de tolerancia al avanzar una distancia
POSE_ANGLE_TOLERANCE = 0.02        # radianes de tolerancia al girar un angulo (~1.1 grados)

# Reduccion de velocidad al acercarse al objetivo en trayectorias automaticas
ANGLE_SLOWDOWN_THRESHOLD = math.radians(5)    
DISTANCE_SLOWDOWN_THRESHOLD = 0.5             
SLOWDOWN_FACTOR = 0.3                         

AUTO_TRAJECTORY_DURATION = 20.0    # s que dura la trayectoria automatica (tecla A)
BOUNDARY_MARGIN = 1.2              # distancia al borde a partir de la cual se gira
WINDOW_MIN = 0.0                   # limites por defecto de la ventana de turtlesim
WINDOW_MAX = 11.08

# Pose inicial por defecto de turtle1 en turtlesim
DEFAULT_X = 5.544445
DEFAULT_Y = 5.544445
DEFAULT_THETA = 0.0


class MoveTurtle(Node):
    """Nodo principal que controla la(s) tortuga(s) de turtlesim."""

    def __init__(self):
        super().__init__('move_turtle_node')

        # --- LIDER: turtle1 ---
        self.cmd_vel_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.current_pose = None
        self.pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10
        )

        # Estado persistente para el movimiento fluido y simultaneo
        self.current_v = 0.0
        self.current_w = 0.0
        self.last_key_time = time.time()

        # Clientes de servicio para turtle1
        self.teleport_client = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        self.set_pen_client = self.create_client(SetPen, '/turtle1/set_pen')
        self.clear_client = self.create_client(Empty, '/clear')
        self.spawn_client = self.create_client(Spawn, '/spawn')
        self.kill_client = self.create_client(Kill, '/kill')

        # Estado del lapiz de turtle1
        self.pen_on = True
        self.pen_color = (255, 255, 255)
        self.pen_width = 3
        self.initials_mode = False

        # --- SEGUIDOR: turtle2 ---
        self.turtle2_spawned = False
        self.pose2 = None
        self.pose2_sub = self.create_subscription(Pose, '/turtle2/pose', self.pose2_callback, 10)
        self.cmd_vel2_pub = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)
        
        # Timer para calcular el seguimiento constantemente a 20Hz (0.05s)
        self.follower_timer = self.create_timer(0.05, self.follower_control_callback)

        # Guardamos la configuracion original de la terminal para restaurarla al salir
        self.original_term_settings = termios.tcgetattr(sys.stdin)

        self.get_logger().info(
            '\nNodo move_turtle iniciado.\n'
            '  [Flechas]: mover la tortuga de forma fluida, simultanea y sin bloqueos\n'
            '  [ I ]: Alternar Modo Iniciales ON/OFF\n'
            '  --- MODO NORMAL ---\n'
            '      S: cuadrado | T: triangulo | R: reset total | P: lapiz | A: trayectoria auto\n'
            '  --- MODO INICIALES ---\n'
            '      D, S, P, F, C: Dibujar letras individualmente\n'
            '  --- ACCIONES ESPECIALES ---\n'
            '  [ V ]: Iniciar secuencia de VIDEO (D S P S / D F C C)\n'
            '  [ 2 ]: Generar a turtle2 (Seguidor)\n'
            '  [ 3 ]: Eliminar a turtle2\n'
            '  [ Q ]: detener el movimiento / abortar accion (Ctrl+C para salir)\n'
        )

        # Hilo dedicado que procesa mensajes de ROS 2 de forma continua
        self._spin_thread = threading.Thread(target=self._spin_loop, daemon=True)
        self._spin_thread.start()

    def _spin_loop(self):
        """Funcion del hilo de fondo: mantiene vivo el procesamiento de ROS 2."""
        try:
            rclpy.spin(self)
        except Exception:
            pass  

    # ------------------------------------------------------------------
    # Lectura de teclado en modo "raw"
    # ------------------------------------------------------------------
    def get_key(self, timeout=0.05):
        rlist, _, _ = select.select([sys.stdin], [], [], timeout)
        if not rlist:
            return ''

        key = sys.stdin.read(1)
        if key == '\x1b':  
            key += sys.stdin.read(2)
        return key

    # ------------------------------------------------------------------
    # Requerimiento 4: Sistema Lider-Seguidor (Control Proporcional)
    # ------------------------------------------------------------------
    def spawn_turtle2(self):
        if self.turtle2_spawned:
            self.get_logger().info('turtle2 (Seguidor) ya esta presente en el simulador.')
            return
            
        self.get_logger().info('Generando turtle2 (seguidor) en el simulador...')
        request = Spawn.Request()
        request.x = 2.0
        request.y = 2.0
        request.theta = 0.0
        request.name = 'turtle2'
        self.call_service_sync(self.spawn_client, request, '/spawn', timeout=3.0)
        self.turtle2_spawned = True

    def kill_turtle2(self):
        if not self.turtle2_spawned:
            self.get_logger().info('turtle2 no existe actualmente en el simulador.')
            return
            
        self.get_logger().info('Eliminando a turtle2 del simulador...')
        request = Kill.Request()
        request.name = 'turtle2'
        self.call_service_sync(self.kill_client, request, '/kill', timeout=3.0)
        self.turtle2_spawned = False

    def pose2_callback(self, msg):
        self.pose2 = msg

    def follower_control_callback(self):
        if not self.turtle2_spawned or self.current_pose is None or self.pose2 is None:
            return

        dx = self.current_pose.x - self.pose2.x
        dy = self.current_pose.y - self.pose2.y
        distance = math.hypot(dx, dy)
        
        msg = Twist()
        if distance > 0.5:
            target_theta = math.atan2(dy, dx)
            error_theta = self._normalize_angle(target_theta - self.pose2.theta)
            
            msg.linear.x = 1.5 * distance      
            msg.angular.z = 6.0 * error_theta  
            
            if msg.linear.x > 3.5:
                msg.linear.x = 3.5
                
        self.cmd_vel2_pub.publish(msg)

    # ------------------------------------------------------------------
    # Publicacion de velocidades y Pose Callback (turtle1)
    # ------------------------------------------------------------------
    def publish_velocity(self, linear=0.0, angular=0.0):
        msg = Twist()
        msg.linear.x = linear
        msg.angular.z = angular
        self.cmd_vel_pub.publish(msg)

    def stop(self):
        # Reinicia los estados de memoria de velocidad
        self.current_v = 0.0
        self.current_w = 0.0
        self.publish_velocity(0.0, 0.0)

    def pose_callback(self, msg):
        self.current_pose = msg

    # ------------------------------------------------------------------
    # Requerimiento 1: Control de movimiento manual FLUIDO y SIN BLOQUEOS
    # ------------------------------------------------------------------
    def move_forward(self):
        self.current_v = LINEAR_SPEED
        self.publish_velocity(linear=self.current_v, angular=self.current_w)

    def move_backward(self):
        self.current_v = -LINEAR_SPEED
        self.publish_velocity(linear=self.current_v, angular=self.current_w)

    def turn_left(self):
        self.current_w = ANGULAR_SPEED
        self.publish_velocity(linear=self.current_v, angular=self.current_w)

    def turn_right(self):
        self.current_w = -ANGULAR_SPEED
        self.publish_velocity(linear=self.current_v, angular=self.current_w)

    # ------------------------------------------------------------------
    # Funciones auxiliares de trayectoria AUTOMATICAS (Lazo Cerrado)
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_angle(angle):
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle <= -math.pi:
            angle += 2 * math.pi
        return angle

    def _wait_for_pose(self, timeout=2.0):
        start = time.time()
        while self.current_pose is None and rclpy.ok() and time.time() - start < timeout:
            time.sleep(0.02)

    def move_by_distance(self, distance, linear_speed=AUTO_LINEAR_SPEED):
        self._wait_for_pose()
        start_x, start_y = self.current_pose.x, self.current_pose.y

        while rclpy.ok():
            key = self.get_key(timeout=0.0)
            if key.lower() == 'q' or key == CTRL_C:
                self.stop()
                self.get_logger().info('Trayectoria interrumpida por el usuario.')
                return False

            traveled = math.hypot(self.current_pose.x - start_x, self.current_pose.y - start_y)
            remaining = distance - traveled
            if remaining <= POSE_DISTANCE_TOLERANCE:
                break

            speed = linear_speed if remaining > DISTANCE_SLOWDOWN_THRESHOLD else linear_speed * SLOWDOWN_FACTOR
            self.publish_velocity(linear=speed, angular=0.0)
            time.sleep(0.02)

        self.stop()
        return True

    def turn_by_angle(self, angle_rad, angular_speed=AUTO_ANGULAR_SPEED):
        """Giro relativo exacto en lazo cerrado (USADO SOLO EN FIGURAS AUTOMATICAS)."""
        self._wait_for_pose()
        target_theta = self._normalize_angle(self.current_pose.theta + angle_rad)
        direction = 1.0 if angle_rad >= 0 else -1.0

        while rclpy.ok():
            key = self.get_key(timeout=0.0)
            if key.lower() == 'q' or key == CTRL_C:
                self.stop()
                return False

            error = self._normalize_angle(target_theta - self.current_pose.theta)
            if abs(error) < POSE_ANGLE_TOLERANCE:
                break

            speed = angular_speed if abs(error) > ANGLE_SLOWDOWN_THRESHOLD else angular_speed * SLOWDOWN_FACTOR
            self.publish_velocity(linear=0.0, angular=direction * speed)
            time.sleep(0.02)

        self.stop()
        return True

    def turn_to_angle(self, target_theta, angular_speed=AUTO_ANGULAR_SPEED):
        """Giro absoluto para corregir orientacion y evitar letras torcidas."""
        self._wait_for_pose()
        target_theta = self._normalize_angle(target_theta)

        while rclpy.ok():
            key = self.get_key(timeout=0.0)
            if key.lower() == 'q' or key == CTRL_C:
                self.stop()
                return False

            error = self._normalize_angle(target_theta - self.current_pose.theta)
            if abs(error) < POSE_ANGLE_TOLERANCE:
                break

            direction = 1.0 if error > 0 else -1.0
            speed = angular_speed if abs(error) > ANGLE_SLOWDOWN_THRESHOLD else angular_speed * SLOWDOWN_FACTOR
            self.publish_velocity(linear=0.0, angular=direction * speed)
            time.sleep(0.02)

        self.stop()
        return True

    def draw_arc(self, angle_rad, radius, linear_speed=AUTO_LINEAR_SPEED):
        """Dibuja un arco aplicando frenado proporcional para evitar sobrepasarse."""
        self._wait_for_pose()
        base_angular_speed = linear_speed / radius
        direction = 1.0 if angle_rad >= 0 else -1.0
        
        accumulated_angle = 0.0
        last_theta = self.current_pose.theta
        
        while rclpy.ok():
            key = self.get_key(timeout=0.0)
            if key.lower() == 'q' or key == CTRL_C:
                self.stop()
                return False
                
            current_theta = self.current_pose.theta
            delta_theta = self._normalize_angle(current_theta - last_theta)
            accumulated_angle += delta_theta
            last_theta = current_theta
            
            remaining = abs(angle_rad) - abs(accumulated_angle)
            if remaining <= POSE_ANGLE_TOLERANCE:
                break
                
            if remaining < ANGLE_SLOWDOWN_THRESHOLD:
                curr_v = linear_speed * SLOWDOWN_FACTOR
                curr_w = base_angular_speed * SLOWDOWN_FACTOR
            else:
                curr_v = linear_speed
                curr_w = base_angular_speed
                
            self.publish_velocity(linear=curr_v, angular=direction * curr_w)
            time.sleep(0.02)
            
        self.stop()
        return True

    # ------------------------------------------------------------------
    # Figuras Automáticas (Requerimiento 2)
    # ------------------------------------------------------------------
    def draw_square(self, side_length=SHAPE_SIDE_LENGTH):
        self.get_logger().info('Dibujando cuadrado...')
        for lado in range(4):
            if not self.move_by_distance(side_length): return
            if not self.turn_by_angle(math.pi / 2): return
        self.get_logger().info('Cuadrado completado.')

    def draw_triangle(self, side_length=SHAPE_SIDE_LENGTH):
        self.get_logger().info('Dibujando triangulo...')
        for lado in range(3):
            if not self.move_by_distance(side_length): return
            if not self.turn_by_angle(2 * math.pi / 3): return
        self.get_logger().info('Triangulo completado.')

    # ------------------------------------------------------------------
    # Iniciales Tipográficas (Requerimiento 3)
    # ------------------------------------------------------------------
    def draw_D(self):
        self.get_logger().info('Dibujando letra D...')
        self._set_pen(False) 
        if not self.turn_to_angle(math.pi / 2): return       
        if not self.move_by_distance(2.0): return            
        if not self.turn_to_angle(0.0): return               
        if not self.draw_arc(-math.pi, radius=1.0): return   
        self._set_pen(True)  
        self.turn_to_angle(0.0)

    def draw_S(self):
        self.get_logger().info('Dibujando letra S...')
        self._set_pen(False) 
        if not self.turn_to_angle(math.pi / 2): return               
        if not self.draw_arc(1.5 * math.pi, radius=0.5): return    
        if not self.turn_to_angle(0.0): return           
        if not self.draw_arc(-1.5 * math.pi, radius=0.5): return   
        self._set_pen(True)  
        self.turn_to_angle(0.0) 

    def draw_P(self):
        self.get_logger().info('Dibujando letra P...')
        self._set_pen(False) 
        if not self.turn_to_angle(math.pi / 2): return       
        if not self.move_by_distance(2.0): return            
        if not self.turn_to_angle(0.0): return               
        if not self.draw_arc(-math.pi, radius=0.65): return   
        self._set_pen(True)  
        self.turn_to_angle(0.0)

    def draw_F(self):
        self.get_logger().info('Dibujando letra F...')
        self._set_pen(False) 
        if not self.turn_to_angle(math.pi / 2): return       
        if not self.move_by_distance(2.0): return            
        if not self.turn_to_angle(0.0): return               
        if not self.move_by_distance(1.0): return            
        
        self._set_pen(True)  
        if not self.turn_to_angle(math.pi): return           
        if not self.move_by_distance(1.0): return            
        if not self.turn_to_angle(-math.pi / 2): return      
        if not self.move_by_distance(1.0): return            
        if not self.turn_to_angle(0.0): return               
        
        self._set_pen(False) 
        if not self.move_by_distance(0.8): return            
        self._set_pen(True)  
        self.turn_to_angle(0.0)

    def draw_C(self):
        self.get_logger().info('Dibujando letra C...')
        self._set_pen(True)  
        if not self.turn_to_angle(math.pi / 2): return       
        if not self.move_by_distance(2.0): return
        if not self.turn_to_angle(0.0): return               
        if not self.move_by_distance(1.0): return
        if not self.turn_to_angle(math.pi): return           
        
        self._set_pen(False) 
        if not self.draw_arc(math.pi, radius=1.0): return    
        self._set_pen(True)  
        self.turn_to_angle(0.0)

    # ------------------------------------------------------------------
    # Servicios y Secuencia de Video
    # ------------------------------------------------------------------
    def call_service_sync(self, client, request, service_name, timeout=2.0):
        if not client.wait_for_service(timeout_sec=timeout):
            self.get_logger().warn(f'Servicio {service_name} no disponible.')
            return None

        future = client.call_async(request)
        start = time.time()
        while not future.done() and time.time() - start < timeout:
            time.sleep(0.01)

        if not future.done():
            self.get_logger().warn(f'Tiempo de espera agotado llamando a {service_name}.')
            return None
        return future.result()

    def _set_pen(self, off):
        request = SetPen.Request()
        r, g, b = self.pen_color
        request.r = r
        request.g = g
        request.b = b
        request.width = self.pen_width
        request.off = 1 if off else 0
        self.call_service_sync(self.set_pen_client, request, '/turtle1/set_pen')
        self.pen_on = not off

    def toggle_pen(self):
        self._set_pen(off=self.pen_on)
        estado = 'desactivado' if not self.pen_on else 'activado'
        self.get_logger().info(f'Lapiz {estado}.')

    def teleport_to(self, x, y, theta=0.0):
        request = TeleportAbsolute.Request()
        request.x = x
        request.y = y
        request.theta = theta
        self.call_service_sync(self.teleport_client, request, '/turtle1/teleport_absolute')
        time.sleep(0.1) 

    def reset_turtle(self):
        self.get_logger().info('Reiniciando posicion y limpiando marcas...')
        was_pen_on = self.pen_on
        if was_pen_on: self._set_pen(off=True)  

        self.teleport_to(DEFAULT_X, DEFAULT_Y, DEFAULT_THETA)

        clear_req = Empty.Request()
        self.call_service_sync(self.clear_client, clear_req, '/clear')

        if was_pen_on: self._set_pen(off=False)
        self.get_logger().info('Posicion reiniciada y fondo limpio.')

    def _smart_sleep(self, duration):
        start = time.time()
        while time.time() - start < duration and rclpy.ok():
            key = self.get_key(timeout=0.0)
            if key.lower() == 'q' or key == CTRL_C:
                self.stop()
                self.get_logger().info('Secuencia interrumpida por el usuario.')
                return False
            time.sleep(0.05)
        return True

    def draw_video_sequence(self):
        self.get_logger().info('\n=== INICIANDO SECUENCIA DE VIDEO (D S P S / D F C C) ===\n')
        self.reset_turtle()
        
        if not self._smart_sleep(2.0): return
        
        fila1_bases = [(1.5, 7.0), (4.0, 7.0), (6.5, 7.0), (9.0, 7.0)]
        fila1_letras = [self.draw_D, self.draw_S, self.draw_P, self.draw_S]
        
        fila2_bases = [(1.5, 3.0), (4.0, 3.0), (6.5, 3.0), (9.0, 3.0)]
        fila2_letras = [self.draw_D, self.draw_F, self.draw_C, self.draw_C]
        
        def dibujar_con_pausa(func, x_base, y_base):
            if not rclpy.ok(): return False
            
            if func == self.draw_S:
                start_x, start_y = x_base + 1.0, y_base + 1.5
            else:
                start_x, start_y = x_base, y_base
                
            self._set_pen(True)
            self.teleport_to(start_x, start_y)
            if not self._smart_sleep(0.5): return False
            
            func()
            if not self._smart_sleep(1.5): return False
            return True

        for base, letra in zip(fila1_bases, fila1_letras):
            if not dibujar_con_pausa(letra, base[0], base[1]): return
            
        for base, letra in zip(fila2_bases, fila2_letras):
            if not dibujar_con_pausa(letra, base[0], base[1]): return
            
        self.get_logger().info('=== SECUENCIA DE VIDEO FINALIZADA ===')
        
        self._set_pen(True)
        self.teleport_to(DEFAULT_X, DEFAULT_Y)
        self._set_pen(False)

    def auto_trajectory(self):
        self.get_logger().info('Iniciando trayectoria automatica (tecla Q para detener)...')
        start_time = time.time()

        while time.time() - start_time < AUTO_TRAJECTORY_DURATION:
            key = self.get_key(timeout=0.0)
            if key.lower() == 'q' or key == CTRL_C:
                self.get_logger().info('Trayectoria automatica interrumpida por el usuario.')
                break

            if self.current_pose is None:
                self.publish_velocity(linear=AUTO_LINEAR_SPEED, angular=0.0)
                time.sleep(0.05)
                continue

            x, y = self.current_pose.x, self.current_pose.y
            cerca_del_borde = (
                x < WINDOW_MIN + BOUNDARY_MARGIN or x > WINDOW_MAX - BOUNDARY_MARGIN or
                y < WINDOW_MIN + BOUNDARY_MARGIN or y > WINDOW_MAX - BOUNDARY_MARGIN
            )

            if cerca_del_borde:
                self.publish_velocity(linear=0.0, angular=AUTO_ANGULAR_SPEED)
            else:
                self.publish_velocity(linear=AUTO_LINEAR_SPEED, angular=0.0)

            time.sleep(0.05)

        self.stop()
        self.get_logger().info('Trayectoria automatica finalizada.')

    # ------------------------------------------------------------------
    # Bucle principal
    # ------------------------------------------------------------------
    def run(self):
        tty.setraw(sys.stdin.fileno())
        try:
            while rclpy.ok():
                key = self.get_key(timeout=0.05)
                now = time.time()

                if key:
                    self.last_key_time = now
                    
                    if key == KEY_UP:
                        self.move_forward()
                    elif key == KEY_DOWN:
                        self.move_backward()
                    elif key == KEY_LEFT:
                        self.turn_left()
                    elif key == KEY_RIGHT:
                        self.turn_right()
                    
                    elif key == '2':
                        self.spawn_turtle2()
                    elif key == '3':
                        self.kill_turtle2()
                    elif key.lower() == 'v':
                        self.draw_video_sequence()
                    elif key.lower() == 'i':
                        self.initials_mode = not self.initials_mode
                        estado_str = "ACTIVADO (d, s, p, f, c dibujan letras)" if self.initials_mode else "DESACTIVADO (teclas estandar en uso)"
                        self.get_logger().info(f'\nModo Iniciales: {estado_str}\n')
                    elif key.lower() == 'q':
                        self.stop()
                    elif key == CTRL_C:
                        break
                    
                    elif self.initials_mode:
                        if key.lower() == 'd': self.draw_D()
                        elif key.lower() == 's': self.draw_S()
                        elif key.lower() == 'p': self.draw_P()
                        elif key.lower() == 'f': self.draw_F()
                        elif key.lower() == 'c': self.draw_C()
                    else:
                        if key.lower() == 's': self.draw_square()
                        elif key.lower() == 't': self.draw_triangle()
                        elif key.lower() == 'r': self.reset_turtle()
                        elif key.lower() == 'p': self.toggle_pen()
                        elif key.lower() == 'a': self.auto_trajectory()
                else:
                    # Inactividad detectada (0.15s), frenar para evitar que la tortuga siga infinitamente
                    if now - self.last_key_time > 0.15:
                        if self.current_v != 0.0 or self.current_w != 0.0:
                            self.stop()
                            
        except Exception as e:
            self.get_logger().error(f'Error en el bucle principal: {e}')
        finally:
            self.stop()
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.original_term_settings)


def main(args=None):
    rclpy.init(args=args)
    node = MoveTurtle()
    try:
        node.run()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
