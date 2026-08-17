#!/usr/bin/env python3
"""Interpolacion de trayectorias (Actividad 9) — DATOS REALES.

Lee los CSV grabados por el nodo ``recorder`` mientras el sistema ROS ejecutaba
cada trayectoria (codo de -90 a +90 en 3 s con interpolacion lineal, cubica y
quintica) y grafica la posicion comandada (deseada) y la medida por el servo, mas
la velocidad obtenida por diferenciacion numerica de los datos reales.

El analisis se enfoca en la ventana de la rampa (la transicion -90 -> +90),
excluyendo el reposicionamiento inicial hacia la configuracion de arranque.

Requiere haber corrido antes: bash run_experiments.sh
"""

import sys

import _common  # noqa: F401

import math

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

METHODS = [('linear', 'lineal', '#7f8c8d'),
           ('cubic', 'cubica', '#2980b9'),
           ('quintic', 'quintica', '#c0392b')]

Q0, QF = -90.0, 90.0


def _ramp_window(tc, c_deg):
    """Devuelve (t_ini, t_fin) de la rampa Q0->QF en el comando."""
    rising = np.where(c_deg > Q0 + 2.0)[0]
    t_ini = tc[rising[0]] if len(rising) else tc[0]
    reached = np.where(c_deg >= QF - 2.0)[0]
    t_fin = tc[reached[0]] if len(reached) else tc[-1]
    return t_ini, t_fin


# Sufijo de los CSV: vacio = datos de simulacion; '_hw' = medidos sobre el robot.
SUFIJO = sys.argv[1] if len(sys.argv) > 1 else ''


def main() -> None:
    fig, (ax_p, ax_v) = plt.subplots(1, 2, figsize=(13, 5))
    print('Interpolacion (Actividad 9) — datos reales grabados (ventana de rampa):')
    for key, label, color in METHODS:
        cmd, _ = _common.load_csv(f'interp_{key}{SUFIJO}_cmd.csv')
        st, _ = _common.load_csv(f'interp_{key}{SUFIJO}_state.csv')
        tc, c = cmd['t'], np.degrees(cmd['c_elbow'])
        ts, q = st['t'], np.degrees(st['q_elbow'])

        t0, t1 = _ramp_window(tc, c)
        # ventana de visualizacion: un poco antes y despues de la rampa
        w0, w1 = t0 - 0.2, t1 + 1.0
        mc = (tc >= w0) & (tc <= w1)
        ms = (ts >= w0) & (ts <= w1)
        tcw, cw = tc[mc] - t0, c[mc]
        tsw, qw = ts[ms] - t0, q[ms]
        vw = np.gradient(qw, tsw)
        # v_max medida durante la rampa (excluye colas)
        ramp = (tsw >= 0) & (tsw <= (t1 - t0) + 0.4)
        vmax = float(np.nanmax(np.abs(vw[ramp]))) if np.any(ramp) else float('nan')
        print(f'  {label:9s}: v_max medida en rampa = {vmax:6.1f} °/s')

        ax_p.plot(tcw, cw, color=color, lw=1.0, ls='--', alpha=0.6)
        ax_p.plot(tsw, qw, color=color, lw=1.9, label=f'{label} (medida)')
        ax_v.plot(tsw, vw, color=color, lw=1.7, label=label)

    ax_p.set_title('Posicion angular del codo q(t)\n(— medida,  - - comando)')
    ax_p.set_xlabel('tiempo desde inicio de la rampa (s)')
    ax_p.set_ylabel('q (°)')
    ax_p.set_xlim(-0.2, 4.0)
    ax_p.grid(alpha=0.3)
    ax_p.legend(fontsize=8)

    ax_v.set_title('Velocidad angular (derivada de la señal medida)')
    ax_v.set_xlabel('tiempo desde inicio de la rampa (s)')
    ax_v.set_ylabel('velocidad (°/s)')
    ax_v.set_xlim(-0.2, 4.0)
    ax_v.grid(alpha=0.3)
    ax_v.legend(fontsize=8)

    fig.suptitle('Actividad 9 — Interpolacion lineal vs cubica vs quintica '
                 '(codo, datos reales del sistema ROS)', fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    _common.save(fig, f'interpolacion{SUFIJO}.png')


if __name__ == '__main__':
    main()
