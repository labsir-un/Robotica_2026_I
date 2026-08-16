#!/usr/bin/env python3
"""Diagrama cinematico, espacio de trabajo y plano de planta (Actividades 3 y entrega).

Genera:
  - diagrama_cinematico.png : esquema del brazo en el plano sagital con las
    dimensiones (L1..L4, Lm), los ejes de movimiento y los sistemas coordenados.
  - espacio_trabajo.png     : nube de puntos alcanzables (corte sagital) y
    alcance maximo.
  - plano_planta.png        : vista superior del puesto de trabajo con el robot,
    el area de dibujo y la zona segura.
"""

import _common  # noqa: F401

import math

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

import kinematics as k


def diagrama_cinematico() -> None:
    fig, ax = plt.subplots(figsize=(8, 8))

    # Pose representativa para que se distingan los eslabones.
    q = [0.0, math.radians(-35), math.radians(60), math.radians(35)]
    # Posiciones en el plano sagital (r, z).
    pts = []
    Tt = np.eye(4)
    Tt = Tt @ k._txyz_rpy(0, 0, k.H - k.L1, 0, 0, 0) @ k._rotz(q[0])
    Tt = Tt @ k._txyz_rpy(0, 0, k.L1, -math.pi / 2, 0, 0) @ k._rotz(q[1])
    pts.append(('hombro', Tt[:3, 3].copy()))
    Tt = Tt @ k._txyz_rpy(k.Lm, -k.L2, 0, 0, 0, -k.B) @ k._rotz(q[2])
    pts.append(('codo', Tt[:3, 3].copy()))
    Tt = Tt @ k._txyz_rpy(k.L3 * math.cos(k.B), k.L3 * math.sin(k.B), 0, 0, 0, k.B) @ k._rotz(q[3])
    pts.append(('muneca', Tt[:3, 3].copy()))
    Tt = Tt @ k._txyz_rpy(k.L4, 0, 0, 0, 0, 0)
    pts.append(('TCP', Tt[:3, 3].copy()))

    base = np.array([0.0, 0.0])
    sh = np.array([0.0, k.H])
    chain = [sh] + [np.array([math.hypot(p[0], p[1]), p[2]]) for _, p in pts[1:]]

    # Suelo y base.
    ax.add_patch(plt.Rectangle((-0.06, -0.01), 0.12, 0.01, color='0.6'))
    ax.plot([-0.07, 0.07], [0, 0], 'k', lw=2)
    ax.plot([base[0], sh[0]], [base[1], sh[1]], color='#34495e', lw=6,
            solid_capstyle='round')

    seg_labels = ['a1 (hombro-codo)', 'a2 (codo-muneca)', 'a3 (muneca-TCP)']
    seg_colors = ['#2980b9', '#27ae60', '#c0392b']
    for i in range(len(chain) - 1):
        x0, y0 = chain[i]
        x1, y1 = chain[i + 1]
        ax.plot([x0, x1], [y0, y1], color=seg_colors[i], lw=5,
                solid_capstyle='round', label=seg_labels[i])

    joint_names = ['J1 base (z0)', 'J2 hombro', 'J3 codo', 'J4 muneca']
    joint_pts = [base, chain[0], chain[1], chain[2]]
    for name, p in zip(joint_names, joint_pts):
        ax.plot(p[0], p[1], 'o', color='black', ms=9, zorder=5)
        ax.annotate(name, (p[0], p[1]), textcoords='offset points',
                    xytext=(8, 8), fontsize=9)
    ax.plot(chain[-1][0], chain[-1][1], '*', color='#e67e22', ms=18, zorder=6)
    ax.annotate('TCP (x,y,z)', chain[-1], textcoords='offset points',
                xytext=(8, -14), fontsize=9)

    # Eje z0 (vertical, base) y cota de altura H.
    ax.annotate('', xy=(0, k.H + 0.03), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color='0.4'))
    ax.annotate('z0 (eje J1)', (0, k.H + 0.03), fontsize=9, color='0.3')
    ax.annotate(f'H = {k.H*1000:.1f} mm', (0.005, k.H / 2), fontsize=9, rotation=90,
                va='center')

    txt = (f'L1 = {k.L1*1000:.1f} mm\nL2 = {k.L2*1000:.1f} mm\n'
           f'L3 = {k.L3*1000:.1f} mm\nL4 = {k.L4*1000:.1f} mm\n'
           f'Lm = {k.Lm*1000:.1f} mm\n'
           f'a1 = {k.A1*1000:.1f} mm\na2 = {k.A2*1000:.1f} mm\n'
           f'a3 = {k.A3*1000:.1f} mm\nb  = {math.degrees(k.B):.1f}°')
    ax.text(0.20, 0.02, txt, fontsize=9, family='monospace',
            bbox=dict(boxstyle='round', fc='#fdf6e3', ec='0.7'))

    ax.set_title('Actividad 3 — Diagrama cinematico (plano sagital)\n'
                 'PhantomX Pincher X100 — ejes, eslabones y sistema coordenado')
    ax.set_xlabel('r = √(x²+y²)  [m]')
    ax.set_ylabel('z  [m]')
    ax.set_aspect('equal')
    ax.grid(alpha=0.3)
    ax.legend(loc='upper right', fontsize=8)
    ax.set_xlim(-0.1, 0.34)
    ax.set_ylim(-0.03, 0.32)
    _common.save(fig, 'diagrama_cinematico.png')


