import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    package_share = get_package_share_directory('pincher_description')
    display_launch = PythonLaunchDescriptionSource(
        os.path.join(package_share, 'launch', 'display.launch.py')
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_meshes',
            default_value='true',
            description='Mostrar mallas 3D del robot y la celda.',
        ),
        IncludeLaunchDescription(
            display_launch,
            launch_arguments={
                'use_meshes': LaunchConfiguration('use_meshes'),
                'start_jsp': 'true',
                'start_rviz': 'true',
            }.items(),
        ),
    ])