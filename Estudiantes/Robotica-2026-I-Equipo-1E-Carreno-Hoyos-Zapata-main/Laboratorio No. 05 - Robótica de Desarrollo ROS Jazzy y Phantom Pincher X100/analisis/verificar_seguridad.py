#!/usr/bin/env python3
"""Verificacion de seguridad de una rutina ANTES de ejecutarla en el robot real.

La guia exige que "cada movimiento debe verificarse antes de ejecutarse sobre el
robot real". Comprobar solo las posturas no basta: el camino entre dos posturas
seguras puede pasar por una zona peligrosa, y una transicion corta entre posturas
lejanas puede exigir una velocidad que el servomotor no puede seguir.

Esta herramienta reconstruye la trayectoria completa muestra a muestra y evalua:

  1. LIMITES     — que ninguna muestra salga de los limites seguros.
  2. COLISION    — distancia del BRAZO ENTERO (no solo el TCP) a los accesorios
                   de la plataforma del kit, muestreando puntos a lo largo de los
                   tres eslabones.
  3. VELOCIDAD   — velocidad cartesiana del TCP, para detectar latigazos que el
                   AX-12A no puede seguir y que golpean la estructura.

Uso:
    python3 verificar_seguridad.py [coreografia|figura]
"""

from __future__ import annotations

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'src', 'pincher_lab'))

from pincher_lab import safe_limits                              # noqa: E402
from pincher_lab.kinematics import A1, A2, A3, B, H              # noqa: E402
from pincher_lab.motion import deg5, ramp                        # noqa: E402

RATE = 50.0
V_MAX_RECOMENDADA = 700.0     # mm/s de TCP; por encima el AX-12A no sigue

# Accesorios de la plataforma del kit (phantomx_pincher_description), medidos de
# su URDF y de la malla canecaGrande.stl.
CANECAS = [
    ("frontal derecha (verde)", 194.0, -92.5),
    ("frontal izquierda (azul)", 194.0, +92.5),
    ("lateral izquierda", -13.5, +127.8),
    ("lateral derecha", -13.5, -127.8),
]
BORDE_Z = 67.0        # altura del borde superior de una caneca (16 + 51 mm)
HALF_X, HALF_Y = 50.0, 74.0
MARGEN_MIN = 40.0     # holgura minima que consideramos aceptable

# RADIO DEL BRAZO. La primera version de esta herramienta modelaba la cadena como
# lineas de GROSOR CERO, y eso provoco un choque real contra las canecas
# frontales: el hueco entre ellas mide solo 37 mm (y = -18.5 .. +18.5) mientras
# que el antebrazo, con su servo y soportes, mide unos 38 mm de ancho. El eje
# pasaba "limpio" por el centro del hueco mientras la estructura rozaba los lados.
#
# 30 mm cubre el semiancho del antebrazo (19 mm) y de la pinza (12 mm) con
# margen. La huella de cada caneca se infla en este radio antes de comprobar.
RADIO_BRAZO = 30.0


def puntos_brazo(q):
    """Muestrea puntos a lo largo de los tres eslabones (mm)."""
    q1, q2, q3, q4 = q[0], q[1], q[2], q[3]
    a1 = B - q2
    a2 = math.pi / 2 - q2 - q3
    a3 = math.pi / 2 - q2 - q3 - q4
    r0, z0 = 0.0, H
    r1, z1 = r0 + A1 * math.cos(a1), z0 + A1 * math.sin(a1)
    r2, z2 = r1 + A2 * math.cos(a2), z1 + A2 * math.sin(a2)
    r3, z3 = r2 + A3 * math.cos(a3), z2 + A3 * math.sin(a3)
    pts = []
    for (ra, za), (rb, zb) in (((r0, z0), (r1, z1)),
                               ((r1, z1), (r2, z2)),
                               ((r2, z2), (r3, z3))):
        for t in (i / 6 for i in range(7)):
            r, z = ra + (rb - ra) * t, za + (zb - za) * t
            pts.append((r * math.cos(q1) * 1000, r * math.sin(q1) * 1000, z * 1000))
    return pts


