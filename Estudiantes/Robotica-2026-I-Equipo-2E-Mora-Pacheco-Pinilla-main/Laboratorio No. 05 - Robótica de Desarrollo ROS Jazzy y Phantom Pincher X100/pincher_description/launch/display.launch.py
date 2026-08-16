import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, TimerAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
import xacro


EXPECTED_MESHES = [
    'visual/ax12.dae',
    'visual/f2.dae',
    'visual/f3.dae',
    'visual/f4.dae',
    'visual/finger.dae',
    'visual/gripper_base.dae',
    'visual/phantomx_pincher_mount.dae',
    'STL/caseBaseRobot.stl',
]


def _all_meshes_exist(package_share: str) -> bool:
    mesh_dir = os.path.join(package_share, 'meshes')
    return all(os.path.isfile(os.path.join(mesh_dir, name)) for name in EXPECTED_MESHES)


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
            package='pincher_description',
            executable='robot_desc_pub',
            name='robot_desc_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}],
        ),
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
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config],
            parameters=[{'robot_description': robot_description}],
            condition=IfCondition(LaunchConfiguration('start_rviz')),
        ),
    ]


def generate_launch_description():
    package_share = get_package_share_directory('pincher_description')
    default_meshes = 'true' if _all_meshes_exist(package_share) else 'false'

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_meshes',
            default_value=default_meshes,
            description=(
                'Usa las ocho mallas STL. El valor predeterminado es true solo '
                'cuando todas están instaladas; de lo contrario usa cajas.'
            ),
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
