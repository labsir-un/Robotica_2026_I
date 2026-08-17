import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import Spawn, SetPen, TeleportAbsolute 
from std_srvs.srv import Empty
import math
import sys
import termios
import tty
import threading
import select
import random

# Almacenamiento de la configuración estándar de E/S de la terminal de Linux
# para su posterior restauración al finalizar la ejecución segura del programa.
settings = termios.tcgetattr(sys.stdin)

class TurtleController(Node):
    def __init__(self):
        # Inicialización del nodo maestro encargado del control cinemático de turtle1
        super().__init__('turtle_controller')
        
        # Publicador de comandos de velocidad Twist hacia el actuador del simulador
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        
        # Suscriptor al tópico de retroalimentación de posición y orientación (pose)
        self.pose_subscriber = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        
        # Instanciación de clientes de servicios para interactuar asíncronamente con turtlesim
        self.clear_client = self.create_client(Empty, '/clear')
        self.pen_client = self.create_client(SetPen, '/turtle1/set_pen')
        self.teleport_client = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        self.teleport2_client = self.create_client(TeleportAbsolute, '/turtle2/teleport_absolute')
        
        # Inicialización del estado interno del robot y modos operativos
        self.pose = Pose()
        self.pen_active = True
        self.mode = 'MANUAL'
        
        # Estructuras de datos para la gestión y ejecución de trayectorias automáticas
        self.target_waypoints = []
        self.current_waypoint_index = 0
        self.is_smooth_trajectory = False 
        
        # Inicialización de registros de control temporal y angular para la caminata aleatoria
        self.random_z = 0.0
        self.random_timer = 0
        
        # Temporizador periódico de alta frecuencia (100 Hz) para el bucle de control discreto
        self.timer = self.create_timer(0.01, self.control_loop)
        
        # Creación y lanzamiento de un hilo independiente dedicado a la escucha del teclado
        # con el fin de evitar el bloqueo del hilo principal de callbacks del Middleware
        self.keyboard_thread = threading.Thread(target=self.keyboard_listener, daemon=True)
        self.keyboard_thread.start()

        print('\r\n--- Controlador Avanzado Iniciado ---')
        print('\rFlechas = Mover | S, T, J, D, L, F = Figuras | A = Aleatorio | Q = Stop | R = Reset | P = Lápiz\r\n')

    def pose_callback(self, msg):
        # Callback síncrono encargado de actualizar el vector de estado cinemático del robot líder
        self.pose = msg

    def keyboard_listener(self):
        # Captura asíncrona de caracteres en terminal mediante E/S no bloqueante de Linux
        settings = termios.tcgetattr(sys.stdin)
        try:
            # Reconfiguración de la terminal a modo raw (lectura cruda carácter por carácter)
            tty.setraw(sys.stdin.fileno())
            while rclpy.ok():
                # Multiplexación de E/S con un timeout de 100 ms para inspeccionar el flujo de entrada
                rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
                key = ''
                if rlist:
                    key = sys.stdin.read(1)
                    # Gestión del escape de caracteres para decodificar las flechas del teclado
                    if key == '\x1b':  
                        key += sys.stdin.read(2)
                
                # Mapeo cinemático directo en lazo abierto bajo el modo operativo manual
                if self.mode == 'MANUAL':
                    msg = Twist()
                    if key == '\x1b[A':   msg.linear.x = 2.0
                    elif key == '\x1b[B': msg.linear.x = -2.0
                    elif key == '\x1b[C': msg.angular.z = -2.0
                    elif key == '\x1b[D': msg.angular.z = 2.0
                    self.publisher_.publish(msg)

                # Máquina de estados desencadenada por la entrada de caracteres alfanuméricos
                if key != '':
                    k = key.lower()
                    if k == 's':
                        print('\rDibujando Cuadrado (Modo Estricto)...\r\n')
                        self.load_trajectory([(0,0,0), (2,0,1), (2,2,1), (0,2,1), (0,0,1)], smooth=False)
                    elif k == 't':
                        print('\rDibujando Triángulo (Modo Estricto)...\r\n')
                        self.load_trajectory([(0,0,0), (2,0,1), (1,1.732,1), (0,0,1)], smooth=False)
                    elif k == 'l':
                        print('\rDibujando Letra L (Modo Estricto)...\r\n')
                        self.load_trajectory([(0,2.0,0), (0,0,1), (1.5,0,1)], smooth=False)
                    elif k == 'f':
                        print('\rDibujando Letra F (Modo Estricto)...\r\n')
                        self.load_trajectory([(0,0,0), (0,2.0,1), (1.0,2.0,1), (0,1.0,0), (0.8,1.0,1), (0,0,0)], smooth=False)
                    elif k == 'j':
                        print('\rDibujando Letra J (Modo Fluido)...\r\n')
                        self.load_trajectory(self.get_letter_J(), smooth=True)
                    elif k == 'd':
                        print('\rDibujando Letra D (Modo Fluido)...\r\n')
                        self.load_trajectory(self.get_letter_D(), smooth=True)
                    elif k == 'a':
                        print('\rModo Aleatorio Activado (No se saldrá de pantalla)\r\n') 
                        self.mode = 'AVOIDANCE'
                    elif k == 'q':
                        print('\rStop Total\r\n')
                        self.mode = 'MANUAL'
                        self.target_waypoints.clear()
                        self.publisher_.publish(Twist())
                    elif k == 'r':
                        self.reset_turtle()
                    elif k == 'p':
                        self.toggle_pen()
        finally:
            # Restauración forzada de la terminal para retornar el control al usuario de forma segura
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

    def get_letter_D(self):
        # Generación analítica de un perfil paramétrico semicircular para trazar la letra D
        pts = [(0, 0, 0), (0, 2.0, 1)] 
        for i in range(1, 14):
            theta = math.pi/2 - i * (math.pi / 14)
            dx = math.cos(theta) * 1.5
            dy = 1.0 + math.sin(theta) * 1.0
            pts.append((dx, dy, 1))
        pts.append((0, 0, 1)) 
        return pts

    def get_letter_J(self):
        # Generación geométrica por discretización circular para el arco inferior de la letra J
        pts = [(0.5, 0, 0), (0.5, -1.5, 1)] 
        for i in range(1, 10):
            theta = 0 - i * (math.pi / 9)
            dx = math.cos(theta) * 0.5
            dy = -1.5 + math.sin(theta) * 0.5
            pts.append((dx, dy, 1))
        return pts

    def load_trajectory(self, offsets, smooth=False):
        # Función matemática encargada de transformar desplazamientos relativos (offsets)
        # en coordenadas absolutas del entorno cartesiano (World frame de turtlesim)
        self.mode = 'CLOSED_LOOP'
        self.target_waypoints = []
        self.is_smooth_trajectory = smooth 
        
        start_x = self.pose.x
        start_y = self.pose.y
        
        for dx, dy, pen_down in offsets:
            # Saturación de consignas espaciales para prevenir colisiones contra los límites físicos (0 a 11)
            abs_x = max(0.2, min(10.8, start_x + dx))
            abs_y = max(0.2, min(10.8, start_y + dy))
            self.target_waypoints.append((abs_x, abs_y, pen_down))
            
        self.current_waypoint_index = 0
        self.publisher_.publish(Twist())

    def control_loop(self):
        # Bucle periódico de control cinemático conmutado por la máquina de estados del nodo
        if self.mode == 'CLOSED_LOOP' and self.target_waypoints:
            # Validación de la frontera final del arreglo de waypoints cargados
            if self.current_waypoint_index >= len(self.target_waypoints):
                print('\rTrayectoria finalizada con éxito.\r\n')
                self.mode = 'MANUAL'
                self.publisher_.publish(Twist())
                return

            # Extracción del objetivo actual de la trayectoria y conmutación del rastro (lápiz)
            target_x, target_y, pen_down = self.target_waypoints[self.current_waypoint_index]
            self.set_pen_state(bool(pen_down))

            # Cálculo numérico del error de posición euclidiana respecto al waypoint objetivo
            dx = target_x - self.pose.x
            dy = target_y - self.pose.y
            distance = math.sqrt(dx**2 + dy**2)
            
            # Cálculo del error angular y acotamiento al rango geométrico fundamental [-pi, pi]
            angle_to_target = math.atan2(dy, dx)
            angle_error = angle_to_target - self.pose.theta
            angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))

            msg = Twist()
            is_last_point = (self.current_waypoint_index == len(self.target_waypoints) - 1)
            
            # Sub-controlador 1: Perfil dinámico fluido (Smooth Mode) con tolerancias holgadas
            if self.is_smooth_trajectory:
                tolerance = 0.05 if is_last_point else 0.15
                if distance < tolerance:
                    self.current_waypoint_index += 1
                    if is_last_point: self.publisher_.publish(Twist()) 
                    return

                # Desacoplamiento de control: Si el error angular es elevado, realiza giro puro en el eje
                if abs(angle_error) > 0.4: 
                    msg.linear.x = 0.0
                    msg.angular.z = max(-2.0, min(2.0, 3.0 * angle_error))
                else:
                    # Control síncrono proporcional para velocidad lineal y velocidad angular
                    msg.linear.x = min(1.2, 1.0 * distance) 
                    msg.angular.z = 2.0 * angle_error 
            
            # Sub-controlador 2: Perfil ortogonal estricto (Strict Mode) para trazos lineales precisos
            else:
                tolerance = 0.03
                if distance < tolerance:
                    self.current_waypoint_index += 1
                    self.publisher_.publish(Twist()) 
                    return

                # Alineación geométrica estricta de alta sensibilidad previa al avance lineal
                if abs(angle_error) > 0.05: 
                    msg.linear.x = 0.0 
                    msg.angular.z = max(-2.0, min(2.0, 3.0 * angle_error))
                else:
                    msg.linear.x = min(1.2, 1.0 * distance) 
                    msg.angular.z = 2.0 * angle_error 

            self.publisher_.publish(msg)
            
        elif self.mode == 'AVOIDANCE':
            # Implementación de un comportamiento adaptativo de caminata aleatoria y rebote reactivo
            msg = Twist()
            
            # Actualización periódica de la tasa de giro aleatoria cada 500 ms (50 iteraciones)
            self.random_timer += 1
            if self.random_timer > 50:
                self.random_z = random.uniform(-1.5, 1.5)
                self.random_timer = 0
                
            msg.linear.x = 1.2
            msg.angular.z = self.random_z
            
            # Evasión de muros: Activación de zona de amortiguamiento y cálculo del vector de rebote
            margin = 1.5
            if self.pose.x < margin or self.pose.x > 11.0 - margin or self.pose.y < margin or self.pose.y > 11.0 - margin:
                msg.linear.x = 0.6 
                
                # Orientación forzada hacia las coordenadas centrales del espacio virtual (5.5, 5.5)
                angle_to_center = math.atan2(5.5 - self.pose.y, 5.5 - self.pose.x)
                angle_error = angle_to_center - self.pose.theta
                angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))
                
                # Inyección de velocidad angular límite para forzar el escape seguro del muro
                msg.angular.z = max(-3.0, min(3.0, 3.0 * angle_error))
                
            self.publisher_.publish(msg)

    def set_pen_state(self, active):
        # Gestión y filtrado de llamadas redundantes al servicio nativo /set_pen de turtlesim
        if self.pen_active == active: return
        self.pen_active = active
        req = SetPen.Request()
        # Conmutación cromática dinámica: Blanco para dibujo activo y Negro (color de fondo) para trazo invisible
        req.r, req.g, req.b = (255, 255, 255) if self.pen_active else (0, 0, 0)
        req.width = 2
        req.off = int(not self.pen_active)
        self.pen_client.call_async(req)

    def reset_turtle(self):
        # Rutina inteligente de reinicio asíncrono para preservar las entidades sin destruir nodos
        req_clear = Empty.Request()
        self.clear_client.call_async(req_clear)
        
        # Teletransportación absoluta de la tortuga líder a las coordenadas centrales nominales
        req_t1 = TeleportAbsolute.Request()
        req_t1.x = 5.544445
        req_t1.y = 5.544445
        req_t1.theta = 0.0
        self.teleport_client.call_async(req_t1)
        
        # Teletransportación síncrona del agente seguidor a su punto coordenado de origen seguro
        req_t2 = TeleportAbsolute.Request()
        req_t2.x = 2.0
        req_t2.y = 2.0
        req_t2.theta = 0.0
        self.teleport2_client.call_async(req_t2)
        
        self.target_waypoints.clear()
        self.mode = 'MANUAL'
        print('\rPosiciones y pantalla reiniciadas.\r\n')

    def toggle_pen(self):
        # Interfaz de conmutación manual de estado para el lápiz del agente líder
        self.set_pen_state(not self.pen_active)
        estado = "Activado" if self.pen_active else "Desactivado"
        print(f'\rLápiz {estado}\r\n')