def trayectoria_coreografia():
    from pincher_lab.choreography import BLOCK, FINALE, INTRO, POSES, REST
    beat, min_dur = 0.45, 45.0
    samples, etiquetas, cur = [], [], list(REST)

    def mover(nombre, beats, metodo):
        nonlocal cur
        nxt = safe_limits.clamp_vector_safe(deg5(POSES[nombre]))[0]
        s = ramp(cur, nxt, max(0.2, beats * beat), RATE, metodo)
        samples.extend(s)
        etiquetas.extend([nombre] * len(s))
        cur = nxt

    for n, b, m in INTRO:
        mover(n, b, m)
    while len(samples) / RATE < min_dur - 5.0:
        for n, b, m in BLOCK:
            mover(n, b, m)
    for n, b, m in FINALE:
        mover(n, b, m)
    mover('rest', 3.0, 'cubic')
    return samples, etiquetas


def revisar(samples, etiquetas, nombre_rutina):
    print(f"Rutina: {nombre_rutina}")
    print(f"Muestras: {len(samples)}  ({len(samples) / RATE:.1f} s)\n")
    fallos = 0

    # 1) limites
    fuera = 0
    for q in samples:
        _, recortado = safe_limits.clamp_vector_safe(list(q))
        if recortado:
            fuera += 1
    if fuera:
        print(f"[LIMITES]  {fuera} muestras fuera de los limites seguros  <-- REVISAR")
        fallos += 1
    else:
        print("[LIMITES]  todas las muestras dentro de los limites seguros")

    # 2) colision del brazo completo
    peor = None
    for i, (q, lab) in enumerate(zip(samples, etiquetas)):
        for (x, y, z) in puntos_brazo(q):
            for nombre, cx, cy in CANECAS:
                # Huella inflada por el radio del brazo: no basta con que el eje
                # quede fuera, la estructura ocupa espacio a su alrededor.
                if (abs(x - cx) <= HALF_X + RADIO_BRAZO
                        and abs(y - cy) <= HALF_Y + RADIO_BRAZO):
                    margen = z - BORDE_Z
                    if peor is None or margen < peor[0]:
                        peor = (margen, nombre, lab, i / RATE)
    if peor is None:
        print("[COLISION] el brazo nunca entra en la vertical de un accesorio")
    else:
        margen, nombre, lab, t = peor
        estado = "CHOQUE" if margen < 0 else ("JUSTO" if margen < MARGEN_MIN else "ok")
        print(f"[COLISION] holgura minima {margen:6.1f} mm sobre {nombre}"
              f"  (pose '{lab}', t={t:.1f}s)  -> {estado}")
        if margen < MARGEN_MIN:
            fallos += 1

    # 3) velocidad cartesiana del TCP
    vmax = (0.0, '', 0.0)
    prev = None
    for i, (q, lab) in enumerate(zip(samples, etiquetas)):
        tcp = puntos_brazo(q)[-1]
        if prev is not None:
            v = math.dist(tcp, prev) * RATE
            if v > vmax[0]:
                vmax = (v, lab, i / RATE)
        prev = tcp
    rapido = vmax[0] > V_MAX_RECOMENDADA
    estado = "EXCEDE" if rapido else "ok"
    print(f"[VELOCIDAD] pico {vmax[0]:6.0f} mm/s en '{vmax[1]}' (t={vmax[2]:.1f}s)"
          f"  -> {estado} (recomendado <= {V_MAX_RECOMENDADA:.0f})")
    if rapido:
        print("            No es un choque: el servo simplemente saturara y quedara")
        print("            rezagado, asi que el gesto se vera mas lento y arrastrado")
        print("            que en simulacion. Alargar la transicion si molesta.")

    print()
    if fallos:
        print(f"RESULTADO: {fallos} punto(s) A CORREGIR antes de ejecutar en hardware")
    elif rapido:
        print("RESULTADO: APTA para el robot real, con advertencia de velocidad")
    else:
        print("RESULTADO: APTA para el robot real")
    return fallos


def trayectoria_poses():
    """Actividad 13: recorrido por las poses guardadas en config/poses.yaml."""
    import yaml
    ruta = os.path.join(os.path.dirname(HERE), 'src', 'pincher_lab',
                        'config', 'poses.yaml')
    with open(ruta) as fh:
        datos = yaml.safe_load(fh) or {}
    poses = datos.get('poses', {})
    samples, etiquetas, cur = [], [], [0.0] * 5
    for nombre, grados in poses.items():
        nxt = safe_limits.clamp_vector_safe(deg5(grados))[0]
        s = ramp(cur, nxt, 2.0, RATE, 'cubic')
        samples.extend(s)
        etiquetas.extend([nombre] * len(s))
        cur = nxt
    return samples, etiquetas


