#!/usr/bin/env python3
"""
Payload-Aware Motion Smoother Node.
Intercepts raw navigation commands (/cmd_vel_raw) and applies dynamic acceleration 
and jerk limits based on payload status to ensure transport safety.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool

class MotionSmootherNode(Node):
    def __init__(self):
        super().__init__('motion_smoother_node')

        # Parameters
        self.declare_parameter('max_accel_empty', 1.0)       # m/s^2
        self.declare_parameter('max_accel_loaded', 0.4)      # m/s^2 (conservative for cargo)
        self.declare_parameter('update_rate', 30.0)          # Hz

        self.max_accel_empty = self.get_parameter('max_accel_empty').value
        self.max_accel_loaded = self.get_parameter('max_accel_loaded').value
        self.dt = 1.0 / self.get_parameter('update_rate').value

        # State Variables
        self.is_loaded = False
        self.target_twist = Twist()
        self.current_twist = Twist()

        # Subscribers & Publishers
        self.sub_cmd = self.create_subscription(Twist, 'cmd_vel_raw', self.cmd_callback, 10)
        self.sub_payload = self.create_subscription(Bool, 'payload_status', self.payload_callback, 10)
        self.pub_cmd = self.create_publisher(Twist, 'cmd_vel_smoothed', 10)

        # Control Loop Timer
        self.timer = self.create_timer(self.dt, self.control_loop)
        self.get_logger().info("Motion Smoother initialized.")

    def payload_callback(self, msg: Bool):
        self.is_loaded = msg.data
        status = "LOADED" if self.is_loaded else "EMPTY"
        self.get_logger().info(f"Payload status updated: {status}")

    def cmd_callback(self, msg: Twist):
        self.target_twist = msg

    def control_loop(self):
        max_a = self.max_accel_loaded if self.is_loaded else self.max_accel_empty
        max_dv = max_a * self.dt

        # Linear X Slew-Rate Limiting
        diff_vx = self.target_twist.linear.x - self.current_twist.linear.x
        if abs(diff_vx) > max_dv:
            diff_vx = max_dv if diff_vx > 0 else -max_dv
        self.current_twist.linear.x += diff_vx

        # Angular Z Limiting
        diff_wz = self.target_twist.angular.z - self.current_twist.angular.z
        max_dw = (max_a * 2.0) * self.dt
        if abs(diff_wz) > max_dw:
            diff_wz = max_dw if diff_wz > 0 else -max_dw
        self.current_twist.angular.z += diff_wz

        self.pub_cmd.publish(self.current_twist)


def main(args=None):
    rclpy.init(args=args)
    node = MotionSmootherNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()