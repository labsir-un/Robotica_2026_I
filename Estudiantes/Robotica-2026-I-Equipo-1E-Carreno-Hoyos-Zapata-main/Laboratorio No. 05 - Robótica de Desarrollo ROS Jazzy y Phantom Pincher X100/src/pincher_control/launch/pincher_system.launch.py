"""Sistema completo con hardware/GUI: control_servo + GUI Tkinter + RViz.

Lanza:
  - pincher_controller (control_servo): abre el puerto DYNAMIXEL (si
    use_hardware:=true), publica /joint_states y recibe /pincher/command.
  - pincher_gui: ventana Tkinter con sliders, velocidad, HOME, Torque ON/OFF
    y parada de software.
  - display.launch.py de pincher_description: robot_state_publisher + RViz2.

Uso con el robot AX-12A real:
  ros2 launch pincher_control pincher_system.launch.py use_hardware:=true

Uso en simulacion (sin abrir el puerto):
  ros2 launch pincher_control pincher_system.launch.py use_hardware:=false

Por defecto motor_model:=ax12a (los servos de nuestro Pincher) y una velocidad
inicial conservadora (moving_speed=60) para las primeras pruebas.
"""

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
        DeclareLaunchArgument('motor_model', default_value='ax12a'),
        DeclareLaunchArgument('use_hardware', default_value='false'),
        DeclareLaunchArgument('port', default_value='/dev/ttyUSB0'),
        DeclareLaunchArgument('baudrate', default_value='1000000'),
        DeclareLaunchArgument('moving_speed', default_value='60'),
        DeclareLaunchArgument('read_rate_hz', default_value='20.0'),
        DeclareLaunchArgument('home_on_startup', default_value='false'),
        DeclareLaunchArgument('start_gui', default_value='true'),
        DeclareLaunchArgument('start_rviz', default_value='true'),
        DeclareLaunchArgument('use_meshes', default_value='true'),
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
                'moving_speed': ParameterValue(
                    LaunchConfiguration('moving_speed'),
                    value_type=int,
                ),
                'torque_limit': 800,
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
