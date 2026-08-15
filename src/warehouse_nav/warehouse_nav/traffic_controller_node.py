#!/usr/bin/env python3
"""
Conflict-Aware MAPF Traffic Controller Node.
Monitors multi-robot positions, manages intersection zone reservations, 
and issues yield/stop signals to prevent deadlocks in narrow corridors.
"""

import math
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool

class TrafficControllerNode(Node):
    def __init__(self):
        super().__init__('traffic_controller_node')

        # Conflict Zone Threshold
        self.declare_parameter('conflict_distance_threshold', 1.2) # meters
        self.threshold = self.get_parameter('conflict_distance_threshold').value

        self.positions = {}

        # Fleet Subscriptions
        self.create_subscription(Odometry, '/amr_1/odom', lambda msg: self.odom_cb('amr_1', msg), 10)
        self.create_subscription(Odometry, '/amr_2/odom', lambda msg: self.odom_cb('amr_2', msg), 10)

        # Priority Signal Publishers (Yield triggers)
        self.pub_yield_amr1 = self.create_publisher(Bool, '/amr_1/yield_flag', 10)
        self.pub_yield_amr2 = self.create_publisher(Bool, '/amr_2/yield_flag', 10)

        self.timer = self.create_timer(0.2, self.evaluate_traffic)
        self.get_logger().info("Conflict-Aware MAPF Traffic Controller active.")

    def odom_cb(self, robot_id, msg: Odometry):
        self.positions[robot_id] = (
            msg.pose.pose.position.x,
            msg.pose.pose.position.y
        )

    def evaluate_traffic(self):
        if 'amr_1' not in self.positions or 'amr_2' not in self.positions:
            return

        p1 = self.positions['amr_1']
        p2 = self.positions['amr_2']
        dist = math.hypot(p1[0] - p2[0], p1[1] - p2[1])

        yield_1 = Bool()
        yield_2 = Bool()

        if dist < self.threshold:
            # Priority rule: Lower priority vehicle (amr_2) yields to higher priority (amr_1)
            self.get_logger().warn(
                f"Conflict detected! Distance: {dist:.2f}m. Ordering AMR-2 to yield.", 
                throttle_duration_sec=2.0
            )
            yield_1.data = False
            yield_2.data = True
        else:
            yield_1.data = False
            yield_2.data = False

        self.pub_yield_amr1.publish(yield_1)
        self.pub_yield_amr2.publish(yield_2)


def main(args=None):
    rclpy.init(args=args)
    node = TrafficControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()