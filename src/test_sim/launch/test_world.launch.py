import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    pkg_test_sim = get_package_share_directory('test_sim')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    # Process Xacro
    xacro_file = os.path.join(pkg_test_sim, 'urdf', 'simple_robot.urdf.xacro')
    robot_description_raw = xacro.process_file(xacro_file).toxml()

    # Launch Gazebo GUI
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        )
    )

    # Robot State Publisher
    robot_state_pub = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_raw, 'use_sim_time': True}]
    )

    # Spawn Robot Entity in Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'simple_bot', '-z', '0.2'],
        output='screen'
    )

    # RViz2
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        robot_state_pub,
        spawn_entity,
        rviz
    ])