#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    use_meshes = LaunchConfiguration('use_meshes')

    package_share = FindPackageShare('pincher_description')

    xacro_file = PathJoinSubstitution([
        package_share,
        'urdf',
        'robot.xacro',
    ])

    rviz_config_file = PathJoinSubstitution([
        package_share,
        'rviz',
        'pincher.rviz',
    ])

    robot_description_content = Command([
        FindExecutable(name='xacro'),
        ' ',
        xacro_file,
        ' ',
        'use_meshes:=',
        use_meshes,
    ])

    robot_description = {
        'robot_description': robot_description_content
    }

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            robot_description,
            {
                'publish_frequency': 30.0,
                'ignore_timestamp': False,
            },
        ],
    )

    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen',
        parameters=[
            robot_description,
            {
                'rate': 30,
                'publish_default_positions': True,
                'publish_default_velocities': False,
                'publish_default_efforts': False,
                'use_mimic_tags': True,
            },
        ],
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=[
            '-d',
            rviz_config_file,
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_meshes',
            default_value='true',
            description='Mostrar las mallas STL del robot.',
        ),

        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node,
    ])
