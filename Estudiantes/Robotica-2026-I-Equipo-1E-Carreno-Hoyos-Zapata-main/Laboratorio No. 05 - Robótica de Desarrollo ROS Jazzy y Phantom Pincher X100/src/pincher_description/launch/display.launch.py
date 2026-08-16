"""Visualiza el PhantomX Pincher X100 en RViz.

Lanza robot_state_publisher (publica /tf a partir de /joint_states) y RViz2.
Quien publica /joint_states es un nodo externo (pincher_lab) o la GUI de
joint_state_publisher (ver display_gui.launch.py).
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
import xacro


EXPECTED_MESHES = [
    'px100_1_base.stl',
    'px100_2_shoulder.stl',
    'px100_3_upper_arm.stl',
    'px100_4_forearm.stl',
    'px100_5_gripper.stl',
    'px100_6_gripper_prop.stl',
    'px100_7_gripper_bar.stl',
    'px100_8_gripper_finger.stl',
]


def _all_meshes_exist(package_share: str) -> bool:
    mesh_dir = os.path.join(package_share, 'meshes')
    return all(os.path.isfile(os.path.join(mesh_dir, name)) for name in EXPECTED_MESHES)


def _launch_setup(context):
    package_share = get_package_share_directory('pincher_description')
    modelo = LaunchConfiguration('model').perform(context).lower()
    extra = []

    if modelo == 'kit':
        # Modelo 3D REALISTA del repositorio base oficial. No se duplica aqui:
        # el brazo del KIT se compone de 18 sub-eslabones (servos ax12 y soportes
        # f2/f3/f4/f10), asi que copiar las mallas obligaria a replicar su URDF.
        # Se declara `phantomx_pincher_description` como dependencia y se usa tal
        # cual. Sus juntas tienen otros nombres, de modo que `kit_bridge` traduce
        # /joint_states_sim -> /joint_states (y convierte la pinza, que en ese
        # modelo es una junta prismatica en metros).
        # urdf_kit carga el URDF oficial y le aplica nuestros ajustes de montaje
        # (colores de las canecas laterales) sin tocar el paquete de terceros.
        from pincher_lab import urdf_kit
        robot_description = urdf_kit.cargar()
        rviz_config = os.path.join(package_share, 'rviz', 'pincher_kit.rviz')
        extra.append(Node(
            package='pincher_lab', executable='kit_bridge',
            name='kit_bridge', output='screen',
        ))
    else:
        xacro_file = os.path.join(package_share, 'urdf', 'robot.xacro')
        rviz_config = os.path.join(package_share, 'rviz', 'pincher.rviz')
        use_meshes = LaunchConfiguration('use_meshes').perform(context).lower()
        robot_description = xacro.process_file(
            xacro_file,
            mappings={'use_meshes': use_meshes},
        ).toxml()

    return extra + [
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
            condition=IfCondition(LaunchConfiguration('start_rviz')),
        ),
    ]


def generate_launch_description():
    package_share = get_package_share_directory('pincher_description')
    default_meshes = 'true' if _all_meshes_exist(package_share) else 'false'

    return LaunchDescription([
        # 'kit'   -> modelo realista oficial (phantomx_pincher_description)
        # 'propio'-> nuestro URDF simplificado (mallas px100, aproximacion visual)
        DeclareLaunchArgument('model', default_value='kit'),
        DeclareLaunchArgument('use_meshes', default_value=default_meshes),
        DeclareLaunchArgument('start_rviz', default_value='true'),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        OpaqueFunction(function=_launch_setup),
    ])
