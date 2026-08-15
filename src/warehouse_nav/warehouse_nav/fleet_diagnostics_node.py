#!/usr/bin/env python3
"""
System Diagnostics & Health Check Node.
Monitors topic health across /amr_1 and /amr_2 namespaces, checking for map updates,
odometry telemetry, and safety node Heartbeats.
"""

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry, OccupancyGrid
from std_msgs.msg import Bool

class FleetDiagnosticsNode(Node):
    def __init__(self):
        super().__init__('fleet_diagnostics')
        
        self.heartbeats = {
            'amr_1_odom': False,
            'amr_2_odom': False,
            'amr_1_safety': False,
            'amr_2_safety': False,
            'global_map': False
        }

        # Dynamic Subscriptions for Diagnostics
        self.create_subscription(Odometry, '/amr_1/odom', lambda msg: self.mark_alive('amr_1_odom'), 10)
        self.create_subscription(Odometry, '/amr_2/odom', lambda msg: self.mark_alive('amr_2_odom'), 10)
        self.create_subscription(Bool, '/amr_1/safety_override', lambda msg: self.mark_alive('amr_1_safety'), 10)
        self.create_subscription(Bool, '/amr_2/safety_override', lambda msg: self.mark_alive('amr_2_safety'), 10)
        self.create_subscription(OccupancyGrid, '/map_throttled', lambda msg: self.mark_alive('global_map'), 10)

        self.timer = self.create_timer(5.0, self.report_health)
        self.get_logger().info("Fleet Diagnostics Monitor initialized.")

    def mark_alive(self, key):
        self.heartbeats[key] = True

    def report_health(self):
        self.get_logger().info("=== FLEET SYSTEM HEALTH REPORT ===")
        all_passed = True
        for subsystem, active in self.heartbeats.items():
            status = "OK" if active else "OFFLINE/WAITING"
            if not active:
                all_passed = False
            self.get_logger().info(f"  [{subsystem}]: {status}")
            self.heartbeats[subsystem] = False

        if all_passed:
            self.get_logger().info("Status: ALL SYSTEMS OPERATIONAL")
        else:
            self.get_logger().warn("Status: DEGRADED PERFORMANCE / WAITING FOR TOPICS")
        self.get_logger().info("==================================")


def main(args=None):
    rclpy.init(args=args)
    node = FleetDiagnosticsNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()