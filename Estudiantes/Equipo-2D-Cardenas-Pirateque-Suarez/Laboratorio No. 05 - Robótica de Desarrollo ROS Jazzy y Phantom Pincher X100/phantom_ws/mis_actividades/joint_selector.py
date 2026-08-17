import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from sensor_msgs.msg import JointState
from builtin_interfaces.msg import Duration
import math
import time
import os
import json

JOINTS = {"base": 1, "hombro": 2, "codo": 3, "muneca": 4, "pinza": 5}

# Límites por defecto (adaptados a los nombres y rangos del nuevo modelo)
LIMITS_DEG = {
    "base": (-150.0, 150.0),
    "hombro": (-110.0, 110.0),
    "codo": (-130.0, 130.0),
    "muneca": (-100.0, 100.0),
    "pinza": (-35, 35),
}

# =======================================================================
# INTEGRACIÓN ACTIVIDAD 6: Cargar límites seguros si existen
# =======================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIMITES_JSON = os.path.join(BASE_DIR, "limites_act6", "limites_seguros.json")

if os.path.exists(LIMITES_JSON):
    try:
        with open(LIMITES_JSON, 'r') as f:
            datos = json.load(f)
            for nombre, limites in datos.items():
                if nombre in LIMITS_DEG:
                    LIMITS_DEG[nombre] = (float(limites["limite_inferior"]), float(limites["limite_superior"]))
        print("[INFO] Límites seguros cargados desde Actividad 6.")
    except Exception as e:
        print(f"[WARN] Error leyendo límites JSON: {e}")
# =======================================================================

# 3 posiciones diferentes por articulación (sin incluir 0.0)
DEMO_POSICIONES = {
    "base": [45.0, -45.0, 90.0], 
    "hombro": [30.0, -30.0, 45.0], 
    "codo": [30.0, -30.0, 45.0], 
    "muneca": [30.0, -30.0, 60.0], 
    "pinza": [15.0, 30.0, 45.0]
}

class JointSelector(Node):
    def __init__(self):
        super().__init__("joint_selector_act4")
        
        # Publicadores hacia ros2_control
        self.arm_pub = self.create_publisher(JointTrajectory, '/joint_trajectory_controller/joint_trajectory', 10)
        self.gripper_pub = self.create_publisher(JointTrajectory, '/gripper_trajectory_controller/joint_trajectory', 10)
        
        # Suscriptor para leer los ángulos en tiempo real del simulador/robot real
        self.sub = self.create_subscription(JointState, '/joint_states', self._js_cb, 10)

        # Nombres exactos de las articulaciones del BRAZO
        self.nombres_brazo = [
            'phantomx_pincher_arm_shoulder_pan_joint',
            'phantomx_pincher_arm_shoulder_lift_joint',
            'phantomx_pincher_arm_elbow_flex_joint',
            'phantomx_pincher_arm_wrist_flex_joint'
        ]
        
        # Nombres exactos de los DEDOS DE LA PINZA según el .yaml
        self.nombres_pinza = [
            'phantomx_pincher_gripper_finger1_joint',
            'phantomx_pincher_gripper_finger2_joint'
        ]

        self.mediciones_rad = {}
        self.torque_habilitado = True
        self.speed = 80
        self.last_measured_deg = 0.0

    def _js_cb(self, msg):
        for i, name in enumerate(msg.name):
            self.mediciones_rad[name] = msg.position[i]

    def _obtener_medicion(self, joint_key):
        if joint_key == "pinza":
            # Leemos la posición lineal del dedo 1 (en metros)
            val_m = self.mediciones_rad.get(self.nombres_pinza[0], 0.0)
            # Revertimos la escala matemática para mostrar "grados" en la GUI
            return math.degrees(val_m / 0.015)

        mapa = {
            "base": self.nombres_brazo[0],
            "hombro": self.nombres_brazo[1],
            "codo": self.nombres_brazo[2],
            "muneca": self.nombres_brazo[3]
        }
        nombre_ros = mapa.get(joint_key)
        if nombre_ros in self.mediciones_rad:
            return math.degrees(self.mediciones_rad[nombre_ros])
        return 0.0

    def leer_posicion(self, nombre):
        return self._obtener_medicion(nombre)

    def leer_todas(self):
        return {k: self._obtener_medicion(k) for k in JOINTS.keys()}

    def mover_articulacion(self, nombre, angulo_deg, espera_s=1.5):
        self.last_measured_deg = self._obtener_medicion(nombre)
        res = self.mover_simultaneo({nombre: angulo_deg}, espera_s)
        return res[nombre][0]

    def mover_simultaneo(self, objetivos_deg, espera_s=0.6):
        if not self.torque_habilitado:
            return {k: (False, self._obtener_medicion(k)) for k in objetivos_deg}

        mueve_brazo = False
        mueve_pinza = False

        # Conservar la posición actual para las articulaciones que no se están moviendo
        brazo_target = [self.mediciones_rad.get(n, 0.0) for n in self.nombres_brazo]
        
        # Ambos dedos comienzan donde estén actualmente
        pinza_target = [
            self.mediciones_rad.get(self.nombres_pinza[0], 0.0),
            self.mediciones_rad.get(self.nombres_pinza[1], 0.0)
        ]

        for nombre, ang_deg in objetivos_deg.items():
            rad = math.radians(ang_deg)
            if nombre == "base": brazo_target[0] = rad; mueve_brazo = True
            elif nombre == "hombro": brazo_target[1] = rad; mueve_brazo = True
            elif nombre == "codo": brazo_target[2] = rad; mueve_brazo = True
            elif nombre == "muneca": brazo_target[3] = rad; mueve_brazo = True
            elif nombre == "pinza": 
                # Convertimos el "ángulo" simulado del slider a una apertura en metros
                apertura_m = rad * 0.015
                pinza_target = [apertura_m, apertura_m]
                mueve_pinza = True

        sec = int(espera_s)
        nanosec = int((espera_s - sec) * 1e9)
        dur = Duration(sec=sec, nanosec=nanosec)

        # 1. Enviar trayectoria al controlador del brazo
        if mueve_brazo:
            msg = JointTrajectory()
            msg.joint_names = self.nombres_brazo
            pt = JointTrajectoryPoint()
            pt.positions = brazo_target
            pt.time_from_start = dur
            msg.points.append(pt)
            self.arm_pub.publish(msg)

        # 2. Enviar trayectoria al controlador de la pinza
        if mueve_pinza:
            msg = JointTrajectory()
            msg.joint_names = self.nombres_pinza
            pt = JointTrajectoryPoint()
            pt.positions = pinza_target
            pt.time_from_start = dur
            msg.points.append(pt)
            self.gripper_pub.publish(msg)

        time.sleep(espera_s)
        return {k: (True, self._obtener_medicion(k)) for k in objetivos_deg}

    def set_velocidad(self, velocidad):
        self.speed = velocidad
        return True

    def apagar_torque_solamente(self):
        self.torque_habilitado = False

    def habilitar_torque(self):
        self.torque_habilitado = True

    def apagar(self):
        pass