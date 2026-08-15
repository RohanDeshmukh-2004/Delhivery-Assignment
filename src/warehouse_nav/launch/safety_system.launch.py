from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    nodes = []
    
    for robot_id in ['amr_1', 'amr_2']:
        # BSP IMU Validator Node per robot
        bsp_node = Node(
            package='warehouse_nav',
            executable='bsp_validation_node.py',
            namespace=robot_id,
            name='bsp_validation',
            output='screen',
            parameters=[{
                'max_angular_velocity': 5.0,
                'imu_raw_topic': 'imu/data',
                'imu_validated_topic': 'imu/data_validated'
            }]
        )

        # Dynamic Safety Override Node per robot
        safety_node = Node(
            package='warehouse_nav',
            executable='safety_override_node.py',
            namespace=robot_id,
            name='safety_override',
            output='screen',
            parameters=[{
                'k_factor': 0.5,
                'd_min': 0.4,
                'scan_angle_deg': 45.0
            }]
        )

        nodes.extend([bsp_node, safety_node])

    return LaunchDescription(nodes)