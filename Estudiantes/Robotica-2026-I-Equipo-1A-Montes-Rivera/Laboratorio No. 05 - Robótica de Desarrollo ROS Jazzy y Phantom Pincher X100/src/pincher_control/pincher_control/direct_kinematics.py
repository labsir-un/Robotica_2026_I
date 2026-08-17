#!/usr/bin/env python3
import math
import sys
import numpy as np

# Robot physical lengths
L1 = 0.0445
L2 = 0.1010
L3 = 0.1010
L4 = 0.1190
Lm = 0.0315

# Derived parameters
BETA = math.atan2(Lm, L2) # ~17.31 degrees
A2 = math.sqrt(Lm**2 + L2**2) # ~0.1058 meters
D1 = 0.08945 # Height base to shoulder

# DH parameters: (theta_offset, d, a, alpha)
DH_PARAMS = [
    (0.0, D1, 0.0, -math.pi/2),              # Joint 1
    (BETA - math.pi/2, 0.0, A2, 0.0),       # Joint 2
    (-BETA, 0.0, L3, 0.0),                  # Joint 3
    (0.0, 0.0, L4, 0.0)                     # Joint 4
]

# Tool transform: fixed rotation at the end of Link 4
# RPY: [-pi/2, 0, -pi/2]
TOOL_RPY = [-math.pi/2, 0.0, -math.pi/2]

def get_transform(xyz, rpy):
    roll, pitch, yaw = rpy
    Rz = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw), np.cos(yaw), 0],
        [0, 0, 1]
    ])
    Ry = np.array([
        [np.cos(pitch), 0, np.sin(pitch)],
        [0, 1, 0],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)]
    ])
    R = Rz @ Ry @ Rx
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = xyz
    return T

def rotation_to_rpy(R):
    """Converts a rotation matrix to Roll, Pitch, Yaw (ZYX convention) in degrees."""
    pitch = math.atan2(-R[2, 0], math.sqrt(R[0, 0]**2 + R[1, 0]**2))
    if math.cos(pitch) > 1e-6:
        roll = math.atan2(R[2, 1], R[2, 2])
        yaw = math.atan2(R[1, 0], R[0, 0])
    else:
        # Gimbal lock
        roll = 0.0
        yaw = math.atan2(-R[0, 1], R[1, 1])
    return math.degrees(roll), math.degrees(pitch), math.degrees(yaw)

def dh_matrix(theta, d, a, alpha):
    ct = math.cos(theta)
    st = math.sin(theta)
    ca = math.cos(alpha)
    sa = math.sin(alpha)
    return np.array([
        [ct, -st*ca, st*sa, a*ct],
        [st, ct*ca, -ct*sa, a*st],
        [0, sa, ca, d],
        [0, 0, 0, 1]
    ])

def forward_kinematics_dh(q_deg):
    """Calculates forward kinematics using the optimized Denavit-Hartenberg parameters."""
    q = [math.radians(val) for val in q_deg]
    
    # Waist (Joint 1)
    T1 = dh_matrix(q[0] + DH_PARAMS[0][0], DH_PARAMS[0][1], DH_PARAMS[0][2], DH_PARAMS[0][3])
    # Shoulder (Joint 2)
    T2 = dh_matrix(q[1] + DH_PARAMS[1][0], DH_PARAMS[1][1], DH_PARAMS[1][2], DH_PARAMS[1][3])
    # Elbow (Joint 3)
    T3 = dh_matrix(q[2] + DH_PARAMS[2][0], DH_PARAMS[2][1], DH_PARAMS[2][2], DH_PARAMS[2][3])
    # Wrist (Joint 4)
    T4 = dh_matrix(q[3] + DH_PARAMS[3][0], DH_PARAMS[3][1], DH_PARAMS[3][2], DH_PARAMS[3][3])
    
    T_dh = T1 @ T2 @ T3 @ T4
    
    # Tool rotation
    T_tool = get_transform([0.0, 0.0, 0.0], TOOL_RPY)
    T_tcp = T_dh @ T_tool
    return T_tcp

def forward_kinematics_urdf(q_deg):
    """Calculates forward kinematics directly mapping the URDF frame translations and rotations."""
    q = [math.radians(val) for val in q_deg]
    
    # Waist
    T_w_1 = get_transform([0.0, 0.0, 0.08945 - L1], [0.0, 0.0, 0.0]) @ get_transform([0.0, 0.0, 0.0], [0.0, 0.0, q[0]])
    # Shoulder
    T_w_2 = T_w_1 @ get_transform([0.0, 0.0, L1], [-math.pi/2, 0.0, 0.0]) @ get_transform([0.0, 0.0, 0.0], [0.0, 0.0, q[1]])
    # Elbow
    alpha = math.atan2(L2, Lm)
    T_w_3 = T_w_2 @ get_transform([Lm, -L2, 0.0], [0.0, 0.0, -math.pi/2 - alpha]) @ get_transform([0.0, 0.0, 0.0], [0.0, 0.0, q[2]])
    # Wrist
    T_w_4 = T_w_3 @ get_transform([L3 * math.cos(alpha), L3 * math.sin(alpha), 0.0], [0.0, 0.0, alpha]) @ get_transform([0.0, 0.0, 0.0], [0.0, 0.0, q[3]])
    # TCP (fixed origin L4, orientation rpy: -pi/2 0 -pi/2)
    T_w_tcp = T_w_4 @ get_transform([L4, 0.0, 0.0], [-math.pi/2, 0.0, -math.pi/2])
    return T_w_tcp

