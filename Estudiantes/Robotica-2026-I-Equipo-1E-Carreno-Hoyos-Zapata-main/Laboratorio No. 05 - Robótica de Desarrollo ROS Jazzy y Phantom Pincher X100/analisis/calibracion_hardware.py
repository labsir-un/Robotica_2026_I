#!/usr/bin/env python3
"""Gráficas de calibración con los datos MEDIDOS SOBRE EL ROBOT REAL (Actividad 5).

Los datos provienen de `bringup/calibrar_cero.py`, ejecutado sobre el manipulador
el 19-jul-2026: cinco posiciones por articulación en ±40°, con 2 s de asentamiento
antes de leer el `Present Position` de cada AX-12A.

Genera `imagenes/calibracion_hardware.png` con dos filas:

  * fila superior: deseado vs medido por articulación, con la recta ideal y el
    ajuste lineal `medido = a·deseado + b`;
  * fila inferior: el error `e = deseado − medido` frente al ángulo, que es donde
    se ve la diferencia entre un error de CERO (constante) y uno de GANANCIA
    (proporcional al ángulo).

Uso:  python3 analisis/calibracion_hardware.py
"""

from __future__ import annotations

import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt          # noqa: E402
import numpy as np                        # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(os.path.dirname(HERE), 'imagenes', 'calibracion_hardware.png')

# (deseado, medido) en grados, tal como los reporto el robot.
MEDIDAS = {
    'base (waist)':     [(-40, -40.18), (-20, -20.23), (0, -0.29), (20, 19.35), (40, 39.59)],
    'hombro (shoulder)': [(-40, -41.35), (-20, -21.11), (0, -0.29), (20, 20.53), (40, 41.06)],
    'codo (elbow)':     [(-40, -41.06), (-20, -21.11), (0, -0.59), (20, 20.23), (40, 40.18)],
    'muñeca (wrist)':   [(-40, -40.47), (-20, -20.53), (0, -0.29), (20, 19.65), (40, 39.59)],
}


def main() -> None:
    fig, ejes = plt.subplots(2, 4, figsize=(17, 8))
    resumen = []

    for col, (nombre, datos) in enumerate(MEDIDAS.items()):
        x = np.array([d[0] for d in datos], dtype=float)
        y = np.array([d[1] for d in datos], dtype=float)
        err = x - y
        a, b = np.polyfit(x, y, 1)
        e_max = err[np.argmax(np.abs(err))]
        resumen.append((nombre, np.abs(err).max(), err.mean(), a, b))

        # --- fila 1: deseado vs medido
        ax = ejes[0, col]
        lim = [-46, 46]
        ax.plot(lim, lim, 'k--', lw=1, label='ideal  y = x')
        ax.plot(x, y, 'o-', color='#c0392b', label='medido')
        ax.set_title(f'{nombre}\n$e_{{max}}$ = {np.abs(err).max():.2f}°  |  '
                     f'ganancia = {a:.4f}', fontsize=10)
        ax.set_xlabel('deseado (°)')
        if col == 0:
            ax.set_ylabel('medido (°)')
        ax.grid(alpha=.3)
        ax.legend(fontsize=8)
        ax.set_xlim(lim)
        ax.set_ylim(lim)

        # --- fila 2: error frente al angulo
        ax = ejes[1, col]
        ax.axhline(0, color='k', lw=1)
        ax.plot(x, err, 'o-', color='#2471a3', label='error medido')
        ax.plot(lim, [np.mean(err)] * 2, ':', color='#7f8c8d',
                label=f'offset medio = {err.mean():+.2f}°')
        ax.set_xlabel('ángulo deseado (°)')
        if col == 0:
            ax.set_ylabel('error  $e = q_{des} - q_{med}$  (°)')
        ax.grid(alpha=.3)
        ax.legend(fontsize=8)
        ax.set_xlim(lim)
        ax.set_ylim(-1.8, 1.8)

    fig.suptitle('Actividad 5 — Calibración de cero y error articular '
                 'sobre el ROBOT REAL (5 posiciones por articulación, ±40°)',
                 fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(SALIDA, dpi=110)
    print(f'  guardado: {os.path.relpath(SALIDA, os.path.dirname(HERE))}')

    print()
    print(f'{"articulacion":<20}{"e_max":>8}{"e_prom":>9}{"ganancia":>10}{"offset":>9}   tipo')
    for nombre, emax, eprom, a, b in resumen:
        tipo = 'GANANCIA (gravedad)' if abs(a - 1) > 0.015 else 'cero (offset puro)'
        print(f'{nombre:<20}{emax:8.2f}{eprom:9.2f}{a:10.4f}{b:9.2f}   {tipo}')


if __name__ == '__main__':
    main()
