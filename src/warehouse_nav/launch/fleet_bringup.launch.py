import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg_share = FindPackageShare(package='warehouse_nav').find('warehouse_nav')
    
    # 1. Base Simulation Stack (Gazebo & URDFs)
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_share, 'launch', 'fleet_sim.launch.py'))
    )

    # 2. Safety Stack (BSP Validation & E-Stop Overrides)
    safety_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_share, 'launch', 'safety_system.launch.py'))
    )

    # 3. Traffic Stack (Motion Smoothers & MAPF Controller)
    traffic_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_share, 'launch', 'traffic_system.launch.py'))
    )

    return LaunchDescription([
        sim_launch,
        safety_launch,
        traffic_launch
    ])