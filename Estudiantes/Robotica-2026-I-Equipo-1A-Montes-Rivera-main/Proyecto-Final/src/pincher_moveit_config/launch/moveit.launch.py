import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from moveit_configs_builder import MoveItConfigsBuilder


def generate_launch_description():
    description_share = get_package_share_directory('pincher_description')
    xacro_file = os.path.join(description_share, 'urdf', 'robot.xacro')

    moveit_config = (
        MoveItConfigsBuilder('phantomx_pincher', package_name='pincher_moveit_config')
        .robot_description(file_path=xacro_file)
        .robot_description_semantic(file_path='config/phantomx_pincher.srdf')
        .trajectory_execution(file_path='config/moveit_controllers.yaml')
        .planning_pipelines(pipelines=['ompl'], default_planning_pipeline='ompl')
        .to_moveit_configs()
    )

    move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[moveit_config.to_dict()],
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2_moveit',
        output='screen',
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.planning_pipelines,
            moveit_config.robot_description_kinematics,
        ],
    )

    return LaunchDescription([
        move_group_node,
        rviz_node,
    ])
