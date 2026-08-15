#!/usr/bin/env python3
"""
Selective Map Update Throttler Node.
Subscribes to raw slam_toolbox /map streams and throttles publish frequency 
to conserve multi-robot ROS 2 network bandwidth.
"""

import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid

class MapThrottlerNode(Node):
    def __init__(self):
        super().__init__('map_throttler_node')

        # Parameters
        self.declare_parameter('update_interval_sec', 2.0)
        self.declare_parameter('input_map_topic', 'map')
        self.declare_parameter('throttled_map_topic', 'map_throttled')

        self.interval = self.get_parameter('update_interval_sec').get_parameter_value().double_value
        in_topic = self.get_parameter('input_map_topic').get_parameter_value().string_value
        out_topic = self.get_parameter('throttled_map_topic').get_parameter_value().string_value

        self.latest_map = None
        self.last_published_time = self.get_clock().now()

        # Subscription & Publisher
        self.subscription = self.create_subscription(OccupancyGrid, in_topic, self.map_callback, 10)
        self.publisher = self.create_publisher(OccupancyGrid, out_topic, 10)

        # Timer for controlled throttling rate
        self.timer = self.create_timer(self.interval, self.timer_callback)

        self.get_logger().info(
            f"Map Throttler Active: '{in_topic}' -> '{out_topic}' at {self.interval}s interval."
        )

    def map_callback(self, msg: OccupancyGrid):
        self.latest_map = msg

    def timer_callback(self):
        if self.latest_map is not None:
            self.publisher.publish(self.latest_map)


def main(args=None):
    rclpy.init(args=args)
    node = MapThrottlerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()