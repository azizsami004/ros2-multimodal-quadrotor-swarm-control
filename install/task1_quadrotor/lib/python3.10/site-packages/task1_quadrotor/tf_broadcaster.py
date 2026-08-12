import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped

from tf2_ros import TransformBroadcaster

from tf2_ros import (
    TransformBroadcaster,
    StaticTransformBroadcaster
)


class RobotTFBroadcaster(Node):

    def __init__(self):
        super().__init__('robot_tf_broadcaster')

        # TF broadcaster
        self.tf_broadcaster = TransformBroadcaster(self)

        self.static_tf_broadcaster = StaticTransformBroadcaster(
            self
        )

        self.publish_static_transforms()

        # X3 odometry subscriber
        self.x3_sub = self.create_subscription(
            Odometry,
            '/model/X3/odometry',
            self.x3_odom_callback,
            10
        )

        # TurtleBot3 odometry subscriber
        self.tb3_sub = self.create_subscription(
            Odometry,
            '/tb3/odom',
            self.tb3_odom_callback,
            10
        )

        self.get_logger().info(
            'Robot TF Broadcaster started'
        )

    def publish_static_transforms(self):

    # ---------------------------------
    # world -> X3/odom
    # ---------------------------------
        x3_transform = TransformStamped()

        x3_transform.header.stamp = (
            self.get_clock().now().to_msg()
        )

        x3_transform.header.frame_id = 'world'
        x3_transform.child_frame_id = 'X3/odom'

        x3_transform.transform.translation.x = 0.0
        x3_transform.transform.translation.y = 0.0
        x3_transform.transform.translation.z = 0.0

        x3_transform.transform.rotation.x = 0.0
        x3_transform.transform.rotation.y = 0.0
        x3_transform.transform.rotation.z = 0.0
        x3_transform.transform.rotation.w = 1.0


        # ---------------------------------
        # world -> tb3/odom
        # ---------------------------------

        tb3_transform = TransformStamped()

        tb3_transform.header.stamp = (
            self.get_clock().now().to_msg()
        )

        tb3_transform.header.frame_id = 'world'
        tb3_transform.child_frame_id = 'tb3/odom'

        # Same XY position used when spawning TurtleBot.
        tb3_transform.transform.translation.x = -2.0
        tb3_transform.transform.translation.y = 0.0
        tb3_transform.transform.translation.z = 0.0

        tb3_transform.transform.rotation.x = 0.0
        tb3_transform.transform.rotation.y = 0.0
        tb3_transform.transform.rotation.z = 0.0
        tb3_transform.transform.rotation.w = 1.0


        self.static_tf_broadcaster.sendTransform([
            x3_transform,
            tb3_transform
        ])


    # ======================================================
    # X3 TRANSFORM
    # ======================================================

    def x3_odom_callback(self, msg):

        transform = TransformStamped()

        transform.header.stamp = (
            self.get_clock().now().to_msg()
        )

        transform.header.frame_id = 'X3/odom'
        transform.child_frame_id = 'X3/base_link'

        transform.transform.translation.x = (
            msg.pose.pose.position.x
        )
        transform.transform.translation.y = (
            msg.pose.pose.position.y
        )
        transform.transform.translation.z = (
            msg.pose.pose.position.z
        )

        transform.transform.rotation = (
            msg.pose.pose.orientation
        )

        self.tf_broadcaster.sendTransform(transform)


    # ======================================================
    # TURTLEBOT3 TRANSFORM
    # ======================================================

    def tb3_odom_callback(self, msg):

        transform = TransformStamped()

        transform.header.stamp = (
            self.get_clock().now().to_msg()
        )

        transform.header.frame_id = 'tb3/odom'
        transform.child_frame_id = 'tb3/base_footprint'

        transform.transform.translation.x = (
            msg.pose.pose.position.x
        )
        transform.transform.translation.y = (
            msg.pose.pose.position.y
        )
        transform.transform.translation.z = (
            msg.pose.pose.position.z
        )

        transform.transform.rotation = (
            msg.pose.pose.orientation
        )

        self.tf_broadcaster.sendTransform(transform)


def main(args=None):

    rclpy.init(args=args)

    node = RobotTFBroadcaster()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()