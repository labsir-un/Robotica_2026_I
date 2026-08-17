#!/usr/bin/env python3
"""Actividad 12 — Cinemática Inversa (grid search sobre FK Bioloid real)"""
import math
from fk_dh import fk as fk_fn

L0b = 0.0540; L1b = 0.0995; L2b = 0.0995; L3b = 0.0835
MAX_REACH = L0b + L1b + L2b + L3b

JOINT_LIMITS_DEG = {
    'waist':    (-150, 150),
    'shoulder': (-120, 120),
    'elbow':    (-139, 139),
    'wrist':    (-98, 103),
}
LIM = [(JOINT_LIMITS_DEG[j]) for j in ['waist','shoulder','elbow','wrist']]


def _grid_ik(x, y, z, step):
    q1 = math.degrees(math.atan2(y, x))
    best, best_err = None, float('inf')
    rng2 = range(LIM[1][0], LIM[1][1] + 1, step)
    rng3 = range(LIM[2][0], LIM[2][1] + 1, step)
    rng4 = range(LIM[3][0], LIM[3][1] + 1, step)
    for q2d in rng2:
        for q3d in rng3:
            for q4d in rng4:
                q = [q1, q2d, q3d, q4d]
                xf, yf, zf, _, _, _ = fk_fn(q)
                err = (xf-x)**2 + (yf-y)**2 + (zf-z)**2
                if err < best_err:
                    best_err = err
                    best = list(q)
                    if best_err < 1e-9:  # early exit on perfect match
                        return best
    return best


def ik(x, y, z, elbow_up=False):
    return _grid_ik(x, y, z, 20)


def _grid_ik(x, y, z, step):
    q1 = math.degrees(math.atan2(y, x))
    best, best_err = None, float('inf')
    for q2d in range(LIM[1][0], LIM[1][1] + 1, step):
        for q3d in range(LIM[2][0], LIM[2][1] + 1, step):
            for q4d in range(LIM[3][0], LIM[3][1] + 1, step):
                q = [q1, q2d, q3d, q4d]
                xf, yf, zf, _, _, _ = fk_fn(q)
                err = (xf-x)**2 + (yf-y)**2 + (zf-z)**2
                if err < best_err:
                    best_err = err
                    best = list(q)
    return best


def nearest_solution(x, y, z, current_q=None):
    q = ik(x, y, z)
    return (False, q) if q else (None, None)


def main():
    print('Actividad 12 — Cinemática Inversa')
    print(f'  L0={L0b*1000:.0f} L1={L1b*1000:.0f} L2={L2b*1000:.0f} L3={L3b*1000:.0f} mm')
    tests = [
        ('Home FK',        0.321, 0.00, 0.089),
        ('Tri apex',       0.130, 0.00, 0.129),
        ('Tri base izq',   0.130,-0.025, 0.086),
        ('Tri base der',   0.130, 0.025, 0.086),
        ('Sq sup izq',     0.130,-0.025, 0.125),
        ('Sq inf der',     0.130, 0.025, 0.075),
        ('Centro',         0.130, 0.00, 0.100),
    ]
    for name, x, y, z in tests:
        q = ik(x, y, z)
        if q:
            xf, yf, zf, _, _, _ = fk_fn(q)
            err = math.sqrt((xf-x)**2 + (yf-y)**2 + (zf-z)**2)
            print(f'  {name:15s} q={[f"{v:.1f}" for v in q]} err={err*1e3:.1f}mm')
        else:
            print(f'  {name:15s} NO ALCANZABLE')
    print()
    print('  Manual: x(mm) y(mm) z(mm) o Enter para salir.')
    while True:
        try:
            inp = input('  > ').strip()
            if not inp: break
            x,y,z = [float(v)/1000.0 for v in inp.split()[:3]]
            q = ik(x, y, z)
            if q:
                xf, yf, zf, _, _, _ = fk_fn(q)
                print(f'    q={[f"{v:.1f}" for v in q]}, err={math.sqrt((xf-x)**2+(yf-y)**2+(zf-z)**2)*1e3:.1f}mm')
            else:
                print('    NO ALCANZABLE')
        except: break

if __name__ == '__main__':
    main()
