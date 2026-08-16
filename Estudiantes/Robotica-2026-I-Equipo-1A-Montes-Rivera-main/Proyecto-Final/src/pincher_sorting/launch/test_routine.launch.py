import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    control_share = get_package_share_directory('pincher_control')

    pincher_system_launch = PythonLaunchDescriptionSource(
        os.path.join(control_share, 'launch', 'pincher_system.launch.py')
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_hardware', default_value='false'),
        DeclareLaunchArgument('motor_model', default_value='ax12a'),
        DeclareLaunchArgument('port', default_value='/dev/ttyUSB0'),
        DeclareLaunchArgument('start_gui', default_value='true'),
        DeclareLaunchArgument('start_rviz', default_value='true'),

        # Lanzar la celda y robot PhantomX Pincher en RViz (sin iniciar rutinas automáticas)
        IncludeLaunchDescription(
            pincher_system_launch,
            launch_arguments={
                'use_hardware': LaunchConfiguration('use_hardware'),
                'motor_model': LaunchConfiguration('motor_model'),
                'port': LaunchConfiguration('port'),
                'start_gui': LaunchConfiguration('start_gui'),
                'start_rviz': LaunchConfiguration('start_rviz'),
            }.items(),
        ),
    ])
