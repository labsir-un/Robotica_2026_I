import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'camera_device',
            default_value='2',
            description='Índice del dispositivo de cámara OpenCV.',
        ),
        DeclareLaunchArgument(
            'model_path',
            default_value='/home/isaac-linux/vision_robot/best.pt',
            description='Ruta al archivo del modelo YOLO .pt.',
        ),
        DeclareLaunchArgument(
            'confidence',
            default_value='0.6',
            description='Umbral mínimo de confianza de la detección.',
        ),
        DeclareLaunchArgument(
            'show_window',
            default_value='true',
            description='Muestra la ventana OpenCV con las detecciones.',
        ),
        Node(
            package='pincher_vision',
            executable='pxp_yolo_node',
            name='pxp_yolo_node',
            output='screen',
            parameters=[{
                'camera_device': LaunchConfiguration('camera_device'),
                'model_path': LaunchConfiguration('model_path'),
                'confidence': LaunchConfiguration('confidence'),
                'show_window': LaunchConfiguration('show_window'),
            }],
        ),
    ])
