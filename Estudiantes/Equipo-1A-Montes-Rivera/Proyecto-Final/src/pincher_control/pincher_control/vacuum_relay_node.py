#!/usr/bin/env python3
"""
Nodo ROS 2 para el Control del Relé de la Bomba de Vacío vía GPIO 17.

Escucha en el tópico '/pincher/vacuum' ('std_msgs/msg/String'):
- Comandos de Encendido: 'VACUUM_ON', 'ON', '1' -> GPIO 17 HIGH
- Comandos de Apagado: 'VACUUM_OFF', 'OFF', '0' -> GPIO 17 LOW
"""

import sys
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

# Intentar importar controladores de GPIO para Raspberry Pi
GPIO_AVAILABLE = False
GPIO_LIB = None

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
    GPIO_LIB = 'RPi.GPIO'
except ImportError:
    try:
        import gpiod
        GPIO_AVAILABLE = True
        GPIO_LIB = 'gpiod'
    except ImportError:
        GPIO_AVAILABLE = False


class VacuumRelayNode(Node):
    """Nodo ROS 2 para accionar el relé de succión por vacío."""

    def __init__(self) -> None:
        super().__init__('vacuum_relay_node')

        self.declare_parameter('gpio_pin', 17)
        self.gpio_pin = int(self.get_parameter('gpio_pin').value)

        self.is_vacuum_on = False
        self.gpiod_line = None

        # Inicialización del Pin GPIO
        if GPIO_AVAILABLE:
            try:
                if GPIO_LIB == 'RPi.GPIO':
                    GPIO.setmode(GPIO.BCM)
                    GPIO.setup(self.gpio_pin, GPIO.OUT, initial=GPIO.LOW)
                    self.get_logger().info(f'✅ Relé de Vacío iniciado en GPIO {self.gpio_pin} usando RPi.GPIO')
                elif GPIO_LIB == 'gpiod':
                    chip = gpiod.Chip('gpiochip4')
                    self.gpiod_line = chip.get_line(self.gpio_pin)
                    self.gpiod_line.request(consumer='vacuum_relay', type=gpiod.LINE_REQ_DIR_OUT)
                    self.gpiod_line.set_value(0)
                    self.get_logger().info(f'✅ Relé de Vacío iniciado en GPIO {self.gpio_pin} usando gpiod')
            except Exception as e:
                self.get_logger().warn(f'⚠️ No se pudo acceder al hardware GPIO ({e}). Operando en modo Simulación log.')
        else:
            self.get_logger().warning('⚠️ Librería GPIO no disponible en el sistema. Modo simulación activo.')

        # Suscriptor al tópico de vacío
        self.sub_vacuum = self.create_subscription(
            String,
            '/pincher/vacuum',
            self._vacuum_callback,
            10
        )

        # Publicador de estado
        self.pub_status = self.create_publisher(String, '/pincher/vacuum/status', 10)

        self.get_logger().info('🧲 VacuumRelayNode listo. Esperando comandos en /pincher/vacuum...')

    def _vacuum_callback(self, msg: String) -> None:
        cmd = msg.data.upper().strip()

        if cmd in ['VACUUM_ON', 'ON', '1', 'TRUE']:
            self._set_relay(True)
        elif cmd in ['VACUUM_OFF', 'OFF', '0', 'FALSE']:
            self._set_relay(False)
        else:
            self.get_logger().warn(f'⚠️ Comando de vacío desconocido: "{msg.data}"')

    def _set_relay(self, state: bool) -> None:
        self.is_vacuum_on = state

        if GPIO_AVAILABLE:
            try:
                if GPIO_LIB == 'RPi.GPIO':
                    GPIO.output(self.gpio_pin, GPIO.HIGH if state else GPIO.LOW)
                elif GPIO_LIB == 'gpiod' and self.gpiod_line is not None:
                    self.gpiod_line.set_value(1 if state else 0)
            except Exception as e:
                self.get_logger().error(f'Error al cambiar estado GPIO: {e}')

        state_str = 'VACUUM_ON' if state else 'VACUUM_OFF'
        log_icon = '🌀' if state else '🔴'
        self.get_logger().info(f'{log_icon} Relé de Vacío: {state_str}')

        status_msg = String()
        status_msg.data = state_str
        self.pub_status.publish(status_msg)

    def destroy_node(self) -> None:
        self._set_relay(False)
        if GPIO_AVAILABLE and GPIO_LIB == 'RPi.GPIO':
            GPIO.cleanup()
        super().destroy_node()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = VacuumRelayNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
