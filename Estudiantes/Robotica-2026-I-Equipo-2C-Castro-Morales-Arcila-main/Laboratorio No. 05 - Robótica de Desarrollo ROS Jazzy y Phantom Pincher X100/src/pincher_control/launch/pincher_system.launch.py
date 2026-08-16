import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    description_share = get_package_share_directory('pincher_description')
    display_launch = PythonLaunchDescriptionSource(
        os.path.join(description_share, 'launch', 'display.launch.py')
    )

    return LaunchDescription([
        DeclareLaunchArgument('motor_model', default_value='xl430'),
        DeclareLaunchArgument('use_hardware', default_value='false'),
        DeclareLaunchArgument('port', default_value='/dev/ttyUSB0'),
        DeclareLaunchArgument('baudrate', default_value='1000000'),
        DeclareLaunchArgument('read_rate_hz', default_value='20.0'),
        DeclareLaunchArgument('home_on_startup', default_value='false'),
        DeclareLaunchArgument('start_gui', default_value='true'),
        DeclareLaunchArgument('start_rviz', default_value='true'),
        DeclareLaunchArgument('use_meshes', default_value='false'),
        IncludeLaunchDescription(
            display_launch,
            launch_arguments={
                'use_meshes': LaunchConfiguration('use_meshes'),
                'start_rviz': LaunchConfiguration('start_rviz'),
                'use_sim_time': 'false',
            }.items(),
        ),
        Node(
            package='pincher_control',
            executable='control_servo',
            name='pincher_controller',
            output='screen',
            parameters=[{
                'motor_model': LaunchConfiguration('motor_model'),
                'use_hardware': ParameterValue(
                    LaunchConfiguration('use_hardware'),
                    value_type=bool,
                ),
                'port': LaunchConfiguration('port'),
                'baudrate': ParameterValue(
                    LaunchConfiguration('baudrate'),
                    value_type=int,
                ),
                'read_rate_hz': ParameterValue(
                    LaunchConfiguration('read_rate_hz'),
                    value_type=float,
                ),
                'home_on_startup': ParameterValue(
                    LaunchConfiguration('home_on_startup'),
                    value_type=bool,
                ),
            }],
        ),
        Node(
            package='pincher_control',
            executable='pincher_gui',
            name='pincher_gui',
            output='screen',
            condition=IfCondition(LaunchConfiguration('start_gui')),
        ),
    ])
