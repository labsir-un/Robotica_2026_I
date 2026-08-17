#!/usr/bin/env python3
"""Mide los topes mecanicos de una articulacion moviendola A MANO.

El torque debe estar DESACTIVADO (ver ir_a_home.py). El programa solo LEE el
encoder: no manda ningun movimiento, asi que no puede forzar la mecanica. Se
registra el minimo y el maximo alcanzados durante la ventana de medicion.

Uso:  python3 medir_topes.py --id 1 --segundos 40
"""

from __future__ import annotations

import argparse
import time

from dynamixel_sdk import PacketHandler, PortHandler

PUERTO, BAUD = '/dev/ttyUSB0', 1000000
ADDR_TORQUE, ADDR_PRESENT = 24, 36
CENTRO, ESCALA = 512, 300.0 / 1023.0
NOMBRES = {1: 'base (waist)', 2: 'hombro (shoulder)', 3: 'codo (elbow)',
           4: 'muneca (wrist)', 5: 'pinza (gripper)'}


def grados(raw: int) -> float:
    return (raw - CENTRO) * ESCALA


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--id', type=int, required=True, choices=[1, 2, 3, 4, 5])
    ap.add_argument('--segundos', type=float, default=40.0)
    args = ap.parse_args()

    port, packet = PortHandler(PUERTO), PacketHandler(1.0)
    if not port.openPort():
        print(f'ERROR: no se pudo abrir {PUERTO}')
        return 1
    port.setBaudRate(BAUD)

    # Comprobar que el torque esta suelto: mover a mano con torque activo forzaria
    # el engranaje.
    tq, _, _ = packet.read1ByteTxRx(port, args.id, ADDR_TORQUE)
    if tq:
        print(f'AVISO: el motor {args.id} tiene el TORQUE ACTIVADO. Se desactiva.')
        packet.write1ByteTxRx(port, args.id, ADDR_TORQUE, 0)
        time.sleep(0.2)

    print(f'Midiendo {NOMBRES[args.id]} durante {args.segundos:.0f} s.')
    print('Muevela despacio hasta notar resistencia en AMBOS sentidos, sin forzar.')

    lo, hi, muestras, fallos = 1e9, -1e9, 0, 0
    fin = time.time() + args.segundos
    while time.time() < fin:
        raw, res, _ = packet.read2ByteTxRx(port, args.id, ADDR_PRESENT)
        if res != 0:
            fallos += 1
            continue
        g = grados(raw)
        lo, hi = min(lo, g), max(hi, g)
        muestras += 1
        time.sleep(0.02)

    port.closePort()
    if not muestras:
        print('ERROR: ninguna lectura valida.')
        return 1

    print(f'\n  recorrido observado: {lo:+.1f} deg  ..  {hi:+.1f} deg'
          f'   (amplitud {hi - lo:.1f} deg)')
    print(f'  muestras={muestras}  fallos_lectura={fallos}')
    print(f'  sugerencia de limite seguro (3 deg hacia adentro): '
          f'{lo + 3:+.0f} .. {hi - 3:+.0f}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
