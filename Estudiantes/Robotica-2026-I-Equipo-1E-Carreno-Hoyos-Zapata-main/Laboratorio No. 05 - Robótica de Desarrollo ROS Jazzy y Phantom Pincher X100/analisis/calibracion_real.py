#!/usr/bin/env python3
"""Calibracion / exactitud articular (Actividad 5) — DATOS REALES.

Lee el CSV grabado mientras cada articulacion recorrio cinco escalones en el
sistema ROS. Para cada escalon detecta la posicion comandada (deseada) y la
posicion medida en regimen permanente (respuesta del servo simulado), calcula el
error e_q = q_deseado - q_medido, su maximo y promedio, y el desplazamiento de
cero. Tambien grafica una respuesta transitoria real (dinamica del servo).

Importante: en simulacion el controlador es exacto, por lo que el error de
exactitud es del orden de la resolucion del muestreo. Sobre el robot fisico, el
mismo procedimiento, leyendo el registro Present Position de cada Dynamixel,
caracteriza el error real del servo y el desplazamiento de cero a corregir.

Requiere haber corrido antes: bash run_experiments.sh
"""

import _common  # noqa: F401

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from safe_limits import JOINT_NAMES


def _plateaus(t, c):
    """Detecta segmentos de comando constante no nulo (>0.8 s). Devuelve lista
    de (valor_comando, t_inicio, t_fin)."""
    segs = []
    if len(t) == 0:
        return segs
    start = 0
    for i in range(1, len(c)):
        if abs(c[i] - c[start]) > 1e-4:
            if abs(c[start]) > 1e-3 and (t[i - 1] - t[start]) > 0.8:
                segs.append((c[start], t[start], t[i - 1]))
            start = i
    if abs(c[start]) > 1e-3 and (t[-1] - t[start]) > 0.8:
        segs.append((c[start], t[start], t[-1]))
    return segs


def main() -> None:
    cmd, _ = _common.load_csv('calib_cmd.csv')
    st, _ = _common.load_csv('calib_state.csv')

    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    axes = axes.ravel()
    print('Calibracion / exactitud (Actividad 5) — datos reales:')
    print(f'{"art.":>9} | {"e_max(°)":>8} | {"e_prom(°)":>9} | {"offset0(°)":>10}')

    summary = []
    transient_joint = None
    for i, name in enumerate(JOINT_NAMES):
        c = cmd[f'c_{name}']
        tc = cmd['t']
        q = st[f'q_{name}']
        ts = st['t']
        segs = _plateaus(tc, c)
        desired, measured = [], []
        for val, _t0, t1 in segs:
            # posicion medida en regimen permanente: promedio del ultimo 0.3 s
            mask = (ts >= t1 - 0.3) & (ts <= t1)
            if np.any(mask):
                measured.append(float(np.nanmean(q[mask])))
                desired.append(float(val))
        desired = np.degrees(np.array(desired))
        measured = np.degrees(np.array(measured))
        if len(desired) == 0:
            continue
        err = desired - measured
        e_max = float(np.nanmax(np.abs(err)))
        e_mean = float(np.nanmean(np.abs(err)))
        slope, intercept = np.polyfit(desired, measured, 1)
        zero_off = float(intercept)
        summary.append((name, e_max, e_mean, zero_off))
        print(f'{name:>9} | {e_max:8.3f} | {e_mean:9.3f} | {zero_off:10.3f}')

        ax = axes[i]
        lim = max(abs(desired.min()), abs(desired.max())) * 1.1
        ax.plot([-lim, lim], [-lim, lim], 'k--', lw=1, label='ideal y=x')
        ax.plot(desired, measured, 'o-', color='#c0392b', label='medida')
        ax.set_title(f'{name}  (e_max={e_max:.3f}°)')
        ax.set_xlabel('deseada (°)')
        ax.set_ylabel('medida (°)')
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
        if transient_joint is None and len(segs) >= 1:
            transient_joint = (name, segs)

    # Panel 6: respuesta transitoria real (dinamica del servo) de un escalon.
    ax = axes[5]
    if transient_joint is not None:
        name, segs = transient_joint
        val, t0, t1 = segs[1] if len(segs) > 1 else segs[0]
        ts = st['t']
        q = np.degrees(st[f'q_{name}'])
        tc = cmd['t']
        c = np.degrees(cmd[f'c_{name}'])
        # ventana alrededor del inicio del escalon
        w0, w1 = t0 - 0.2, t0 + 1.3
        m = (ts >= w0) & (ts <= w1)
        mc = (tc >= w0) & (tc <= w1)
        ax.plot(tc[mc] - t0, c[mc], color='#2980b9', lw=1.6, label='comando')
        ax.plot(ts[m] - t0, q[m], color='#c0392b', lw=1.6, label='medida (servo)')
        ax.set_title(f'Respuesta transitoria real — {name}')
        ax.set_xlabel('tiempo desde el escalon (s)')
        ax.set_ylabel('q (°)')
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)

    fig.suptitle('Actividad 5 — Calibracion / exactitud articular '
                 '(datos reales del sistema ROS)', fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    _common.save(fig, 'calibracion.png')


if __name__ == '__main__':
    main()
