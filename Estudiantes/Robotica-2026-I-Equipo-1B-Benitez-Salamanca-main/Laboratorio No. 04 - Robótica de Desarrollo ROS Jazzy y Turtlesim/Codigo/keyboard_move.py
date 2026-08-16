import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import SetPen
from std_srvs.srv import Empty
import sys
import tty
import termios
import threading
import math

class TurtleController(Node):

    def __init__(self):
        super().__init__('turtle_controller')


        self.fd = sys.stdin.fileno()
        self.old_settings = termios.tcgetattr(self.fd)

        tty.setcbreak(self.fd)

        # Publicador de velocidades
        self.publisher_ = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # Temporizador
        self.timer = self.create_timer(0.005, self.move_turtle)

        # Suscriptor a la posición
        self.pose_sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        # Clientes de servicios
        self.reset_client = self.create_client(
            Empty,
            '/reset'
        )

        self.pen_client = self.create_client(
            SetPen,
            '/turtle1/set_pen'
        )

        # Variables de movimiento
        self.linear = 0.0
        self.angular = 0.0

        # Estado del lápiz
        self.pen_on = True

        # Modo automático
        self.auto_mode = False

        # Posición inicial
        self.x = 5.5
        self.y = 5.5
        self.theta = 0.0

        self.stop_requested = False

        threading.Thread(target=self.keyboard_loop, daemon=True).start()

    def mover(self, linear, angular, tiempo):

        self.linear = linear
        self.angular = angular

        fin = time.perf_counter() + tiempo

        while time.perf_counter() < fin:

            if self.stop_requested:
                break

        self.linear = 0.0
        self.angular = 0.0

        # Esperar un ciclo para que el timer publique el paro
        time.sleep(0.012)

    def dibujar_cuadrado(self):

        self.stop_requested = False

        lado = 2.0
        velocidad = 2.0
        tiempo_recto = lado / velocidad

        theta0 = self.theta

        for i in range(4):

            if self.stop_requested:
                return

            self.mover(velocidad, 0.0, tiempo_recto)

            if self.stop_requested:
                return

            self.orientar(theta0 + (i + 1) * math.pi/2)


    def dibujar_triangulo(self):

        self.stop_requested = False

        lado = 2.0
        velocidad = 2.0
        tiempo_recto = lado / velocidad

        theta0 = self.theta

        for i in range(3):

            if self.stop_requested:
                return

            self.mover(velocidad, 0.0, tiempo_recto)

            if self.stop_requested:
                return

            self.orientar(theta0 + (i + 1) * 2 * math.pi / 3)


    def reiniciar(self):

        while not self.reset_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Esperando servicio reset...")

        request = Empty.Request()

        future = self.reset_client.call_async(request)

        while not future.done():
            time.sleep(0.01)



    def cambiar_lapiz(self):

        while not self.pen_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Esperando servicio set_pen...")

        request = SetPen.Request()

        request.r = 179
        request.g = 184
        request.b = 255
        request.width = 3

        if self.pen_on:
            request.off = 1
            self.pen_on = False
        else:
            request.off = 0
            self.pen_on = True

        future = self.pen_client.call_async(request)

        while not future.done():
            time.sleep(0.01)



    def detener(self):

        self.stop_requested = True
        self.auto_mode = False

        self.linear = 0.0
        self.angular = 0.0


    def trayectoria_automatica(self):

        self.auto_mode = True


    def orientar(self, angulo_objetivo):

        while True:

            error = angulo_objetivo - self.theta
            error = math.atan2(math.sin(error), math.cos(error))

            if abs(error) < 0.005:      # ≈0.3°
                break

            w = 6.0 * error

            # Saturación
            if w > 2.5:
                w = 2.5
            elif w < -2.5:
                w = -2.5

            self.linear = 0.0
            self.angular = w

            time.sleep(0.01)

        self.linear = 0.0
        self.angular = 0.0

    def dibujar_J(self):

        self.stop_requested = False

        # Dar la vuelta
        self.orientar(-math.pi/2)

        # Bajar casi toda la barra
        self.mover(2.0, 0.0, 0.6)

        # Gancho inferior
        self.mover(1.2, -2.5, 1.25)


    def dibujar_B(self):

        self.stop_requested = False

        # Mirar hacia +X
        self.orientar(0.0)

        # Parte superior
        self.mover(2.0, 0.0, 0.16)

        # Lóbulo superior (20 % más pequeño)
        self.mover(0.8, -2.0, math.pi/2)

        # Avanzar hasta la mitad
        self.mover(2.0, 0.0, 0.16)

        # Volver a orientar
        self.orientar(0.0)

        # Regresar al centro
        self.mover(2.0, 0.0, 0.20)

        # Lóbulo inferior (20 % más pequeño)
        self.mover(0.8, -2.0, math.pi/2)

        # Parte inferior
        self.mover(2.0, 0.0, 0.22)

        # Orientarse hacia arriba
        self.orientar(math.pi/2)

        # Barra vertical (20 % más corta)
        self.mover(2.0, 0.0, 0.8)



    def dibujar_M(self):

        self.stop_requested = False

        # Mirar hacia arriba
        self.orientar(math.pi/2)

        # Primer palo
        self.mover(2.0, 0.0, 0.8)

        # Orientar
        self.orientar(-math.pi/3)

        # Movimiento al centro
        self.mover(2.0, 0.0, 0.5)

        # Orientar
        self.orientar(math.pi/3)

        # Movimiento al centro
        self.mover(2.0, 0.0, 0.5)

        # Mirar hacia abajo
        self.orientar(-math.pi/2)

        # Segundo palo
        self.mover(2.0, 0.0, 0.8)



    def dibujar_F(self):

        self.stop_requested = False

        # Barra vertical
        self.orientar(math.pi/2)
        self.mover(2.0, 0.0, 0.8)

        # Barra superior
        self.orientar(0.0)
        self.mover(2.0, 0.0, 0.4)

        # Apagar lápiz para regresar
        self.cambiar_lapiz()

        # Volver al extremo izquierdo
        self.orientar(math.pi)
        self.mover(2.0, 0.0, 0.4)

        # Bajar hasta la mitad
        self.orientar(-math.pi/2)
        self.mover(2.0, 0.0, 0.4)

        # Encender nuevamente
        self.cambiar_lapiz()

        # Barra central
        self.orientar(0.0)
        self.mover(2.0, 0.0, 0.25)


    def dibujar_S(self):

        self.stop_requested = False

        # Comenzar mirando hacia la derecha
        self.orientar(0.0)

        # Brazo superior
        self.mover(2.0, 0.0, 0.2)

        # Media circunferencia superior
        self.mover(0.8, 2.0, math.pi/2)

        # Enlace central
        self.mover(2.0, 0.0, 0.08)

        # Media circunferencia inferior
        self.mover(0.8, -2.0, math.pi/2)

        # Brazo inferior
        self.mover(2.0, 0.0, 0.2)


    def dibujar_L(self):

        self.stop_requested = False

        # Barra vertical
        self.orientar(-math.pi/2)
        self.mover(2.0, 0.0, 0.8)

        # Barra inferior
        self.orientar(0.0)
        self.mover(2.0, 0.0, 0.4)
    

    def dibujar_D(self):

        self.stop_requested = False

        # Barra vertical
        self.orientar(math.pi/2)
        self.mover(2.0, 0.0, 0.8)

        # Parte superior
        self.orientar(0.0)
        self.mover(2.0, 0.0, 0.25)

        # Cuarto de circunferencia superior
        self.mover(0.8, -2.0, math.pi/4)

        # Lado derecho
        self.orientar(-math.pi/2)
        self.mover(2.0, 0.0, 0.4)

        # Cuarto de circunferencia inferior
        self.mover(0.8, -2.0, math.pi/4)

        # Cierre inferior
        self.orientar(math.pi)
        self.mover(2.0, 0.0, 0.25)
    

    def move_turtle(self):

        if self.auto_mode:

            self.linear = 2.0

            if self.x > 10.2 or self.x < 0.8:
                self.angular = 3.0

            elif self.y > 10.2 or self.y < 0.8:
                self.angular = 3.0

            else:
                self.angular = 0.0

        msg = Twist()

        msg.linear.x = self.linear
        msg.angular.z = self.angular

        self.publisher_.publish(msg)



    def pose_callback(self, msg):

        self.x = msg.x
        self.y = msg.y
        self.theta = msg.theta

    def get_key(self):

        ch1 = sys.stdin.read(1)

        if ch1 == '\x1b':
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            return ch1 + ch2 + ch3

        return ch1

    def keyboard_loop(self):

        while rclpy.ok():

            key = self.get_key()



            # S
            if key.lower() == 's':
                self.stop_requested = False
                threading.Thread(
                    target=self.dibujar_cuadrado,
                    daemon=True
                ).start()
            
            # T
            elif key.lower() == 't':
                self.stop_requested = False
                threading.Thread(
                    target=self.dibujar_triangulo,
                    daemon=True
                ).start()

            # R
            elif key.lower() == 'r':
                self.reiniciar()

            # P
            elif key.lower() == 'p':
                self.cambiar_lapiz()

            # A
            elif key.lower() == 'a':
                self.trayectoria_automatica()

            # Q
            elif key.lower() == 'q':
                self.detener()

            # J
            elif key.lower() == 'j':
                self.stop_requested = False
                threading.Thread(
                    target=self.dibujar_J,
                    daemon=True
                ).start()

            # D
            elif key.lower() == 'd':
                self.stop_requested = False
                threading.Thread(
                    target=self.dibujar_D,
                    daemon=True
                ).start()

            # B
            elif key.lower() == 'b':
                self.stop_requested = False
                threading.Thread(
                    target=self.dibujar_B,
                    daemon=True
                ).start()

            # M
            elif key.lower() == 'm':
                self.stop_requested = False
                threading.Thread(
                    target=self.dibujar_M,
                    daemon=True
                ).start()

            # F
            elif key.lower() == 'f':
                self.stop_requested = False
                threading.Thread(
                    target=self.dibujar_F,
                    daemon=True
                ).start()

            # S
            elif key.lower() == 'z':
                self.stop_requested = False
                threading.Thread(
                    target=self.dibujar_S,
                    daemon=True
                ).start()

            # L
            elif key.lower() == 'l':
                self.stop_requested = False
                threading.Thread(
                    target=self.dibujar_L,
                    daemon=True
                ).start()



def main(args=None):

    rclpy.init(args=args)

    node = TurtleController()

    try:
        rclpy.spin(node)

    finally:
        termios.tcsetattr(
            node.fd,
            termios.TCSADRAIN,
            node.old_settings
        )

        node.destroy_node()
        rclpy.shutdown()
    


if __name__ == '__main__':
    main()






    