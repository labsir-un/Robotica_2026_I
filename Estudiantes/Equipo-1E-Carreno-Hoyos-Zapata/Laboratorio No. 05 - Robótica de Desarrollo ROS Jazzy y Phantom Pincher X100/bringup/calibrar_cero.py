#!/usr/bin/env python3
"""Calibracion de cero y error articular sobre el robot REAL (Actividad 5).

Para cada articulacion envia varias posiciones conocidas, espera a que asiente y
lee el `Present Position`. Con el error e = deseado - medido calcula el error
maximo, el promedio y el desplazamiento de cero a aplicar.

Seguridad:
  - Solo mueve UNA articulacion cada vez; las demas se mantienen en cero, con lo
    que el brazo queda vertical y despejado.
  - Antes de mover valida cada pose con la guarda de suelo del entregable.
  - Velocidad de perfil baja y anti-tiron (Goal = Present antes del torque).
  - Al terminar devuelve todo a home y suelta el torque.

Uso:  python3 calibrar_cero.py [--amplitud 40] [--velocidad 50] [--asentar 2.0]
"""

from __future__ import annotations

import argparse
import math
import os
import sys
import time

from dynamixel_sdk import PacketHandler, PortHandler

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'src', 'pincher_lab'))
from pincher_lab import safe_limits                      # noqa: E402

PUERTO, BAUD = '/dev/ttyUSB0', 1000000
ADDR_TORQUE, ADDR_GOAL, ADDR_SPEED, ADDR_PRESENT = 24, 30, 32, 36
CENTRO, ESCALA = 512, 300.0 / 1023.0
# La pinza se excluye: su mecanismo no permite una referencia externa fiable.
JUNTAS = [(1, 'base'), (2, 'hombro'), (3, 'codo'), (4, 'muneca')]


def a_grados(raw: int) -> float:
    return (raw - CENTRO) * ESCALA


def a_raw(grados: float) -> int:
    return int(round(CENTRO + grados / ESCALA))


def poses_seguras(idx: int, angulos) -> bool:
    """Comprueba con la guarda de suelo que mover SOLO esa junta es seguro."""
    for g in angulos:
        q = [0.0] * 5
        q[idx] = math.radians(g)
        if not safe_limits.is_above_floor(q):
            print(f'  ABORTADO: {g:+.0f} deg dejaria el brazo a '
                  f'{safe_limits.min_arm_height(q) * 1000:.0f} mm del suelo.')
            return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--amplitud', type=float, default=40.0)
    ap.add_argument('--velocidad', type=int, default=50)
    ap.add_argument('--asentar', type=float, default=2.0)
    args = ap.parse_args()

    a = args.amplitud
    objetivos = [-a, -a / 2.0, 0.0, a / 2.0, a]

    port, packet = PortHandler(PUERTO), PacketHandler(1.0)
    if not port.openPort():
        print(f'ERROR: no se pudo abrir {PUERTO}')
        return 1
    port.setBaudRate(BAUD)

    # Anti-tiron: fijar Goal = Present antes de energizar.
    for i, _ in JUNTAS + [(5, 'pinza')]:
        raw, res, _ = packet.read2ByteTxRx(port, i, ADDR_PRESENT)
        if res == 0:
            packet.write2ByteTxRx(port, i, ADDR_GOAL, raw)
        packet.write2ByteTxRx(port, i, ADDR_SPEED, args.velocidad)
        packet.write1ByteTxRx(port, i, ADDR_TORQUE, 1)
    time.sleep(0.3)

    # Llevar todo a cero antes de empezar.
    print(f'Posicionando en home (velocidad {args.velocidad})...')
    for i, _ in JUNTAS + [(5, 'pinza')]:
        packet.write2ByteTxRx(port, i, ADDR_GOAL, CENTRO)
    time.sleep(3.0)

    resumen = []
    for idx, (dxl_id, nombre) in enumerate(JUNTAS):
        print(f'\n--- {nombre} (ID {dxl_id}) ---')
        if not poses_seguras(idx, objetivos):
            continue
        errores = []
        print(f'{"deseado":>9} {"medido":>9} {"error":>8}')
        for g in objetivos:
            packet.write2ByteTxRx(port, dxl_id, ADDR_GOAL, a_raw(g))
            time.sleep(args.asentar)
            raw, res, _ = packet.read2ByteTxRx(port, dxl_id, ADDR_PRESENT)
            if res != 0:
                print(f'{g:9.1f}  sin lectura')
                continue
            medido = a_grados(raw)
            e = g - medido
            errores.append(e)
            print(f'{g:9.1f} {medido:9.2f} {e:8.2f}')
        packet.write2ByteTxRx(port, dxl_id, ADDR_GOAL, CENTRO)
        time.sleep(1.5)
        if errores:
            emax = max(errores, key=abs)
            eprom = sum(errores) / len(errores)
            resumen.append((nombre, emax, eprom))
            print(f'  error max = {emax:+.2f} deg | promedio = {eprom:+.2f} deg'
                  f' | offset de cero = {eprom:+.2f} deg')

    print('\n================ RESUMEN ================')
    print(f'{"articulacion":<12} {"e_max":>8} {"e_prom":>8} {"offset":>8}')
    for nombre, emax, eprom in resumen:
        print(f'{nombre:<12} {emax:8.2f} {eprom:8.2f} {eprom:8.2f}')

    print('\nDevolviendo a home y soltando torque...')
    for i, _ in JUNTAS + [(5, 'pinza')]:
        packet.write2ByteTxRx(port, i, ADDR_GOAL, CENTRO)
    time.sleep(2.5)
    for i, _ in JUNTAS + [(5, 'pinza')]:
        packet.write1ByteTxRx(port, i, ADDR_TORQUE, 0)
    port.closePort()
    print('Listo.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
