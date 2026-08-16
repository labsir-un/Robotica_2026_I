#!/usr/bin/env python3
"""
Nodo ROS 2 de Visión Artificial (YOLOv8 + OpenCV).

Carga los modelos entrenados (best_piezascolor.pt / best_piezasnegras.pt),
captura la imagen de la cámara, detecta los bloques/piezas, transforma
las coordenadas de píxeles (u, v) a coordenadas reales (X_cm, Y_cm) en el marco 'world'
y publica la detección hacia el nodo de clasificación 'sorting_node'.
"""

from __future__ import annotations

import os
import sys
import math
import time
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from std_msgs.msg import String

# Asegurar que ROS 2 encuentre librerías instaladas con pip --user / --break-system-packages
import site
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

# Importar Ultralytics YOLO
try:
    from ultralytics import YOLO
    HAS_ULTRALYTICS = True
except ImportError:
    HAS_ULTRALYTICS = False


class VisionNode(Node):
    """Nodo de Visión para detección autónoma de bloques con YOLOv8."""

    def __init__(self) -> None:
        super().__init__('vision_node')
        self.cap = None

        # Parámetros del nodo
        self.declare_parameter('model_name', 'best_piezascolor.pt')
        self.declare_parameter('camera_device', '/dev/v4l/by-id/usb-046d_0825_A5DECA50-video-index0')
        self.declare_parameter('conf_threshold', 0.5)
        self.declare_parameter('publish_rate_hz', 2.0)
        self.declare_parameter('use_simulated_camera', False)
        self.declare_parameter('show_window', False)
        self.declare_parameter('camera_offset_x_cm', -1.0)  # Ajuste fino: punto medio exacto de alineación en X
        self.declare_parameter('invert_x_axis', False)
        self.declare_parameter('invert_y_axis', True)

        self.model_name = str(self.get_parameter('model_name').value)
        self.camera_device = str(self.get_parameter('camera_device').value)
        self.conf_threshold = float(self.get_parameter('conf_threshold').value)
        self.publish_rate_hz = float(self.get_parameter('publish_rate_hz').value)
        self.use_simulated_camera = bool(self.get_parameter('use_simulated_camera').value)
        self.show_window = bool(self.get_parameter('show_window').value)
        self.camera_offset_x_cm = float(self.get_parameter('camera_offset_x_cm').value)
        self.invert_x_axis = bool(self.get_parameter('invert_x_axis').value)
        self.invert_y_axis = bool(self.get_parameter('invert_y_axis').value)

        self.window_name = "YOLOv8_Vision_PhantomX"
        self.window_created = False

        # Publicadores
        self.point_pub = self.create_publisher(Point, 'vision/coordenada_pieza', 10)
        self.color_pub = self.create_publisher(String, 'vision/color_pieza', 10)

        # Suscriptor al estado del robot
        self.last_detection_time = 0.0
        self.robot_is_busy = False
        self.status_sub = self.create_subscription(String, '/pincher/status', self._status_callback, 10)

    def _status_callback(self, msg: String) -> None:
        status_str = msg.data.lower()
        if 'scan' in status_str or 'home' in status_str:
            self.robot_is_busy = False
        else:
            self.robot_is_busy = True

        # Mapeo de clases YOLO a colores de destino del robot
        self.class_to_color_map: Dict[str, str] = {
            # Modelo piezas a color
            'cubo_rojo': 'red',
            'cubo_azul': 'blue',
            'cubo_verde': 'green',
            'rectangulo_amarillo': 'yellow',
            'pentagono_azul': 'blue',
            'cilindro_verde': 'green',
            'cilindro_naranja': 'yellow',
            # Modelo piezas negras / general
            'cubo negro': 'green',
            'rectangulo': 'yellow',
            'cubo rojo': 'red',
            'cilindro': 'blue',
        }

        # Matriz de Calibración / Homografía (Píxeles u,v -> cm X,Y en el marco 'world')
        # Centroide por defecto de la plataforma blanca: X = 9.6 cm, Y = 0.0 cm
        # Resolución típica de cámara: 640x480 (Centro u=320, v=240)
        self.px_center_u = 320.0
        self.px_center_v = 240.0
        self.scale_x_cm_per_px = 0.05   # 1 px ≈ 0.5 mm
        self.scale_y_cm_per_px = -0.05  # Inversión de eje Y de imagen

        # Cargar Modelo YOLO
        self.model = None
        self._load_yolo_model()

        # Inicializar Cámara
        self.cap = None
        if not self.use_simulated_camera:
            self._init_camera()

        # Timer de procesamiento
        period_sec = 1.0 / self.publish_rate_hz
        self.timer = self.create_timer(period_sec, self.timer_callback)

        self.get_logger().info('📷 Nodo de Visión Artificial YOLOv8 Iniciado Correctamente.')

    def _load_yolo_model(self) -> None:
        if not HAS_ULTRALYTICS:
            self.get_logger().error('❌ La librería ultralytics no está instalada (pip install ultralytics). Se usará modo simulación.')
            return

        # Lista de posibles rutas para encontrar el archivo de pesos .pt
        candidates = [
            os.path.join('/home/jesus-rivera/ros2_jazzy/phantomproyect_ws/src/pincher_sorting/models', self.model_name),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models', self.model_name),
        ]

        model_path = None
        for path in candidates:
            if os.path.exists(path) and os.path.isfile(path):
                model_path = path
                break

        if model_path:
            try:
                self.get_logger().info(f'📦 Cargando modelo YOLOv8 desde: {model_path}')
                self.model = YOLO(model_path)
                self.get_logger().info(f'✅ Modelo YOLOv8 cargado con éxito. Clases disponibles: {self.model.names}')
            except Exception as e:
                self.get_logger().error(f'❌ Error al cargar modelo YOLOv8: {e}')
        else:
            self.get_logger().warn(f'⚠️ No se encontró el archivo de pesos YOLO válido en ninguna ruta.')

    def _init_camera(self) -> None:
        try:
            # Resolver enlace simbólico persistente si aplica (ej. /dev/v4l/by-id/... -> /dev/video4)
            dev_path = self.camera_device
            if os.path.islink(dev_path):
                dev_path = os.path.realpath(dev_path)

            self.get_logger().info(f'🎥 Intentando abrir cámara en: {self.camera_device} (Ruta real: {dev_path})')

            if dev_path.isdigit():
                self.cap = cv2.VideoCapture(int(dev_path))
            else:
                self.cap = cv2.VideoCapture(dev_path, cv2.CAP_V4L2)

            if not self.cap.isOpened():
                # Reintentos de respaldo con /dev/video4, 4, /dev/video0, 0
                for alt_dev in ['/dev/video4', 4, '/dev/video0', 0]:
                    self.get_logger().warn(f'⚠️ Reintentando apertura en dispositivo de respaldo: {alt_dev}...')
                    self.cap = cv2.VideoCapture(alt_dev, cv2.CAP_V4L2) if isinstance(alt_dev, str) else cv2.VideoCapture(alt_dev)
                    if self.cap.isOpened():
                        dev_path = str(alt_dev)
                        break

            if not self.cap.isOpened():
                self.get_logger().warn(f'⚠️ No se pudo abrir ninguna cámara USB. Pasando a modo simulación.')
                self.use_simulated_camera = True
            else:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.get_logger().info(f'📷 Cámara USB Logitech ABIERTA Y ACTIVA con éxito en: {dev_path} (640x480).')
        except Exception as e:
            self.get_logger().error(f'Error al inicializar cámara: {e}')
            self.use_simulated_camera = True

    def pixel_to_world_cm(self, u: float, v: float) -> Tuple[float, float]:
        """Convierte coordenadas de píxel (u, v) a coordenadas (X_cm, Y_cm) en la celda."""
        # Desplazamiento respecto al centro de imagen
        du = u - self.px_center_u
        dv = v - self.px_center_v

        # Inversión de ejes por montaje de la cámara (ubicada al frente del robot)
        if self.invert_x_axis:
            dv = -dv
        if self.invert_y_axis:
            du = -du

        x_cm = 9.6 + (dv * self.scale_y_cm_per_px) + self.camera_offset_x_cm
        y_cm = 0.0 + (du * self.scale_x_cm_per_px)

        return round(x_cm, 2), round(y_cm, 2)

    def timer_callback(self) -> None:
        if self.use_simulated_camera or self.cap is None or not self.cap.isOpened():
            # Modo de prueba/simulación (Publicación para test)
            return

        ret, frame = self.cap.read()
        if not ret or frame is None:
            return

        if self.model is None:
            return

        # Realizar Inferencia YOLO
        results = self.model(frame, conf=self.conf_threshold, verbose=False)

        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Obtener clase y confianza
                cls_id = int(box.cls[0].item())
                raw_class_name = self.model.names.get(cls_id, f'class_{cls_id}').lower().strip()
                confidence = float(box.conf[0].item())

                # Centroide [u, v]
                u_center = (xyxy[0] + xyxy[2]) / 2.0
                v_center = (xyxy[1] + xyxy[3]) / 2.0

                # Filtrar objetos fuera del plato blanco central de recolección (320, 240, r=140px)
                dist_from_center = math.hypot(u_center - 320.0, v_center - 240.0)
                if dist_from_center > 140.0:
                    continue

                # Calcular coordenada real (X, Y)
                x_cm, y_cm = self.pixel_to_world_cm(u_center, v_center)

                # Mapear clase a color de destino de forma robusta por palabras clave
                target_color = None
                if 'roj' in raw_class_name or 'red' in raw_class_name:
                    target_color = 'red'
                elif 'az' in raw_class_name or 'blue' in raw_class_name:
                    target_color = 'blue'
                elif 'verd' in raw_class_name or 'green' in raw_class_name:
                    target_color = 'green'
                elif 'amarill' in raw_class_name or 'yellow' in raw_class_name or 'naranj' in raw_class_name:
                    target_color = 'yellow'
                else:
                    target_color = self.class_to_color_map.get(raw_class_name, None)

                if target_color is None:
                    self.get_logger().warn(f'⚠️ Clase YOLO "{raw_class_name}" no reconocida. Omitiendo envío.')
                    continue

                self.get_logger().info(
                    f'🎯 Detección YOLO: "{raw_class_name}" (Conf: {confidence:.2f}) -> '
                    f'Centroide pxl=({u_center:.0f}, {v_center:.0f}) => World=({x_cm}cm, {y_cm}cm) | Caneca Objetivo: {target_color.upper()}'
                )

                # Renderizar cuadro, cruz de calibración y texto en ventana de visualización
                if self.show_window:
                    x1, y1, x2, y2 = map(int, xyxy)
                    color_bgr = (0, 255, 0)
                    if target_color == 'red':
                        color_bgr = (0, 0, 255)
                    elif target_color == 'blue':
                        color_bgr = (255, 0, 0)
                    elif target_color == 'yellow':
                        color_bgr = (0, 255, 255)

                    # Dibujar cruz de referencia del centro de la cámara (320, 240)
                    cv2.line(frame, (310, 240), (330, 240), (255, 255, 255), 1)
                    cv2.line(frame, (320, 230), (320, 250), (255, 255, 255), 1)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color_bgr, 2)
                    cv2.circle(frame, (int(u_center), int(v_center)), 5, (0, 0, 255), -1)
                    label_str = f"{raw_class_name} ({confidence:.2f}) -> X={x_cm}cm, Y={y_cm}cm"
                    cv2.putText(frame, label_str, (x1, max(y1 - 10, 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color_bgr, 2)

                # Publicar primero el color y luego la coordenada a los tópicos de ROS 2
                now = time.time()
                if not self.robot_is_busy and (now - self.last_detection_time > 3.0):
                    self.last_detection_time = now

                    msg_color = String()
                    msg_color.data = target_color
                    self.color_pub.publish(msg_color)
                    time.sleep(0.08)  # Pequeña pausa para asegurar sincronización en sorting_node

                    msg_point = Point()
                    msg_point.x = x_cm
                    msg_point.y = y_cm
                    msg_point.z = 1.45  # Altura de pick sobre la superficie blanca (1 cm más bajo)
                    self.point_pub.publish(msg_point)
                    self.get_logger().info(f'🚀 Detección enviada a sorting_node -> Color: {target_color.upper()}, Posición: ({x_cm}cm, {y_cm}cm)')

                # Procesar una sola detección válida por ciclo
                break

        if self.show_window:
            if not self.window_created:
                cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)
                self.window_created = True
            cv2.imshow(self.window_name, frame)
            cv2.waitKey(1)

    def destroy_node(self) -> None:
        cap = getattr(self, 'cap', None)
        if cap is not None and cap.isOpened():
            cap.release()
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = VisionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
