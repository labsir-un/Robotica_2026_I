import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    control_share = get_package_share_directory('pincher_control')
    pincher_system_launch = PythonLaunchDescriptionSource(
        os.path.join(control_share, 'launch', 'pincher_system.launch.py')
    )

    return LaunchDescription([
        # Argumentos de Lanzamiento
        DeclareLaunchArgument('use_hardware', default_value='true'),
        DeclareLaunchArgument('motor_model', default_value='ax12a'),
        DeclareLaunchArgument('port', default_value='/dev/ttyUSB0'),
        DeclareLaunchArgument('baudrate', default_value='1000000'),
        DeclareLaunchArgument('gpio_pin', default_value='17'),
        DeclareLaunchArgument('camera_device', default_value='/dev/v4l/by-id/usb-046d_0825_A5DECA50-video-index0'),
        DeclareLaunchArgument('start_rviz', default_value='true'),

        # 1. Driver de Control de Servos y Visualización
        IncludeLaunchDescription(
            pincher_system_launch,
            launch_arguments={
                'use_hardware': LaunchConfiguration('use_hardware'),
                'motor_model': LaunchConfiguration('motor_model'),
                'port': LaunchConfiguration('port'),
                'baudrate': LaunchConfiguration('baudrate'),
                'start_gui': 'false',  # HMI reemplaza a pincher_gui
                'start_rviz': LaunchConfiguration('start_rviz'),
            }.items(),
        ),

        # 2. Control de Relé de Vacío por GPIO 17
        Node(
            package='pincher_control',
            executable='vacuum_relay_node',
            name='vacuum_relay_node',
            output='screen',
            parameters=[{
                'gpio_pin': LaunchConfiguration('gpio_pin'),
            }],
        ),

        # 3. Nodo de Visión YOLOv8
        Node(
            package='pincher_sorting',
            executable='vision_node',
            name='vision_node',
            output='screen',
            parameters=[{
                'model_name': 'best_piezascolor.pt',
                'camera_device': LaunchConfiguration('camera_device'),
                'conf_threshold': 0.5,
                'show_window': False,
            }],
        ),

        # 4. Nodo de Clasificación Pick & Place (Máquina de Estados)
        Node(
            package='pincher_sorting',
            executable='sorting_node',
            name='sorting_node',
            output='screen',
            parameters=[{
                'simulation_mode': ParameterValue(
                    LaunchConfiguration('use_hardware'),
                    value_type=bool,
                ),
            }],
        ),

        # 5. Interfaz HMI Industrial en PyQt5
        Node(
            package='pincher_hmi',
            executable='hmi_gui',
            name='pincher_hmi',
            output='screen',
            parameters=[{
                'camera_device': LaunchConfiguration('camera_device'),
            }],
        ),
    ])