class TurtleFollower(Node):
    def __init__(self):
        # Inicialización del nodo esclavo encargado del seguimiento cinemático de dos cuerpos
        super().__init__('turtle_follower')
        
        # Clientes de servicios exclusivos para la instanciación y parametrización de turtle2
        self.spawn_client = self.create_client(Spawn, '/spawn')
        self.pen_client = self.create_client(SetPen, '/turtle2/set_pen')
        
        # Inicialización de los vectores de estado de posición para ambos agentes móviles
        self.pose1 = Pose()
        self.pose2 = Pose()
        
        # Suscripción simultánea a los tópicos de telemetría espacial de ambos agentes
        self.create_subscription(Pose, '/turtle1/pose', self.pose1_callback, 10)
        self.create_subscription(Pose, '/turtle2/pose', self.pose2_callback, 10)
        
        # Publicador de comandos cinemáticos Twist exclusivo para gobernar a la tortuga seguidora
        self.publisher_ = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)
        
        # Temporizador periódico acoplado a 50 Hz para la ejecución del bucle líder-seguidor
        self.timer = self.create_timer(0.02, self.follow_loop)
        
        # Máquina de estados temporal para la instanciación segura y secuencial de turtle2 en el entorno
        self.setup_step = 0
        self.setup_timer = self.create_timer(0.5, self.setup_sequence)

    def setup_sequence(self):
        # Secuencia de inicialización física asíncrona para la creación controlada del agente esclavo
        if self.setup_step == 0:
            if self.spawn_client.service_is_ready():
                req = Spawn.Request()
                req.x = 2.0; req.y = 2.0; req.theta = 0.0; req.name = 'turtle2'
                future = self.spawn_client.call_async(req)
                # Enlace de una función callback anónima (lambda) tras la resolución exitosa del spawn
                future.add_done_callback(lambda f: self.advance_setup())
        elif self.setup_step == 1:
            if self.pen_client.service_is_ready():
                req = SetPen.Request()
                # Configuración estética fija del rastro para turtle2 (Color Rojo puro de ancho 1)
                req.r = 255; req.g = 0; req.b = 0; req.width = 1; req.off = False
                self.pen_client.call_async(req)
                self.setup_timer.cancel()

    def advance_setup(self):
        # Conmutador de la secuencia de configuración inicial
        self.setup_step = 1

    def pose1_callback(self, msg):
        # Suscriptor síncrono de la telemetría espacial del agente líder
        self.pose1 = msg

    def pose2_callback(self, msg):
        # Suscriptor síncrono de la telemetría espacial del agente esclavo
        self.pose2 = msg

    def follow_loop(self):
        # Algoritmo de control síncrono de lazo cerrado para seguimiento cinemático de objetivos móviles
        if self.pose1.x == 0.0 and self.pose1.y == 0.0:
            return 
            
        # Cálculo de la distancia euclidiana instantánea entre ambos agentes móviles
        distance = math.sqrt((self.pose1.x - self.pose2.x)**2 + (self.pose1.y - self.pose2.y)**2)
        
        # Determinación de la orientación requerida y acotamiento del error angular relativo [-pi, pi]
        angle_to_target = math.atan2(self.pose1.y - self.pose2.y, self.pose1.x - self.pose2.x)
        angle_diff = angle_to_target - self.pose2.theta
        angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))

        msg = Twist()
        
        # Lógica de zona muerta y saturación para suavizar el comportamiento del lazo proporcional
        if distance > 0.3:
            # Control por desacoplamiento: Si el error es severo, prioriza rotación pura en el eje
            if abs(angle_diff) > 0.5:
                msg.linear.x = 0.0
            else:
                # Inyección de ganancia proporcional acotada por saturación lineal superior (1.5 m/s)
                msg.linear.x = min(1.5, 1.2 * distance) 
                
            # Inyección de velocidad angular proporcional limitada magnitudinalmente a +/- 2.5 rad/s
            msg.angular.z = max(-2.5, min(2.5, 3.0 * angle_diff))
        else:
            # Frenado total de actuadores virtuales al ingresar a la vecindad de tolerancia de la meta
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            
        self.publisher_.publish(msg)

def main(args=None):
    # Inicialización del contexto de comunicación global de ROS 2
    rclpy.init(args=args)
    
    # Instanciación de un ejecutor multihilo para procesar callbacks concurrentemente
    executor = MultiThreadedExecutor()
    controller_node = TurtleController()
    follower_node = TurtleFollower()
    
    # Inyección de ambos nodos concurrentes dentro de la estructura lógica del ejecutor
    executor.add_node(controller_node)
    executor.add_node(follower_node)
    
    try:
        # Spin concurrente y asíncrono para despachar de forma eficiente los subprocesos de ROS 2
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        # Garantía estructural de cierre seguro de nodos y desenergización de librerías E/S
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        controller_node.destroy_node()
        follower_node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
