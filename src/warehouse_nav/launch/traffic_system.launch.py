import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    nodes = []

    # Central MAPF Traffic Controller
    traffic_node = Node(
        package='warehouse_nav',
        executable='traffic_controller_node.py',
        name='traffic_controller',
        output='screen',
        parameters=[{'conflict_distance_threshold': 1.5}]
    )
    nodes.append(traffic_node)

    # Per-robot Motion Smoothers
    for robot_id in ['amr_1', 'amr_2']:
        smoother_node = Node(
            package='warehouse_nav',
            executable='motion_smoother_node.py',
            namespace=robot_id,
            name='motion_smoother',
            output='screen',
            parameters=[{
                'max_accel_empty': 1.0,
                'max_accel_loaded': 0.35,
                'update_rate': 30.0
            }]
        )
        nodes.append(smoother_node)

    return LaunchDescription(nodes)