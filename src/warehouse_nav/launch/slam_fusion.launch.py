import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('warehouse_nav')
    slam_config = os.path.join(pkg_share, 'config', 'slam_async.yaml')

    nodes = []

    for robot_id in ['amr_1', 'amr_2']:
        # SLAM Toolbox Node per robot
        slam_node = Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            namespace=robot_id,
            name='slam_toolbox',
            output='screen',
            parameters=[
                slam_config,
                {
                    'use_sim_time': True,
                    'odom_frame': f'{robot_id}/odom',
                    'map_frame': f'{robot_id}/map',
                    'base_frame': f'{robot_id}/base_footprint',
                    'scan_topic': f'/{robot_id}/scan'
                }
            ]
        )

        # Map Throttler Node per robot
        throttler_node = Node(
            package='warehouse_nav',
            executable='map_throttler_node.py',
            namespace=robot_id,
            name='map_throttler',
            output='screen',
            parameters=[{
                'update_interval_sec': 2.0,
                'input_map_topic': 'map',
                'throttled_map_topic': 'map_throttled'
            }]
        )

        nodes.extend([slam_node, throttler_node])

    return LaunchDescription(nodes)