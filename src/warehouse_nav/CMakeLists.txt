cmake_minimum_required(VERSION 3.8)
project(warehouse_nav)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rviz2 REQUIRED)
find_package(gazebo_ros REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(nav_msgs REQUIRED)

# Install resource directories
install(
  DIRECTORY launch urdf worlds config models
  DESTINATION share/${PROJECT_NAME}
)

# Install executable Python scripts
install(
  PROGRAMS
    warehouse_nav/__init__.py
    warehouse_nav/bsp_validation_node.py
    warehouse_nav/safety_override_node.py
    warehouse_nav/map_throttler_node.py
    warehouse_nav/motion_smoother_node.py
    warehouse_nav/traffic_controller_node.py
    warehouse_nav/fleet_diagnostics_node.py
  DESTINATION lib/${PROJECT_NAME}
)
 
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
