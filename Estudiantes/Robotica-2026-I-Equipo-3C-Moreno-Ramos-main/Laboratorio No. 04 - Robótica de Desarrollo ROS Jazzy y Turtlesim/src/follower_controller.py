#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import Spawn
import math

class TurtleFollower(Node):
    def __init__(self):
        super().__init__('turtle_follower')
        
        # Guardar las posiciones de ambas tortugas
        self.leader_pose = None
        self.follower_pose = None
        
        # 1. Clientes, Suscriptores y Publicadores
        self.spawn_client = self.create_client(Spawn, '/spawn')
        self.spawn_turtle2() # Llamar a la función para crear a turtle2
        
        # Suscribirse a la posición del Líder (turtle1)
        self.leader_sub = self.create_subscription(
            Pose, '/turtle1/pose', self.leader_pose_callback, 10)
            
        # Suscribirse a la posición del Seguidor (turtle2)
        self.follower_sub = self.create_subscription(
            Pose, '/turtle2/pose', self.follower_pose_callback, 10)
            
        # Publicar la velocidad para el Seguidor (turtle2)
        self.cmd_vel_pub = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)
        
        # Bucle de control dinámico a 20Hz (cada 0.05 segundos)
        self.timer = self.create_timer(0.05, self.control_loop)
        
        self.get_logger().info('🤖 Nodo Seguidor (Turtle2) Iniciado y listo.')

    def spawn_turtle2(self):
        """Llama al servicio para spawnear a turtle2 de forma segura si no existe"""
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Esperando al servicio /spawn de turtlesim...')
            
        req = Spawn.Request()
        req.x = 2.0
        req.y = 2.0
        req.theta = 0.0
        req.name = 'turtle2'
        
        future = self.spawn_client.call_async(req)
        future.add_done_callback(self.spawn_callback)

    def spawn_callback(self, future):
        try:
            response = future.result()
            self.get_logger().info(f'🐢 {response.name} creada exitosamente en (2.0, 2.0).')
        except Exception as e:
            self.get_logger().error(f'No se pudo crear a turtle2: {e} (Tal vez ya existía)')

    def leader_pose_callback(self, msg):
        self.leader_pose = msg

    def follower_pose_callback(self, msg):
        self.follower_pose = msg

    def control_loop(self):
        # Si aún no tenemos datos de telemetría de ambas tortugas, esperamos.
        if self.leader_pose is None or self.follower_pose is None:
            return

        msg = Twist()

        # 2. CALCULAR DISTANCIA Y ORIENTACIÓN RELATIVA (Matemáticas del documento)
        dx = self.leader_pose.x - self.follower_pose.x
        dy = self.leader_pose.y - self.follower_pose.y
        
        # Distancia euclidiana (Hipotenusa)
        distance = math.sqrt(dx**2 + dy**2)
        
        # Ángulo absoluto hacia el líder
        target_angle = math.atan2(dy, dx)
        
        # Error de orientación relativo al seguidor
        angle_error = target_angle - self.follower_pose.theta
        # Normalizar el ángulo entre -pi y pi para que tome el camino de giro más corto
        angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))

        # 3. CONTROLADOR PROPORCIONAL (Aproximación progresiva)
        # Distancia mínima de seguridad para que no choque exactamente encima del líder (0.8 unidades)
        safety_distance = 0.8 

        if distance > safety_distance:
            # Ganancia lineal (K_linear = 1.5). Modifica para que vaya más rápido o lento.
            msg.linear.x = 1.5 * (distance - safety_distance)
            
            # Ganancia angular (K_angular = 4.5). Asegura un giro rápido hacia el objetivo.
            msg.angular.z = 4.5 * angle_error
            
            # Límites de velocidad para un comportamiento suave y estético
            if msg.linear.x > 3.0: msg.linear.x = 3.0
        else:
            # Si está lo suficientemente cerca, frena por completo
            msg.linear.x = 0.0
            msg.angular.z = 0.0

        # 4. PUBLICAR COMANDOS DE VELOCIDAD
        self.cmd_vel_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TurtleFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()