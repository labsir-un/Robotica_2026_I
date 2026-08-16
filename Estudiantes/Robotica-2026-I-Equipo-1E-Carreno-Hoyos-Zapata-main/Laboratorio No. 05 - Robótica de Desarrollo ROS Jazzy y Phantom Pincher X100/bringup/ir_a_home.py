#!/usr/bin/env python3
"""Lleva el robot a home de forma suave y deja el torque desactivado.

Pensado como paso previo a la medicion manual de topes: deja el brazo en el cero
mecanico (vertical) y luego suelto para poder moverlo con la mano.

Secuencia:
  1. Lee la posicion actual de los cinco AX-12A.
  2. Fija Goal = Present ANTES de activar el torque (evita el tiron inicial).
  3. Baja la velocidad de perfil.
  4. Interpola la meta hasta el centro (512) en pasos pequenos.
  5. Desactiva el torque.

Uso:  python3 ir_a_home.py [--velocidad 40] [--pasos 60]
"""

from __future__ import annotations

import argparse
import time

from dynamixel_sdk import PacketHandler, PortHandler

PUERTO = '/dev/ttyUSB0'
BAUD = 1000000
IDS = [1, 2, 3, 4, 5]
NOMBRES = {1: 'base', 2: 'hombro', 3: 'codo', 4: 'muneca', 5: 'pinza'}

ADDR_TORQUE, ADDR_GOAL, ADDR_SPEED, ADDR_PRESENT = 24, 30, 32, 36
CENTRO = 512
GRADOS_POR_PASO = 300.0 / 1023.0


def grados(raw: int) -> float:
    return (raw - CENTRO) * GRADOS_POR_PASO


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--velocidad', type=int, default=40,
                    help='velocidad de perfil (1-1023, bajo = lento)')
    ap.add_argument('--pasos', type=int, default=60,
                    help='numero de pasos de interpolacion hasta home')
    args = ap.parse_args()

    port, packet = PortHandler(PUERTO), PacketHandler(1.0)
    if not port.openPort():
        print(f'ERROR: no se pudo abrir {PUERTO}')
        return 1
    port.setBaudRate(BAUD)

    # 1) leer posiciones actuales
    actual = {}
    for i in IDS:
        raw, res, _ = packet.read2ByteTxRx(port, i, ADDR_PRESENT)
        if res != 0:
            print(f'ERROR: el motor {i} ({NOMBRES[i]}) no responde.')
            port.closePort()
            return 1
        actual[i] = raw
    print('Posicion actual:')
    for i in IDS:
        print(f'  {i} {NOMBRES[i]:<8} {grados(actual[i]):+7.1f} deg')

    # 2) anti-tiron + 3) velocidad baja + activar torque
    print(f'\nFijando Goal = Present y activando torque (velocidad {args.velocidad})...')
    for i in IDS:
        packet.write2ByteTxRx(port, i, ADDR_GOAL, actual[i])
        packet.write2ByteTxRx(port, i, ADDR_SPEED, args.velocidad)
        packet.write1ByteTxRx(port, i, ADDR_TORQUE, 1)
    time.sleep(0.3)

    # 4) interpolar hasta el centro
    print('Moviendo a home (vertical)...')
    for paso in range(1, args.pasos + 1):
        t = paso / args.pasos
        for i in IDS:
            objetivo = int(round(actual[i] + (CENTRO - actual[i]) * t))
            packet.write2ByteTxRx(port, i, ADDR_GOAL, objetivo)
        time.sleep(0.05)
    time.sleep(1.5)

    final = {}
    for i in IDS:
        raw, res, _ = packet.read2ByteTxRx(port, i, ADDR_PRESENT)
        final[i] = raw if res == 0 else actual[i]
    print('Posicion alcanzada:')
    for i in IDS:
        print(f'  {i} {NOMBRES[i]:<8} {grados(final[i]):+7.1f} deg')

    # 5) soltar
    print('\nDesactivando torque: el brazo queda suelto.')
    for i in IDS:
        packet.write1ByteTxRx(port, i, ADDR_TORQUE, 0)

    port.closePort()
    print('Listo. Sujeta el brazo antes de soltarlo si esta en una pose alta.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
