```python

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.srv import TeleportAbsolute, SetPen
from turtlesim.msg import Pose# para la posiciòn
from std_srvs.srv import Empty# para borrar el tablero
from turtlesim.srv import Spawn# Par poder traer la nueva tortuga

import curses
import threading
import time
import math


class TurtleController(Node):

    def __init__(self):
        super().__init__('turtle_controller')

        self.pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)#publisher tortuga 1
        self.pub2 = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)#publishet tortuga 2

        self.teleport = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        self.pen = self.create_client(SetPen, '/turtle1/set_pen')
        self.clear_client = self.create_client(Empty, '/clear')#inicializa lo que es el servicio de borrado
        self.spawn_client = self.create_client(Spawn, '/spawn')#inicializa lo que es el servicio para crear la nueva tortuga
        self.lin = 2.0
        self.ang = 3.5
        self.pen_on = True
        self.x = 5.5 #inicializa las variables de la posicion, primera tortuga
        self.y = 5.5
        self.x2 = 5.5 #inicializa las variables de la posicion
        self.y2 = 5.5
        self.theta = 0.0
        self.theta2 = 0.0
        self.auto_running = False
        #Se crea una suscripciòn, adentro del parentesis vienen
        #las especificaciones de la cosa
        
        self.pose_sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback1,
            10
        )
        self.pose2_sub = self.create_subscription(
            Pose,
            '/turtle2/pose',
            self.pose_callback2,
            10
        )
    #Esta funciòn se encarga de guardar la informaciòn del mensaje de la suscripciòn en nuestras variables, para la tortuga 1
    def pose_callback1(self, msg):
        self.x = msg.x
        self.y = msg.y
        self.theta = msg.theta
    def pose_callback2(self, msg):
        self.x2 = msg.x
        self.y2 = msg.y
        self.theta2 = msg.theta
    # ---------------- MOVIMIENTO ----------------
    def move(self, l=0.0, a=0.0):
        #es importante considerar que las unidades de la velocidad angular son rad/segundos
        msg = Twist()
        msg.linear.x = l
        msg.angular.z = a
        self.pub.publish(msg)

    def clear_screen(self):
        if not self.clear_client.wait_for_service(timeout_sec=1.0):
            return

        req = Empty.Request()
        self.clear_client.call_async(req)
    def follower_loop(self): #while donde se asegura de seguir a la tortuga 1

        while rclpy.ok():
            self.follow_turtle1()
            time.sleep(0.05)

    def follow_turtle1(self):
        # nuevamente un control proporcional
        # calculo de errores en x y en y
        dx = self.x - self.x2
        dy = self.y - self.y2
        # distancia total
        distance = math.sqrt(dx**2 + dy**2)
        # àngulo que falta hasta el objetivo
        angle_to_goal = math.atan2(dy, dx)
        # diferencia entre angulo a la tortuga 1 y el angulo propio de la tortuga 2
        error_angle = angle_to_goal - self.theta2
        error_angle = math.atan2(math.sin(error_angle), math.cos(error_angle))

        msg = Twist()

        # control proporcional
        msg.linear.x = 2.0 * distance
        msg.angular.z = 4.0 * error_angle# se mueve mucho màs ràpido al angulo

        self.pub2.publish(msg)
    def stop(self):
        self.move(0.0, 0.0)
    #Control proporcional para poder ubicar en el angulo deseado
    def go_to_angle(self, target):
        kp = 2.0  # ganancia de control
        
        while rclpy.ok():
            error = target - self.theta

            # normalizar error a [-pi, pi]
            error = math.atan2(math.sin(error), math.cos(error))

            if abs(error) < 0.01:
                self.stop()  # detiene el while si el error es menor al que aparece aqui
                break

            self.move(0.0, kp * error) # segun el error que tanto se mueve
            time.sleep(0.01)

        self.stop()
    # ---------------- SERVICIOS ----------------
    def reset(self):
        if not self.teleport.wait_for_service(timeout_sec=1.0):
            return

        req = TeleportAbsolute.Request()
        req.x = 5.5
        req.y = 5.5
        req.theta = 0.0
        self.teleport.call_async(req)

    def toggle_pen(self):
        if not self.pen.wait_for_service(timeout_sec=1.0):
            return

        self.pen_on = not self.pen_on

        req = SetPen.Request()
        req.r = 255
        req.g = 255
        req.b = 255
        req.width = 3
        req.off = 0 if self.pen_on else 1

        self.pen.call_async(req)
    
    # ---------------- FIGURAS ----------------
    def square(self):
        side_time = 2.0   # tiempo en el que dibuja el cuadrado

        for _ in range(4):
            # self.move es una funciòn que se define arriba, utiliza Twist y ahì se le modifican las cosas
            # avanzar recto
            self.move(2.0, 0.0)
            time.sleep(side_time)

            self.stop()
            time.sleep( 0.2)

            # giro 90°
            self.move(0.0, 2.0)  
            time.sleep(math.pi/(2*2)) # aqui estoy dividiendo el angulo deseado por su respectiva velocidad

            self.stop()
            time.sleep(0.2)

            self.stop()
    def A(self):
        self.go_to_angle(2*math.pi/3)
        # lado izquierdo
        self.move(2.0, 0.0)
        time.sleep(1.5)
        self.stop()
        time.sleep(0.2)

        self.move(0.0, self.ang)
        time.sleep((2*math.pi/3) / self.ang)

        # lado derecho
        self.move(2.0, 0.0)
        time.sleep(1.5)
        self.stop()
        time.sleep(0.2)

        # subir barra horizontal
        self.move(0.0, self.ang)
        time.sleep((math.pi)/self.ang)
        
        self.stop()
        time.sleep(0.2)
        
        self.move(2.0, 0.0)
        time.sleep(1.5/4)
        
        self.stop()
        time.sleep(0.2)

        
        self.move(0.0, -self.ang)
        time.sleep((math.pi/3) / self.ang)

        self.stop()
        time.sleep(0.2)
        
        self.move(2.0, 0.0)
        time.sleep(0.6)
        self.stop()

    
    def J(self):
        self.go_to_angle(-math.pi/2)
        # línea vertical
        self.move(2.0, 0.0)
        time.sleep(2.0)
        self.stop()
        time.sleep(0.2)

        # curva inferior (aproximación)
        self.move(2.0, -self.ang)
        time.sleep(math.pi/self.ang)

        self.stop()

    def M(self):
            self.go_to_angle(math.pi/2)
            # lado izquierdo
            self.move(2.0, 0.0)
            time.sleep(1.5)
            self.stop()
            time.sleep(0.2)

            self.go_to_angle(-math.pi/4)

            self.move(2.0, 0.0)
            time.sleep(1.0)

            self.go_to_angle(math.pi/4)

            self.move(2.0, 0.0)
            time.sleep(1.0)

            self.go_to_angle(-math.pi/2)

            self.move(2.0, 0.0)
            time.sleep(1.5)
    def S(self):
        self.go_to_angle(-math.pi/4)
        # parte superior curva
        self.move(2.0, self.ang)
        time.sleep(1.2)
        self.stop()
        time.sleep(0.2)

        self.move(2.0, -self.ang)
        time.sleep(1.2)
        self.stop()

    def D(self):
        self.go_to_angle(math.pi/2)
        # línea vertical
        self.move(2.0, 0.0)
        time.sleep(2.0)
        self.stop()
        time.sleep(0.2)

        # gira para alistarse para hacer la d
        self.move(0.0, -self.ang)
        time.sleep((math.pi/2)/self.ang)

        self.stop()
        time.sleep(0.2)

        # Aqui lo que se hace es lo siguiente, con la velocidad angular se encuentra lo que es el tiempo, haciendo la mitar de la
        # circunferencia igual a pi eso es la ditancia, por lo que la velocidad lineal se consigue mediante distancia/tiempo
        self.move((math.pi)/((math.pi)/self.ang), -self.ang)
        time.sleep((math.pi)/self.ang)

        self.stop()
        time.sleep(0.2)
        

        self.stop()
    def spawn_turtle2(self):# con esta funciòn se crea la tortuga 2
        if not self.spawn_client.wait_for_service(timeout_sec=1.0):
            return

        req = Spawn.Request()
        req.x = 1.0
        req.y = 1.0
        req.theta = 0.0
        req.name = "turtle2"

        self.spawn_client.call_async(req)    
    def triangle(self):
        side_time = 2.0 
        for _ in range(3):
            # Se mueve linealmente
            self.move(2.0, 0.0)
            time.sleep(side_time)
            # Para
            self.stop()
            time.sleep(0.2)
            # gira 120 grados,que es 2pi/3 radianes
            self.move(0.0, self.ang)
            time.sleep(2*math.pi/(3*self.ang))
            # Para
            self.stop()
            time.sleep(0.2)
            self.stop()
        

    def auto(self):

        i = 0

        while rclpy.ok() and self.auto_running:

            # Si está cerca del borde → detener y girar
            if (self.x <= 0.5 or self.x >= 10.5 or
                self.y <= 0.5 or self.y >= 10.5):

                self.stop()
                self.move(0.0, self.ang)
                time.sleep(math.pi / self.ang)
                self.stop()

            # movimiento continuo
            self.move(2.0, math.sin(i))
            time.sleep(0.4)

            i += 1


        self.stop()

# ---------------- CONTROL TECLADO ----------------
def keyboard_loop(stdscr, node: TurtleController):

    stdscr.nodelay(True)
    stdscr.clear()
    stdscr.addstr(0, 0, "Control tortuga ROS2")
    stdscr.addstr(1, 0, "Flechas: mover | C cuadrado | T triángulo| B limpia pantalla| N crear una nueva turtuga")
    stdscr.addstr(2, 0, "K auto | R reset | P pen | Q stop | X salir | Letras: A, D, J, S, M ")

    while True:
        key = stdscr.getch()
        
        if (key != ord('k') and key != -1):
            node.auto_running = False

        # Flechas
        if key == curses.KEY_UP:
            node.move(node.lin, 0.0)

        elif key == curses.KEY_DOWN:
            node.move(-node.lin, 0.0)

        elif key == curses.KEY_LEFT:
            node.move(0.0, node.ang)

        elif key == curses.KEY_RIGHT:
            node.move(0.0, -node.ang)

        # letras
        elif key == ord('q'):
            node.stop()

        elif key == ord('r'):
            node.reset()

        elif key == ord('p'):
            node.toggle_pen()

        elif key == ord('c'):
            threading.Thread(target=node.square).start()

        elif key == ord('t'):
            threading.Thread(target=node.triangle).start()

        elif key == ord('k'):
            node.auto_running = True
            threading.Thread(target=node.auto).start()
            

        elif key == ord('a'):
            threading.Thread(target=node.A).start()
       
        elif key == ord('j'):
            threading.Thread(target=node.J).start()

        elif key == ord('s'):
            threading.Thread(target=node.S).start()

        elif key == ord('d'):
            threading.Thread(target=node.D).start()
        elif key == ord('m'):
            threading.Thread(target=node.M).start()
        elif key == ord('b'):
            node.clear_screen()
        elif key == ord('n'):    
            node.spawn_turtle2()
            threading.Thread(target=node.follower_loop, daemon=True).start()
        elif key == ord('x'):
            break

        time.sleep(0.05)


# ---------------- MAIN ----------------
def main(args=None):
    rclpy.init(args=args)
    node = TurtleController()
    
    #Se crea un nuevo hilo
    spin_thread = threading.Thread(
        target=rclpy.spin,
        args=(node,),# le pasa  el nodo como argumento
        daemon=True
    )
    spin_thread.start()

    try:
        curses.wrapper(keyboard_loop, node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()

    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class TurtleController(Node):
    def __init__(self):
        super().__init__('turtle_controller')
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.timer = self.create_timer(0.5, self.move_turtle)

    def move_turtle(self):
        msg = Twist()
        msg.linear.x = 2.0   # Velocidad hacia adelante
        msg.angular.z = 1.0  # Rotación
        self.publisher_.publish(msg)
        self.get_logger().info('Moviendo la tortuga')

def main(args=None):
    rclpy.init(args=args)
    node = TurtleController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    
"""

```
