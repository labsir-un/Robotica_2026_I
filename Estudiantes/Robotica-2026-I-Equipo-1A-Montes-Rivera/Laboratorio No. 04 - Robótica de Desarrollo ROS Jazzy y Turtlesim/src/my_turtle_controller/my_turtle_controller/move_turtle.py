# ==============================================================================
# Laboratorio No. 04 - Introducción a ROS 2 Jazzy Jalisco - Turtlesim
# Proyecto: Controlador Avanzado de Tortuga (POO en Python con rclpy)
# Autores: Jesus Alberto Rivera Molina, Isaac Montes Luna
# ==============================================================================

import rclpy                       # Biblioteca principal para desarrollo en ROS 2 con Python
from rclpy.node import Node         # Clase base para la creación de Nodos de ROS 2
from geometry_msgs.msg import Twist # Mensaje estándar para comandos de velocidad (lineal y angular)
from turtlesim.srv import TeleportAbsolute # Servicio para teletransportar la tortuga
from turtlesim.srv import SetPen    # Servicio para activar/desactivar y configurar el trazo (lápiz)
from turtlesim.srv import Spawn     # Servicio para instanciar (spawnear) una segunda tortuga
from turtlesim.msg import Pose      # Mensaje para recibir la pose (posición x, y, theta y velocidades)
import sys, select, tty, termios   # Módulos para interactuar con la terminal y leer teclado en tiempo real
import time                         # Biblioteca estándar de Python para temporizaciones (sleeps)
import math                         # Biblioteca matemática para operaciones con radianes (pi)
import threading                    # Biblioteca para ejecutar hilos concurrentes en segundo plano

