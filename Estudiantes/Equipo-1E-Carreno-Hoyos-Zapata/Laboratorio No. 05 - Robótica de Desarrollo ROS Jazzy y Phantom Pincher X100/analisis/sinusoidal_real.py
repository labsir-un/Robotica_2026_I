#!/usr/bin/env python3
"""Trayectoria sinusoidal de una articulacion (Actividad 10) — DATOS REALES.

Lee los CSV grabados durante las cuatro pruebas sinusoidales (2 amplitudes x 2
frecuencias) ejecutadas en el sistema ROS, grafica la posicion deseada (comando)
y la medida (respuesta del servo) y calcula el error maximo y el error cuadratico
medio (RMS) a partir de los datos reales.

Requiere haber corrido antes: bash run_experiments.sh
"""

import sys

import _common  # noqa: F401

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

TESTS = [
    ('sinus_a20_f025', 20, 0.25),
    ('sinus_a20_f050', 20, 0.50),
    ('sinus_a40_f025', 40, 0.25),
    ('sinus_a40_f050', 40, 0.50),
]


# Sufijo de los CSV: vacio = datos de simulacion; '_hw' = medidos sobre el robot.
SUFIJO = sys.argv[1] if len(sys.argv) > 1 else ''


def main() -> None:
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    axes = axes.ravel()
    print('Trayectoria sinusoidal (Actividad 10) — datos reales:')
    print(f'{"prueba":>16} | {"A":>3} | {"f":>4} | {"e_max(°)":>8} | {"RMS(°)":>7}')

    for i, (key, A, f) in enumerate(TESTS):
        cmd, _ = _common.load_csv(f'{key}{SUFIJO}_cmd.csv')
        st, _ = _common.load_csv(f'{key}{SUFIJO}_state.csv')
        tc, c = cmd['t'], np.degrees(cmd['c_elbow'])
        ts, q = st['t'], np.degrees(st['q_elbow'])

        # error: interpola el comando a los tiempos de medida
        c_at_state = np.interp(ts, tc, c)
        err = q - c_at_state
        e_max = float(np.nanmax(np.abs(err)))
        rms = float(np.sqrt(np.nanmean(err ** 2)))
        print(f'{key:>16} | {A:3d} | {f:4.2f} | {e_max:8.2f} | {rms:7.2f}')

        ax = axes[i]
        ax.plot(tc, c, color='#2980b9', lw=1.6, label='deseada (comando)')
        ax.plot(ts, q, color='#c0392b', lw=1.1, label='medida (servo)')
        ax.set_title(f'A={A}°, f={f:.2f} Hz  (e_max={e_max:.1f}°, RMS={rms:.1f}°)',
                     fontsize=10)
        ax.set_xlabel('tiempo (s)')
        ax.set_ylabel('q codo (°)')
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)

    fig.suptitle('Actividad 10 — Trayectoria sinusoidal q(t)=A·sin(2π f t) '
                 '(datos reales del sistema ROS)', fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    _common.save(fig, f'sinusoidal{SUFIJO}.png')


if __name__ == '__main__':
    main()
