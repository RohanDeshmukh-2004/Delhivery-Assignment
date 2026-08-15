import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    pkg_warehouse_nav = get_package_share_directory('warehouse_nav')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    world_path = os.path.join(pkg_warehouse_nav, 'worlds', 'warehouse_ramps.world')
    amr1_xacro = os.path.join(pkg_warehouse_nav, 'urdf', 'amr_1.urdf.xacro')
    amr2_xacro = os.path.join(pkg_warehouse_nav, 'urdf', 'amr_2.urdf.xacro')

    doc_amr1 = xacro.process_file(amr1_xacro)
    doc_amr2 = xacro.process_file(amr2_xacro)

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': world_path}.items()
    )

    rsp_amr1 = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace='amr_1',
        output='screen',
        parameters=[{
            'robot_description': doc_amr1.toxml(),
            'frame_prefix': 'amr_1/'
        }]
    )

    rsp_amr2 = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace='amr_2',
        output='screen',
        parameters=[{
            'robot_description': doc_amr2.toxml(),
            'frame_prefix': 'amr_2/'
        }]
    )

    spawn_amr1 = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', '/amr_1/robot_description',
            '-entity', 'amr_1',
            '-robot_namespace', 'amr_1',
            '-x', '-2.0', '-y', '1.0', '-z', '0.2'
        ],
        output='screen'
    )

    spawn_amr2 = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', '/amr_2/robot_description',
            '-entity', 'amr_2',
            '-robot_namespace', 'amr_2',
            '-x', '-2.0', '-y', '-1.0', '-z', '0.2'
        ],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        rsp_amr1,
        rsp_amr2,
        spawn_amr1,
        spawn_amr2
    ])