def espacio_trabajo() -> None:
    fig, ax = plt.subplots(figsize=(8, 7))
    rng = np.random.default_rng(3)
    rs, zs = [], []
    for _ in range(40000):
        q2 = rng.uniform(*k.URDF_LIMITS['shoulder'])
        q3 = rng.uniform(*k.URDF_LIMITS['elbow'])
        q4 = rng.uniform(*k.URDF_LIMITS['wrist'])
        p = k.forward_kinematics(0.0, q2, q3, q4)
        rs.append(math.hypot(p.x, p.y))
        zs.append(p.z)
    ax.scatter(rs, zs, s=1, alpha=0.15, color='#2980b9')
    ax.plot(0, k.H, 'ko', ms=7)
    ax.annotate('hombro', (0, k.H), textcoords='offset points', xytext=(6, 6))
    reach = k.A1 + k.A2 + k.A3
    ax.set_title(f'Espacio de trabajo (corte sagital, cintura=0)\n'
                 f'alcance maximo desde el hombro ≈ {reach*1000:.0f} mm')
    ax.set_xlabel('r [m]')
    ax.set_ylabel('z [m]')
    ax.set_aspect('equal')
    ax.grid(alpha=0.3)
    _common.save(fig, 'espacio_trabajo.png')


def plano_planta() -> None:
    fig, ax = plt.subplots(figsize=(8, 8))
    reach = k.A1 + k.A2 + k.A3

    # Mesa de trabajo.
    ax.add_patch(plt.Rectangle((-0.35, -0.35), 0.70, 0.70, fc='#f4ecd8',
                               ec='0.6', zorder=0))
    # Alcance maximo (vista superior).
    ax.add_patch(plt.Circle((0, 0), reach, fc='#d6eaf8', ec='#2980b9',
                            ls='--', alpha=0.5, label='alcance maximo'))
    # Rango de cintura seguro (+/-145 deg).
    th = np.radians(np.linspace(-145, 145, 100))
    ax.fill(np.r_[0, reach * np.cos(th)], np.r_[0, reach * np.sin(th)],
            color='#abebc6', alpha=0.4, label='zona segura cintura ±145°')
    # Base del robot.
    ax.add_patch(plt.Circle((0, 0), 0.05, fc='#34495e', zorder=5))
    ax.annotate('base / J1', (0, 0), textcoords='offset points', xytext=(8, 8),
                fontsize=9, color='white')
    # Area de dibujo (figuras): plano frontal y=0, proyectado como una linea.
    ax.plot([0.09, 0.20], [0, 0], color='#e67e22', lw=6,
            solid_capstyle='round', label='area de trazado (plano y=0)')
    # Direccion frontal +x.
    ax.annotate('', xy=(0.30, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color='0.4'))
    ax.annotate('+x (frente)', (0.30, 0.01), fontsize=9)
    ax.annotate('+y', (0.01, 0.30), fontsize=9)
    ax.annotate('', xy=(0, 0.30), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color='0.4'))

    ax.set_title('Plano de planta — puesto de trabajo del PhantomX Pincher X100\n'
                 '(vista superior)')
    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.set_aspect('equal')
    ax.grid(alpha=0.3)
    ax.legend(loc='lower right', fontsize=8)
    ax.set_xlim(-0.4, 0.4)
    ax.set_ylim(-0.4, 0.4)
    _common.save(fig, 'plano_planta.png')


if __name__ == '__main__':
    print('Generando diagramas:')
    diagrama_cinematico()
    espacio_trabajo()
    plano_planta()
