# Importar librerías.
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

import numpy as np
import rclpy

# Se crea la clase seguidor.
class Seguidor(Node):
    # Método principal de la clase.
    def __init__(self):
        super().__init__('turtle_follower') # Nombre del nodo.
        self.stop_request = False
        self.pose1 = None   # Se inicializa la pose de turtle1 como vacía.
        self.pose2 = None   # Se inicializa la pose de turtle2 como vacía.
        self.pose_sub1 = self.create_subscription(Pose, "/turtle1/pose",self.pose1_callback,10)     # Se suscribe al tópico /turtle1/pose.
        self.pose_sub2 = self.create_subscription(Pose, "/turtle2/pose",self.pose2_callback,10)     # Se suscribe al tópico /turtle2/pose.
        self.pub = self.create_publisher(Twist,"/turtle2/cmd_vel",10)   # Permite publicar en el tópico /turtle2/cmd_vel.
        self.timer = self.create_timer(0.5, self.follow)    # Llama al método follow cada cierto tiempo.
    
    # Métodos para recibir los mensajes de los tópicos a los que está suscrito.
    def pose1_callback(self, msg):
        self.pose1 = msg

    def pose2_callback(self, msg):
        self.pose2 = msg

    # Método que utiliza los mensajes de entrada para generar el comando de control de turtle2.
    def follow(self):
        twist = Twist() # Crea un mensaje de tipo Twist
        if self.pose1 is None or self.pose2 is None: # Indica que, si las poses están vacías, no realiza ninguna acción.
            return
        # Obtener las componentes de posición de las poses de las tortugas.
        x1 = self.pose1.x
        y1 = self.pose1.y
        x2 = self.pose2.x
        y2 = self.pose2.y
        # Cálculo de las diferencias entre las componentes de las posiciones.
        dx = x1 - x2
        dy = y1 - y2
        # Cálculo del ángulo entre la posición de turtle1 y turtle2.
        angulo = np.arctan2(dy, dx)
        # Cálculo del error en el ángulo.
        error = angulo - self.pose2.theta
        # Normalización del ángulo.
        error = np.arctan2(np.sin(error), np.cos(error))
        # Cálculo del error en la distancia.
        distancia = np.sqrt(dx**2 + dy**2)
        if distancia < 0.05: # Condicional para evitar que la turtle2 gire indefinidamente al llegar a la posición de turtle1.
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.pub.publish(twist)
            return
        # Construcción del mensaje de salida para turtle2 mediante un control proporcional.
        twist.linear.x = 2*distancia
        twist.angular.z = 2.4*error
        self.pub.publish(twist) # Envío del mensaje.

def main(args=None):
    rclpy.init(args=args) # Inicializa la comunicación con ROS 2.
    node = Seguidor() # Crea el nodo seguidor.
    rclpy.spin(node) # Mantiene el nodo en ejecución atendiendo los temporizadores, servicios y demás eventos hasta que el usuario finalice el programa. 
    node.destroy_node() # Libera los recursos asociados al nodo.
    rclpy.shutdown() # Finaliza correctamente la comunicación con ROS 2.