def trayectoria_figura(figura='initials', texto='CHZ'):
    """Actividad 14: trazado por cinematica inversa."""
    from pincher_lab import figure_player as fp
    from pincher_lab.kinematics import inverse_kinematics, nearest_solution

    if figura == 'initials':
        cartesianos = _puntos_iniciales(texto)
    else:
        cartesianos = _puntos_cuadrado()

    samples, etiquetas, prev = [], [], None
    cur = [0.0] * 5
    perdidos = 0
    for (x, y, z) in cartesianos:
        sols = inverse_kinematics(x, y, z, fp.TOOL_PITCH, only_within_limits=True)
        sol = nearest_solution(sols, prev if prev else cur)
        if sol is None:
            perdidos += 1
            continue
        q = sol.joints(gripper=0.0)
        s = ramp(prev or cur, q, 0.15, RATE, 'linear')
        samples.extend(s)
        etiquetas.extend([figura] * len(s))
        prev = q
    if perdidos:
        print(f'  AVISO: {perdidos} puntos de la figura no son alcanzables')
    return samples, etiquetas


def _puntos_iniciales(texto):
    from pincher_lab import figure_player as fp
    pts, ancho = [], 0.9 * fp.SIZE
    alto, sep = 1.4 * fp.SIZE, 1.3 * fp.SIZE
    x0 = fp.CX - sep * (len(texto) - 1) / 2.0
    for i, ch in enumerate(texto.upper()):
        for trazo in fp.STROKE_FONT.get(ch, []):
            for u, v in trazo:
                pts.append((fp.CX, x0 + i * sep + (u - 0.5) * ancho - fp.CX,
                            fp.CZ + (v - 0.5) * alto))
    return pts


def _puntos_cuadrado():
    from pincher_lab import figure_player as fp
    esquinas = [(-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1)]
    return [(fp.CX + fp.SIZE * u, 0.0, fp.CZ + fp.SIZE * v) for u, v in esquinas]


def trayectoria_interpolacion():
    """Actividad 9: interpolacion lineal y quintica entre dos configuraciones."""
    from pincher_lab import trajectories
    from pincher_lab.trajectory_demo import CONFIG_A_DEG, CONFIG_B_DEG
    qa = safe_limits.clamp_vector_safe(deg5(CONFIG_A_DEG))[0]
    qb = safe_limits.clamp_vector_safe(deg5(CONFIG_B_DEG))[0]
    t = trajectories.time_vector(3.0, RATE)
    samples, etiquetas = [], []
    for metodo in ('linear', 'quintic'):
        for desde, hasta in ((qa, qb), (qb, qa)):
            mat = trajectories.interpolate_vector(desde, hasta, 3.0, t, metodo)
            s = [safe_limits.clamp_vector_safe(list(r))[0] for r in mat]
            samples.extend(s)
            etiquetas.extend([metodo] * len(s))
    return samples, etiquetas


RUTINAS = {
    'coreografia': (trayectoria_coreografia, 'coreografia (Actividad 15)'),
    'poses': (trayectoria_poses, 'ensenanza y repeticion (Actividad 13)'),
    'figura': (trayectoria_figura, 'trazado de iniciales (Actividad 14)'),
    'cuadrado': (lambda: trayectoria_figura('square'), 'trazado de cuadrado (Actividad 14)'),
    'interpolacion': (trayectoria_interpolacion, 'interpolacion (Actividad 9)'),
}


def main() -> int:
    pedido = sys.argv[1] if len(sys.argv) > 1 else 'todo'
    nombres = list(RUTINAS) if pedido == 'todo' else [pedido]
    if any(n not in RUTINAS for n in nombres):
        print(f'Rutinas disponibles: {", ".join(RUTINAS)}, todo')
        return 2
    fallos = 0
    for i, n in enumerate(nombres):
        if i:
            print('\n' + '=' * 64 + '\n')
        constructor, etiqueta = RUTINAS[n]
        samples, etiquetas = constructor()
        fallos += revisar(samples, etiquetas, etiqueta)
    if len(nombres) > 1:
        print('\n' + '=' * 64)
        print('TOTAL:', 'todas las rutinas aptas' if fallos == 0
              else f'{fallos} punto(s) a corregir')
    return 1 if fallos else 0


if __name__ == '__main__':
    raise SystemExit(main())
