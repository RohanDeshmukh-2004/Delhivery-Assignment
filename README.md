# Multi-Robot Logistics Stack (ROS 2 / Gazebo)

A multi-robot logistics demonstration built using ROS 2 and Gazebo featuring dual Autonomous Mobile Robots (`AMR-1` and `AMR-2`), isolated topic namespacing, custom TF frame prefixing, RViz2 visualization, and 2D SLAM mapping.

## Key Features

* **Multi-Robot Isolation:** Clean namespacing (`/amr_1`, `/amr_2`) across command velocity, odometry, scan, and TF frames.
* **Dual AMR Visualization:** Pre-configured RViz2 setup displaying dual `RobotModel` layers with dynamic frame prefixes.
* **SLAM Integration:** 2D mapping and occupancy grid generation powered by `slam_toolbox`.
* **Flexible Control:** Options to drive individual robots or mirror velocity commands to control both simultaneously.

## Repository Structure

```text
gazebo_test_ws/
├── src/
│   ├── fleet_bringup/       # Launch files for dual-AMR Gazebo & RViz setup
│   ├── fleet_description/   # URDF models, meshes, and robot TF configurations
│   ├── fleet_diagnostics/   # System health and node monitoring
│   └── fleet_slam/          # SLAM toolbox configurations and map data
├── .gitignore
└── README.md
