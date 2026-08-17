# node.py — nodo principal TurtleController
#
# Une los tres módulos mediante herencia múltiple:
#   TopicsManager  → publicadores, suscriptores, seguidor
#   ServiceManager → clientes de servicio turtlesim
#   ActionsManager → trayectorias, letras, control manual
#
# __init__ solo registra infraestructura ROS 2.
# La inicialización que requiere spin activo se hace en _deferred_init.

import threading
import time

import rclpy
from rclpy.node import Node

from .topics   import TopicsManager
from .services import ServiceManager
from .actions  import ActionsManager


class TurtleController(Node, TopicsManager, ServiceManager, ActionsManager):
    """
    Nodo ROS 2 principal del laboratorio.

    Arquitectura:
      Publicadores : /turtle1/cmd_vel, /turtle2/cmd_vel
      Suscriptores : /turtle1/pose,    /turtle2/pose   (QoS BEST_EFFORT)
      Servicios    : /spawn, /clear, /turtle1/teleport_absolute,
                     /turtle1/set_pen, /turtle2/set_pen
      Timer        : follower_callback 10 Hz
      Parámetros   : linear_speed, angular_speed, border_margin,
                     follower_gain_lin, follower_gain_ang
    """

    def __init__(self):
        Node.__init__(self, 'turtle_controller')

        # ── Parámetros ROS 2 ──────────────────────────────────────────
        # Modificables en tiempo real:
        #   ros2 param set /turtle_controller linear_speed 3.0
        self.declare_parameter('linear_speed',      2.0)
        self.declare_parameter('angular_speed',     1.5)
        self.declare_parameter('border_margin',     1.8)
        self.declare_parameter('follower_gain_lin', 1.5)
        self.declare_parameter('follower_gain_ang', 4.0)

        # ── Inicializar módulos ───────────────────────────────────────
        self.init_topics()           # TopicsManager: pubs, subs, locks
        self.init_service_clients()  # ServiceManager: clientes de servicio

        # ── Estado interno ────────────────────────────────────────────
        self.pen_active   = True
        self.auto_running = False
        self.running      = True

        # ── Timer seguidor 10 Hz ──────────────────────────────────────
        self.create_timer(0.1, self.follower_callback)

        # ── Inicialización diferida ───────────────────────────────────
        # spawn + disable_pen2 se hacen 1 s después para que
        # rclpy.spin ya esté activo y los futuros puedan resolverse.
        self._init_done = False
        self.create_timer(1.0, self._deferred_init)

        self.get_logger().info('TurtleController registrado. Esperando spin...')

    def _deferred_init(self):
        """Timer de un solo disparo: lanza setup de turtle2 en hilo secundario."""
        if self._init_done:
            return
        self._init_done = True
        threading.Thread(target=self.svc_setup_turtle2, daemon=True).start()


def main(args=None):
    rclpy.init(args=args)
    node = TurtleController()

    # spin en hilo separado para que keyboard_loop no bloquee el executor
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()

    try:
        from .keyboard import keyboard_loop
        keyboard_loop(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.running      = False
        node.auto_running = False
        node.stop_all()
        node.get_logger().info('Nodo cerrado correctamente.')
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
