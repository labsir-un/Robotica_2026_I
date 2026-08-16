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
        DeclareLaunchArgument('use_hardware', default_value='false'),
        DeclareLaunchArgument('motor_model', default_value='ax12a'),
        DeclareLaunchArgument('port', default_value='/dev/ttyUSB0'),
        DeclareLaunchArgument('baudrate', default_value='1000000'),
        DeclareLaunchArgument('start_rviz', default_value='true'),
        DeclareLaunchArgument('camera_device', default_value='/dev/v4l/by-id/usb-046d_0825_A5DECA50-video-index0'),

        IncludeLaunchDescription(
            pincher_system_launch,
            launch_arguments={
                'use_hardware': LaunchConfiguration('use_hardware'),
                'motor_model': LaunchConfiguration('motor_model'),
                'port': LaunchConfiguration('port'),
                'baudrate': LaunchConfiguration('baudrate'),
                'start_gui': 'false',  # Reemplazar pincher_gui básica por HMI industrial
                'start_rviz': LaunchConfiguration('start_rviz'),
            }.items(),
        ),

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
