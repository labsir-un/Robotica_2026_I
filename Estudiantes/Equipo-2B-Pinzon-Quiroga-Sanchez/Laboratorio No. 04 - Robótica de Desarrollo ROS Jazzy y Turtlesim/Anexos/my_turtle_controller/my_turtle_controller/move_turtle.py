# ==========================
# Librerías de ROS 2
# ==========================

import rclpy                              # Biblioteca principal de ROS 2 para Python
from rclpy.node import Node               # Permite crear un nodo de ROS 2
from geometry_msgs.msg import Twist       # Mensaje para controlar velocidades lineales y angulares
from turtlesim.srv import TeleportAbsolute # Servicio para teletransportar la tortuga
from turtlesim.srv import SetPen          # Servicio para configurar el lápiz de la tortuga

# ==========================
# Librerías para generación de trayectorias
# ==========================

from matplotlib.textpath import TextPath  # Convierte texto en trayectorias (vértices) para dibujar letras

# ==========================
# Librerías del sistema
# ==========================

import sys           # Acceso a la entrada estándar (teclado)
import tty           # Configura la terminal en modo lectura carácter por carácter
import termios       # Modifica la configuración del terminal en Linux
import time          # Manejo de tiempos y retardos
import numpy as np   # Operaciones matemáticas y generación de puntos
import select        # Verifica si hay una tecla disponible sin bloquear el programa
import threading     # Permite ejecutar la lectura del teclado en un hilo independiente

# ==========================
# Lectura del teclado
# ==========================

def get_key():
    # Guarda la configuración actual del terminal
    settings = termios.tcgetattr(sys.stdin)

    # Coloca el terminal en modo "raw", permitiendo leer una tecla
    # inmediatamente sin necesidad de presionar Enter
    tty.setraw(sys.stdin.fileno())

    # Verifica si hay una tecla disponible para leer.
    # El tiempo de espera es 0 segundos, por lo que la función
    # no bloquea la ejecución del programa.
    dr, _, _ = select.select([sys.stdin], [], [], 0)

    if dr:
        # Lee el primer carácter presionado
        key = sys.stdin.read(1)

        # Si corresponde a una tecla especial (flechas),
        # lee los dos caracteres restantes de la secuencia ANSI.
        if key == '\x1b':
            key += sys.stdin.read(2)
    else:
        # Si no se presionó ninguna tecla, retorna None
        key = None

    # Restaura la configuración original del terminal
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

    # Devuelve la tecla leída
    return key

# ==========================
# Nodo principal de control
# ==========================