class TurtleController(Node):
    """
    Clase principal que hereda de rclpy.node.Node.
    Implementa un controlador interactivo con lectura de teclado no bloqueante,
    dibujo de trayectorias automáticas y un controlador líder-seguidor para dos tortugas.
    """
    def __init__(self):
        # Inicialización del nodo ROS 2 con el nombre 'turtle_controller'
        super().__init__('turtle_controller')
        
        # ----------------------------------------------------------------------
        # 1. PUBLICADORES (ROS 2 Publishers)
        # ----------------------------------------------------------------------
        # Publicador de velocidad para la tortuga principal (turtle1)
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        # Publicador de velocidad para la tortuga seguidora (turtle2)
        self.publisher_turtle2 = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)
        
        # ----------------------------------------------------------------------
        # 2. CLIENTES DE SERVICIOS (ROS 2 Service Clients)
        # ----------------------------------------------------------------------
        # Cliente para teletransportar de forma absoluta a turtle1
        self.teleport_client = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        # Cliente para configurar el trazo de dibujo de turtle1
        self.set_pen_client = self.create_client(SetPen, '/turtle1/set_pen')
        # Cliente para crear (spawnear) nuevas tortugas en la ventana
        self.spawn_client = self.create_client(Spawn, '/spawn')
        
        # ----------------------------------------------------------------------
        # 3. VARIABLES DE ESTADO Y FLAGS DE CONTROL
        # ----------------------------------------------------------------------
        self.pen_enabled = True          # Estado del lápiz de turtle1 (True = Activado/Escribe)
        self.current_pose = None         # Almacena la pose actual recibida de /turtle1/pose
        self.turtle2_pose = None         # Almacena la pose actual recibida de /turtle2/pose
        self.stop_execution = False      # Bandera para interrumpir trayectorias automáticas en curso
        self.current_twist = Twist()     # Comando de velocidad actual para movimiento manual continuo
        self.motion_active = False       # Indica si hay un comando de movimiento por flechas activo
        self.turtle2_exists = False      # Controla si turtle2 ya ha sido creada en la simulación
        self.follow_mode = False         # Activa/Desactiva el modo líder-seguidor de dos tortugas
        self.initial_distance = None     # Distancia inicial entre tortugas al iniciar seguimiento
        self.initial_angle_diff = None   # Diferencia de ángulo inicial entre ambas tortugas
        
        # ----------------------------------------------------------------------
        # 4. SUSCRIPTORES (ROS 2 Subscribers)
        # ----------------------------------------------------------------------
        # Suscripción al tópico de posición de la tortuga principal
        self.pose_subscriber = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        # Suscripción al tópico de posición de la tortuga seguidora
        self.pose_subscriber_turtle2 = self.create_subscription(Pose, '/turtle2/pose', self.pose_callback_turtle2, 10)
        
        # ----------------------------------------------------------------------
        # 5. TEMPORIZADORES (ROS 2 Timers)
        # ----------------------------------------------------------------------
        # Publica la velocidad manual de las flechas a 100 Hz (cada 0.01s)
        self.motion_timer = self.create_timer(0.01, self.publish_current_motion)
        # Bucle de control del seguidor que corre a 20 Hz (cada 0.05s) en segundo plano
        self.follow_timer = self.create_timer(0.05, self.control_leader_follower)
        
        # ----------------------------------------------------------------------
        # 6. HILO DE ENTRADA (Multi-threading)
        # ----------------------------------------------------------------------
        # Lanzamos un hilo secundario exclusivo para leer el teclado sin bloquear
        # el executor principal de ROS 2 (permitiendo que callbacks y timers corran fluidamente).
        self.keyboard_thread = threading.Thread(target=self.escuchar_teclado, daemon=True)
        self.keyboard_thread.start()

    # Callback para procesar los datos de pose de turtle1
    def pose_callback(self, msg):
        self.current_pose = msg

    # Callback para procesar los datos de pose de turtle2
    def pose_callback_turtle2(self, msg):
        self.turtle2_pose = msg

    def spawn_turtle2(self):
        """Llama al servicio de simulación para crear a turtle2 en el centro de la pantalla."""
        if self.turtle2_exists:
            self.get_logger().info('Turtle2 ya existe')
            return
        
        # Estructurar la petición del servicio
        req = Spawn.Request()
        req.x = 5.5
        req.y = 5.5
        req.theta = 0.0
        req.name = 'turtle2'
        
        # Esperar la conexión al servicio con un timeout de 1 segundo
        if not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().error('Servicio /spawn no disponible')
            return
        
        # Llamada asíncrona al servicio para evitar congelar el nodo
        future = self.spawn_client.call_async(req)
        self.turtle2_exists = True
        self.get_logger().info('¡Turtle2 spawnada en el centro de la ventana!')
        time.sleep(0.5)  # Espera de cortesía para estabilizar la creación

    def calculate_distance_and_angle(self):
        """Calcula la distancia y orientación relativa en 2D entre ambas tortugas."""
        if self.current_pose is None or self.turtle2_pose is None:
            return None, None
        
        dx = self.current_pose.x - self.turtle2_pose.x
        dy = self.current_pose.y - self.turtle2_pose.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Diferencia de ángulo en la orientación actual
        angle_diff = self.current_pose.theta - self.turtle2_pose.theta
        
        return distance, angle_diff

    def follow_turtle1(self):
        """Activa el seguidor automático. Si no existe turtle2, la crea."""
        if not self.turtle2_exists:
            self.spawn_turtle2()
        
        # Esperar hasta 2 segundos para asegurar la recepción de poses por los suscriptores
        for _ in range(20):
            if self.current_pose is not None and self.turtle2_pose is not None:
                break
            time.sleep(0.1)
        
        if self.current_pose is None or self.turtle2_pose is None:
            self.get_logger().warning('No se pudo obtener las posiciones de ambas tortugas')
            return
        
        self.follow_mode = True
        self.initial_distance, self.initial_angle_diff = self.calculate_distance_and_angle()
        if self.initial_distance is not None:
            self.get_logger().info(f'¡Seguimiento activado! Distancia inicial: {self.initial_distance:.2f} unidades')
        else:
            self.get_logger().info('¡Seguimiento activado!')

    def control_leader_follower(self):
        """
        Implementa un Controlador Proporcional (P) en lazo cerrado.
        Ajusta la velocidad lineal y angular de turtle2 en función de la pose de turtle1.
        """
        if not self.follow_mode or not self.turtle2_exists:
            return
        
        if self.current_pose is None or self.turtle2_pose is None:
            return
            
        # Calcular el vector de error de distancia
        dx = self.current_pose.x - self.turtle2_pose.x
        dy = self.current_pose.y - self.turtle2_pose.y
        distance = math.sqrt(dx**2 + dy**2)
        
        msg = Twist()
        safe_distance = 1.2  # Distancia de seguridad para evitar colisión de texturas
        
        if distance > safe_distance:
            # Ángulo de orientación objetivo hacia turtle1
            target_angle = math.atan2(dy, dx)
            # Error de orientación angular
            angle_error = target_angle - self.turtle2_pose.theta
            
            # Normalizar el ángulo en el rango [-pi, pi] para evitar giros de 360 grados innecesarios
            angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))
            
            # Ganancias proporcionales sintonizadas
            kp_linear = 1.5
            kp_angular = 5.0
            
            # Leyes de control Proporcional
            msg.linear.x = kp_linear * (distance - safe_distance)
            msg.angular.z = kp_angular * angle_error
            
            # Límites de seguridad física para suavizar el comportamiento en la simulación
            msg.linear.x = min(msg.linear.x, 3.0)
            msg.angular.z = max(min(msg.angular.z, 4.0), -4.0)
        else:
            # Si se entra en el área de seguridad, detener por completo a turtle2
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            
        self.publisher_turtle2.publish(msg)

    def _stop_turtle(self):
        """Detiene el movimiento de la tortuga principal publicando velocidades nulas."""
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.publisher_.publish(msg)

    def _stop_turtle2(self):
        """Detiene el movimiento de la segunda tortuga."""
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.publisher_turtle2.publish(msg)

    def _publish_vel_for_duration(self, linear_x: float, angular_z: float, duration: float):
        """
        Método robusto contra timeouts en Turtlesim.
        Publica repetidamente comandos Twist a una frecuencia constante (50 Hz).
        """
        rate = 0.02  # Periodo de 20ms (Frecuencia de 50 Hz)
        steps = int(duration / rate)
        msg = Twist()
        msg.linear.x = linear_x
        msg.angular.z = angular_z
        
        for _ in range(steps):
            if self.stop_execution:
                break
            self.publisher_.publish(msg)
            time.sleep(rate)
            
        self._stop_turtle()

    def _move_forward(self, speed: float, duration: float):
        """Avanza linealmente a una velocidad dada durante un tiempo determinado."""
        self._publish_vel_for_duration(speed, 0.0, duration)

    def _turn(self, speed: float, duration: float):
        """Gira angularmente en su propio eje durante un tiempo determinado."""
        self._publish_vel_for_duration(0.0, speed, duration)

    def _teleport_to(self, x: float, y: float, theta: float = 0.0):
        """Llama al servicio de teletransportación absoluto desactivando previamente el lápiz para no rayar."""
        self.set_pen(False) # Desactivar trazo para evitar rayas de rastro al desplazarse
        time.sleep(0.1)     # Pequeña espera para sincronizar los llamados a los servicios de Turtlesim
        
        req = TeleportAbsolute.Request()
        req.x = x
        req.y = y
        req.theta = theta

        if not self.teleport_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().error('Servicio /turtle1/teleport_absolute no disponible')
            return False

        self.teleport_client.call_async(req)
        time.sleep(0.2)     # Esperar la ejecución física antes de que inicie la siguiente instrucción
        return True

    def triangulo(self):
        """Trayectoria automática para dibujar un triángulo equilátero en base a 3 iteraciones."""
        self.stop_execution = False
        self.get_logger().info('¡Tecla "t" detectada! Moviendo la tortuga')
        for _ in range(3):
            if self.stop_execution:
                break
            self._move_forward(2.0, 1.0)
                
            if self.stop_execution:
                break
            # Giro exterior de un triángulo equilátero (120 grados = 2*pi/3 radianes)
            self._turn(2 * math.pi / 3, 1.0)
                
        self._stop_turtle()
        
    def reinicio_pos(self):
        """Interrumpe ejecuciones activas y resetea a la tortuga al centro de la ventana."""
        self.stop_execution = True
        self._teleport_to(5.5, 5.5, 0.0)

    # ==========================================================================
    # DIBUJO AUTOMÁTICO DE LETRAS PERSONALIZADAS (Iniciales: J, A, R, M, I, L)
    # ==========================================================================

    def letra_j(self):
        self.stop_execution = False
        self.get_logger().info('Dibujando la letra J')
        if not self._teleport_to(1.0, 1.0, 0.0):
            return
        self.set_pen(True)
        self._move_forward(1.0, 1.0)
        self._turn(math.pi/2, 1.0)
        self._move_forward(2.0, 1.0)
        self._turn(math.pi/2, 1.0)
        self._move_forward(1.0, 1.0)
        self._turn(math.pi, 1.0)
        self._move_forward(2.0, 1.0)
        self._stop_turtle()

    def letra_a(self):
        self.stop_execution = False
        self.get_logger().info('Dibujando la letra A')
        if not self._teleport_to(3.5, 1.0, 0.0):
            return
        self.set_pen(True)
        self._turn(5*math.pi/12, 1.0)
        self._move_forward(2.0, 1.0)
        self._turn(-10*math.pi/12, 1.0)
        self._move_forward(2.0, 1.0)
        self._turn(math.pi, 1.0)
        self._move_forward(0.6, 1.0)
        self._turn(5*math.pi/12, 1.0)
        self._move_forward(1.0, 1.0)
        self._stop_turtle()

    def letra_r(self):
        self.stop_execution = False
        self.get_logger().info('Dibujando la letra R')
        if not self._teleport_to(5.0, 1.0, 0.0):
            return
        self.set_pen(True)
        self._turn(math.pi/2, 1.0)
        self._move_forward(2.0, 1.0)
        self._turn(-math.pi/2, 1.0)
        self._move_forward(1.0, 1.0)
        self._turn(-math.pi/2, 1.0)
        self._move_forward(1.0, 1.0)
        self._turn(-math.pi/2, 1.0)
        self._move_forward(1.0, 1.0)
        self._turn(3*math.pi/4, 1.0)
        self._move_forward(1.5, 1.0)
        self._stop_turtle()

    def letra_m(self):
        self.stop_execution = False
        self.get_logger().info('Dibujando la letra M')
        if not self._teleport_to(3.5, 4.0, 0.0):
            return
        self.set_pen(True)
        self._turn(math.pi/2, 1.0)
        self._move_forward(2.0, 1.0)
        self._turn(-5*math.pi/6, 1.0)
        self._move_forward(1.0, 1.0)
        self._turn(4*math.pi/6, 1.0)
        self._move_forward(1.0, 1.0)
        self._turn(-5*math.pi/6, 1.0)
        self._move_forward(2.0, 1.0)
        self._stop_turtle()

    def letra_i(self):
        self.stop_execution = False
        self.get_logger().info('Dibujando la letra I')
        if not self._teleport_to(1.0, 4.0, 0.0):
            return
        self.set_pen(True)
        self._move_forward(2.0, 1.0)
        self._turn(math.pi, 1.0)
        self._move_forward(1.0, 1.0)
        self._turn(-math.pi/2, 1.0)
        self._move_forward(2.0, 1.0)
        self._turn(math.pi/2, 1.0)
        self._move_forward(1.0, 1.0)
        self._turn(math.pi, 1.0)
        self._move_forward(2.0, 1.0)
        self._stop_turtle()

    def letra_l(self):
        self.stop_execution = False        
        self.get_logger().info('Dibujando la letra L')
        if not self._teleport_to(5.5, 4.0, 0.0):
            return
        self.set_pen(True)
        self._turn(math.pi/2, 1.0)
        self._move_forward(2.0, 1.0)
        self._turn(math.pi, 1.0)
        self._move_forward(2.0, 1.0)
        self._turn(math.pi/2, 1.0)
        self._move_forward(1.0, 1.0)
        self._stop_turtle()

    def set_pen(self, enable: bool):
        """Llama al servicio /turtle1/set_pen asíncronamente para activar/desactivar el lápiz 26,72,255."""
        req = SetPen.Request()
        req.r = 26
        req.g = 72
        req.b = 255
        req.width = 3
        req.off = 0 if enable else 1

        if not self.set_pen_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().error('Servicio /turtle1/set_pen no disponible')
            return

        self.set_pen_client.call_async(req)
        self.get_logger().info('Lápiz ' + ('activado' if enable else 'desactivado'))

    def publish_current_motion(self):
        """Se ejecuta en el temporizador motion_timer para mantener el movimiento manual continuo de las flechas."""
        if self.motion_active:
            self.publisher_.publish(self.current_twist)

    def move_linear(self, speed: float):
        """Configura velocidad lineal manual interrumpiendo cualquier dibujo automático."""
        self.stop_execution = True
        self.current_twist = Twist()
        self.current_twist.linear.x = speed
        self.current_twist.angular.z = 0.0
        self.motion_active = True

    def move_angular(self, speed: float):
        """Configura velocidad angular manual interrumpiendo cualquier dibujo automático."""
        self.stop_execution = True
        self.current_twist = Twist()
        self.current_twist.linear.x = 0.0
        self.current_twist.angular.z = speed
        self.motion_active = True

    def lapiz(self):
        """Activa/Desactiva el estado local del lápiz al pulsar la tecla 'p'."""
        self.pen_enabled = not self.pen_enabled
        self.set_pen(self.pen_enabled)

    def bordes(self):
        """
        Trayectoria automática continua de rebote en los límites.
        Detecta proximidad a los límites de la ventana del simulador y gira en sentido contrario.
        """
        self.stop_execution = False
        if self.current_pose is None:
            self.get_logger().warning('Posición de la tortuga no disponible aún')
            return
        
        self.get_logger().info('Iniciando evasión de bordes automática continua...')
        while not self.stop_execution:
            # Límites de la ventana de Turtlesim (tamaño aprox. 11.0 x 11.0)
            if (self.current_pose.x < 0.1 or self.current_pose.x > 10.9 or 
                self.current_pose.y < 0.1 or self.current_pose.y > 10.9):
                self.get_logger().info('¡Borde detectado! Girando...')
                
                # Girar 120 grados (2*pi/3) en su lugar de forma controlada
                self._publish_vel_for_duration(0.0, 2 * math.pi / 3, 1.0)
                # Avanzar 2 segundos lineales para salir de la zona límite
                self._publish_vel_for_duration(2.0, 0.0, 1.0)
            else:
                # Si está dentro de zona segura, avanzar continuamente a velocidad segura
                msg = Twist()
                msg.linear.x = 2.0
                msg.angular.z = 0.0
                self.publisher_.publish(msg)
                time.sleep(0.1)  # Tasa de lectura de límites (10 Hz)
        
        self._stop_turtle()

    def detener(self):
        """Detiene todos los movimientos manuales o automáticos activos inmediatamente."""
        self.stop_execution = True
        self.motion_active = False
        self.current_twist = Twist()
        self._stop_turtle()
        self.get_logger().info('¡Tortuga detenida!')

    def cuadrado(self):
        """Trayectoria automática modular de 4 pasos para dibujar un cuadrado exacto."""
        self.stop_execution = False
        for _ in range(4):
            if self.stop_execution:
                break
            self._move_forward(2.0, 1.0)
                
            if self.stop_execution:
                break
            # Giro de 90 grados exactos (pi/2)
            self._turn(math.pi / 2, 1.0)
                
        self._stop_turtle()
        self.get_logger().info('¡Cuadrado completado!')

    def iniciar_trayectoria(self, target_func):
        """
        Manejador de Concurrencia de Hilos (Thread Synchronization).
        Detiene de forma segura cualquier hilo automático en ejecución, espera a que muera,
        y lanza ordenadamente el nuevo hilo seleccionado para evitar movimientos caóticos superpuestos.
        """
        self.stop_execution = True
        self.motion_active = False
        
        def worker():
            time.sleep(0.15)  # Tiempo de espera estratégico para asegurar que el hilo anterior terminó
            self.stop_execution = False
            target_func()
            
        threading.Thread(target=worker, daemon=True).start()

    def escuchar_teclado(self):
        """
        Bucle de lectura de teclado de bajo nivel en un hilo secundario continuo.
        Utiliza os.read para evitar buffers internos de Python y select para lectura no bloqueante.
        """
        import os
        settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            while rclpy.ok():
                rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
                if rlist:
                    # Leemos directamente del descriptor del SO sin buffering de TextIOWrapper
                    data = os.read(sys.stdin.fileno(), 3)
                    if not data:
                        continue
                    
                    seq = data.decode('utf-8', errors='ignore')
                    seq_lower = seq.lower()
                    
                    if seq == '\x03':  # Ctrl+C
                        rclpy.shutdown()
                        break

                    if seq.startswith('\x1b'):
                        # Procesar secuencias de escape ANSI de las flechas
                        if seq_lower == '\x1b[a':
                            self.move_linear(1.5)
                        elif seq_lower == '\x1b[b':
                            self.move_linear(-1.5)
                        elif seq_lower == '\x1b[c':
                            self.move_angular(-2.0)
                        elif seq_lower == '\x1b[d':
                            self.move_angular(2.0)
                        continue

                    # Si es una tecla simple de una sola letra, procesar
                    if len(seq) == 1:
                        self.procesar_tecla(seq_lower)
        except Exception as e:
            self.get_logger().error(f'Error en hilo de teclado: {e}')
        finally:
            # Devolver la terminal a su estado original (cooked mode) al finalizar
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

    def procesar_tecla(self, key):
        """Realiza el enrutamiento de la tecla presionada a la función correspondiente."""
        match key:
            case 's':
                self.iniciar_trayectoria(self.cuadrado)
            case 't':
                self.iniciar_trayectoria(self.triangulo)
            case 'z':
                self.reinicio_pos()
            case 'p':
                self.lapiz()
            case 'x':
                self.iniciar_trayectoria(self.bordes)
            case 'q':
                self.detener()
            case 'j':
                self.iniciar_trayectoria(self.letra_j)
            case 'a':
                self.iniciar_trayectoria(self.letra_a)
            case 'r':
                self.iniciar_trayectoria(self.letra_r)
            case 'm':
                self.iniciar_trayectoria(self.letra_m)
            case 'i':
                self.iniciar_trayectoria(self.letra_i)
            case 'l':
                self.iniciar_trayectoria(self.letra_l)
            case 'f':
                # Ejecutar el controlador líder-seguidor en un hilo independiente para evitar
                # bloquear la lectura del teclado en la espera inicial de poses
                threading.Thread(target=self.follow_turtle1, daemon=True).start()
            case _:
                pass
            
def main(args=None):
    # Inicialización del contexto rclpy
    rclpy.init(args=args)
    
    # Instanciación del nodo controlador
    node = TurtleController()
    
    try:
        # Bucle de eventos de ROS 2 (Spinning)
        rclpy.spin(node)
    except KeyboardInterrupt:
        # Captura un cierre limpio mediante señal Ctrl+C
        node.get_logger().info('Cerrando nodo por teclado...')
    finally:
        # Destruir el nodo de forma explícita y apagar el contexto
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()