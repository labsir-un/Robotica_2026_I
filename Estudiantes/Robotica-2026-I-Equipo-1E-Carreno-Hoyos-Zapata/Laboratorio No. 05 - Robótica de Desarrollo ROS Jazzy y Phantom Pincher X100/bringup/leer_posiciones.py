#!/usr/bin/env python3
"""Lectura SEGURA de posiciones del PhantomX Pincher X100 (torque OFF).

Uso durante el *bring-up* del robot físico. NO mueve ningún motor: solo se
conecta, verifica que respondan los 5 servos, DESACTIVA el torque (para poder
mover las articulaciones a mano) y muestra la posición de cada junta en grados
en tiempo real, registrando el mínimo y máximo alcanzado.

Flujo pensado (medición manual de topes acordada con el equipo):
  1. Ejecutar este script.               -> torque OFF, empieza a leer.
  2. Mover CADA articulación a mano,      -> hasta el tope físico seguro.
     lentamente, una por una.
  3. Ctrl-C.                              -> imprime el resumen mín/máx = límites.

Convención (idéntica al driver oficial del KIT, AX-12A protocolo 1.0):
  rad = (present - 512) * 2.618/512 ; grados = rad*180/pi ; se aplica joint_sign.

Requisitos: dynamixel_sdk, adaptador serial conectado (/dev/ttyUSB0 por defecto).
No requiere ROS. Argumentos opcionales: --port /dev/ttyUSB0 --baud 1000000
"""

import argparse
import math
import sys
import time

from dynamixel_sdk import PortHandler, PacketHandler

# --- Parámetros AX-12A (protocolo 1.0) --------------------------------------
PROTOCOL_VERSION = 1.0
ADDR_TORQUE_ENABLE = 24
ADDR_PRESENT_POSITION = 36
CENTER = 512.0
SCALE_RAD = 2.618 / 512.0  # rad por unidad Dynamixel (2.618 rad = 150 deg)

# ID de motor -> (nombre de junta, signo). Confirmado por driver KIT y equipo 3A.
JOINTS = [
    (1, 'waist',    +1),
    (2, 'shoulder', -1),
    (3, 'elbow',    -1),
    (4, 'wrist',    -1),
    (5, 'gripper',  +1),
]


def present_deg(packet, port, dxl_id, sign):
    """Lee Present Position y devuelve grados (o None si no responde)."""
    pos, result, error = packet.read2ByteTxRx(port, dxl_id, ADDR_PRESENT_POSITION)
    if result != 0 or error != 0:
        return None
    rad = (pos - CENTER) * SCALE_RAD * sign
    return math.degrees(rad)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', default='/dev/ttyUSB0')
    ap.add_argument('--baud', type=int, default=1000000)
    args = ap.parse_args()

    port = PortHandler(args.port)
    packet = PacketHandler(PROTOCOL_VERSION)

    if not port.openPort():
        print(f'ERROR: no se pudo abrir {args.port}. '
              f'¿Está conectado el adaptador? ¿permisos (grupo dialout)?')
        sys.exit(1)
    if not port.setBaudRate(args.baud):
        print(f'ERROR: no se pudo fijar baudrate {args.baud}.')
        port.closePort()
        sys.exit(1)

    print(f'Puerto {args.port} @ {args.baud} baud abierto.\n')

    # --- Verificar presencia de cada motor (ping) ---------------------------
    presentes = []
    print('=== Verificación de motores (ping) ===')
    for dxl_id, nombre, sign in JOINTS:
        model, result, error = packet.ping(port, dxl_id)
        if result == 0 and error == 0:
            print(f'  [OK]   ID {dxl_id} ({nombre:<8}) modelo #{model}')
            presentes.append((dxl_id, nombre, sign))
        else:
            print(f'  [----] ID {dxl_id} ({nombre:<8}) NO responde')
    print()

    if not presentes:
        print('Ningún motor respondió. Verifica alimentación de la fuente y cableado.')
        port.closePort()
        sys.exit(1)

    # --- Desactivar torque para poder mover a mano --------------------------
    print('=== Desactivando torque (mover a mano) ===')
    for dxl_id, nombre, _ in presentes:
        packet.write1ByteTxRx(port, dxl_id, ADDR_TORQUE_ENABLE, 0)
        print(f'  torque OFF -> ID {dxl_id} ({nombre})')
    print('\nMueve cada articulación LENTAMENTE hasta su tope físico seguro.')
    print('Pulsa Ctrl-C cuando termines para ver el resumen mín/máx.\n')

    mins = {n: math.inf for _, n, _ in presentes}
    maxs = {n: -math.inf for _, n, _ in presentes}

    try:
        while True:
            fila = []
            for dxl_id, nombre, sign in presentes:
                deg = present_deg(packet, port, dxl_id, sign)
                if deg is None:
                    fila.append(f'{nombre}:  ----  ')
                    continue
                mins[nombre] = min(mins[nombre], deg)
                maxs[nombre] = max(maxs[nombre], deg)
                fila.append(f'{nombre}:{deg:7.1f}° [{mins[nombre]:6.1f},{maxs[nombre]:6.1f}]')
            print('  ' + ' | '.join(fila) + '        ', end='\r', flush=True)
            time.sleep(0.05)
    except KeyboardInterrupt:
        print('\n\n=== RESUMEN: topes físicos observados (grados) ===')
        print(f'  {"Junta":<10}{"mínimo":>10}{"máximo":>10}')
        for _, nombre, _ in presentes:
            lo = mins[nombre] if mins[nombre] != math.inf else float("nan")
            hi = maxs[nombre] if maxs[nombre] != -math.inf else float("nan")
            print(f'  {nombre:<10}{lo:>10.1f}{hi:>10.1f}')
        print('\nUsa estos valores (con margen hacia adentro) para safe_limits.py.')
    finally:
        port.closePort()


if __name__ == '__main__':
    main()