class TurtleController(Node):

    def __init__(self):

        # Inicializa el nodo de ROS 2
        super().__init__('turtle_controller')

        # ==========================
        # Clientes y publicadores ROS
        # ==========================

        # Cliente para controlar el estado del lápiz
        self.pen_client = self.create_client(
            SetPen,
            '/turtle1/set_pen'
        )

        # Cliente para teletransportar la tortuga
        self.teleport_client = self.create_client(
            TeleportAbsolute,
            '/turtle1/teleport_absolute'
        )

        # Publicador de velocidades lineales y angulares
        self.publisher_ = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # ==========================
        # Variables de estado
        # ==========================

        # Última tecla presionada por el usuario
        self.key = None

        # Paso actual de una trayectoria automática
        self.action_step = 0

        # Velocidades lineal y angular actuales
        self.linear_speed = 0.0
        self.angular_speed = 0.0

        # Tiempo de finalización del movimiento programado
        self.motion_end_time = None

        # Acción automática que se está ejecutando
        self.action = None

        # Variables utilizadas para el dibujo de letras
        self.letter_vertices = None
        self.letter_codes = None
        self.letter_index = 0

        # Estado actual del lápiz
        self.pen_state = False

        # Contadores para controlar la velocidad de dibujo
        # de la mariposa y las letras
        self.butterfly_wait = 0
        self.letter_wait = 0

        # ==========================
        # Temporizador e hilo
        # ==========================

        # Ejecuta periódicamente el controlador principal
        self.control_timer = self.create_timer(
            0.02,
            self.control_loop
        )

        # Hilo independiente para leer el teclado
        self.keyboard_thread = threading.Thread(
            target=self.keyboard_loop,
            daemon=True
        )

        # Inicia el hilo de lectura del teclado
        self.keyboard_thread.start()

    # ==========================
    # Lectura continua del teclado
    # ==========================

    def keyboard_loop(self):

        # Mientras ROS permanezca en ejecución
        while rclpy.ok():

            # Lee una tecla sin bloquear el programa
            key = get_key()

            # Si se detectó una tecla,
            # se almacena para que el controlador principal la procese.
            if key is not None:
                self.key = key

    # ==========================
    # Control principal del programa
    # ==========================

    def control_loop(self):

        # Si el usuario ha presionado una tecla,
        # ejecuta la acción correspondiente.
        if self.key is not None:

            match self.key:

                # Movimiento manual mediante las flechas del teclado
                case '\x1b[A':
                    self.start_motion(2.0,0.0,0.2)

                case '\x1b[B':
                    self.start_motion(-2.0,0.0,0.2)

                case '\x1b[C':
                    self.start_motion(0.0,-2.0,0.2)

                case '\x1b[D':
                    self.start_motion(0.0,2.0,0.2)

                # Inicio de trayectorias automáticas
                case 'Y':
                    self.action = "square"
                    self.action_step = 0

                case 'T':
                    self.action = "triangle"
                    self.action_step = 0

                # Reinicia la posición de la tortuga
                case 'G':
                    self.reset()

                # Activa o desactiva el lápiz
                case 'O':
                    self.toggle_pen()

                # Prepara la trayectoria de la mariposa
                case 'M':
                    self.prepare_butterfly()
                    self.action = "butterfly"

                # Preparación de las letras de los integrantes
                case 'P':
                    self.prepare_letter("P",5.544445,5.544445)

                case 'N':
                    self.prepare_letter("N",0,2)

                case 'Q':
                    self.prepare_letter("Q",2,2)

                case 'R':
                    self.prepare_letter("R",4,2)

                case 'D':
                    self.prepare_letter("D",8,2)

                case 'S':
                    self.prepare_letter("S",0,7)

                case 'H':
                    self.prepare_letter("H",2,7)

                case 'J':
                    self.prepare_letter("J",4,7)

                case 'C':
                    self.prepare_letter("C",8,7)

                # Finaliza completamente la ejecución del nodo
                case 'X':
                    self.stop()
                    rclpy.shutdown()

                # Cancela cualquier trayectoria automática en ejecución
                case 'L':
                    self.cancel_action()

            # Borra la tecla para evitar procesarla nuevamente
            self.key = None

        # Mensaje de velocidades que será enviado a la tortuga
        msg = Twist()

        # Mantiene el movimiento programado hasta que
        # se cumpla el tiempo establecido
        if self.motion_end_time is not None:

            if time.time() < self.motion_end_time:

                msg.linear.x = self.linear_speed
                msg.angular.z = self.angular_speed

            else:

                # Finaliza el movimiento
                self.motion_end_time = None
                msg.linear.x = 0.0
                msg.angular.z = 0.0

        # Publica el comando de velocidad
        self.publisher_.publish(msg)

        # Ejecuta un paso de la trayectoria automática seleccionada
        if self.action == "square":
            self.square_step()

        elif self.action == "triangle":
            self.triangle_step()

        elif self.action == "butterfly":
            self.butterfly_step()

        elif self.action == "letter":
            self.letter_step()

    # Inicia un movimiento temporizado de la tortuga.
    # Se almacenan las velocidades lineal y angular, así como el
    # instante en el que debe finalizar el movimiento. El envío de
    # estas velocidades se realiza posteriormente desde control_loop().
    def start_motion(self, linear, angular, duration):
        self.linear_speed = linear
        self.angular_speed = angular
        self.motion_end_time = time.time() + duration

    # Dibuja un cuadrado mediante una secuencia de movimientos.
    # Cada estado corresponde a un lado o a un giro de 90°. Cuando un
    # movimiento termina (motion_end_time es None), se inicia el siguiente
    # hasta completar la figura.
    def square_step(self):

        # Paso 0: recorrer el primer lado
        if self.action_step == 0:
            self.start_motion(2.0,0.0,1.0)
            self.action_step = 1

        # Paso 1: giro de 90°
        elif self.action_step == 1:
            if self.motion_end_time is None:
                self.start_motion(0.0,-2.0,np.pi/4)
                self.action_step = 2

        # Paso 2: recorrer el segundo lado
        elif self.action_step == 2:
            if self.motion_end_time is None:
                self.start_motion(2.0,0.0,1.0)
                self.action_step = 3

        # Paso 3: giro de 90°
        elif self.action_step == 3:
            if self.motion_end_time is None:
                self.start_motion(0.0,-2.0,np.pi/4)
                self.action_step = 4

        # Paso 4: recorrer el tercer lado
        elif self.action_step == 4:
            if self.motion_end_time is None:
                self.start_motion(2.0,0.0,1.0)
                self.action_step = 5

        # Paso 5: giro de 90°
        elif self.action_step == 5:
            if self.motion_end_time is None:
                self.start_motion(0.0,-2.0,np.pi/4)
                self.action_step = 6

        # Paso 6: recorrer el cuarto lado
        elif self.action_step == 6:
            if self.motion_end_time is None:
                self.start_motion(2.0,0.0,1.0)
                self.action_step = 7

        # Paso 7: giro final para recuperar la orientación inicial
        elif self.action_step == 7:
            if self.motion_end_time is None:
                self.start_motion(0.0,-2.0,np.pi/4)
                self.action_step = 8

        # Paso final: finalizar la acción y reiniciar el estado
        elif self.action_step == 8:
            if self.motion_end_time is None:
                self.action = None
                self.action_step = 0
                self.get_logger().info("Cuadrado terminado")

    # Dibuja un triángulo equilátero mediante una secuencia de movimientos.
    # La función avanza por una máquina de estados donde se alternan los
    # desplazamientos rectos con giros de 120° hasta completar la figura.
    def triangle_step(self):

        # Paso 0: recorrer el primer lado
        if self.action_step == 0:
            self.start_motion(2.0, 0.0, 1.0)
            self.action_step = 1

        # Paso 1: giro de 120°
        elif self.action_step == 1:
            if self.motion_end_time is None:
                self.start_motion(0.0, -2.0, np.pi/3)
                self.action_step = 2

        # Paso 2: recorrer el segundo lado
        elif self.action_step == 2:
            if self.motion_end_time is None:
                self.start_motion(2.0, 0.0, 1.0)
                self.action_step = 3

        # Paso 3: giro de 120°
        elif self.action_step == 3:
            if self.motion_end_time is None:
                self.start_motion(0.0, -2.0, np.pi/3)
                self.action_step = 4

        # Paso 4: recorrer el tercer lado
        elif self.action_step == 4:
            if self.motion_end_time is None:
                self.start_motion(2.0, 0.0, 1.0)
                self.action_step = 5

        # Paso 5: giro final para recuperar la orientación inicial
        elif self.action_step == 5:
            if self.motion_end_time is None:
                self.start_motion(0.0, -2.0, np.pi/3)
                self.action_step = 6

        # Paso final: finalizar la acción y reiniciar el estado
        elif self.action_step == 6:
            if self.motion_end_time is None:
                self.action = None
                self.action_step = 0
                self.get_logger().info("Triángulo terminado")

    # Calcula previamente los puntos que forman la trayectoria de la mariposa.
    # La curva se genera a partir de una ecuación paramétrica, se escala y se
    # traslada al centro de la ventana de turtlesim. Solo se almacenan los
    # puntos que permanecen dentro de los límites de la pantalla.
    def prepare_butterfly(self):
        self.butterfly_points = []

        centro_x = 5.5
        centro_y = 5.5
        escala = 0.02

        theta = np.linspace(0,8*np.pi,1500)

        for t in theta:

            r = 200*np.cos(5*t/4)*np.sin(2*t)

            x = centro_x + escala*r*np.cos(t)
            y = centro_y + escala*r*np.sin(t)

            if 0.2 < x < 10.8 and 0.2 < y < 10.8:
                self.butterfly_points.append((x,y))

        # Inicia el recorrido desde el primer punto
        self.point_index = 0

    # Recorre secuencialmente los puntos de la trayectoria de la mariposa.
    # Se introduce una pequeña espera entre puntos para reducir la velocidad
    # del dibujo y obtener una animación más suave.
    def butterfly_step(self):

        # Control de velocidad del dibujo
        if self.butterfly_wait < 2:
            self.butterfly_wait += 1
            return

        self.butterfly_wait = 0

        # Finaliza cuando todos los puntos han sido recorridos
        if self.point_index >= len(self.butterfly_points):

            self.action = None
            self.get_logger().info("Mariposa terminada")
            return

        # Mueve la tortuga al siguiente punto de la trayectoria
        x, y = self.butterfly_points[self.point_index]
        self.goto(x, y)

        self.point_index += 1

    # Prepara la información necesaria para dibujar una letra.
    # Se obtiene el contorno mediante TextPath, se desplaza hasta la
    # posición indicada y se inicializan las variables de recorrido.
    def prepare_letter(self, letra, x, y):

        tp = TextPath((0,0), letra, size=3).interpolated(15)

        self.letter_vertices = tp.vertices.copy()
        self.letter_codes = tp.codes.copy()

        # Desplaza la letra a la posición deseada
        self.letter_vertices[:,0] += x
        self.letter_vertices[:,1] += y

        # Comienza el recorrido desde el primer vértice
        self.letter_index = 0
        self.action = "letter"

    # Dibuja la letra recorriendo cada uno de los vértices generados por
    # TextPath. Dependiendo del código asociado al vértice, se activa o
    # desactiva el lápiz para evitar trazos no deseados entre segmentos.
    def letter_step(self):

        # Control de velocidad del dibujo
        if self.letter_wait < 2:
            self.letter_wait += 1
            return

        self.letter_wait = 0

        # Finaliza cuando todos los vértices han sido recorridos
        if self.letter_index >= len(self.letter_vertices):

            self.action = None
            self.get_logger().info("Letra terminada")
            return

        code = self.letter_codes[self.letter_index]

        x = self.letter_vertices[self.letter_index,0]
        y = self.letter_vertices[self.letter_index,1]

        # Los códigos de TextPath determinan cuándo levantar o bajar el lápiz
        if code == 1:
            self.pen(True)
            self.goto(x,y)

        elif code == 79:
            self.pen(True)

        else:
            self.pen(False)
            self.goto(x,y)

        # Avanza al siguiente vértice
        self.letter_index += 1

    # Detiene inmediatamente el movimiento de la tortuga enviando
    # velocidades lineal y angular iguales a cero.
    def stop(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.publisher_.publish(msg)

    # Cancela la acción automática que se esté ejecutando.
    # Reinicia la máquina de estados, elimina cualquier movimiento
    # programado y detiene la tortuga.
    def cancel_action(self):
        self.action = None
        self.action_step = 0
        self.motion_end_time = None
        self.stop()
        self.get_logger().info("Movimiento detenido")
        
    # Reubica la tortuga en la posición inicial del escenario
    # utilizando el servicio TeleportAbsolute.
    def reset(self):
        request = TeleportAbsolute.Request()
        request.x = 5.544445
        request.y = 5.544445
        request.theta = 0.0
        self.teleport_client.call_async(request)
        self.get_logger().info("Posición reiniciada")
        
    # Cambia el estado actual del lápiz. Si está activado lo desactiva,
    # y si está desactivado lo vuelve a activar.
    def toggle_pen(self):
        self.pen(not self.pen_state)
        
    # Activa o desactiva el lápiz mediante el servicio SetPen.
    # Antes de enviar la solicitud verifica si el estado solicitado ya
    # coincide con el actual para evitar llamadas innecesarias al servicio.
    def pen(self, off):
        if off == self.pen_state:
            return
        request = SetPen.Request()
        request.r = 255
        request.g = 255
        request.b = 255
        request.width = 3
        request.off = int(off)
        self.pen_client.call_async(request)
        self.pen_state = off

    # Desplaza instantáneamente la tortuga hasta la posición indicada
    # utilizando el servicio TeleportAbsolute.
    def goto(self, x, y):

        request = TeleportAbsolute.Request()
        request.x = x
        request.y = y
        request.theta = 0.0

        self.teleport_client.call_async(request)
  
# -----------------------------------------------------------------------------
# Función principal del programa
# -----------------------------------------------------------------------------
def main(args=None):

    # Inicializa la comunicación con ROS 2.
    rclpy.init(args=args)

    # Crea el nodo controlador de la tortuga.
    node = TurtleController()

    # Mantiene el nodo en ejecución atendiendo los temporizadores,
    # servicios y demás eventos hasta que el usuario finalice el programa.
    rclpy.spin(node)

    # Libera los recursos asociados al nodo.
    node.destroy_node()

    # Finaliza correctamente la comunicación con ROS 2.
    rclpy.shutdown()
