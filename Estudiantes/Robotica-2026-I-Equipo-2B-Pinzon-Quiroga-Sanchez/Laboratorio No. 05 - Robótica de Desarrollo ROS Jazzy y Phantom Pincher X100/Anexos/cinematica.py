import numpy as np


L1 = 0.0415
L2 = 0.1070
L3 = 0.1070
L4 = 0.0926

# Límites físicos de las articulaciones (grados)

LIMITES_ARTICULACIONES = [
    [-145, 145],   # q1 Waist
    [-80, 80],     # q2 Shoulder
    [-130, 130],   # q3 Elbow
    [-90, 85]    # q4 Wrist
]


def DH(theta, d, a, alpha):

    theta = np.radians(theta)
    alpha = np.radians(alpha)

    return np.array([

        [
            np.cos(theta),
            -np.sin(theta)*np.cos(alpha),
            np.sin(theta)*np.sin(alpha),
            a*np.cos(theta)
        ],

        [
            np.sin(theta),
            np.cos(theta)*np.cos(alpha),
            -np.cos(theta)*np.sin(alpha),
            a*np.sin(theta)
        ],

        [
            0,
            np.sin(alpha),
            np.cos(alpha),
            d
        ],

        [
            0,
            0,
            0,
            1
        ]

    ])



def cinematica_directa(q):

    q1,q2,q3,q4=q


    tabla=[

        [q1,L1,0,90],

        [q2+90,0,L2,0],

        [q3,0,L3,0],

        [q4+90,0,0,90],

        [0,L4,0,0]

    ]


    T=np.eye(4)


    for fila in tabla:

        T=T@DH(
            fila[0],
            fila[1],
            fila[2],
            fila[3]
        )


    return T

def obtener_rpy(T):

    R = T[:3,:3]


    roll = np.arctan2(
        R[2,1],
        R[2,2]
    )


    pitch = np.arctan2(
        -R[2,0],
        np.sqrt(
            R[0,0]**2 +
            R[1,0]**2
        )
    )


    yaw = np.arctan2(
        R[1,0],
        R[0,0]
    )


    return np.degrees(
        [
            roll,
            pitch,
            yaw
        ]
    )

def verificar_limites(q):

    for i, angulo in enumerate(q):

        minimo = LIMITES_ARTICULACIONES[i][0]
        maximo = LIMITES_ARTICULACIONES[i][1]


        if angulo < minimo or angulo > maximo:

            return False


    return True

def normalizar_angulo(angulo):
    return (angulo + 180) % 360 - 180

def cinematica_inversa(x, y, z, theta_deg):

    theta = np.radians(theta_deg)  # phi = theta2+theta3+theta4, en radianes
    
    # ---------------------------------
    # 1. Rotación de la base
    # ---------------------------------

    theta1 = np.arctan2(y,x)
    offset_ang = theta + np.pi/2

    # ---------------------------------
    # 2. Calcular posición de muñeca
    # ---------------------------------

    xw = x - L4*np.cos(offset_ang)*np.cos(theta1)
    yw = y - L4*np.cos(offset_ang)*np.sin(theta1)
    zw = z - L4*np.sin(offset_ang)
    rw = np.sqrt(xw**2+yw**2)

    # altura respecto a la base

    zin = zw - L1

    # distancia total del 0 a la muñeca

    r = np.sqrt(xw**2+yw**2+zin**2)

    # ---------------------------------
    # 3. Ley de cosenos
    # ---------------------------------

    c3=(r**2-L2**2-L3**2)/(2*L2*L3)

    # punto fuera del alcance

    if abs(c3)>1:

        return None



    soluciones=[]



    # ---------------------------------
    # 4. Codo arriba y abajo
    # ---------------------------------

    for signo in [1,-1]:

        theta3=np.arctan2(signo*np.sqrt(1-c3**2),c3)

        # ---------------------------------
        # 5. Theta 2
        # ---------------------------------

        theta2=(
            
            np.arctan2(zin,rw)
            -
            np.arctan2(L3*np.sin(theta3),L2+L3*np.cos(theta3))

        )



        # ---------------------------------
        # 6. Theta 4
        # ---------------------------------

        theta4 = theta-theta2-theta3-np.pi

        q = np.degrees([
            theta1,
            theta2,
            theta3,
            theta4
        ])

        # Offsets
        q[1] -= 90
        q[3] -= 90
        q = np.array([normalizar_angulo(a) for a in q])


        if verificar_limites(q):

            soluciones.append(q)

        else:

            print("Descartada por límites:", q)


    return soluciones


def elegir_solucion_cercana(soluciones, q_actual):


    if len(soluciones)==0:
        return None


    mejor_solucion=None

    menor_distancia=float("inf")


    for q in soluciones:


        distancia=np.linalg.norm(
            np.array(q)-np.array(q_actual)
        )


        if distancia < menor_distancia:

            menor_distancia=distancia

            mejor_solucion=q


    return mejor_solucion