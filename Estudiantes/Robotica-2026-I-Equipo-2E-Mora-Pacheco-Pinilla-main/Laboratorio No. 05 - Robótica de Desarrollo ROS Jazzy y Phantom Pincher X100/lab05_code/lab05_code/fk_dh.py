#!/usr/bin/env python3
"""Actividad 11 — Cinemática Directa (Bioloid Phantom X Pincher)
Recibe q1..q4 en grados, calcula TCP (x,y,z) + orientación.
"""
import math
import numpy as np

L0b = 0.0540
L1b = 0.0995
L2b = 0.0995
L3b = 0.0835

DEG = math.pi / 180.0
PI = math.pi


def _R_x(a): return np.array([[1,0,0],[0,math.cos(a),-math.sin(a)],[0,math.sin(a),math.cos(a)]])
def _R_y(a): return np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
def _R_z(a): return np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
def _rpy(r,p,y): return _R_z(y) @ _R_y(p) @ _R_x(r)
def _T(R, t):
    M = np.eye(4); M[:3,:3] = R; M[:3,3] = t; return M


def fk(q_deg):
    """Compute TCP (x,y,z,roll,pitch,yaw) from joint angles in degrees.
    Returns (x,y,z,roll,pitch,yaw) in meters and degrees."""
    aw = 0.038; ah = 0.032; fh = 0.0525; f10h = 0.004
    f2h = 0.0265; fo = 0.001; fx = 0.019; fy = 0.0115

    q = [math.radians(v) for v in q_deg[:4]]
    M = np.eye(4)
    def add(R, t):
        nonlocal M
        M = M @ _T(R, np.array(t))

    add(_rpy(PI/2, 0, PI/2), [0, 0, 0])
    add(_rpy(-PI/2, PI/2, PI), [0, aw/2, 0])
    add(_R_z(-q[0]), [0, 0, 0])                    # waist
    add(_rpy(0, PI, 0), [0, 0, -ah - f10h + fo])
    add(_R_y(q[1]), [0, 0, 0])                      # shoulder
    add(np.eye(3), [0, 0, fh + f10h/2])
    add(np.eye(3), [0, 0, f10h])
    add(np.eye(3), [0, 0, f10h])
    add(_rpy(0, PI, 0), [0, 0, f10h/2])
    add(_rpy(0, PI, 0), [0, 0, -ah - f10h + fo])
    add(_R_y(q[2]), [0, 0, 0])                      # elbow
    add(np.eye(3), [0, 0, fh + f10h/2])
    add(np.eye(3), [0, 0, f10h])
    add(np.eye(3), [0, 0, f10h])
    add(_rpy(0, PI, 0), [0, 0, f10h/2])
    add(_rpy(0, PI, 0), [0, 0, -ah - f10h + fo])
    add(_R_y(q[3]), [0, 0, 0])                      # wrist
    add(_rpy(0, PI, -PI), [0, 0, f2h])
    add(_rpy(PI/2, PI, PI/2), [0, 0, -aw/2])
    add(_rpy(PI, 0, PI/2), [0, aw/2, 0])
    add(_rpy(PI/2, -PI/2, PI/2), [fx, 0, 0])

    x, y, z = M[0, 3], M[1, 3], M[2, 3]
    R = M[:3, :3]
    roll = math.degrees(math.atan2(R[2, 1], R[2, 2]))
    pitch = math.degrees(math.atan2(-R[2, 0], math.sqrt(R[2, 1]**2 + R[2, 2]**2)))
    yaw = math.degrees(math.atan2(R[1, 0], R[0, 0]))
    return x, y, z, roll, pitch, yaw


def main():
    print('Actividad 11 — FK Bioloid')
    print(f'L0={L0b*1000:.0f} L1={L1b*1000:.0f} L2={L2b*1000:.0f} L3={L3b*1000:.0f} mm')
    configs = [
        ('Home', [0,0,0,0]),
        ('Config 2', [25,25,20,-20]),
        ('Config 3', [-35,35,-30,30]),
        ('Config 4', [85,-20,55,25]),
        ('Config 5', [80,-35,55,-45]),
    ]
    for name, q in configs:
        x,y,z,r,p,yw = fk(q)
        print(f'{name:10s}: x={x*1000:7.1f} y={y*1000:7.1f} z={z*1000:7.1f} roll={r:6.1f} pitch={p:6.1f} yaw={yw:6.1f}')
    print()
    while True:
        try:
            inp = input('q1 q2 q3 q4 (grados) > ').strip()
            if not inp: break
            q = [float(v) for v in inp.split()[:4]]
            x,y,z,r,p,yw = fk(q)
            print(f'TCP: ({x*1000:.1f}, {y*1000:.1f}, {z*1000:.1f}) mm  RPY: ({r:.1f}, {p:.1f}, {yw:.1f})°')
        except: break

if __name__ == '__main__':
    main()
