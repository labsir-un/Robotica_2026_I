import sys
import termios
import tty
import threading

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class TurtleController(Node):
    def __init__(self):
        super().__init__('turtle_controller')
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.move_turtle)

        # Velocidades actuales (se modifican con las flechas)
        self.linear_speed = 0.0
        self.angular_speed = 0.0

        # Incrementos por cada pulsación de tecla
        self.linear_step = 0.5
        self.angular_step = 0.5

        # Guardamos la configuración original de la terminal
        # para poder leer teclas sin necesidad de presionar Enter
        self.settings = termios.tcgetattr(sys.stdin)

        self.running = True

        # Para no inundar la terminal: solo logueamos cuando algo cambia
        self.last_logged_linear = None
        self.last_logged_angular = None

        # El teclado se lee en un hilo separado, así no depende
        # del timing del timer de ROS2 (que es lo que fallaba antes)
        self.keyboard_thread = threading.Thread(target=self.keyboard_loop, daemon=True)
        self.keyboard_thread.start()

        self.print_instructions()
        self.print_table_header()

    def print_instructions(self):
        print(
            "\r\nControl con flechas:\r\n"
            "  Arriba    -> aumentar velocidad lineal\r\n"
            "  Abajo     -> disminuir velocidad lineal\r\n"
            "  Izquierda -> aumentar velocidad angular\r\n"
            "  Derecha   -> disminuir velocidad angular\r\n"
            "  Espacio   -> detener\r\n"
            "  q         -> salir\r"
        )

    def print_table_header(self):
        # Encabezado tipo tabla; se imprime una sola vez con print()
        # directo (no get_logger) para que no se mezcle con el prefijo
        # de timestamp de ROS2 y quede alineado.
        # En modo "raw" (tty.setraw) la terminal NO traduce \n -> \r\n,
        # así que hay que mandar el \r explícitamente o el texto queda
        # en cascada (cada línea más corrida hacia la derecha).
        print(f"\r\n{'TECLA':<12}{'LINEAR (m/s)':<16}{'ANGULAR (rad/s)':<16}\r")
        print("-" * 44 + "\r")

    def keyboard_loop(self):
        """
        Corre en un hilo separado. Se queda bloqueado esperando una tecla
        (sys.stdin.read(1) sí bloquea, pero como está en su propio hilo,
        no congela el spin() de ROS2 ni el timer de publicación).
        """
        tty.setraw(sys.stdin.fileno())
        try:
            while self.running:
                key = sys.stdin.read(1)
                if key == '\x1b':  # inicio de secuencia de escape -> flecha
                    key += sys.stdin.read(2)

                key_label = None

                if key == '\x1b[A':  # flecha arriba
                    self.linear_speed += self.linear_step
                    key_label = 'ARRIBA'
                elif key == '\x1b[B':  # flecha abajo
                    self.linear_speed -= self.linear_step
                    key_label = 'ABAJO'
                elif key == '\x1b[D':  # flecha izquierda
                    self.angular_speed += self.angular_step
                    key_label = 'IZQUIERDA'
                elif key == '\x1b[C':  # flecha derecha
                    self.angular_speed -= self.angular_step
                    key_label = 'DERECHA'
                elif key == ' ':  # espacio: detener
                    self.linear_speed = 0.0
                    self.angular_speed = 0.0
                    key_label = 'STOP'
                elif key == 'q':  # salir
                    self.running = False
                    print("-" * 44 + "\r")
                    print("Saliendo...\r")
                    break

                if key_label:
                    self.log_state(key_label)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)

    def log_state(self, key_label):
        """Imprime una fila de la tabla solo cuando hay un cambio real."""
        if (self.linear_speed == self.last_logged_linear and
                self.angular_speed == self.last_logged_angular):
            return
        print(f"{key_label:<12}{self.linear_speed:<16.2f}{self.angular_speed:<16.2f}\r")
        self.last_logged_linear = self.linear_speed
        self.last_logged_angular = self.angular_speed

    def move_turtle(self):
        # El timer solo se encarga de publicar el estado actual de las
        # velocidades; el log de tabla ya se hace en keyboard_loop()
        # cuando hay un cambio, para no inundar la terminal.
        if not self.running:
            self.stop_and_shutdown()
            return

        msg = Twist()
        msg.linear.x = self.linear_speed
        msg.angular.z = self.angular_speed
        self.publisher_.publish(msg)

    def stop_and_shutdown(self):
        # Publica velocidad cero antes de cerrar
        self.running = False
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.publisher_.publish(msg)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        self.destroy_node()
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = TurtleController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.stop_and_shutdown()


if __name__ == '__main__':
    main()
