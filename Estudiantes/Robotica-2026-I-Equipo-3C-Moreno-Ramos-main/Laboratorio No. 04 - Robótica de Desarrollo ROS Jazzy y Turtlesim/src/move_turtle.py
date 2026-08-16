#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_srvs.srv import Empty
from turtlesim.srv import SetPen
from turtlesim.msg import Pose
from collections import deque

import sys
import select
import tty
import termios
import math
import random

settings = termios.tcgetattr(sys.stdin)

def get_key():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
    if rlist:
        key = sys.stdin.read(1)
        if key == '\x1b':
            key += sys.stdin.read(2)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


class TurtleController(Node):
    def __init__(self):
        super().__init__('turtle_controller')
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_sub = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.current_pose = Pose()
        
        # Timer a 0.05s para que los movimientos de coordenadas sean fluidos
        self.timer = self.create_timer(0.05, self.control_loop) 
        
        self.reset_client = self.create_client(Empty, '/reset')
        self.pen_client = self.create_client(SetPen, '/turtle1/set_pen')
        self.pen_on = True
        
        self.automation_queue = deque()
        self.auto_avoid_mode = False  # Restaurado
        
        self.get_logger().info('=== Controlador Híbrido (Letras Absolutas + Figuras Relativas) ===')
        self.get_logger().info('[M] MRC | [J] JAMB | [S] Cuadrado | [T] Triángulo')
        self.get_logger().info('[P] Lápiz ON/OFF | [R] Reiniciar | [A] Modo Evasión')

    def pose_callback(self, msg):
        self.current_pose = msg

    def call_reset_service(self):
        if self.reset_client.service_is_ready():
            self.reset_client.call_async(Empty.Request())
            self.get_logger().info('🔄 Simulación reiniciada.')

    def call_set_pen_service(self, state):
        if self.pen_client.service_is_ready():
            req = SetPen.Request()
            self.pen_on = state
            req.off = 0 if state else 1
            req.r = 255; req.g = 0; req.b = 0; req.width = 3
            self.pen_client.call_async(req)
            estado = "ENCENDIDO 🔴" if state else "APAGADO ⚪"
            self.get_logger().info(f'✏️ Lápiz {estado}')

    # --- COMANDOS PARA LA COLA HÍBRIDA ---
    def queue_pen(self, state):
        self.automation_queue.append(['PEN', state])

    def go_to(self, x, y):
        """Estrategia de Coordenadas (Para Letras)"""
        self.automation_queue.append(['GO', x, y])

    def add_move(self, lin, ang, ticks):
        """Estrategia Relativa (Para Figuras y Evasión)"""
        # Como el timer es el doble de rápido (0.05s), duplicamos los ticks internamente 
        # para mantener la misma velocidad que tenías antes en 0.1s
        self.automation_queue.append(['MOVE', lin, ang, ticks * 2])

    # --- DISEÑO CARTESIANO DE INICIALES (MANTENIDO) ---
    def generate_MRC(self):
        self.automation_queue.clear(); self.auto_avoid_mode = False
        self.get_logger().info('📐 Navegando MRC por coordenadas...')
        
        # Letra M
        self.queue_pen(False); self.go_to(2.0, 5.0)
        self.queue_pen(True);  self.go_to(2.0, 8.0)
        self.go_to(3.5, 6.5)
        self.go_to(5.0, 8.0)
        self.go_to(5.0, 5.0)
        
        # Letra R
        self.queue_pen(False); self.go_to(6.0, 5.0)
        self.queue_pen(True);  self.go_to(6.0, 8.0)
        self.go_to(7.5, 8.0)
        self.go_to(7.5, 6.5)
        self.go_to(6.0, 6.5)
        self.go_to(7.5, 5.0)
        
        # Letra C
        self.queue_pen(False); self.go_to(10.0, 8.0)
        self.queue_pen(True);  self.go_to(8.5, 8.0)
        self.go_to(8.5, 5.0)
        self.go_to(10.0, 5.0)
        self.queue_pen(False)

    def generate_JAMB(self):
        self.automation_queue.clear(); self.auto_avoid_mode = False
        self.get_logger().info('📐 Navegando JAMB por coordenadas...')
        
        # Letra J
        self.queue_pen(False); self.go_to(1.5, 8.0)
        self.queue_pen(True);  self.go_to(3.5, 8.0)  # Techo
        self.queue_pen(False); self.go_to(2.5, 8.0)
        self.queue_pen(True);  self.go_to(2.5, 5.5)  # Tronco
        self.go_to(1.5, 5.5)                         # Base gancho
        self.go_to(1.5, 6.5)                         # Punta gancho
        
        # Letra A
        self.queue_pen(False); self.go_to(4.0, 5.0)
        self.queue_pen(True);  self.go_to(5.0, 8.0)
        self.go_to(6.0, 5.0)
        self.queue_pen(False); self.go_to(4.5, 6.5)
        self.queue_pen(True);  self.go_to(5.5, 6.5)  # Trazo central
        
        # Letra M
        self.queue_pen(False); self.go_to(6.5, 5.0)
        self.queue_pen(True);  self.go_to(6.5, 8.0)
        self.go_to(7.5, 6.5)
        self.go_to(8.5, 8.0)
        self.go_to(8.5, 5.0)
        
        # Letra B
        self.queue_pen(False); self.go_to(9.0, 5.0)
        self.queue_pen(True);  self.go_to(9.0, 8.0)
        self.go_to(10.5, 7.25)
        self.go_to(9.0, 6.5)
        self.go_to(10.5, 5.75)
        self.go_to(9.0, 5.0)
        self.queue_pen(False)

    # --- FIGURAS CLÁSICAS RESTAURADAS ---
    def generate_square(self):
        self.automation_queue.clear(); self.auto_avoid_mode = False
        self.get_logger().info('📐 Dibujando Cuadrado clásico...')
        self.queue_pen(True)
        for _ in range(4):
            self.add_move(1.5, 0.0, 15)   # Avanzar
            self.add_move(0.0, 1.5708, 10) # Girar 90 grados
        self.queue_pen(False)

    def generate_triangle(self):
        self.automation_queue.clear(); self.auto_avoid_mode = False
        self.get_logger().info('📐 Dibujando Triángulo clásico...')
        self.queue_pen(True)
        for _ in range(3):
            self.add_move(1.5, 0.0, 10)    # Avanzar
            self.add_move(0.0, 2.0944, 10) # Girar 120 grados
        self.queue_pen(False)

    def generate_avoidance_sequence(self):
        self.automation_queue.clear()
        self.add_move(-1.5, 0.0, 5) # Retroceder
        self.add_move(0.0, random.choice([-1.57, 1.57]), 10) # Girar aleatorio

    def control_loop(self):
        key = get_key()
        msg = Twist()

        if key == '\x03' or key == '\x1a':
            self.get_logger().warn('🛑 Cerrando el nodo de forma segura...')
            raise KeyboardInterrupt

        if key.lower() == 'q':
            self.automation_queue.clear(); self.auto_avoid_mode = False
            self.publisher_.publish(msg); return
        elif key.lower() == 'm':   self.generate_MRC()
        elif key.lower() == 'j':   self.generate_JAMB()
        elif key.lower() == 's':   self.generate_square()
        elif key.lower() == 't':   self.generate_triangle()
        elif key.lower() == 'r':   self.automation_queue.clear(); self.auto_avoid_mode = False; self.call_reset_service(); return
        elif key.lower() == 'p':   self.call_set_pen_service(not self.pen_on); return
        elif key.lower() == 'a':
            self.auto_avoid_mode = not self.auto_avoid_mode
            self.get_logger().info(f'🤖 Modo Evasión: {"ON" if self.auto_avoid_mode else "OFF"}')
            self.automation_queue.clear()

        # MODO EVASIÓN RESTAURADO
        if self.auto_avoid_mode and not self.automation_queue:
            margin = 1.2
            if (self.current_pose.x < margin or self.current_pose.x > (11.0 - margin) or
                self.current_pose.y < margin or self.current_pose.y > (11.0 - margin)):
                self.generate_avoidance_sequence()
            else:
                msg.linear.x = 2.2
            self.publisher_.publish(msg)
            return

        # PROCESAR COLA HÍBRIDA
        if self.automation_queue:
            cmd = self.automation_queue[0]
            
            if cmd[0] == 'PEN':
                self.call_set_pen_service(cmd[1])
                self.automation_queue.popleft()
                return
                
            elif cmd[0] == 'GO':
                # Estrategia de Coordenadas
                target_x, target_y = cmd[1], cmd[2]
                dx = target_x - self.current_pose.x
                dy = target_y - self.current_pose.y
                distance = math.sqrt(dx**2 + dy**2)
                
                angle_to_target = math.atan2(dy, dx)
                angle_error = angle_to_target - self.current_pose.theta
                angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))
                
                if abs(angle_error) > 0.05 and distance > 0.05:
                    msg.angular.z = 4.0 * angle_error
                    self.publisher_.publish(msg)
                    return
                    
                if distance > 0.05:
                    msg.linear.x = 2.5 * distance
                    if msg.linear.x > 2.0: msg.linear.x = 2.0
                    self.publisher_.publish(msg)
                    return
                    
                self.automation_queue.popleft()
                self.publisher_.publish(Twist())
                return
                
            elif cmd[0] == 'MOVE':
                # Estrategia Clásica Relativa
                msg.linear.x = cmd[1]
                msg.angular.z = cmd[2]
                cmd[3] -= 1
                if cmd[3] <= 0:
                    self.automation_queue.popleft()
                self.publisher_.publish(msg)
                return

        # Control manual
        if key == '\x1b[A':    msg.linear.x = 1.5
        elif key == '\x1b[B':  msg.linear.x = -1.5
        elif key == '\x1b[D':  msg.angular.z = 1.5
        elif key == '\x1b[C':  msg.angular.z = -1.5
        elif key != '':        return
        
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TurtleController()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()