#!/usr/bin/env python3
"""
Board Support Package (BSP) IMU Validation Routine.
Filters and validates raw IMU angular velocity telemetry against physically plausible thresholds.
"""

import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu

class BSPIMUValidationNode(Node):
    def __init__(self):
        super().__init__('bsp_validation_node')

        # Parameters
        self.declare_parameter('max_angular_velocity', 5.0)  # rad/s threshold limit
        self.declare_parameter('imu_raw_topic', 'imu/data')
        self.declare_parameter('imu_validated_topic', 'imu/data_validated')

        self.max_ang_vel = self.get_parameter('max_angular_velocity').get_parameter_value().double_value
        raw_topic = self.get_parameter('imu_raw_topic').get_parameter_value().string_value
        val_topic = self.get_parameter('imu_validated_topic').get_parameter_value().string_value

        # Subscription & Publisher
        self.subscription = self.create_subscription(
            Imu,
            raw_topic,
            self.imu_callback,
            10
        )
        self.publisher = self.create_publisher(Imu, val_topic, 10)

        self.get_logger().info(
            f"BSP Validation Active. Monitoring '{raw_topic}' -> Threshold: {self.max_ang_vel} rad/s"
        )

    def imu_callback(self, msg: Imu):
        # Calculate magnitude of 3-axis angular velocity
        gx, gy, gz = msg.angular_velocity.x, msg.angular_velocity.y, msg.angular_velocity.z
        ang_vel_mag = math.sqrt(gx**2 + gy**2 + gz**2)

        if ang_vel_mag > self.max_ang_vel:
            self.get_logger().warn(
                f"[BSP ANOMALY DETECTED] Angular velocity spike: {ang_vel_mag:.2f} rad/s "
                f"exceeds max plausible limit ({self.max_ang_vel:.2f} rad/s). Dropping corrupt frame!"
            )
            return  # Reject corrupt data packet

        # Publish validated IMU message downstream
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = BSPIMUValidationNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()