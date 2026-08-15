# Multi-Robot Logistics Stack (ROS 2 / Gazebo)

A multi-robot logistics demonstration built using ROS 2 and Gazebo featuring dual Autonomous Mobile Robots (`AMR-1` and `AMR-2`), isolated topic namespacing, custom TF frame prefixing, RViz2 visualization, dynamic obstacle avoidance, and 2D SLAM mapping.

## Key Features

* **Multi-Robot Isolation:** Clean namespacing (`/amr_1`, `/amr_2`) across command velocity, odometry, scan, and TF frames.
* **Dual AMR Visualization:** Pre-configured RViz2 setup displaying dual `RobotModel` layers with dynamic frame prefixes.
* **SLAM Integration:** 2D mapping and occupancy grid generation powered by `slam_toolbox`.
* **Flexible Control:** Options to drive individual robots or mirror velocity commands to control both simultaneously.


## 🚀 Launch Instructions (Simulation, Navigation & Control)

### 1. Build and Source Workspace
Before launching any nodes, ensure the workspace is built and sourced correctly:

```bash
cd ~/gazebo_test_ws
colcon build --symlink-install
source install/setup.bashbo_test_ws/src/warehouse_nav/maps/warehouse_world

## Repository Structure

```text
gazebo_test_ws/
└── src/
    └── warehouse_nav/
        ├── CMakeLists.txt
        ├── package.xml
        │
        ├── config/
        │   ├── amr_1_nav2.yaml            # Nav2 params for AMR-1 (heavy, lower speed/accel)
        │   ├── amr_2_nav2.yaml            # Nav2 params for AMR-2 (scout, higher speed/accel)
        │   ├── fleet_params.yaml          # Scaling parameters for 10+ fleet deployment
        │   └── rviz_config.rviz           # Multi-robot RViz setup
        │
        ├── launch/
        │   ├── warehouse_sim.launch.py    # Main orchestration entrypoint
        │   ├── spawn_robot.launch.py      # Modular spawn description for any AMR instance
        │   ├── navigation.launch.py       # Namespaced Nav2 stack launcher
        │   └── slam_fusion.launch.py      # SLAM and map-merge pipelines
        │
        ├── maps/
        │   └── warehouse_world.yaml
        │
        ├── models/
        │   ├── amr_1/                     # Mesh resources for AMR-1
        │   └── amr_2/                     # Mesh resources for AMR-2
        │
        ├── warehouse_nav/                 # Python package root for custom nodes
        │   ├── __init__.py
        │   ├── bsp_validation_node.py     # BSP IMU data integrity verification
        │   ├── safety_override_node.py    # Real-time d_safe threshold & halt node
        │   ├── selective_mapping_node.py  # AMR-1 map update throttling & frontier prioritization
        │   ├── motion_smoother_node.py    # Payload-aware acceleration & jerk limiter
        │   └── traffic_controller_node.py # Conflict-aware MAPF trajectory interceptor
        │
        ├── urdf/
        │   ├── common_properties.xacro    # Inertial macros and material colors
        │   ├── amr_1.urdf.xacro           # Heavy mapper robot description
        │   └── amr_2.urdf.xacro           # Light scout robot description
        │
        └── worlds/
            └── warehouse_ramps.world      # Gazebo world with ramps, aisles, dynamic actors


```text
System Architecture Pipeline
[ Dynamic Obstacles / Ramps ]                                                                                                               |
             │
      ┌──────┴──────┐                                                                                                                            
      │ Gazebo Sim  │
      └──────┬──────┘
             │ (LiDAR / IMU Raw Data)
             ▼
   ┌───────────────────┐
   │  BSP Validation   │ ──(Exceeds limit?)──► Log Warnings
   └─────────┬─────────┘
             │ (Validated Sensor Data)
             ├─────────────────────────────────────────┐
             ▼                                         ▼
┌─────────────────────────┐               ┌────────────────────────┐
│ Cooperative SLAM        │               │ Safety Override Node   │
│ (Selective Map Fuser)   │               │ Checks d_safe threshold│
└────────────┬────────────┘               └───────────┬────────────┘
             │                                        │
             ▼                                        │ (High-Priority Stop)
┌─────────────────────────┐                           │
│ Nav2 Global Planner     │                           │
│ (Ramp Cost Layer)       │                           │
└────────────┬────────────┘                           │
             │                                        │
             ▼                                        │
┌─────────────────────────┐                           │
│ Conflict / Traffic Node │                           │
│ (MAPF Trajectory Yield) │                           │
└────────────┬────────────┘                           │
             │                                        │
             ▼                                        │
┌─────────────────────────┐                           │
│ Smooth Local Controller │                           │
│ (Payload Cap Limits)    │                           │
└────────────┬────────────┘                           │
             │                                        │
             ▼                                        ▼
    ┌─────────────────────────────────────────────────────┐
    │                      Twist Mux                      │
    └──────────────────────────┬──────────────────────────┘
                               │
                               ▼
                   [ /amr_X/cmd_vel (Robot) ]












