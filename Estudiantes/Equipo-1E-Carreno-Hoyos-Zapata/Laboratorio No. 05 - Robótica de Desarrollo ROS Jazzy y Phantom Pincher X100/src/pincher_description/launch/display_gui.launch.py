"""Practica 1: modelo del robot movido con joint_state_publisher_gui.

Lanza robot_state_publisher + joint_state_publisher_gui + RViz2. Los sliders
de la GUI publican /joint_states y RViz actualiza la postura del robot.

No ejecutar al mismo tiempo que un nodo de pincher_lab: ambos publicarian
/joint_states.

Nota: el Xacro se procesa con xacro.process_file() en Python (no con la
substitucion Command) para que la ruta funcione aunque contenga espacios,
como en 'Laboratorio No. 05 - ...'.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def _launch_setup(context):
    package_share = get_package_share_directory('pincher_description')
    xacro_file = os.path.join(package_share, 'urdf', 'robot.xacro')
    rviz_config_file = os.path.join(package_share, 'rviz', 'pincher.rviz')

    use_meshes = LaunchConfiguration('use_meshes').perform(context).lower()
    robot_description_content = xacro.process_file(
        xacro_file,
        mappings={'use_meshes': use_meshes},
    ).toxml()
    robot_description = {'robot_description': robot_description_content}

    return [
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[robot_description, {'publish_frequency': 30.0}],
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen',
            parameters=[robot_description, {
                'rate': 30,
                'publish_default_positions': True,
                'use_mimic_tags': True,
            }],
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config_file],
        ),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('use_meshes', default_value='true'),
        OpaqueFunction(function=_launch_setup),
    ])
