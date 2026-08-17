#!/usr/bin/env python3
"""Nodo ROS 2 de visión por computadora con YOLO v8 para detección y localización de bloques."""

import os
import cv2
from cv_bridge import CvBridge
from geometry_msgs.msg import Point
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


class PhantomxYoloNode(Node):
    """Nodo para capturar cámara, ejecutar inferencia YOLO v8 y publicar coordenadas en cm."""

    def __init__(self) -> None:
        super().__init__('pxp_yolo_node')

        # --- PARÁMETROS ROS 2 ---
        self.declare_parameter('camera_device', 2)
        self.declare_parameter('model_path', '/home/isaac-linux/vision_robot/best.pt')
        self.declare_parameter('confidence', 0.6)
        self.declare_parameter('cm_per_pixel_x', 0.06944)
        self.declare_parameter('cm_per_pixel_y', 0.06944)
        self.declare_parameter('offset_robot_x', -22.7)
        self.declare_parameter('offset_robot_y', -9.5)
        self.declare_parameter('show_window', True)
        self.declare_parameter('publish_rate_hz', 10.0)

        self.camera_device = self.get_parameter('camera_device').value
        self.model_path = self.get_parameter('model_path').value
        self.confidence = float(self.get_parameter('confidence').value)
        self.cm_per_pixel_x = float(self.get_parameter('cm_per_pixel_x').value)
        self.cm_per_pixel_y = float(self.get_parameter('cm_per_pixel_y').value)
        self.offset_robot_x = float(self.get_parameter('offset_robot_x').value)
        self.offset_robot_y = float(self.get_parameter('offset_robot_y').value)
        self.show_window = bool(self.get_parameter('show_window').value)
        rate_hz = float(self.get_parameter('publish_rate_hz').value)

        self.bridge = CvBridge()

        # Publicadores
        self.pub_image = self.create_publisher(Image, 'vision/imagen_procesada', 10)
        self.pub_punto = self.create_publisher(Point, 'vision/coordenada_pieza', 10)

        # Cargar Modelo YOLO
        self.model = None
        if YOLO_AVAILABLE and os.path.isfile(self.model_path):
            self.model = YOLO(self.model_path, task='detect')
            self.get_logger().info(f'Modelo YOLO cargado exitosamente desde: {self.model_path}')
        else:
            if not YOLO_AVAILABLE:
                self.get_logger().warning(
                    'Librería ultralytics no instalada en este entorno Python. '
                    'Instala con: pip install ultralytics'
                )
            else:
                self.get_logger().warning(
                    f'Archivo de modelo YOLO no encontrado en la ruta: {self.model_path}'
                )

        # Cámara
        self.camera = cv2.VideoCapture(self.camera_device)
        if not self.camera.isOpened():
            self.get_logger().warning(
                f'No se pudo abrir la cámara index={self.camera_device}. '
                'Verifica el índice de la cámara en el parámetro camera_device.'
            )

        self.timer = self.create_timer(1.0 / rate_hz, self.timer_callback)
        self.get_logger().info('Nodo pxp_yolo_node de visión iniciado correctamente.')

    def timer_callback(self) -> None:
        if not self.camera.isOpened():
            return

        success, frame = self.camera.read()
        if not success or frame is None:
            return

        frame_dibujado = frame.copy()

        if self.model is not None:
            resultados = self.model(frame, conf=self.confidence, verbose=False)
            for caja in resultados[0].boxes:
                clase_id = int(caja.cls[0])
                nombre = self.model.names[clase_id]

                x1, y1, x2, y2 = caja.xyxy[0]
                px_centro_x = float((x1 + x2) / 2)
                px_centro_y = float((y1 + y2) / 2)

                cm_x = (px_centro_x * self.cm_per_pixel_x) + self.offset_robot_x
                cm_y = (px_centro_y * self.cm_per_pixel_y) + self.offset_robot_y

                msg_punto = Point()
                msg_punto.x = cm_x
                msg_punto.y = cm_y
                msg_punto.z = 0.0
                self.pub_punto.publish(msg_punto)

                self.get_logger().info(
                    f'Pieza: {nombre} | Píxeles: ({px_centro_x:.1f}, {px_centro_y:.1f}) | '
                    f'Real: X={cm_x:.1f}cm, Y={cm_y:.1f}cm'
                )

            frame_dibujado = resultados[0].plot()

        if self.show_window:
            cv2.imshow("Vision IA del Robot", frame_dibujado)
            cv2.waitKey(1)

        try:
            msg_imagen = self.bridge.cv2_to_imgmsg(frame_dibujado, encoding='bgr8')
            self.pub_image.publish(msg_imagen)
        except Exception as e:
            self.get_logger().error(f'Error al convertir imagen con CvBridge: {e}')


def main(args=None) -> None:
    rclpy.init(args=args)
    nodo = PhantomxYoloNode()
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        if nodo.camera.isOpened():
            nodo.camera.release()
        cv2.destroyAllWindows()
        nodo.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
