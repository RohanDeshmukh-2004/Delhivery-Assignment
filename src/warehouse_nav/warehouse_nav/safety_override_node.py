#!/usr/bin/env python3
"""
Low-Latency Speed-Dependent Emergency Safety Override Node.
Calculates d_safe = k * v^2 + d_min.
Overrides navigation/teleop commands with a hard halt when safety boundaries are violated.
"""

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry

class SafetyOverrideNode(Node):
    def __init__(self):
        super().__init__('safety_override_node')

        # Safety Parameters
        self.declare_parameter('k_factor', 0.5)      # Speed coefficient
        self.declare_parameter('d_min', 0.4)         # Minimum absolute buffer distance (meters)
        self.declare_parameter('scan_angle_deg', 45.0) # Forward evaluation cone (+/- deg)

        self.k = self.get_parameter('k_factor').get_parameter_value().double_value
        self.d_min = self.get_parameter('d_min').get_parameter_value().double_value
        self.fov = math.radians(self.get_parameter('scan_angle_deg').get_parameter_value().double_value)

        self.current_speed = 0.0
        self.is_emergency_halt = False

        # Subscriptions
        self.sub_odom = self.create_subscription(Odometry, 'odom', self.odom_callback, 10)
        self.sub_scan = self.create_subscription(LaserScan, 'scan', self.scan_callback, 10)
        self.sub_nav_cmd = self.create_subscription(Twist, 'cmd_vel_nav', self.cmd_nav_callback, 10)

        # High-Priority Velocity Output to Motor Driver
        self.pub_cmd_vel = self.create_publisher(Twist, 'cmd_vel', 10)

        self.get_logger().info(
            f"Safety Override Node Active. Configured d_min={self.d_min}m, k={self.k}"
        )

    def odom_callback(self, msg: Odometry):
        # Update current speed state magnitude
        vx = msg.twist.twist.linear.x
        vy = msg.twist.twist.linear.y
        self.current_speed = math.sqrt(vx**2 + vy**2)

    def scan_callback(self, msg: LaserScan):
        # Calculate dynamic threshold: d_safe = k * v^2 + d_min
        d_safe = (self.k * (self.current_speed ** 2)) + self.d_min

        # Evaluate min obstacle distance within forward angular cone
        min_distance = float('inf')
        angle = msg.angle_min

        for r in msg.ranges:
            if -self.fov <= angle <= self.fov:
                if not math.isnan(r) and not math.isinf(r) and r > msg.range_min:
                    if r < min_distance:
                        min_distance = r
            angle += msg.angle_increment

        # Trigger override condition
        if min_distance < d_safe:
            if not self.is_emergency_halt:
                self.get_logger().error(
                    f"[EMERGENCY HALT OVERRIDE] Obstacle detected at {min_distance:.2f}m! "
                    f"Violates d_safe={d_safe:.2f}m (v={self.current_speed:.2f}m/s). Issuing Hard Stop."
                )
            self.is_emergency_halt = True
            self.issue_hard_stop()
        else:
            if self.is_emergency_halt:
                self.get_logger().info("[SAFETY CLEAR] Obstacle cleared safe margin. Restoring trajectory control.")
            self.is_emergency_halt = False

    def cmd_nav_callback(self, msg: Twist):
        # Forward navigation command ONLY if safety check passes
        if not self.is_emergency_halt:
            self.pub_cmd_vel.publish(msg)
        else:
            self.issue_hard_stop()

    def issue_hard_stop(self):
        stop_msg = Twist()
        stop_msg.linear.x = 0.0
        stop_msg.linear.y = 0.0
        stop_msg.angular.z = 0.0
        self.pub_cmd_vel.publish(stop_msg)


def main(args=None):
    rclpy.init(args=args)
    node = SafetyOverrideNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()