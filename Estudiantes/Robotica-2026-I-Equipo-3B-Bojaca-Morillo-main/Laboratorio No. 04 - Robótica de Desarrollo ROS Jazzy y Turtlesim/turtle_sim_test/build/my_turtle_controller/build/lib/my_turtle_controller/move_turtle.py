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
    def __init__(self):
        super().__init__('turtle_controller')

        self.pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pub2 = self.create_publisher(Twist,'/turtle2/cmd_vel', 10)
        self.sub = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.sub2 = self.create_subscription(Pose, '/turtle2/pose', self.pose2_callback, 10)
        self.pen_client = self.create_client(SetPen, '/turtle1/set_pen')

        self.pen2_client = self.create_client(SetPen, '/turtle2/set_pen')


        while not self.pen_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Esperando servicio SetPen...")

        while not self.pen2_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Esperando servicio SetPen de turtle2...")

        self.teleport_client = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        while not self.teleport_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Esperando servicio TeleportAbsolute...")

        self.clear_client = self.create_client(Empty, '/clear')
        while not self.clear_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Esperando servicio /clear...")

        self.spawn_client = self.create_client(Spawn, '/spawn')
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Esperando servicio Spawn...")

        self.timer = self.create_timer(0.01, self.control)
    
        self.pose = None #tortuga1
        self.pose2 = None #tortua2
        self.pen_down = None #Se inicia en None para que con la primer llamada actualice a false
        self.stopped = False
        self.manual_mode = False # bandera para control manual
        self.trayectoria_finalizada = False
        self.posiciones = []
        self.indice = 0
        self.manual_twist = Twist() # Variable para guardar la velocidad manual

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
        


        req = Spawn.Request()
        req.x = 0.0
        req.y = 0.0
        req.theta = 0.0
        req.name = "turtle2"

        self.spawn_client.call_async(req)

        future = self.spawn_client.call_async(req)
        future.add_done_callback(lambda f: self.set_pen2())



        self.set_pen(False)
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

    def pose2_callback(self, msg):
        self.pose2 = msg

    def pose_callback(self, msg):
        self.pose = msg

    def set_pen(self, down):
        if self.pen_down == down: return
        self.pen_down = down
        req = SetPen.Request()
        req.r, req.g, req.b, req.width = 255, 255, 255, 5
        req.off = not down
        self.pen_client.call_async(req)

    def set_pen2(self):
        req = SetPen.Request()
        req.r = 255
        req.g = 0
        req.b = 0
        req.width = 1      # El grosor mínimo
        req.off = False    # Dibujar
        self.pen2_client.call_async(req)

    def set_theta(self, theta):
        req = TeleportAbsolute.Request()
        req.x, req.y, req.theta = self.pose.x, self.pose.y, theta
        self.teleport_client.call_async(req)

    def on_key_press(self, key):
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
        self.get_logger().info(f"Dibujando '{trayectoria_a_dibujar}'")
        if self.pose is not None: #Si hay una pose valida
                    nueva_trayectoria = [] #Nueva trayecoria vacia
                    for punto in trayectoria: #Realiza la copia
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
        if self.pose is None or self.pose2 is None:
            return

        dx = self.pose.x - self.pose2.x
        dy = self.pose.y - self.pose2.y

        distancia = math.sqrt(dx*dx + dy*dy)

        angulo = math.atan2(dy, dx)

        error = angulo - self.pose2.theta

        while error > math.pi:
            error -= 2*math.pi

        while error < -math.pi:
            error += 2*math.pi

        msg = Twist()

        if abs(error) > 0.05:
            msg.angular.z = 1.6 * error

        if distancia > 0.1:
            msg.linear.x = min(4.0, 0.8 * distancia)

        self.pub2.publish(msg)


    def control(self):
        self.seguir_lider()
        if self.pose is None or self.stopped:
            if self.stopped:
                self.pub.publish(Twist())
                self.stopped = not(self.stopped)
                self.indice = len(self.posiciones)+1
            return

         # PRIORIDAD 1: Si el modo manual está activo, usamos la velocidad de las flechas
        if self.manual_mode and self.stopped == False:
            self.pub.publish(self.manual_twist)
            return

        # PRIORIDAD 2: Si no hay modo manual, seguir la trayectoria
        if self.indice >= len(self.posiciones):
            self.pub.publish(Twist())
            if not self.trayectoria_finalizada:
                self.get_logger().info("Trayectoria terminada")
                self.trayectoria_finalizada = True
            return
        
        objetivo = self.posiciones[self.indice]
        x, y, z = objetivo[0], objetivo[1], objetivo[2]

        # Lógica del lápiz: primer punto siempre arriba, luego según z
        if self.indice == 0:
            self.set_pen(False)
        else:
            self.set_pen(z == 0)

        dx, dy = x - self.pose.x, y - self.pose.y
        distancia = math.sqrt(dx**2 + dy**2)
        angulo_obj = math.atan2(dy, dx)
        error = angulo_obj - self.pose.theta
        while error > math.pi: error -= 2 * math.pi
        while error < -math.pi: error += 2 * math.pi

        msg = Twist()
        if abs(error) > 0.01:
            self.set_theta(angulo_obj)
        elif distancia > 0.01:
            msg.linear.x = min(10.0, 5.0*distancia)
        else:
            self.indice += 1

        self.pub.publish(msg)

        

def main(args=None):
    rclpy.init(args=args)
    node = TurtleController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
