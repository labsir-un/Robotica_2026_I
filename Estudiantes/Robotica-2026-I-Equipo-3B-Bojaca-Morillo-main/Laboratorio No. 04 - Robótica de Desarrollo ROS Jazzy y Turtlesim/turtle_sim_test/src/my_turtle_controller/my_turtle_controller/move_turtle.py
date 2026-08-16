"""
Nodo ROS2 para controlar tortugas en el entorno turtlesim.
Este script permite:
- Control manual mediante el teclado.
- Seguir trayectorias predefinidas (letras, formas).
- Seguir a una tortuga líder (turtle2).
- Generación de trayectorias aleatorias.
- Dibujar con un lápiz.
"""

import math
import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import SetPen, TeleportAbsolute
from std_srvs.srv import Empty #Para Clear
from turtlesim.srv import Spawn #Para el seguidor
from pynput import keyboard

class TurtleController(Node):
    """
    Clase de controlador para gestionar múltiples tortugas y sus comportamientos.
    Gestiona la comunicación con turtlesim a través de temas y servicios ROS2.
    """
    def __init__(self):
        """
        Inicializa el nodo ROS2, los publishers, suscriptores y clientes de servicio.
        Configura el estado inicial para las tortugas y las trayectorias.
        """
        super().__init__('turtle_controller')

        # Publishers para controlar el movimiento (velocidad angular y lineal) de ambas tortugas
        self.pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pub2 = self.create_publisher(Twist,'/turtle2/cmd_vel', 10)
        
        # Suscriptores para obtener la posición (pose) actual de las tortugas
        self.sub = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.sub2 = self.create_subscription(Pose, '/turtle2/pose', self.pose2_callback, 10)
        
        # Clientes de servicio para acciones específicas: lápiz, teletransporte y limpieza
        self.pen_client = self.create_client(SetPen, '/turtle1/set_pen')
        self.pen2_client = self.create_client(SetPen, '/turtle2/set_pen')
        self.teleport_client = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        self.clear_client = self.create_client(Empty, '/clear')
        self.spawn_client = self.create_client(Spawn, '/spawn')

        # Bloqueos de seguridad: espera a que los servicios estén disponibles antes de continuar
        while not self.pen_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Esperando servicio SetPen...")
        while not self.teleport_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Esperando servicio TeleportAbsolute...")
        while not self.clear_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Esperando servicio /clear...")
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Esperando servicio Spawn...")


        req = Spawn.Request()
        req.x = 0.0
        req.y = 0.0
        req.theta = 0.0
        req.name = "turtle2"

        self.spawn_client.call_async(req)

        future = self.spawn_client.call_async(req)
        future.add_done_callback(lambda f: self.set_pen2())

        while not self.pen2_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Esperando servicio SetPen de turtle2...")


        # Timer principal para ejecutar la lógica de control a 100Hz (0.01s)
        self.timer = self.create_timer(0.01, self.control)
    
        # Variables de estado
        self.pose = None # Datos de la tortuga 1
        self.pose2 = None # Datos de la tortuga 2
        self.pen_down = None # Estado del lápiz (None inicial fuerza actualización)
        self.stopped = False # Indica si el robot está detenido por el usuario
        self.manual_mode = False # Flag para habilitar/deshabilitar control por teclado
        self.trayectoria_finalizada = False
        self.posiciones = [] # Lista de puntos [x, y, z] a seguir
        self.indice = 0 # Índice actual del punto de la trayectoria
        self.manual_twist = Twist() # Almacena la velocidad manual del teclado


        self.letra_M = [
            [-0.474, -0.606, 5.0],
            [-0.474, -0.606, 0.0],
            [-0.474, 0.612, 0.0],
            [-0.004, -0.595, 0.0],
            [0.474, 0.615, 0.0],
            [0.474, -0.615, 0.0],
            [0.474, -0.615, 5.0]
            ]
        
        self.letra_F = [
            [-0.337, -0.566, 5.0],
            [-0.337, -0.566, 0.0],
            [-0.337, 0.003, 0.0],
            [0.324, 0.003, 0.0],
            [-0.339, 0.003, 0.0],
            [-0.339, 0.566, 0.0],
            [0.338, 0.566, 0.0],
            [0.338, 0.566, 5.0]
            ]
        
        self.letra_T = [
            [0.42, 0.544, 5.0],
            [0.42, 0.544, 0.0],
            [-0.006, 0.544, 0.0],
            [-0.006, -0.544, 0.0],
            [-0.005, 0.544, 0.0],
            [-0.42, 0.544, 0.0],
            [-0.42, 0.544, 5.0]
            ]
        
        self.letra_G = [
            [0.454, 0.26, 5.0],
            [0.454, 0.26, 0.0],
            [0.356, 0.406, 0.0],
            [0.232, 0.486, 0.0],
            [0.083, 0.522, 0.0],
            [-0.087, 0.518, 0.0],
            [-0.279, 0.455, 0.0],
            [-0.4, 0.327, 0.0],
            [-0.45, 0.165, 0.0],
            [-0.466, 0.003, 0.0],
            [-0.447, -0.214, 0.0],
            [-0.353, -0.361, 0.0],
            [-0.241, -0.462, 0.0],
            [-0.111, -0.519, 0.0],
            [0.145, -0.522, 0.0],
            [0.329, -0.456, 0.0],
            [0.466, -0.35, 0.0],
            [0.466, -0.08, 0.0],
            [0.003, -0.08, 0.0],
            [0.003, -0.08, 5.0]
            ]
        
        self.letra_E = [
            [0.362, -0.513, 5.0],
            [0.362, -0.513, 0.0],
            [-0.362, -0.513, 0.0],
            [-0.362, 0.01, 0.0],
            [0.292, 0.009, 0.0],
            [-0.361, 0.009, 0.0],
            [-0.361, 0.514, 0.0],
            [0.337, 0.514, 0.0],
            [0.337, 0.514, 5.0]
            ]
        
        self.letra_B = [
            [-0.361, -0.513, 5.0],
            [-0.361, -0.513, 0.0],
            [-0.362, 0.514, 0.0],
            [0.08, 0.514, 0.0],
            [0.173, 0.503, 0.0],
            [0.26, 0.442, 0.0],
            [0.287, 0.373, 0.0],
            [0.29, 0.241, 0.0],
            [0.245, 0.137, 0.0],
            [0.171, 0.053, 0.0],
            [0.138, 0.042, 0.0],
            [-0.359, 0.042, 0.0],
            [0.13, 0.042, 0.0],
            [0.192, 0.017, 0.0],
            [0.269, -0.032, 0.0],
            [0.348, -0.137, 0.0],
            [0.362, -0.269, 0.0],
            [0.33, -0.385, 0.0],
            [0.25, -0.469, 0.0],
            [0.12, -0.513, 0.0],
            [0.024, -0.513, 0.0],
            [-0.157, -0.513, 0.0],
            [-0.361, -0.513, 0.0],
            [-0.361, -0.513, 5.0]
            ]

        # --- Trayectorias predefinidas ---
        self.trayectoria_cuadrado = [
            [0.5, 0.5, 5.0],
            [0.5, -0.5, 0.0],
            [-0.5, -0.5, 0.0],
            [-0.5, 0.5, 0.0],
            [0.5, 0.5, 0.0],
            [0.0, 0.0, 5.0]
            ]
        self.trayectoria_triangulo = [
            [0.0, 0.577350, 5.0],
            [-0.5,-0.2888675, 0.0],
            [0.5,-0.288675, 0.0],
            [0.0,0.57735, 0.0],
            [0.0, 0.0, 5.0]
            ]
        






        self.set_pen(False)
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

    def pose2_callback(self, msg):
        """Callback para recibir la pose de la tortuga2."""
        self.pose2 = msg
    
    def pose_callback(self, msg):
        """Callback para recibir la pose de la tortuga1."""
        self.pose = msg


    def set_pen(self, down):
        """Configura el estado del lápiz para la tortuga1.
        
        Args:
            down (bool): True si el lápiz está abajo (dibujando), False de lo contrario.
        """
        if self.pen_down == down: return
        self.pen_down = down
        req = SetPen.Request()
        req.r, req.g, req.b, req.width = 255, 255, 255, 5
        req.off = not down
        self.pen_client.call_async(req)
    
    def set_pen2(self):
        """Configura el estado del lápiz específicamente para la tortuga2."""
        req = SetPen.Request()
        req.r = 255
        req.g = 0
        req.b = 0
        req.width = 1      # El grosor mínimo
        req.off = False    # Dibujar
        self.pen2_client.call_async(req)
    
    def set_theta(self, theta):
        """Teletransporta la tortuga1 a una orientación (theta) específica."""
        req = TeleportAbsolute.Request()
        req.x, req.y, req.theta = self.pose.x, self.pose.y, theta
        self.teleport_client.call_async(req)


    def on_key_press(self, key):
        """Maneja la entrada del teclado para cambiar modos y control manual."""
        try:
            k = key.char
            # --- Controles de Flechas ---
            if k == 's':
                self.manual_mode = False
                self.ajustar_trayectoria('cuadrado',self.trayectoria_cuadrado)
                self.manual_twist = Twist()
            elif k == 't':
                self.manual_mode = False
                self.ajustar_trayectoria('triangulo',self.trayectoria_triangulo)
                self.manual_twist = Twist()
            elif k == 'r':
                self.manual_mode = False
                req = TeleportAbsolute.Request()
                req.x, req.y, req.theta = 5.5, 5.5, 0.0
                self.teleport_client.call_async(req)
                self.stopped = False
                self.manual_twist = Twist()
            elif k == 'p':
                self.set_pen(not self.pen_down)
            elif k == 'a':
                self.manual_mode = False
                self.stopped = False
                self.get_logger().info("Escribiendo trayectoria aleatoria")
                self.posiciones = self.generar_trayectoria_random()
                self.indice = 0
                self.trayectoria_finalizada = False
                self.manual_twist = Twist()
            elif k == 'q':
                self.stopped = True
                self.manual_twist = Twist()
                self.set_pen(False)
            elif k == 'c':
                self.get_logger().info("Limpiando pantalla")
                req = Empty.Request()
                self.clear_client.call_async(req)
            elif k == 'g':
                self.manual_mode = False
                self.ajustar_trayectoria('G',self.letra_G)
                self.manual_twist = Twist()
            elif k == 'e':
                self.manual_mode = False
                self.ajustar_trayectoria('E',self.letra_E)
                self.manual_twist = Twist()
            elif k == 'b':
                self.manual_mode = False
                self.ajustar_trayectoria('B',self.letra_B)
                self.manual_twist = Twist()
            elif k == 'm':
                self.manual_mode = False
                self.ajustar_trayectoria('M',self.letra_M)
                self.manual_twist = Twist()
            elif k == 'f':
                self.manual_mode = False
                self.ajustar_trayectoria('F',self.letra_F)
                self.manual_twist = Twist()
            elif k == 'v':
                self.manual_mode = False
                self.ajustar_trayectoria('T',self.letra_T)
                self.manual_twist = Twist()
    
        except AttributeError:
            # Esto captura las flechas si no vienen como 'char'
            if key == keyboard.Key.up:
                self.manual_mode = True
                self.manual_twist.linear.x = self.manual_twist.linear.x + 1.0
            elif key == keyboard.Key.down:
                self.manual_mode = True
                self.manual_twist.linear.x = self.manual_twist.linear.x - 1.0
            elif key == keyboard.Key.left:
                self.manual_mode = True
                self.manual_twist.angular.z = self.manual_twist.angular.z + 0.75
            elif key == keyboard.Key.right:
                self.manual_mode = True
                self.manual_twist.angular.z = self.manual_twist.angular.z - 0.75
    
    def ajustar_trayectoria(self, trayectoria_a_dibujar, trayectoria):
        """Ajusta y prepara la trayectoria objetivo basada en la pose actual."""
        self.get_logger().info(f"Dibujando '{trayectoria_a_dibujar}'")
        if self.pose is not None: #Si hay una pose valida
                    nueva_trayectoria = [] #Nueva trayecoria vacia
                    for punto in trayectoria: #Realiza la copia
                        # Traducimos los puntos relativos a coordenadas absolutas
                        # usando la posición actual de la tortuga como origen.
                        # El min/max asegura que la tortuga se mantenga dentro del área 
                        # de simulación (aprox 0.1 a 10.9).
                        nueva_trayectoria.append([
                            min(10.9, max(0.1, self.pose.x + punto[0])),
                            min(10.9, max(0.1, self.pose.y + punto[1])),
                            punto[2]
                        ])
                    self.posiciones = nueva_trayectoria
                    self.indice = 0
                    self.trayectoria_finalizada = False
                    return nueva_trayectoria
        else:
            pass
    
    def generar_trayectoria_random(self):
        """Genera una trayectoria aleatoria de puntos de paso (waypoints)."""
        rng = np.random.default_rng()
        nueva_trayectoria = []
        # Punto inicial con elevación (z=5.0) para que el lápiz no dibuje al empezar
        nueva_trayectoria.append([11.0*rng.random(), 11.0*rng.random(),5.0])
        # Genera 10 puntos intermedios en el plano (z=0.0)
        for i in range(0,10):
            nueva_trayectoria.append([
                11.0*rng.random(),
                11.0*rng.random(),
                0.0
            ])
        # Punto final con elevación
        nueva_trayectoria.append([11.0*rng.random(), 11.0*rng.random(),5.0])
        return nueva_trayectoria
    
    def generar_trayectoria_random(self):
        """Genera una trayectoria aleatoria de puntos de paso (waypoints)."""
        rng = np.random.default_rng()
        nueva_trayectoria = []
        nueva_trayectoria.append([11.0*rng.random(), 11.0*rng.random(),5.0])
        for i in range(0,10):
            nueva_trayectoria.append([
                11.0*rng.random(),
                11.0*rng.random(),
                0.0
            ])
        nueva_trayectoria.append([11.0*rng.random(), 11.0*rng.random(),5.0])
        return nueva_trayectoria


    def seguir_lider(self):
        """Hace que la tortuga1 siga a la tortuga2 usando un comportamiento de dirección básico."""
        if self.pose is None or self.pose2 is None:
            return
    
        # Cálculo de la distancia y el ángulo entre la tortuga1 (seguidor) y la tortuga2 (líder)
        dx = self.pose.x - self.pose2.x
        dy = self.pose.y - self.pose2.y
    
        distancia = math.sqrt(dx*dx + dy*dy)
    
        # El ángulo objetivo es la dirección hacia la tortuga líder
        angulo = math.atan2(dy, dx)
    
        # Calculamos el error de orientación comparando el ángulo objetivo con la orientación actual de la líder
        error = angulo - self.pose2.theta
    
        # Normalizamos el error para que esté en el rango [-pi, pi]
        while error > math.pi:
            error -= 2*math.pi
    
        while error < -math.pi:
            error += 2*math.pi
    
        msg = Twist()
    
        # Si el error de orientación es significativo, aplicamos un torque angular proporcional al error
        if abs(error) > 0.05:
            msg.angular.z = 1.6 * error
    
        # Si hay distancia suficiente, aplicamos una velocidad lineal proporcional a esa distancia
        if distancia > 0.1:
            msg.linear.x = min(4.0, 0.8 * distancia)
    
        self.pub2.publish(msg)
    
    def control(self):
        """Bucle de control principal llamado por el temporizador. Maneja las prioridades de modo."""
        # Ejecuta la lógica de seguimiento de líder (si está activa)
        self.seguir_lider()
        
        # Caso base: si no tenemos datos de posición o si el robot está detenido por el usuario
        if self.pose is None or self.stopped:
            if self.stopped:
                self.pub.publish(Twist())
                self.stopped = not(self.stopped)
                self.indice = len(self.posiciones)+1
            return
    
        # PRIORIDAD 1: Control Manual. Si el modo manual está activo, ignoramos trayectorias
        # y publicamos la velocidad obtenida del teclado.
        if self.manual_mode and self.stopped == False:
            self.pub.publish(self.manual_twist)
            return
    
        # PRIORIDAD 2: Seguimiento de Trayectoria. 
        # Si ya pasamos todos los puntos, detenemos el robot y notificamos el final.
        if self.indice >= len(self.posiciones):
            self.pub.publish(Twist())
            if not self.trayectoria_finalizada:
                self.get_logger().info("Trayectoria terminada")
                self.trayectoria_finalizada = True
            return
        
        # Obtenemos el punto objetivo actual
        objetivo = self.posiciones[self.indice]
        x, y, z = objetivo[0], objetivo[1], objetivo[2]
    
        # Gestión del lápiz: 
        # Si es el primer punto, levantamos el lápiz para evitar "marcas" en el origen.
        # En los demás puntos, el lápiz baja si la coordenada z es 0.0.
        if self.indice == 0:
            self.set_pen(False)
        else:
            self.set_pen(z == 0)
    
        # Cálculo de navegación hacia el punto objetivo
        dx, dy = x - self.pose.x, y - self.pose.y
        distancia = math.sqrt(dx**2 + dy**2)
        angulo_obj = math.atan2(dy, dx)
        error = angulo_obj - self.pose.theta
        
        # Normalización del error de orientación
        while error > math.pi: error -= 2 * math.pi
        while error < -math.pi: error += 2 * math.pi
    
        msg = Twist()
        # Si hay un error de ángulo, giramos primero (prioridad de orientación)
        if abs(error) > 0.01:
            self.set_theta(angulo_obj)
        # Si ya estamos orientados correctamente y hay distancia, avanzamos
        elif distancia > 0.01:
            msg.linear.x = min(10.0, 5.0*distancia)
        # Si estamos muy cerca del punto, pasamos al siguiente índice
        else:
            self.indice += 1
    
        # Publicamos el comando de movimiento final
        self.pub.publish(msg)



        

def main(args=None):
    """Punto de entrada principal para inicializar el nodo ROS2 y ejecutar el spin."""
    rclpy.init(args=args)
    node = TurtleController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()