def print_dh_table():
    print("\n" + "=" * 65)
    print("      TABLA DE PARÁMETROS DENAVIT-HARTENBERG (ESTÁNDAR)")
    print("=" * 65)
    print(f"{'Eslabón':<10}{'Artic.':<10}{'theta_i (rad)':<20}{'d_i (m)':<10}{'a_i (m)':<10}{'alpha_i (rad)':<12}")
    print("-" * 65)
    print(f"1         Base      q1                  0.08945   0.0       -pi/2")
    print(f"2         Hombro    q2 + {BETA:.4f} - pi/2   0.0       {A2:.4f}    0.0")
    print(f"3         Codo      q3 - {BETA:.4f}        0.0       {L3:.4f}    0.0")
    print(f"4         Muñeca    q4                  0.0       {L4:.4f}    0.0")
    print("=" * 65)
    print(f"Nota: beta = {math.degrees(BETA):.2f}° ({BETA:.4f} rad), a2 = {A2*1000:.1f} mm.")
    print("=" * 65)

def print_comparison(q_deg, idx=None):
    T_dh = forward_kinematics_dh(q_deg)
    T_urdf = forward_kinematics_urdf(q_deg)
    
    pos_dh = T_dh[:3, 3]
    pos_urdf = T_urdf[:3, 3]
    
    r_dh, p_dh, y_dh = rotation_to_rpy(T_dh[:3, :3])
    r_urdf, p_urdf, y_urdf = rotation_to_rpy(T_urdf[:3, :3])
    
    pos_err = np.linalg.norm(pos_dh - pos_urdf)
    
    cfg_str = f"Configuración {idx}" if idx else "Configuración"
    print("\n" + "-" * 60)
    print(f"{cfg_str}: q = {q_deg}")
    print("-" * 60)
    print(f"{'Eje':<10}{'Cálculo DH':<20}{'Observado (RViz)':<20}{'Diferencia (m)':<10}")
    print(f"X (m)     {pos_dh[0]: 8.5f}           {pos_urdf[0]: 8.5f}           {abs(pos_dh[0] - pos_urdf[0]):.1e}")
    print(f"Y (m)     {pos_dh[1]: 8.5f}           {pos_urdf[1]: 8.5f}           {abs(pos_dh[1] - pos_urdf[1]):.1e}")
    print(f"Z (m)     {pos_dh[2]: 8.5f}           {pos_urdf[2]: 8.5f}           {abs(pos_dh[2] - pos_urdf[2]):.1e}")
    print("-" * 60)
    print(f"Roll (°)  {r_dh: 8.2f}           {r_urdf: 8.2f}           {abs(r_dh - r_urdf):.1e}")
    print(f"Pitch (°) {p_dh: 8.2f}           {p_urdf: 8.2f}           {abs(p_dh - p_urdf):.1e}")
    print(f"Yaw (°)   {y_dh: 8.2f}           {y_urdf: 8.2f}           {abs(y_dh - y_urdf):.1e}")
    print(f"Distancia de Error Tridimensional: {pos_err*1000:.3f} mm")
    print("-" * 60)

def main():
    print_dh_table()
    
    # 5 configurations from Actividad 7
    configs = [
        [0.0, 0.0, 0.0, 0.0],
        [25.0, 25.0, 20.0, -20.0],
        [-35.0, 35.0, -30.0, 30.0],
        [85.0, -20.0, 55.0, 25.0],
        [80.0, -35.0, 55.0, -45.0]
    ]

    while True:
        print("\n" + "=" * 50)
        print("          MENÚ DE CINEMÁTICA DIRECTA")
        print("=" * 50)
        print("1. Evaluar las 5 configuraciones de la Actividad 7")
        print("2. Calcular cinemática directa manual (ingresar q1,q2,q3,q4)")
        print("3. Mostrar tabla de parámetros DH")
        print("4. Salir")
        print("-" * 50)
        
        choice = input("Seleccione una opción: ").strip()
        if choice == '1':
            print("\nEvaluating 5 configurations against reference URDF...")
            for idx, c in enumerate(configs, 1):
                print_comparison(c, idx)
        elif choice == '2':
            try:
                q1 = float(input("Ingrese q1 (Base) en grados: "))
                q2 = float(input("Ingrese q2 (Hombro) en grados: "))
                q3 = float(input("Ingrese q3 (Codo) en grados: "))
                q4 = float(input("Ingrese q4 (Muñeca) en grados: "))
                print_comparison([q1, q2, q3, q4])
            except ValueError:
                print("[Error] Debe ingresar valores numéricos válidos.")
        elif choice == '3':
            print_dh_table()
        elif choice == '4':
            print("\nSaliendo...")
            break
        else:
            print("[Error] Opción no válida. Intente de nuevo.")

if __name__ == '__main__':
    main()
