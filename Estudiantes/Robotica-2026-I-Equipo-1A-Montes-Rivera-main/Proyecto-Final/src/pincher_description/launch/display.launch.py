import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
import xacro


def _launch_setup(context):
    package_share = get_package_share_directory('pincher_description')
    xacro_file = os.path.join(package_share, 'urdf', 'robot.xacro')
    rviz_config = os.path.join(package_share, 'rviz', 'pincher.rviz')

    use_meshes = LaunchConfiguration('use_meshes').perform(context).lower()
    robot_description = xacro.process_file(
        xacro_file,
        mappings={'use_meshes': use_meshes},
    ).toxml()

    return [
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': ParameterValue(
                    LaunchConfiguration('use_sim_time'),
                    value_type=bool,
                ),
            }],
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen',
            parameters=[{'robot_description': robot_description}],
            condition=IfCondition(LaunchConfiguration('start_jsp')),
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config],
            condition=IfCondition(LaunchConfiguration('start_rviz')),
        ),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_meshes',
            default_value='true',
            description='Usa las mallas del robot y la celda.',
        ),
        DeclareLaunchArgument(
            'start_jsp',
            default_value='false',
            description='Inicia joint_state_publisher_gui solo si no hay otro controlador (como control_servo) publicando /joint_states.',
        ),
        DeclareLaunchArgument(
            'start_rviz',
            default_value='true',
            description='Inicia RViz2.',
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Usa el reloj de simulación.',
        ),
        OpaqueFunction(function=_launch_setup),
    ])