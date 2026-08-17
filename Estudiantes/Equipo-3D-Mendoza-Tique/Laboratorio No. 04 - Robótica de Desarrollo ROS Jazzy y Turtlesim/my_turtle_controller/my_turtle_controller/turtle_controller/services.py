# services.py — clientes de servicio ROS 2
#
# Contiene ServiceManager, una clase mixin que el nodo principal hereda.
# Cada método llama a un servicio turtlesim de forma segura desde
# hilos secundarios usando threading.Event (nunca spin_until_future_complete).

import threading
import time

from turtlesim.srv import TeleportAbsolute, SetPen, Spawn
from std_srvs.srv import Empty


class ServiceManager:
    """
    Mixin con todos los clientes de servicio del laboratorio.
    Se espera que la clase que lo herede sea un rclpy.Node.
    """

    def init_service_clients(self):
        """
        Registra los clientes de servicio.
        Llamar desde __init__ del nodo DESPUÉS de super().__init__().
        No hace wait_for_service aquí: el nodo no debe bloquearse
        en el constructor antes de que spin esté corriendo.
        """
        self.cli_teleport1 = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        self.cli_pen1      = self.create_client(SetPen,           '/turtle1/set_pen')
        self.cli_pen2      = self.create_client(SetPen,           '/turtle2/set_pen')
        self.cli_spawn     = self.create_client(Spawn,            '/spawn')
        self.cli_clear     = self.create_client(Empty,            '/clear')

    # ── Primitiva base ──────────────────────────────────────────────────

    def _call_service(self, client, request, timeout: float = 3.0):
        """
        Llama a un servicio ROS 2 de forma segura desde un hilo secundario.

        Usa threading.Event para esperar la respuesta sin bloquear
        el executor (que ya está en rclpy.spin en otro hilo).

        IMPORTANTE: nunca llamar desde un callback del executor
        (timer, suscriptor), solo desde hilos secundarios.
        """
        if not client.wait_for_service(timeout_sec=timeout):
            self.get_logger().warn(f'{client.srv_name} no disponible.')
            return None

        future = client.call_async(request)
        event  = threading.Event()
        future.add_done_callback(lambda _: event.set())

        if not event.wait(timeout=timeout):
            self.get_logger().warn(f'Timeout en {client.srv_name}.')
            return None

        try:
            return future.result()
        except Exception as e:
            self.get_logger().error(f'Error en {client.srv_name}: {e}')
            return None

    # ── Wrappers de alto nivel ──────────────────────────────────────────

    def svc_set_pen1(self, r: int, g: int, b: int, width: int, off: int):
        """Configura el lápiz de turtle1. off=0 → ON, off=1 → OFF."""
        req = SetPen.Request()
        req.r = r; req.g = g; req.b = b; req.width = width; req.off = off
        self._call_service(self.cli_pen1, req)

    def svc_disable_pen2(self):
        """Desactiva permanentemente el lápiz de turtle2."""
        req = SetPen.Request()
        req.r = 0; req.g = 0; req.b = 0; req.width = 0; req.off = 1
        result = self._call_service(self.cli_pen2, req, timeout=2.0)
        if result is not None:
            self.get_logger().info('Lápiz de turtle2 desactivado.')

    def svc_teleport(self, x: float, y: float, theta: float):
        """Teletransporta turtle1 a (x, y, theta) sin dejar trazo."""
        req = TeleportAbsolute.Request()
        req.x = x; req.y = y; req.theta = theta
        self._call_service(self.cli_teleport1, req)

    def svc_spawn_turtle2(self):
        """Crea turtle2 en (8, 2). Si ya existe, lo ignora silenciosamente."""
        req = Spawn.Request()
        req.x = 8.0; req.y = 2.0; req.theta = 0.0; req.name = 'turtle2'
        result = self._call_service(self.cli_spawn, req)
        if result is not None:
            self.get_logger().info('turtle2 creada en (8, 2).')
        else:
            self.get_logger().info('turtle2 ya existía o no se pudo crear.')

    def svc_clear(self):
        """Borra todos los trazados del simulador (/clear)."""
        self._call_service(self.cli_clear, Empty.Request())
        self.get_logger().info('Pantalla limpiada.')

    def svc_setup_turtle2(self):
        """Crea turtle2 y desactiva su lápiz (ejecutar en hilo secundario)."""
        self.svc_spawn_turtle2()
        time.sleep(0.3)   # dar tiempo a turtlesim para registrar turtle2
        self.svc_disable_pen2()
