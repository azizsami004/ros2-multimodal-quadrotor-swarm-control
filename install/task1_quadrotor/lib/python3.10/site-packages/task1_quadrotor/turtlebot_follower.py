import math

import rclpy
from rclpy.node import Node
from rclpy.time import Time

from geometry_msgs.msg import Twist

from tf2_ros import (
    Buffer,
    TransformException,
    TransformListener
)


class TurtleBotFollower(Node):

    def __init__(self):
        super().__init__('turtlebot_follower')

        # ---------------------------------------------
        # TF2
        # ---------------------------------------------

        self.tf_buffer = Buffer()

        self.tf_listener = TransformListener(
            self.tf_buffer,
            self
        )

        # ---------------------------------------------
        # TurtleBot velocity publisher
        # ---------------------------------------------

        self.cmd_vel_publisher = self.create_publisher(
            Twist,
            '/tb3/cmd_vel',
            10
        )

        # ---------------------------------------------
        # Controller settings
        # ---------------------------------------------

        # TurtleBot should stop this far from the drone.
        self.desired_distance = 1.0

        # Proportional controller gains.
        self.linear_gain = 0.4
        self.angular_gain = 1.0

        # Maximum speeds.
        self.max_linear_speed = 0.15
        self.max_angular_speed = 0.8

        # If the drone is more than this angle away,
        # rotate first instead of moving forward.
        self.turning_angle_threshold = 0.35

        # Run the follower controller at 10 Hz.
        self.timer = self.create_timer(
            0.1,
            self.follow_drone
        )

        self.get_logger().info(
            'TurtleBot follower started'
        )


    # =====================================================
    # FOLLOW DRONE
    # =====================================================

    def follow_drone(self):

        try:

            # Find X3 relative to TurtleBot3.
            transform = self.tf_buffer.lookup_transform(
                'tb3/base_footprint',
                'X3/base_link',
                Time()
            )

        except TransformException:
            # If TF is unavailable, stop for safety.
            self.stop_robot()
            return


        # -------------------------------------------------
        # Relative drone position in TurtleBot frame
        # -------------------------------------------------

        relative_x = (
            transform.transform.translation.x
        )

        relative_y = (
            transform.transform.translation.y
        )

        # Ignore Z because TurtleBot cannot move vertically.


        # -------------------------------------------------
        # Horizontal distance to drone
        # -------------------------------------------------

        distance = math.sqrt(
            relative_x ** 2
            +
            relative_y ** 2
        )


        # -------------------------------------------------
        # Direction to drone
        # -------------------------------------------------

        angle_to_drone = math.atan2(
            relative_y,
            relative_x
        )


        # -------------------------------------------------
        # Create velocity command
        # -------------------------------------------------

        cmd = Twist()


        # =================================================
        # CASE 1:
        # TurtleBot is already close enough
        # =================================================

        if distance <= self.desired_distance:

            cmd.linear.x = 0.0
            cmd.angular.z = 0.0


        # =================================================
        # CASE 2:
        # Drone is far to the left or right
        #
        # Rotate toward drone first.
        # =================================================

        elif abs(angle_to_drone) > (
            self.turning_angle_threshold
        ):

            cmd.linear.x = 0.0

            cmd.angular.z = (
                self.angular_gain
                *
                angle_to_drone
            )


        # =================================================
        # CASE 3:
        # TurtleBot roughly faces the drone
        #
        # Move forward and correct heading.
        # =================================================

        else:

            distance_error = (
                distance
                -
                self.desired_distance
            )

            cmd.linear.x = (
                self.linear_gain
                *
                distance_error
            )

            cmd.angular.z = (
                self.angular_gain
                *
                angle_to_drone
            )


        # -------------------------------------------------
        # Limit the linear speed
        # -------------------------------------------------

        cmd.linear.x = max(
            -self.max_linear_speed,
            min(
                self.max_linear_speed,
                cmd.linear.x
            )
        )


        # -------------------------------------------------
        # Limit the angular speed
        # -------------------------------------------------

        cmd.angular.z = max(
            -self.max_angular_speed,
            min(
                self.max_angular_speed,
                cmd.angular.z
            )
        )


        # -------------------------------------------------
        # Publish command
        # -------------------------------------------------

        self.cmd_vel_publisher.publish(cmd)


    # =====================================================
    # STOP TURTLEBOT
    # =====================================================

    def stop_robot(self):

        cmd = Twist()

        cmd.linear.x = 0.0
        cmd.angular.z = 0.0

        self.cmd_vel_publisher.publish(cmd)


# =========================================================
# MAIN
# =========================================================

def main(args=None):

    rclpy.init(args=args)

    node = TurtleBotFollower()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:

        node.stop_robot()

        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()