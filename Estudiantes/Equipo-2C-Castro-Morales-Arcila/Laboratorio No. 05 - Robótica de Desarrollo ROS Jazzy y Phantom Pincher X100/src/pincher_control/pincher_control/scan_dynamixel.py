#!/usr/bin/env python3
"""Escáner de IDs DYNAMIXEL para protocolo 1.0 o 2.0."""

from __future__ import annotations

from typing import List, Optional

import rclpy
from dynamixel_sdk import COMM_SUCCESS, PacketHandler, PortHandler
from rclpy.node import Node

class DynamixelScanner(Node):
    def __init__(self) -> None:
        super().__init__('dynamixel_scanner')
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 1000000)
        self.declare_parameter('protocol_version', 2.0)
        self.declare_parameter('min_id', 0)
        self.declare_parameter('max_id', 20)

        self.port_name = str(self.get_parameter('port').value)
        self.baudrate = int(self.get_parameter('baudrate').value)
        self.protocol_version = float(self.get_parameter('protocol_version').value)
        self.min_id = max(0, int(self.get_parameter('min_id').value))
        self.max_id = min(252, int(self.get_parameter('max_id').value))

        if self.min_id > self.max_id:
            raise ValueError('min_id no puede ser mayor que max_id.')
        if self.protocol_version not in (1.0, 2.0):
            raise ValueError('protocol_version debe ser 1.0 o 2.0.')

    def scan(self) -> List[int]:
        port = PortHandler(self.port_name)
        packet = PacketHandler(self.protocol_version)
        detected: List[int] = []

        if not port.openPort():
            raise RuntimeError(f'No se pudo abrir {self.port_name}.')
        try:
            if not port.setBaudRate(self.baudrate):
                raise RuntimeError(f'No se pudo configurar baudrate={self.baudrate}.')

            self.get_logger().info(
                f'Escaneando IDs {self.min_id}..{self.max_id} en {self.port_name}, '
                f'{self.baudrate} baud, protocolo {self.protocol_version:.1f}.'
            )
            for dxl_id in range(self.min_id, self.max_id + 1):
                model_number, comm_result, dxl_error = packet.ping(port, dxl_id)
                if comm_result == COMM_SUCCESS and dxl_error == 0:
                    detected.append(dxl_id)
                    self.get_logger().info(
                        f'ID detectado: {dxl_id} | model_number={model_number}'
                    )

            if detected:
                self.get_logger().info(f'IDs encontrados: {detected}')
            else:
                self.get_logger().warning(
                    'No se detectaron motores. Revisa alimentación, puerto, baudrate y protocolo.'
                )
            return detected
        finally:
            port.closePort()

def main(args=None) -> None:
    rclpy.init(args=args)
    node: Optional[DynamixelScanner] = None
    try:
        node = DynamixelScanner()
        node.scan()
    except Exception as exc:
        if node is not None:
            node.get_logger().error(str(exc))
        else:
            print(f'Error iniciando el escáner: {exc}')
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
