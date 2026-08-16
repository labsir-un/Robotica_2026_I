import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import Spawn


class TurtleFollower(Node):
    """
    Spawnea una segunda tortuga (turtle2) y la mueve para que persiga
    a la tortuga principal (turtle1), usando un controlador proporcional
    simple sobre distancia y ángulo.
    """

    def __init__(self):
        super().__init__('turtle_follower')

        # Ganancias del controlador proporcional. Si turtle2 se mueve
        # demasiado brusco, bajar estos valores; si reacciona muy lento,
        # subirlos un poco.
        self.linear_gain = 1.0
        self.angular_gain = 4.0

        # Última pose conocida de cada tortuga (None hasta que llegue el
        # primer mensaje de cada topic)
        self.leader_pose = None   # pose de turtle1
        self.follower_pose = None  # pose de turtle2

        self.follower_spawned = False

        # Publicador hacia turtle2. Aunque turtle2 todavía no exista,
        # esto no falla: simplemente nadie escucha hasta que se spawnee.
        self.cmd_vel_pub = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)

        # Suscripción a la pose del líder (turtle1), que turtlesim
        # siempre publica por defecto.
        self.create_subscription(Pose, '/turtle1/pose', self.leader_pose_callback, 10)

        # Cliente del servicio /spawn para crear turtle2
        self.spawn_client = self.create_client(Spawn, '/spawn')

        self.spawn_turtle2()

        # Timer de control: corre el cálculo de persecución periódicamente
        self.control_timer = self.create_timer(0.1, self.control_loop)

    def spawn_turtle2(self):
        """Llama al servicio /spawn de forma asíncrona para crear turtle2."""
        self.get_logger().info('Esperando el servicio /spawn...')
        self.spawn_client.wait_for_service()

        request = Spawn.Request()
        request.x = 3.0
        request.y = 3.0
        request.theta = 0.0
        request.name = 'turtle2'

        future = self.spawn_client.call_async(request)
        future.add_done_callback(self.spawn_done_callback)

    def spawn_done_callback(self, future):
        try:
            response = future.result()
            self.get_logger().info(f'turtle2 creada: {response.name}')
        except Exception as e:
            self.get_logger().error(f'No se pudo spawnear turtle2: {e}')
            return

        # Solo ahora que turtle2 existe, nos suscribimos a su pose
        self.create_subscription(Pose, '/turtle2/pose', self.follower_pose_callback, 10)
        self.follower_spawned = True

    def leader_pose_callback(self, msg):
        self.leader_pose = msg

    def follower_pose_callback(self, msg):
        self.follower_pose = msg

    def control_loop(self):
        # Esperamos a tener ambas poses antes de intentar calcular nada
        if not self.follower_spawned:
            return
        if self.leader_pose is None or self.follower_pose is None:
            return

        # Distancia entre las dos tortugas (Pitágoras)
        dx = self.leader_pose.x - self.follower_pose.x
        dy = self.leader_pose.y - self.follower_pose.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Ángulo hacia el que debería apuntar turtle2 para mirar a turtle1
        target_angle = math.atan2(dy, dx)

        # Error angular: diferencia entre hacia dónde mira turtle2 ahora
        # y hacia dónde debería mirar. Normalizado a [-pi, pi] para que
        # siempre gire por el camino más corto.
        angle_error = target_angle - self.follower_pose.theta
        angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))

        msg = Twist()

        # Si ya está muy cerca, se detiene (evita vibrar pegada al líder)
        if distance > 0.3:
            msg.linear.x = self.linear_gain * distance
            msg.angular.z = self.angular_gain * angle_error
        else:
            msg.linear.x = 0.0
            msg.angular.z = 0.0

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
