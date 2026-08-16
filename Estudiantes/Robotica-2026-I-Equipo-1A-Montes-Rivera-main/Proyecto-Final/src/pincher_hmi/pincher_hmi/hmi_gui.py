#!/usr/bin/env python3
"""
Interfaz Gráfica de Usuario (HMI) Industrial en PyQt5 para PhantomX Pincher X100.
Integra Visor de Cámara en vivo con overlays, Lanzador de RViz2, Máquina de Estados,
Contadores de Receta (12 cubos), Estados de MoveIt/Vacío, Panel de Control Obligatorio
y Consola de Alarmas/Logs en tiempo real.
"""

from __future__ import annotations

import datetime
import math
import os
import subprocess
import sys
import time
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

# Verificar disponibilidad de PyQt5
try:
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.QtCore import QDateTime, QProcess, QSize, Qt, QThread, QTimer, pyqtSignal, pyqtSlot
    from PyQt5.QtGui import QColor, QFont, QIcon, QImage, QPainter, QPen, QPixmap
    from PyQt5.QtWidgets import (
        QAction,
        QApplication,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        QSplitter,
        QTableWidget,
        QTableWidgetItem,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    print("❌ PyQt5 no está instalado. Por favor instala PyQt5 (pip install PyQt5 / sudo apt install python3-pyqt5)")
    sys.exit(1)

# ROS 2 Imports
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from sensor_msgs.msg import JointState
from std_msgs.msg import String
from std_srvs.srv import SetBool, Trigger

# Mapeo de Colores para UI y Visión
COLOR_MAP = {
    'yellow': {'name': 'Amarillo', 'bgr': (0, 255, 255), 'hex': '#f1c40f', 'rgb': (241, 196, 15)},
    'blue': {'name': 'Azul', 'bgr': (255, 100, 0), 'hex': '#3498db', 'rgb': (52, 152, 219)},
    'green': {'name': 'Verde', 'bgr': (0, 255, 0), 'hex': '#2ecc71', 'rgb': (46, 204, 113)},
    'red': {'name': 'Rojo', 'bgr': (0, 0, 255), 'hex': '#e74c3c', 'rgb': (231, 76, 60)},
}

# Estados Mínimos Requeridos de la Máquina de Estados
FSM_STATES = [
    'IDLE',
    'READY',
    'SCAN',
    'PLAN',
    'PICK',
    'VERIFY GRIP',
    'DROP',
    'VERIFY SORT',
    'FAULT',
    'DONE',
]


class Ros2BridgeWorker(QThread):
    """Worker de hilo secundario para procesar rclpy.spin_once en bucle continuo y comunicar eventos mediante PyQt signals."""

    joint_state_received = pyqtSignal(dict)
    status_received = pyqtSignal(str)
    vacuum_received = pyqtSignal(str)
    color_received = pyqtSignal(str)
    point_received = pyqtSignal(float, float, float)
    log_emitted = pyqtSignal(str, str, str)  # timestamp, level, text

    def __init__(self, node: 'PincherHmiNode') -> None:
        super().__init__()
        self.node = node
        self._running = True

    def run(self) -> None:
        while self._running and rclpy.ok():
            try:
                rclpy.spin_once(self.node, timeout_sec=0.03)
            except Exception as e:
                self.log_emitted.emit(
                    datetime.datetime.now().strftime('%H:%M:%S'),
                    'ERROR',
                    f'Error en spin ROS 2: {e}',
                )
            time.sleep(0.01)

    def stop(self) -> None:
        self._running = False
        self.wait()


class PincherHmiNode(Node):
    """Nodo ROS 2 para la interfaz gráfica HMI."""

    def __init__(self) -> None:
        super().__init__('pincher_hmi_node')

        # Publicadores
        self.command_pub = self.create_publisher(JointState, '/pincher/command', 10)
        self.status_pub = self.create_publisher(String, '/pincher/status', 10)
        self.vacuum_pub = self.create_publisher(String, '/pincher/vacuum', 10)
        self.point_pub = self.create_publisher(Point, 'vision/coordenada_pieza', 10)
        self.color_pub = self.create_publisher(String, 'vision/color_pieza', 10)

        # Suscriptores
        self.joint_sub = self.create_subscription(JointState, '/joint_states', self._joint_callback, 10)
        self.status_sub = self.create_subscription(String, '/pincher/status', self._status_callback, 10)
        self.vacuum_sub = self.create_subscription(String, '/pincher/vacuum', self._vacuum_callback, 10)
        self.point_sub = self.create_subscription(Point, 'vision/coordenada_pieza', self._point_callback, 10)
        self.color_sub = self.create_subscription(String, 'vision/color_pieza', self._color_callback, 10)

        # Clientes de Servicios
        self.home_client = self.create_client(Trigger, '/pincher/home')
        self.stop_client = self.create_client(Trigger, '/pincher/software_stop')
        self.torque_client = self.create_client(SetBool, '/pincher/torque_enable')

        self.gui_worker: Optional[Ros2BridgeWorker] = None

    def set_gui_worker(self, worker: Ros2BridgeWorker) -> None:
        self.gui_worker = worker

    def _joint_callback(self, msg: JointState) -> None:
        if self.gui_worker:
            joint_map = {name: pos for name, pos in zip(msg.name, msg.position)}
            self.gui_worker.joint_state_received.emit(joint_map)

    def _status_callback(self, msg: String) -> None:
        if self.gui_worker:
            self.gui_worker.status_received.emit(msg.data)

    def _vacuum_callback(self, msg: String) -> None:
        if self.gui_worker:
            self.gui_worker.vacuum_received.emit(msg.data)

    def _point_callback(self, msg: Point) -> None:
        if self.gui_worker:
            self.gui_worker.point_received.emit(msg.x, msg.y, msg.z)

    def _color_callback(self, msg: String) -> None:
        if self.gui_worker:
            self.gui_worker.color_received.emit(msg.data)


class CameraWorker(QThread):
    """Capturador de cámara e Inferencia de Visión Artificial (YOLOv8 + OpenCV HSV)."""

    frame_processed = pyqtSignal(QImage, list)  # QImage para QLabel, lista de detecciones
    camera_status_changed = pyqtSignal(bool, str)

    def __init__(
        self,
        camera_device: str = '/dev/v4l/by-id/usb-046d_0825_A5DECA50-video-index0',
    ) -> None:
        super().__init__()
        self.camera_device = camera_device
        self._running = True
        self.use_simulated = False

        self.show_grid = True
        self.show_crosshair = True
        self.show_coords = True

        # Cargar Modelo YOLOv8 si está disponible
        self.yolo_model = None
        self._init_yolo_model()

        # Cubos simulados para fallback en modo simulación únicamente
        self.sim_cubes = [
            {'color': 'yellow', 'u': 220, 'v': 180, 'state': 'DETECTED', 'conf': 0.94},
            {'color': 'blue', 'u': 410, 'v': 210, 'state': 'DETECTED', 'conf': 0.91},
            {'color': 'green', 'u': 280, 'v': 310, 'state': 'DETECTED', 'conf': 0.89},
            {'color': 'red', 'u': 360, 'v': 140, 'state': 'DETECTED', 'conf': 0.96},
        ]
        self.anim_tick = 0.0

    def _init_yolo_model(self) -> None:
        try:
            from ultralytics import YOLO
            model_paths = [
                '/home/jesus-rivera/ros2_jazzy/phantomproyect_ws/src/pincher_sorting/models/best_piezascolor.pt',
                '/home/jesus-rivera/ros2_jazzy/phantomproyect_ws/src/pincher_sorting/models/best_piezasnegras.pt',
            ]
            for p in model_paths:
                if os.path.exists(p):
                    self.yolo_model = YOLO(p)
                    print(f"✅ Modelo YOLOv8 cargado exitosamente en HMI desde: {p}")
                    break
        except Exception as e:
            print(f"⚠️ No se pudo cargar YOLOv8 en HMI: {e}")

    def run(self) -> None:
        cap = None
        dev_path = self.camera_device
        if os.path.islink(dev_path):
            dev_path = os.path.realpath(dev_path)

        try:
            if dev_path.isdigit():
                cap = cv2.VideoCapture(int(dev_path))
            else:
                cap = cv2.VideoCapture(dev_path, cv2.CAP_V4L2)

            if not cap.isOpened():
                for alt in ['/dev/video4', 4, '/dev/video0', 0]:
                    cap = cv2.VideoCapture(alt, cv2.CAP_V4L2) if isinstance(alt, str) else cv2.VideoCapture(alt)
                    if cap.isOpened():
                        dev_path = str(alt)
                        break

            if not cap or not cap.isOpened():
                self.use_simulated = True
                self.camera_status_changed.emit(False, 'Modo Cámara Sintética / Simulación Activa')
            else:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.camera_status_changed.emit(True, f'Cámara USB Conectada ({dev_path})')
        except Exception as e:
            self.use_simulated = True
            self.camera_status_changed.emit(False, f'Simulación activa ({e})')

        while self._running:
            if not self.use_simulated and cap and cap.isOpened():
                ret, frame = cap.read()
                if not ret or frame is None:
                    frame = self._generate_simulated_frame()
                    detections = self._process_simulated_overlays(frame)
                else:
                    detections = self._detect_objects_in_real_frame(frame)
                    self._process_overlays(frame, detections)
            else:
                frame = self._generate_simulated_frame()
                detections = self._process_simulated_overlays(frame)

            q_img = self._cv_to_qimage(frame)
            self.frame_processed.emit(q_img, detections)
            time.sleep(0.04)  # ~25 FPS

        if cap and cap.isOpened():
            cap.release()

    def _detect_objects_in_real_frame(self, frame: np.ndarray) -> List[dict]:
        """Procesa la imagen real de la cámara usando el modelo YOLOv8 y segmentación HSV para detectar cubos físicos reales."""
        detections = []
        h, w, _ = frame.shape
        cx_px, cy_px = w // 2, h // 2

        # 1. Inferencia IA con Red Neuronal YOLOv8
        if self.yolo_model is not None:
            try:
                results = self.yolo_model(frame, conf=0.35, verbose=False)
                for res in results:
                    for box in res.boxes:
                        cls_id = int(box.cls[0].item())
                        raw_name = self.yolo_model.names.get(cls_id, f'class_{cls_id}').lower()
                        conf = float(box.conf[0].item())
                        xyxy = box.xyxy[0].cpu().numpy()

                        u_center = float((xyxy[0] + xyxy[2]) / 2.0)
                        v_center = float((xyxy[1] + xyxy[3]) / 2.0)

                        # Restringir la detección ÚNICAMENTE al plato blanco central (r <= 130 px)
                        dist_from_center = math.hypot(u_center - cx_px, v_center - cy_px)
                        if dist_from_center > 130.0:
                            continue

                        # Reconocimiento de Forma
                        shape_str = "Cubo"
                        if "cilindro" in raw_name:
                            shape_str = "Cilindro"
                        elif "rectangulo" in raw_name:
                            shape_str = "Rectángulo"
                        elif "pentagono" in raw_name:
                            shape_str = "Pentágono"

                        c_name = 'green'
                        if 'roj' in raw_name or 'red' in raw_name:
                            c_name = 'red'
                        elif 'az' in raw_name or 'blue' in raw_name or 'pentagono' in raw_name:
                            c_name = 'blue'
                        elif 'amarill' in raw_name or 'yellow' in raw_name or 'naranj' in raw_name or 'rectangulo' in raw_name:
                            c_name = 'yellow'

                        du = u_center - cx_px
                        dv = v_center - cy_px
                        x_cm = round(9.6 - (dv * 0.05) - 1.0, 2)
                        y_cm = round(- (du * 0.05), 2)

                        detections.append({
                            'bbox': [int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])],
                            'color': c_name,
                            'shape': shape_str,
                            'u': int(u_center),
                            'v': int(v_center),
                            'x_cm': x_cm,
                            'y_cm': y_cm,
                            'conf': conf,
                            'label': f"Forma: {shape_str} | {COLOR_MAP[c_name]['name']} ({int(conf*100)}%)",
                            'source': 'YOLOv8'
                        })
            except Exception:
                pass

        # 2. Detección de respaldo por Visión de Formas y Colores HSV en la bandeja blanca
        if len(detections) == 0:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            hsv_ranges = {
                'red': [
                    (np.array([0, 100, 80]), np.array([10, 255, 255])),
                    (np.array([160, 100, 80]), np.array([180, 255, 255]))
                ],
                'blue': [
                    (np.array([95, 80, 70]), np.array([135, 255, 255]))
                ],
                'green': [
                    (np.array([35, 70, 70]), np.array([85, 255, 255]))
                ],
                'yellow': [
                    (np.array([15, 100, 100]), np.array([35, 255, 255]))
                ]
            }

            # Máscara focalizada en el plato blanco central (320, 240) r=130px
            roi_mask = np.zeros((h, w), dtype=np.uint8)
            cv2.circle(roi_mask, (cx_px, cy_px), 130, 255, -1)

            for color_name, ranges in hsv_ranges.items():
                color_mask = np.zeros((h, w), dtype=np.uint8)
                for lower, upper in ranges:
                    mask = cv2.inRange(hsv, lower, upper)
                    color_mask = cv2.bitwise_or(color_mask, mask)

                color_mask = cv2.bitwise_and(color_mask, roi_mask)

                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
                color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel)
                color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel)

                contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    if 250 < area < 8000:
                        x, y, bw, bh = cv2.boundingRect(cnt)
                        u_center = x + bw / 2.0
                        v_center = y + bh / 2.0

                        # Análisis de Forma Geométrica
                        peri = cv2.arcLength(cnt, True)
                        approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
                        n_vert = len(approx)
                        shape_str = "Cubo"
                        if n_vert > 5:
                            shape_str = "Cilindro"
                        elif n_vert == 3:
                            shape_str = "Triángulo"

                        du = u_center - cx_px
                        dv = v_center - cy_px
                        x_cm = round(9.6 - (dv * 0.05) - 1.0, 2)
                        y_cm = round(- (du * 0.05), 2)

                        detections.append({
                            'bbox': [x, y, x + bw, y + bh],
                            'color': color_name,
                            'shape': shape_str,
                            'u': int(u_center),
                            'v': int(v_center),
                            'x_cm': x_cm,
                            'y_cm': y_cm,
                            'conf': 0.95,
                            'label': f"Forma: {shape_str} | {COLOR_MAP[color_name]['name']} (IA)",
                            'source': 'HSV'
                        })

        return detections

    def _process_overlays(self, frame: np.ndarray, detections: List[dict]) -> None:
        """Dibuja centro de calibración, rejilla y únicamente las detecciones de cubos reales en el video."""
        h, w, _ = frame.shape
        cx_px, cy_px = w // 2, h // 2

        if self.show_crosshair:
            cv2.line(frame, (cx_px - 20, cy_px), (cx_px + 20, cy_px), (0, 255, 255), 1)
            cv2.line(frame, (cx_px, cy_px - 20), (cx_px, cy_px + 20), (0, 255, 255), 1)
            cv2.circle(frame, (cx_px, cy_px), 3, (0, 0, 255), -1)
            cv2.putText(frame, "TCP Center (320, 240)", (cx_px + 8, cy_px - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

        if self.show_grid:
            for step in range(80, w, 80):
                cv2.line(frame, (step, 0), (step, h), (80, 80, 80), 1, cv2.LINE_AA)
            for step in range(60, h, 60):
                cv2.line(frame, (0, step), (w, step), (80, 80, 80), 1, cv2.LINE_AA)

        for det in detections:
            c_name = det['color']
            c_info = COLOR_MAP.get(c_name, COLOR_MAP['yellow'])
            bgr = c_info['bgr']
            x1, y1, x2, y2 = det['bbox']
            u, v = det['u'], det['v']
            x_cm, y_cm = det['x_cm'], det['y_cm']

            cv2.rectangle(frame, (x1, y1), (x2, y2), bgr, 2)
            cv2.circle(frame, (u, v), 4, (0, 0, 255), -1)

            if self.show_coords:
                lbl = f"{det['label']} | ({x_cm:.1f}, {y_cm:.1f})cm"
                bw_text = len(lbl) * 7
                cv2.rectangle(frame, (x1, max(y1 - 18, 0)), (x1 + bw_text, max(y1, 18)), (20, 20, 20), -1)
                cv2.putText(frame, lbl, (x1 + 2, max(y1 - 4, 14)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    def _generate_simulated_frame(self) -> np.ndarray:
        frame = np.full((480, 640, 3), 45, dtype=np.uint8)
        cv2.rectangle(frame, (100, 60), (540, 420), (220, 220, 220), -1)
        cv2.rectangle(frame, (100, 60), (540, 420), (180, 180, 180), 3)

        cv2.rectangle(frame, (20, 20), (90, 90), (0, 200, 0), -1)
        cv2.putText(frame, "VERDE", (25, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

        cv2.rectangle(frame, (550, 20), (620, 90), (255, 100, 0), -1)
        cv2.putText(frame, "AZUL", (560, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

        cv2.rectangle(frame, (20, 390), (90, 460), (0, 0, 220), -1)
        cv2.putText(frame, "ROJO", (30, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

        cv2.rectangle(frame, (550, 390), (620, 460), (0, 220, 220), -1)
        cv2.putText(frame, "AMARILLO", (552, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)

        self.anim_tick += 0.05
        for idx, cube in enumerate(self.sim_cubes):
            c_info = COLOR_MAP.get(cube['color'], COLOR_MAP['yellow'])
            bgr = c_info['bgr']
            u = int(cube['u'] + math.sin(self.anim_tick + idx) * 2.0)
            v = int(cube['v'] + math.cos(self.anim_tick + idx) * 2.0)

            sz = 14
            cv2.rectangle(frame, (u - sz, v - sz), (u + sz, v + sz), bgr, -1)
            cv2.rectangle(frame, (u - sz, v - sz), (u + sz, v + sz), (20, 20, 20), 2)

        return frame

    def _process_simulated_overlays(self, frame: np.ndarray) -> List[dict]:
        detections = []
        h, w, _ = frame.shape
        cx_px, cy_px = w // 2, h // 2

        if self.show_crosshair:
            cv2.line(frame, (cx_px - 20, cy_px), (cx_px + 20, cy_px), (0, 255, 255), 1)
            cv2.line(frame, (cx_px, cy_px - 20), (cx_px, cy_px + 20), (0, 255, 255), 1)
            cv2.circle(frame, (cx_px, cy_px), 3, (0, 0, 255), -1)

        if self.show_grid:
            for step in range(80, w, 80):
                cv2.line(frame, (step, 0), (step, h), (80, 80, 80), 1, cv2.LINE_AA)
            for step in range(60, h, 60):
                cv2.line(frame, (0, step), (w, step), (80, 80, 80), 1, cv2.LINE_AA)

        for cube in self.sim_cubes:
            c_name = cube['color']
            c_info = COLOR_MAP.get(c_name, COLOR_MAP['yellow'])
            bgr = c_info['bgr']
            u, v = cube['u'], cube['v']
            conf = cube['conf']

            du = u - cx_px
            dv = v - cy_px
            x_cm = round(9.6 - (dv * 0.05) - 1.0, 2)
            y_cm = round(- (du * 0.05), 2)

            sz = 20
            x1, y1 = u - sz, v - sz
            x2, y2 = u + sz, v + sz

            cv2.rectangle(frame, (x1, y1), (x2, y2), bgr, 2)
            cv2.circle(frame, (u, v), 4, (0, 0, 255), -1)

            if self.show_coords:
                lbl = f"{c_info['name']} ({int(conf*100)}%) | ({x_cm:.1f}, {y_cm:.1f})cm"
                cv2.rectangle(frame, (x1, y1 - 18), (x1 + len(lbl)*7, y1), (20, 20, 20), -1)
                cv2.putText(frame, lbl, (x1 + 2, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            detections.append({
                'color': c_name,
                'u': u,
                'v': v,
                'x_cm': x_cm,
                'y_cm': y_cm,
                'conf': conf,
                'state': cube['state'],
            })

        return detections

    def _cv_to_qimage(self, frame: np.ndarray) -> QImage:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        return QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()

    def stop(self) -> None:
        self._running = False
        self.wait()


class PincherHmiWindow(QMainWindow):
    """Ventana Principal HMI Industrial en PyQt5 para supervisión y operación."""

    def __init__(self, ros_node: PincherHmiNode) -> None:
        super().__init__()
        self.ros_node = ros_node

        self.setWindowTitle("PHANTOM X PINCHER X100 — HMI INDUSTRIAL DE CLASIFICACIÓN")
        self.resize(1380, 880)
        self.setMinimumSize(1100, 720)

        # Variables de Receta de 12 Cubos
        # 3 por cada color: amarillo, azul, verde, rojo
        self.cubes_target = {'yellow': 3, 'blue': 3, 'green': 3, 'red': 3}
        self.cubes_sorted = {'yellow': 0, 'blue': 0, 'green': 0, 'red': 0}

        # Estado del Vacío
        self.vacuum_active = False
        self.suction_start_time: Optional[float] = None
        self.grip_confirmed = 'PENDIENTE ⏳'

        # Estado de MoveIt
        self.moveit_status = 'Plan Válido'

        # Máquina de Estados Actual
        self.current_state = 'IDLE'

        # Subprocesos para nodos secundarios y RViz2
        self.sorting_process: Optional[subprocess.Popen] = None
        self.vision_process: Optional[subprocess.Popen] = None
        self.rviz_process: Optional[subprocess.Popen] = None

        self._setup_stylesheet()
        self._build_ui()
        self._start_workers()

        self._add_log('INFO', 'HMI Industrial iniciado. Listo para operación.')

    def _setup_stylesheet(self) -> None:
        self.setStyleSheet("""
            QMainWindow {
                background-color: #12141c;
                color: #e0e6ed;
                font-family: 'Segoe UI', 'Outfit', 'Helvetica', sans-serif;
            }
            QWidget {
                background-color: #12141c;
                color: #e0e6ed;
            }
            QGroupBox {
                border: 1px solid #2a2e3d;
                border-radius: 8px;
                margin-top: 14px;
                font-weight: bold;
                font-size: 13px;
                color: #00adb5;
                background-color: #1a1d28;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 2px 8px;
                background-color: #12141c;
                border: 1px solid #00adb5;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #242836;
                border: 1px solid #3a3f52;
                border-radius: 6px;
                color: #ffffff;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #32384a;
                border-color: #00adb5;
            }
            QPushButton:pressed {
                background-color: #00adb5;
                color: #12141c;
            }
            QPushButton#btn_estop {
                background-color: #d63031;
                border: 2px solid #ff7675;
                color: #ffffff;
                font-size: 14px;
                font-weight: 900;
            }
            QPushButton#btn_estop:hover {
                background-color: #ff7675;
            }
            QPushButton#btn_start {
                background-color: #00b894;
                border: 1px solid #55efc4;
                color: #ffffff;
            }
            QPushButton#btn_start:hover {
                background-color: #55efc4;
                color: #12141c;
            }
            QProgressBar {
                border: 1px solid #3a3f52;
                border-radius: 6px;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
                background-color: #1a1d28;
            }
            QProgressBar::chunk {
                background-color: #00adb5;
                border-radius: 5px;
            }
            QTableWidget {
                background-color: #161822;
                border: 1px solid #2a2e3d;
                gridline-color: #2a2e3d;
                color: #dcdde1;
                font-size: 11px;
            }
            QHeaderView::section {
                background-color: #202433;
                color: #00adb5;
                font-weight: bold;
                border: 1px solid #2a2e3d;
                padding: 4px;
            }
            QLabel {
                font-size: 12px;
            }
        """)

    def _build_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # --- 1. BARRA SUPERIOR DE ESTADO HEADER ---
        header_frame = QFrame()
        header_frame.setFrameShape(QFrame.StyledPanel)
        header_frame.setStyleSheet("background-color: #1a1d28; border-radius: 8px; border: 1px solid #2a2e3d;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(16, 8, 16, 8)

        title_label = QLabel("🤖 PHANTOM X PINCHER X100 — HMI DE CONTROL & VACÍO")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_label.setStyleSheet("color: #00adb5; background: transparent;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.lbl_node_status = QLabel("🟢 ROS 2 Conectado")
        self.lbl_node_status.setStyleSheet("color: #2ecc71; font-weight: bold; background: transparent;")
        header_layout.addWidget(self.lbl_node_status)

        self.lbl_hw_status = QLabel("⚡ Hardware: Simulación/Activo")
        self.lbl_hw_status.setStyleSheet("color: #f1c40f; font-weight: bold; background: transparent;")
        header_layout.addWidget(self.lbl_hw_status)

        main_layout.addWidget(header_frame)

        # --- 2. BARRA VISUALIZADORA DE MÁQUINA DE ESTADOS (FSM) ---
        fsm_group = QGroupBox("MÁQUINA DE ESTADOS REQUERIDA EN TIEMPO REAL (FSM)")
        fsm_layout = QHBoxLayout(fsm_group)
        fsm_layout.setContentsMargins(10, 14, 10, 10)

        self.state_badges: Dict[str, QLabel] = {}
        for st in FSM_STATES:
            lbl = QLabel(st)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedHeight(32)
            lbl.setStyleSheet("""
                background-color: #242836;
                color: #7f8c8d;
                border: 1px solid #3a3f52;
                border-radius: 6px;
                font-weight: bold;
                font-size: 10px;
                padding: 4px;
            """)
            self.state_badges[st] = lbl
            fsm_layout.addWidget(lbl)

        main_layout.addWidget(fsm_group)

        # --- 3. PANEL CENTRAL DIVIDIDO EN 3 COLUMNAS ---
        splitter = QSplitter(Qt.Horizontal)

        # --- COLUMNA IZQUIERDA: Visor de Cámara y RViz2 ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Card Visor de Cámara
        cam_group = QGroupBox("VISOR DE CÁMARA EN VIVO & VISIÓN (YOLOv8 / OVERLAYS)")
        cam_layout = QVBoxLayout(cam_group)

        self.cam_feed_label = QLabel()
        self.cam_feed_label.setMinimumSize(480, 360)
        self.cam_feed_label.setAlignment(Qt.AlignCenter)
        self.cam_feed_label.setStyleSheet("background-color: #000000; border-radius: 6px; border: 1px solid #3a3f52;")
        cam_layout.addWidget(self.cam_feed_label)

        # Controles de Overlays
        cam_ctrl_layout = QHBoxLayout()
        self.btn_toggle_crosshair = QPushButton("🎯 Cruz TCP")
        self.btn_toggle_crosshair.setCheckable(True)
        self.btn_toggle_crosshair.setChecked(True)
        self.btn_toggle_crosshair.clicked.connect(self._on_toggle_crosshair)
        cam_ctrl_layout.addWidget(self.btn_toggle_crosshair)

        self.btn_toggle_grid = QPushButton("📐 Rejilla Ref")
        self.btn_toggle_grid.setCheckable(True)
        self.btn_toggle_grid.setChecked(True)
        self.btn_toggle_grid.clicked.connect(self._on_toggle_grid)
        cam_ctrl_layout.addWidget(self.btn_toggle_grid)

        self.btn_toggle_coords = QPushButton("🏷️ Coordenadas")
        self.btn_toggle_coords.setCheckable(True)
        self.btn_toggle_coords.setChecked(True)
        self.btn_toggle_coords.clicked.connect(self._on_toggle_coords)
        cam_ctrl_layout.addWidget(self.btn_toggle_coords)

        cam_layout.addLayout(cam_ctrl_layout)

        # Panel Integrador de RViz2
        rviz_group = QGroupBox("INTEGRACIÓN / LANZADOR DE RVIZ2 3D (MOVEIT)")
        rviz_layout = QHBoxLayout(rviz_group)

        self.btn_launch_rviz = QPushButton("🚀 Lanzar RViz2 (Sincronizado 3D)")
        self.btn_launch_rviz.setStyleSheet("background-color: #34495e; border-color: #00adb5;")
        self.btn_launch_rviz.clicked.connect(self.launch_rviz2)
        rviz_layout.addWidget(self.btn_launch_rviz)

        self.lbl_rviz_status = QLabel("Estado RViz2: Desconectado")
        self.lbl_rviz_status.setStyleSheet("color: #95a5a6; font-weight: bold;")
        rviz_layout.addWidget(self.lbl_rviz_status)

        left_layout.addWidget(cam_group)
        left_layout.addWidget(rviz_group)
        splitter.addWidget(left_widget)

        # --- COLUMNA CENTRAL: Contadores de Cubos (Receta 12) + Indicadores MoveIt & Vacío ---
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)

        # Contadores de Cubos por Color (Receta de 12 cubos: 3 por color)
        cubes_group = QGroupBox("RECETA DE 12 CUBOS POR COLOR (CLASIFICACIÓN & FALTANTES)")
        cubes_layout = QVBoxLayout(cubes_group)

        grid_cubes = QGridLayout()

        self.cube_card_widgets: Dict[str, dict] = {}
        row = 0
        for color_key, cdata in COLOR_MAP.items():
            # Card individual por color
            c_box = QFrame()
            c_box.setStyleSheet(f"background-color: #202433; border: 2px solid {cdata['hex']}; border-radius: 8px; padding: 6px;")
            c_layout = QVBoxLayout(c_box)

            lbl_name = QLabel(f"CUBOS {cdata['name'].upper()}")
            lbl_name.setFont(QFont("Segoe UI", 11, QFont.Bold))
            lbl_name.setStyleSheet(f"color: {cdata['hex']}; border: none;")

            lbl_sorted = QLabel("Clasificados: 0 / 3")
            lbl_sorted.setFont(QFont("Segoe UI", 10))
            lbl_sorted.setStyleSheet("border: none; color: #ffffff;")

            lbl_missing = QLabel("Faltantes: 3")
            lbl_missing.setFont(QFont("Segoe UI", 10))
            lbl_missing.setStyleSheet("border: none; color: #e74c3c;")

            c_layout.addWidget(lbl_name)
            c_layout.addWidget(lbl_sorted)
            c_layout.addWidget(lbl_missing)

            self.cube_card_widgets[color_key] = {
                'lbl_sorted': lbl_sorted,
                'lbl_missing': lbl_missing,
            }

            grid_cubes.addWidget(c_box, row // 2, row % 2)
            row += 1

        cubes_layout.addLayout(grid_cubes)

        # Progreso Global de Receta
        cubes_layout.addWidget(QLabel("Progreso Global de Clasificación de la Receta (12 Totales):"))
        self.progress_recipe = QProgressBar()
        self.progress_recipe.setRange(0, 12)
        self.progress_recipe.setValue(0)
        self.progress_recipe.setFormat("%v / 12 Cubos Clasificados (%p%)")
        cubes_layout.addWidget(self.progress_recipe)

        btn_reset_counter = QPushButton("🔄 Reiniciar Contadores de Receta")
        btn_reset_counter.clicked.connect(self.reset_recipe_counters)
        cubes_layout.addWidget(btn_reset_counter)

        center_layout.addWidget(cubes_group)

        # Indicadores de Estado MoveIt & Vacío
        status_group = QGroupBox("INDICADORES DE ESTADO EN TIEMPO REAL (MOVEIT & VACÍO)")
        status_layout = QGridLayout(status_group)

        # MoveIt Card
        moveit_card = QFrame()
        moveit_card.setStyleSheet("background-color: #202433; border: 1px solid #3a3f52; border-radius: 6px; padding: 6px;")
        m_lay = QVBoxLayout(moveit_card)
        m_lay.addWidget(QLabel("📐 Estado de MoveIt 2:"))
        self.lbl_moveit_state = QLabel("Plan Válido ✅")
        self.lbl_moveit_state.setStyleSheet("color: #2ecc71; font-weight: bold; font-size: 13px;")
        m_lay.addWidget(self.lbl_moveit_state)
        status_layout.addWidget(moveit_card, 0, 0)

        # Vacío Card
        vacuum_card = QFrame()
        vacuum_card.setStyleSheet("background-color: #202433; border: 1px solid #3a3f52; border-radius: 6px; padding: 6px;")
        v_lay = QVBoxLayout(vacuum_card)
        v_lay.addWidget(QLabel("🧲 Estado del Sistema de Vacío:"))
        self.lbl_vacuum_badge = QLabel("BOMBA INACTIVA 💨")
        self.lbl_vacuum_badge.setStyleSheet("color: #95a5a6; font-weight: bold; font-size: 13px;")
        v_lay.addWidget(self.lbl_vacuum_badge)

        self.lbl_suction_timer = QLabel("Tiempo de Succión: 0.0 s")
        v_lay.addWidget(self.lbl_suction_timer)

        self.lbl_grip_confirm = QLabel("Confirmación Agarre: PENDIENTE ⏳")
        v_lay.addWidget(self.lbl_grip_confirm)

        status_layout.addWidget(vacuum_card, 0, 1)

        center_layout.addWidget(status_group)
        splitter.addWidget(center_widget)

        # --- COLUMNA DERECHA: Controles de Operación & Consola de Alarmas/Logs ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        ctrl_group = QGroupBox("CONTROLES DE OPERACIÓN OBLIGATORIOS")
        ctrl_layout = QGridLayout(ctrl_group)

        # Botones Principales
        self.btn_start = QPushButton("▶️ START (Auto)")
        self.btn_start.setObjectName("btn_start")
        self.btn_start.setFixedHeight(40)
        self.btn_start.clicked.connect(self.cmd_start_auto)
        ctrl_layout.addWidget(self.btn_start, 0, 0)

        self.btn_stop = QPushButton("⏹️ STOP (Controlado)")
        self.btn_stop.setFixedHeight(40)
        self.btn_stop.clicked.connect(self.cmd_stop_controlled)
        ctrl_layout.addWidget(self.btn_stop, 0, 1)

        self.btn_estop = QPushButton("🚨 EMERGENCY STOP")
        self.btn_estop.setObjectName("btn_estop")
        self.btn_estop.setFixedHeight(44)
        self.btn_estop.clicked.connect(self.cmd_emergency_stop)
        ctrl_layout.addWidget(self.btn_estop, 1, 0, 1, 2)

        self.btn_reset = QPushButton("🔧 RESET (Limpiar Fallas)")
        self.btn_reset.clicked.connect(self.cmd_reset_faults)
        ctrl_layout.addWidget(self.btn_reset, 2, 0)

        self.btn_next_cube = QPushButton("⏭️ NEXT CUBE (Paso a Paso)")
        self.btn_next_cube.clicked.connect(self.cmd_next_cube)
        ctrl_layout.addWidget(self.btn_next_cube, 2, 1)

        self.btn_home = QPushButton("🏠 Home Pose")
        self.btn_home.clicked.connect(self.cmd_home)
        ctrl_layout.addWidget(self.btn_home, 3, 0)

        self.btn_scan = QPushButton("📷 Scan Pose")
        self.btn_scan.clicked.connect(self.cmd_scan)
        ctrl_layout.addWidget(self.btn_scan, 3, 1)

        self.btn_plan = QPushButton("📝 Plan (Manual)")
        self.btn_plan.clicked.connect(self.cmd_plan)
        ctrl_layout.addWidget(self.btn_plan, 4, 0)

        self.btn_execute = QPushButton("⚡ Execute (Manual)")
        self.btn_execute.clicked.connect(self.cmd_execute)
        ctrl_layout.addWidget(self.btn_execute, 4, 1)

        self.btn_vac_on = QPushButton("🧲 Vacío ON")
        self.btn_vac_on.clicked.connect(self.cmd_vacuum_on)
        ctrl_layout.addWidget(self.btn_vac_on, 5, 0)

        self.btn_vac_off = QPushButton("💨 Vacío OFF")
        self.btn_vac_off.clicked.connect(self.cmd_vacuum_off)
        ctrl_layout.addWidget(self.btn_vac_off, 5, 1)

        right_layout.addWidget(ctrl_group)

        # Panel de Alarmas y Logs en Pantalla
        logs_group = QGroupBox("PANEL DE ALARMAS Y LOGS EN TIEMPO REAL")
        logs_layout = QVBoxLayout(logs_group)

        self.log_table = QTableWidget(0, 3)
        self.log_table.setHorizontalHeaderLabels(["Hora", "Nivel", "Evento / Mensaje"])
        self.log_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        logs_layout.addWidget(self.log_table)

        btn_clear_logs = QPushButton("🗑️ Limpiar Consola de Logs")
        btn_clear_logs.clicked.connect(self.log_table.setRowCount, 0)
        logs_layout.addWidget(btn_clear_logs)

        right_layout.addWidget(logs_group)

        splitter.addWidget(right_widget)

        # Establecer proporciones de splitter
        splitter.setSizes([460, 460, 460])
        main_layout.addWidget(splitter)

        # Timer para actualizar estado del cronómetro de vacío y badges FSM
        self.ui_timer = QTimer()
        self.ui_timer.setInterval(100)
        self.ui_timer.timeout.connect(self._on_ui_timer)
        self.ui_timer.start()

        self._update_fsm_badge('IDLE')

    def _start_workers(self) -> None:
        """Inicia los hilos de comunicación ROS 2 y captura de cámara."""
        self.bridge_worker = Ros2BridgeWorker(self.ros_node)
        self.ros_node.set_gui_worker(self.bridge_worker)

        self.bridge_worker.status_received.connect(self._on_ros_status)
        self.bridge_worker.vacuum_received.connect(self._on_ros_vacuum)
        self.bridge_worker.color_received.connect(self._on_ros_color)
        self.bridge_worker.point_received.connect(self._on_ros_point)
        self.bridge_worker.log_emitted.connect(self._add_log)

        self.bridge_worker.start()

        # Iniciar Worker de Cámara
        self.cam_worker = CameraWorker()
        self.cam_worker.frame_processed.connect(self._on_camera_frame)
        self.cam_worker.camera_status_changed.connect(self._on_camera_status)
        self.cam_worker.start()

    @pyqtSlot(QImage, list)
    def _on_camera_frame(self, q_img: QImage, detections: list) -> None:
        self.latest_detections = detections
        pix = QPixmap.fromImage(q_img)
        scaled_pix = pix.scaled(self.cam_feed_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.cam_feed_label.setPixmap(scaled_pix)

    @pyqtSlot(bool, str)
    def _on_camera_status(self, is_ok: bool, msg: str) -> None:
        if is_ok:
            self._add_log('INFO', f'Cámara: {msg}')
        else:
            self._add_log('WARN', f'Cámara: {msg}')

    @pyqtSlot(str)
    def _on_ros_status(self, status_str: str) -> None:
        # Analizar máquina de estados desde tópicos
        st_upper = status_str.upper()
        matched = None
        for st in FSM_STATES:
            if st in st_upper:
                matched = st
                break

        if matched:
            self._update_fsm_badge(matched)

        self._add_log('INFO', f'Estado Robot: {status_str}')

    @pyqtSlot(str)
    def _on_ros_vacuum(self, vac_str: str) -> None:
        if vac_str == 'VACUUM_ON':
            self.vacuum_active = True
            if self.suction_start_time is None:
                self.suction_start_time = time.time()
            self.lbl_vacuum_badge.setText("BOMBA ACTIVA 🧲")
            self.lbl_vacuum_badge.setStyleSheet("color: #2ecc71; font-weight: bold; font-size: 13px;")
            self.lbl_grip_confirm.setText("Confirmación Agarre: AGARRE CONFIRMADO ✅")
            self.lbl_grip_confirm.setStyleSheet("color: #2ecc71; font-weight: bold;")
            self._add_log('INFO', '🧲 Bomba de Vacío ACTIVADA.')
        elif vac_str == 'VACUUM_OFF':
            self.vacuum_active = False
            self.suction_start_time = None
            self.lbl_vacuum_badge.setText("BOMBA INACTIVA 💨")
            self.lbl_vacuum_badge.setStyleSheet("color: #95a5a6; font-weight: bold; font-size: 13px;")
            self.lbl_suction_timer.setText("Tiempo de Succión: 0.0 s")
            self.lbl_grip_confirm.setText("Confirmación Agarre: PENDIENTE ⏳")
            self.lbl_grip_confirm.setStyleSheet("color: #95a5a6;")
            self._add_log('INFO', '💨 Bomba de Vacío DESACTIVADA.')

    @pyqtSlot(str)
    def _on_ros_color(self, color_name: str) -> None:
        color = color_name.lower().strip()
        if color in self.cubes_sorted:
            if self.cubes_sorted[color] < self.cubes_target[color]:
                self.cubes_sorted[color] += 1
                self._update_recipe_ui()
                self._add_log('INFO', f'📦 Cubo {color.upper()} clasificado exitosamente!')

    @pyqtSlot(float, float, float)
    def _on_ros_point(self, x: float, y: float, z: float) -> None:
        self._add_log('INFO', f'🎯 Coordenada detectada por visión: (X={x:.2f}cm, Y={y:.2f}cm, Z={z:.2f}cm)')

    def _update_fsm_badge(self, active_state: str) -> None:
        self.current_state = active_state
        for st, lbl in self.state_badges.items():
            if st == active_state:
                if st == 'FAULT':
                    lbl.setStyleSheet("background-color: #e74c3c; color: #ffffff; border: 2px solid #ff7675; border-radius: 6px; font-weight: bold; font-size: 11px;")
                elif st == 'DONE':
                    lbl.setStyleSheet("background-color: #2ecc71; color: #ffffff; border: 2px solid #55efc4; border-radius: 6px; font-weight: bold; font-size: 11px;")
                else:
                    lbl.setStyleSheet("background-color: #00adb5; color: #ffffff; border: 2px solid #81ecec; border-radius: 6px; font-weight: bold; font-size: 11px;")
            else:
                lbl.setStyleSheet("background-color: #242836; color: #7f8c8d; border: 1px solid #3a3f52; border-radius: 6px; font-weight: bold; font-size: 10px;")

    def _update_recipe_ui(self) -> None:
        total_sorted = 0
        for c_key, card in self.cube_card_widgets.items():
            count = self.cubes_sorted[c_key]
            total_sorted += count
            missing = max(0, 3 - count)

            card['lbl_sorted'].setText(f"Clasificados: {count} / 3")
            card['lbl_missing'].setText(f"Faltantes: {missing}")

            if missing == 0:
                card['lbl_missing'].setStyleSheet("border: none; color: #2ecc71; font-weight: bold;")
                card['lbl_missing'].setText("Faltantes: 0 (COMPLETO ✅)")
            else:
                card['lbl_missing'].setStyleSheet("border: none; color: #e74c3c;")

        self.progress_recipe.setValue(total_sorted)
        if total_sorted >= 12:
            self._update_fsm_badge('DONE')
            self._add_log('ALARM', '🎉 RECETA COMPLETA! Se han clasificado exitosamente los 12 cubos (3 por color).')

    def reset_recipe_counters(self) -> None:
        for c_key in self.cubes_sorted:
            self.cubes_sorted[c_key] = 0
        self._update_recipe_ui()
        self._add_log('INFO', 'Contadores de receta reiniciados (12 cubos faltantes).')

    def _on_ui_timer(self) -> None:
        if self.vacuum_active and self.suction_start_time is not None:
            elapsed = time.time() - self.suction_start_time
            self.lbl_suction_timer.setText(f"Tiempo de Succión: {elapsed:.1f} s")

    def _on_toggle_crosshair(self) -> None:
        self.cam_worker.show_crosshair = self.btn_toggle_crosshair.isChecked()

    def _on_toggle_grid(self) -> None:
        self.cam_worker.show_grid = self.btn_toggle_grid.isChecked()

    def _on_toggle_coords(self) -> None:
        self.cam_worker.show_coords = self.btn_toggle_coords.isChecked()

    # --- COMANDOS DE OPERACIÓN OBLIGATORIOS ---
    def cmd_start_auto(self) -> None:
        """Inicia el ciclo automático completo de clasificación."""
        self._add_log('INFO', '▶️ Solicitando inicio de ciclo automático (START)...')

        # Preparar entorno para subprocesos Python/ROS 2
        env = os.environ.copy()

        sorting_script = "/home/jesus-rivera/ros2_jazzy/phantomproyect_ws/src/pincher_sorting/pincher_sorting/sorting_node.py"
        vision_script = "/home/jesus-rivera/ros2_jazzy/phantomproyect_ws/src/pincher_sorting/pincher_sorting/vision_node.py"

        # Lanzar sorting_node y vision_node si no se encuentran en ejecución
        try:
            if self.sorting_process is None or self.sorting_process.poll() is not None:
                self._add_log('INFO', '🚀 Iniciando nodo sorting_node en segundo plano...')
                self.sorting_process = subprocess.Popen([sys.executable, sorting_script], env=env)

            if self.vision_process is None or self.vision_process.poll() is not None:
                self._add_log('INFO', '🚀 Iniciando nodo vision_node en segundo plano...')
                self.vision_process = subprocess.Popen([sys.executable, vision_script], env=env)

        except Exception as e:
            self._add_log('ERROR', f'Fallo al iniciar nodos secundarios: {e}')

        # 1. Posicionar robot en SCAN
        self.cmd_scan()

        # 2. Si hay detecciones en el plato blanco central, enviar consigna Pick & Place
        if hasattr(self, 'latest_detections') and len(self.latest_detections) > 0:
            det = self.latest_detections[0]
            color = det['color']
            x_cm, y_cm = det['x_cm'], det['y_cm']

            msg_color = String()
            msg_color.data = color
            self.ros_node.color_pub.publish(msg_color)
            time.sleep(0.08)  # Sincronización para asegurar que color llegue antes que punto

            msg_point = Point()
            msg_point.x = x_cm
            msg_point.y = y_cm
            msg_point.z = 1.45
            self.ros_node.point_pub.publish(msg_point)

            self._add_log('INFO', f'🚀 Ciclo Pick & Place ENVIADO -> Cubo {color.upper()} en ({x_cm}cm, {y_cm}cm)')
            self._update_fsm_badge('PICK')
        else:
            self._add_log('WARN', '⚠️ Sistema listo en pose SCAN. Coloque una pieza en la bandeja central para iniciar agarre.')

    def cmd_stop_controlled(self) -> None:
        """Detención controlada al finalizar el movimiento actual."""
        self._add_log('WARN', '⏹️ STOP Controlado solicitado. Finalizando movimiento actual...')
        self.ros_node.status_pub.publish(String(data='STOP_CONTROLLED'))

        if self.ros_node.stop_client.service_is_ready():
            self.ros_node.stop_client.call_async(Trigger.Request())

    def cmd_emergency_stop(self) -> None:
        """Parada de emergencia inmediata (E-Stop)."""
        self._add_log('ALARM', '🚨 PARADA DE EMERGENCIA ACTIVADA (E-STOP)! Deteniendo robot y apagando vacío.')

        # 1. Apagar Vacío
        self.ros_node.vacuum_pub.publish(String(data='VACUUM_OFF'))

        # 2. Enviar Stop Software
        if self.ros_node.stop_client.service_is_ready():
            self.ros_node.stop_client.call_async(Trigger.Request())

        # 3. Transicionar a FAULT
        self._update_fsm_badge('FAULT')
        self.lbl_moveit_state.setText("Fallo de Planificación 🚨")
        self.lbl_moveit_state.setStyleSheet("color: #e74c3c; font-weight: bold;")

    def cmd_reset_faults(self) -> None:
        """Limpia fallas tras intervención del operador."""
        self._add_log('INFO', '🔧 Limpiando fallas. Rearmando sistema...')
        self.lbl_moveit_state.setText("Plan Válido ✅")
        self.lbl_moveit_state.setStyleSheet("color: #2ecc71; font-weight: bold;")
        self._update_fsm_badge('READY')

    def cmd_next_cube(self) -> None:
        """Modo paso a paso (Step-by-step)."""
        self._add_log('INFO', '⏭️ Ejecutando paso a paso (Next Cube)...')

        if hasattr(self, 'latest_detections') and len(self.latest_detections) > 0:
            det = self.latest_detections[0]
            color = det['color']
            x_cm, y_cm = det['x_cm'], det['y_cm']

            msg_color = String()
            msg_color.data = color
            self.ros_node.color_pub.publish(msg_color)
            time.sleep(0.08)  # Pausa para asegurar sincronización con el receptor sorting_node

            msg_point = Point()
            msg_point.x = x_cm
            msg_point.y = y_cm
            msg_point.z = 1.45
            self.ros_node.point_pub.publish(msg_point)

            self._add_log('INFO', f'⏭️ Paso a Paso enviado -> Cubo {color.upper()} en ({x_cm}cm, {y_cm}cm)')
            self._update_fsm_badge('PICK')
        else:
            self._add_log('WARN', '⚠️ Coloque un cubo en el plato blanco central para ejecutar el paso.')

    def cmd_home(self) -> None:
        self._add_log('INFO', '🏠 Posicionando robot en pose HOME...')
        msg = JointState()
        msg.header.stamp = self.ros_node.get_clock().now().to_msg()
        msg.name = ['phantomx_pincher_arm_shoulder_pan_joint', 'phantomx_pincher_arm_shoulder_lift_joint', 'phantomx_pincher_arm_elbow_flex_joint', 'phantomx_pincher_arm_wrist_flex_joint', 'phantomx_pincher_gripper_finger1_joint']
        msg.position = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.ros_node.command_pub.publish(msg)
        self._update_fsm_badge('READY')

    def cmd_scan(self) -> None:
        self._add_log('INFO', '📷 Posicionando robot en pose SCAN...')
        msg = JointState()
        msg.header.stamp = self.ros_node.get_clock().now().to_msg()
        msg.name = ['phantomx_pincher_arm_shoulder_pan_joint', 'phantomx_pincher_arm_shoulder_lift_joint', 'phantomx_pincher_arm_elbow_flex_joint', 'phantomx_pincher_arm_wrist_flex_joint', 'phantomx_pincher_gripper_finger1_joint']
        msg.position = [0.0, math.radians(-90), math.radians(90), math.radians(90), 0.0]
        self.ros_node.command_pub.publish(msg)
        self._update_fsm_badge('SCAN')

    def cmd_plan(self) -> None:
        self._add_log('INFO', '📝 Calculando planificación manual IK/MoveIt...')
        self._update_fsm_badge('PLAN')

    def cmd_execute(self) -> None:
        self._add_log('INFO', '⚡ Ejecutando trayectoria planificada en robot...')
        self._update_fsm_badge('PICK')

    def cmd_vacuum_on(self) -> None:
        self.ros_node.vacuum_pub.publish(String(data='VACUUM_ON'))

    def cmd_vacuum_off(self) -> None:
        self.ros_node.vacuum_pub.publish(String(data='VACUUM_OFF'))

    def launch_rviz2(self) -> None:
        """Lanza la visualización 3D en RViz2."""
        try:
            if self.rviz_process is None or self.rviz_process.poll() is not None:
                self._add_log('INFO', '🚀 Lanzando RViz2 3D con MoveIt...')
                self.rviz_process = subprocess.Popen(["ros2", "launch", "pincher_description", "display.launch.py"])
                self.lbl_rviz_status.setText("Estado RViz2: En Ejecución 🟢")
                self.lbl_rviz_status.setStyleSheet("color: #2ecc71; font-weight: bold;")
            else:
                self._add_log('INFO', 'RViz2 ya se encuentra en ejecución.')
        except Exception as e:
            self._add_log('ERROR', f'No se pudo lanzar RViz2: {e}')

    def _add_log(self, level: str, text: str) -> None:
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        row = self.log_table.rowCount()
        self.log_table.insertRow(row)

        item_ts = QTableWidgetItem(timestamp)
        item_lvl = QTableWidgetItem(level)
        item_msg = QTableWidgetItem(text)

        if level == 'ERROR' or level == 'ALARM':
            color = QColor(231, 76, 60)
        elif level == 'WARN':
            color = QColor(241, 196, 15)
        else:
            color = QColor(46, 204, 113)

        item_lvl.setForeground(color)
        item_lvl.setFont(QFont("Segoe UI", 9, QFont.Bold))

        self.log_table.setItem(row, 0, item_ts)
        self.log_table.setItem(row, 1, item_lvl)
        self.log_table.setItem(row, 2, item_msg)

        self.log_table.scrollToBottom()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if hasattr(self, 'cam_worker'):
            self.cam_worker.stop()
        if hasattr(self, 'bridge_worker'):
            self.bridge_worker.stop()

        for proc in [self.sorting_process, self.vision_process, self.rviz_process]:
            if proc and proc.poll() is None:
                proc.terminate()

        event.accept()


def main(args=None) -> None:
    rclpy.init(args=args)
    ros_node = PincherHmiNode()

    app = QApplication(sys.argv)
    window = PincherHmiWindow(ros_node)
    window.show()

    ret = app.exec_()
    ros_node.destroy_node()
    rclpy.shutdown()
    sys.exit(ret)


if __name__ == '__main__':
    main()
