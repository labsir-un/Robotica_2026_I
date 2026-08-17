#!/usr/bin/env python3
"""Nodo ROS 2 para controlar el PhantomX Pincher mediante DynamixelSDK.

El nodo acepta comandos articulares en radianes por ``/pincher/command`` y
publica el estado en ``/joint_states``. Con ``use_hardware:=false`` actúa como
controlador didáctico sin abrir el puerto serie.
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Optional, Tuple

import rclpy
from dynamixel_sdk import COMM_SUCCESS, PacketHandler, PortHandler
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String, UInt32
from std_srvs.srv import SetBool, Trigger

from pincher_control.dynamixel_profiles import MotorProfile, get_motor_profile

class PincherController(Node):
    """Controlador de posición para cinco articulaciones DYNAMIXEL."""

    def __init__(self) -> None:
        super().__init__('pincher_controller')

        self.declare_parameter('motor_model', 'xl430')
        self.declare_parameter('use_hardware', False)
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 1000000)
        self.declare_parameter('dxl_ids', [1, 2, 3, 4, 5])
        self.declare_parameter(
            'joint_names',
            ['waist', 'shoulder', 'elbow', 'wrist', 'gripper'],
        )
        self.declare_parameter('joint_signs', [1.0, -1.0, -1.0, -1.0, 1.0])
        self.declare_parameter('home_positions', [-1, -1, -1, -1, -1])
        self.declare_parameter('moving_speed', 100)
        self.declare_parameter('max_speed_value', 1023)
        self.declare_parameter('torque_limit', -1)
        self.declare_parameter('read_rate_hz', 20.0)
        self.declare_parameter('home_on_startup', False)
        self.declare_parameter('disable_torque_on_shutdown', True)

        self.profile: MotorProfile = get_motor_profile(
            str(self.get_parameter('motor_model').value)
        )
        self.use_hardware = bool(self.get_parameter('use_hardware').value)
        self.port_name = str(self.get_parameter('port').value)
        self.baudrate = int(self.get_parameter('baudrate').value)
        self.dxl_ids = [int(value) for value in self.get_parameter('dxl_ids').value]
        self.joint_names = [str(value) for value in self.get_parameter('joint_names').value]
        self.joint_signs = [float(value) for value in self.get_parameter('joint_signs').value]
        raw_home = [int(value) for value in self.get_parameter('home_positions').value]
        self.moving_speed = int(self.get_parameter('moving_speed').value)
        self.max_speed_value = int(self.get_parameter('max_speed_value').value)
        self.torque_limit = int(self.get_parameter('torque_limit').value)
        self.read_rate_hz = float(self.get_parameter('read_rate_hz').value)
        self.home_on_startup = bool(self.get_parameter('home_on_startup').value)
        self.disable_torque_on_shutdown = bool(
            self.get_parameter('disable_torque_on_shutdown').value
        )

        self._validate_configuration(raw_home)
        self.home_positions = [
            self.profile.raw_center if value < 0 else self.profile.clamp_raw(value)
            for value in raw_home
        ]

        self.port_handler: Optional[PortHandler] = None
        self.packet_handler: Optional[PacketHandler] = None
        self.hardware_ready = False
        self.torque_enabled = not self.use_hardware
        self.software_stop_active = False
        self._closed = False
        self._last_read_error_ns: Dict[int, int] = {}

        self.current_joint_positions = [
            self._raw_to_joint_radians(raw, index)
            for index, raw in enumerate(self.home_positions)
        ]
        self.commanded_joint_positions = list(self.current_joint_positions)

        self.joint_state_publisher = self.create_publisher(JointState, '/joint_states', 10)
        self.status_publisher = self.create_publisher(String, '/pincher/status', 10)
        self.command_subscription = self.create_subscription(
            JointState,
            '/pincher/command',
            self.command_callback,
            10,
        )
        self.speed_subscription = self.create_subscription(
            UInt32,
            '/pincher/profile_velocity',
            self.speed_callback,
            10,
        )
        self.home_service = self.create_service(Trigger, '/pincher/home', self.home_callback)
        self.stop_service = self.create_service(
            Trigger,
            '/pincher/software_stop',
            self.stop_callback,
        )
        self.torque_service = self.create_service(
            SetBool,
            '/pincher/torque_enable',
            self.torque_callback,
        )

        timer_period = 1.0 / max(self.read_rate_hz, 1.0)
        self.state_timer = self.create_timer(timer_period, self.state_timer_callback)

        if self.use_hardware:
            self.hardware_ready = self._connect_hardware()
            if self.hardware_ready and self.home_on_startup:
                self._move_home()
        else:
            self._publish_status(
                f'Modo sin hardware activo. Perfil seleccionado: {self.profile.name}.'
            )

        self.get_logger().info(
            f'Controlador iniciado | modelo={self.profile.name} | '
            f'use_hardware={self.use_hardware} | articulaciones={self.joint_names}'
        )

    def _validate_configuration(self, raw_home: List[int]) -> None:
        expected = len(self.dxl_ids)
        fields = {
            'joint_names': self.joint_names,
            'joint_signs': self.joint_signs,
            'home_positions': raw_home,
        }
        if expected == 0:
            raise ValueError('dxl_ids no puede estar vacío.')
        if len(set(self.dxl_ids)) != expected:
            raise ValueError(f'Los IDs DYNAMIXEL deben ser únicos: {self.dxl_ids}')
        for name, values in fields.items():
            if len(values) != expected:
                raise ValueError(
                    f'{name} debe tener {expected} elementos; se recibieron {len(values)}.'
                )
        for sign in self.joint_signs:
            if not math.isclose(abs(sign), 1.0, abs_tol=1e-9):
                raise ValueError('Cada elemento de joint_signs debe ser 1.0 o -1.0.')

    def _publish_status(self, text: str) -> None:
        msg = String()
        msg.data = text
        self.status_publisher.publish(msg)
        self.get_logger().info(text)

    def _connect_hardware(self) -> bool:
        self.port_handler = PortHandler(self.port_name)
        self.packet_handler = PacketHandler(self.profile.protocol_version)

        if not self.port_handler.openPort():
            self.get_logger().error(f'No se pudo abrir el puerto {self.port_name}.')
            return False
        if not self.port_handler.setBaudRate(self.baudrate):
            self.get_logger().error(f'No se pudo configurar baudrate={self.baudrate}.')
            self.port_handler.closePort()
            return False

        self.get_logger().info(
            f'Puerto {self.port_name} abierto a {self.baudrate} baud, '
            f'protocolo {self.profile.protocol_version:.1f}.'
        )

        all_ok = True
        for dxl_id in self.dxl_ids:
            if not self._write_register(
                dxl_id,
                self.profile.torque_enable_addr,
                1,
                1,
                'Torque Enable',
            ):
                all_ok = False
                continue
            if not self._write_speed(dxl_id, self.moving_speed):
                all_ok = False
            if (
                self.profile.torque_limit_addr is not None
                and self.torque_limit >= 0
                and not self._write_register(
                    dxl_id,
                    self.profile.torque_limit_addr,
                    self.profile.torque_limit_size,
                    max(0, min(1023, self.torque_limit)),
                    'Torque Limit',
                )
            ):
                all_ok = False

        if self.profile.torque_limit_addr is None and self.torque_limit >= 0:
            self.get_logger().warning(
                'El parámetro torque_limit se ignora para XL430: no existe un registro '
                'equivalente al Torque Limit(34) del AX-12A.'
            )

        self.torque_enabled = all_ok
        if all_ok:
            self._publish_status('Comunicación DYNAMIXEL inicializada correctamente.')
            return True

        self.get_logger().error(
            'La inicialización no fue correcta para todos los motores. '
            'Se deshabilitará el torque y se cerrará el puerto por seguridad.'
        )
        for dxl_id in self.dxl_ids:
            self._write_register(
                dxl_id,
                self.profile.torque_enable_addr,
                1,
                0,
                'Torque Enable de recuperación',
            )
        self.torque_enabled = False
        self.port_handler.closePort()
        return False

    def _communication_error_text(self, comm_result: int, dxl_error: int) -> str:
        if self.packet_handler is None:
            return 'PacketHandler no inicializado.'
        parts: List[str] = []
        if comm_result != COMM_SUCCESS:
            parts.append(self.packet_handler.getTxRxResult(comm_result))
        if dxl_error != 0:
            parts.append(self.packet_handler.getRxPacketError(dxl_error))
        return ' | '.join(parts) if parts else 'sin detalle'

    def _write_register(
        self,
        dxl_id: int,
        address: int,
        size: int,
        value: int,
        label: str,
    ) -> bool:
        if self.packet_handler is None or self.port_handler is None:
            return False
        methods = {
            1: self.packet_handler.write1ByteTxRx,
            2: self.packet_handler.write2ByteTxRx,
            4: self.packet_handler.write4ByteTxRx,
        }
        method = methods.get(size)
        if method is None:
            raise ValueError(f'Tamaño de registro no soportado: {size}')
        comm_result, dxl_error = method(
            self.port_handler,
            int(dxl_id),
            int(address),
            int(value),
        )
        if comm_result != COMM_SUCCESS or dxl_error != 0:
            self.get_logger().error(
                f'ID {dxl_id}: error escribiendo {label}: '
                f'{self._communication_error_text(comm_result, dxl_error)}'
            )
            return False
        return True

    def _read_register(
        self,
        dxl_id: int,
        address: int,
        size: int,
        label: str,
    ) -> Tuple[Optional[int], bool]:
        if self.packet_handler is None or self.port_handler is None:
            return None, False
        methods = {
            1: self.packet_handler.read1ByteTxRx,
            2: self.packet_handler.read2ByteTxRx,
            4: self.packet_handler.read4ByteTxRx,
        }
        method = methods.get(size)
        if method is None:
            raise ValueError(f'Tamaño de registro no soportado: {size}')
        value, comm_result, dxl_error = method(
            self.port_handler,
            int(dxl_id),
            int(address),
        )
        if comm_result != COMM_SUCCESS or dxl_error != 0:
            now_ns = self.get_clock().now().nanoseconds
            previous_ns = self._last_read_error_ns.get(dxl_id, 0)
            if now_ns - previous_ns > 2_000_000_000:
                self.get_logger().error(
                    f'ID {dxl_id}: error leyendo {label}: '
                    f'{self._communication_error_text(comm_result, dxl_error)}'
                )
                self._last_read_error_ns[dxl_id] = now_ns
            return None, False
        return int(value), True

    def _write_speed(self, dxl_id: int, speed: int) -> bool:
        safe_speed = max(0, min(self.max_speed_value, int(speed)))
        return self._write_register(
            dxl_id,
            self.profile.speed_addr,
            self.profile.speed_size,
            safe_speed,
            'Moving Speed/Profile Velocity',
        )

    def _raw_to_joint_radians(self, raw: int, joint_index: int) -> float:
        return self.profile.raw_to_radians(raw) * self.joint_signs[joint_index]

    def _joint_radians_to_raw(self, radians: float, joint_index: int) -> int:
        motor_radians = float(radians) / self.joint_signs[joint_index]
        return self.profile.radians_to_raw(motor_radians)

    def _command_pairs(self, msg: JointState) -> Iterable[Tuple[int, float]]:
        if msg.name:
            name_to_position = dict(zip(msg.name, msg.position))
            for index, name in enumerate(self.joint_names):
                if name in name_to_position:
                    yield index, float(name_to_position[name])
        else:
            for index, position in enumerate(msg.position[: len(self.joint_names)]):
                yield index, float(position)

    def command_callback(self, msg: JointState) -> None:
        if self.software_stop_active:
            self.get_logger().warning(
                'Comando ignorado: la parada de software está activa. '
                'Reactiva el torque antes de mover.'
            )
            return

        command_received = False
        for joint_index, radians in self._command_pairs(msg):
            command_received = True
            raw_goal = self._joint_radians_to_raw(radians, joint_index)
            clamped_radians = self._raw_to_joint_radians(raw_goal, joint_index)
            self.commanded_joint_positions[joint_index] = clamped_radians

            if self.use_hardware:
                if not self.hardware_ready or not self.torque_enabled:
                    self.get_logger().warning(
                        f'Comando para {self.joint_names[joint_index]} ignorado: '
                        'hardware no disponible o torque deshabilitado.'
                    )
                    continue
                self._write_register(
                    self.dxl_ids[joint_index],
                    self.profile.goal_position_addr,
                    self.profile.goal_position_size,
                    raw_goal,
                    'Goal Position',
                )
            else:
                self.current_joint_positions[joint_index] = clamped_radians

        if not command_received:
            self.get_logger().warning(
                'El mensaje /pincher/command no contiene articulaciones reconocidas.'
            )

    def speed_callback(self, msg: UInt32) -> None:
        requested = max(0, min(self.max_speed_value, int(msg.data)))
        self.moving_speed = requested
        if not self.use_hardware:
            self._publish_status(f'Velocidad simulada actualizada a {requested}.')
            return
        if not self.hardware_ready:
            self.get_logger().warning('No se puede actualizar velocidad: hardware no disponible.')
            return
        successes = sum(self._write_speed(dxl_id, requested) for dxl_id in self.dxl_ids)
        self._publish_status(
            f'Velocidad actualizada a {requested} en {successes}/{len(self.dxl_ids)} motores.'
        )

    def _move_home(self) -> bool:
        if self.software_stop_active or not self.torque_enabled:
            return False
        success = True
        for index, raw_goal in enumerate(self.home_positions):
            self.commanded_joint_positions[index] = self._raw_to_joint_radians(
                raw_goal,
                index,
            )
            if self.use_hardware:
                success = self._write_register(
                    self.dxl_ids[index],
                    self.profile.goal_position_addr,
                    self.profile.goal_position_size,
                    raw_goal,
                    'Goal Position HOME',
                ) and success
            else:
                self.current_joint_positions[index] = self.commanded_joint_positions[index]
        return success

    def home_callback(self, request: Trigger.Request, response: Trigger.Response) -> Trigger.Response:
        del request
        if self.software_stop_active or not self.torque_enabled:
            response.success = False
            response.message = (
                'HOME bloqueado: activa el torque y libera la parada de software primero.'
            )
            return response
        response.success = self._move_home()
        response.message = (
            'Comando HOME enviado.' if response.success else 'No fue posible enviar HOME.'
        )
        self._publish_status(response.message)
        return response

    def _set_torque_all(self, enabled: bool) -> bool:
        if not self.use_hardware:
            self.torque_enabled = enabled
            return True
        if not self.hardware_ready and enabled:
            return False
        successes = 0
        for dxl_id in self.dxl_ids:
            if self._write_register(
                dxl_id,
                self.profile.torque_enable_addr,
                1,
                1 if enabled else 0,
                'Torque Enable',
            ):
                successes += 1
        all_ok = successes == len(self.dxl_ids)
        if all_ok:
            self.torque_enabled = enabled
        return all_ok

    def torque_callback(
        self,
        request: SetBool.Request,
        response: SetBool.Response,
    ) -> SetBool.Response:
        response.success = self._set_torque_all(bool(request.data))
        if response.success:
            self.software_stop_active = False if request.data else self.software_stop_active
            state = 'habilitado' if request.data else 'deshabilitado'
            response.message = f'Torque {state} en todos los motores.'
        else:
            response.message = 'No fue posible cambiar el torque en todos los motores.'
        self._publish_status(response.message)
        return response

    def stop_callback(self, request: Trigger.Request, response: Trigger.Response) -> Trigger.Response:
        del request
        self.software_stop_active = True
        response.success = self._set_torque_all(False)
        response.message = (
            'Parada de software activa: torque deshabilitado.'
            if response.success
            else 'Parada solicitada, pero no se confirmó el torque de todos los motores.'
        )
        self._publish_status(response.message)
        return response

    def _read_hardware_positions(self) -> None:
        for index, dxl_id in enumerate(self.dxl_ids):
            raw, ok = self._read_register(
                dxl_id,
                self.profile.present_position_addr,
                self.profile.present_position_size,
                'Present Position',
            )
            if ok and raw is not None:
                self.current_joint_positions[index] = self._raw_to_joint_radians(raw, index)

    def state_timer_callback(self) -> None:
        if self.use_hardware and self.hardware_ready:
            self._read_hardware_positions()

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(self.joint_names)
        msg.position = list(self.current_joint_positions)
        self.joint_state_publisher.publish(msg)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self.use_hardware and self.port_handler is not None:
            if self.disable_torque_on_shutdown and self.packet_handler is not None:
                for dxl_id in self.dxl_ids:
                    self._write_register(
                        dxl_id,
                        self.profile.torque_enable_addr,
                        1,
                        0,
                        'Torque Enable al cerrar',
                    )
            self.port_handler.closePort()
            self.get_logger().info('Puerto DYNAMIXEL cerrado.')

    def destroy_node(self) -> bool:
        self.close()
        return super().destroy_node()

def main(args=None) -> None:
    rclpy.init(args=args)
    node: Optional[PincherController] = None
    try:
        node = PincherController()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        if node is not None:
            node.get_logger().fatal(f'Error fatal: {exc}')
        else:
            print(f'Error fatal iniciando pincher_control: {exc}')
        raise
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
