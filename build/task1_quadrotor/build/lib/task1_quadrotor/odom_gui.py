import sys
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

import math

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

class OdomReceiverNode(Node):
    def __init__(self):
        super().__init__('odom_receiver_ui')
        self.odom_received = False

        self.sub_ = self.create_subscription(Odometry, '/model/X3/odometry', self.clbk, 10)

        # Position
        self.pos_y = 0.0
        self.pos_z = 0.0
        self.pos_x = 0.0

        # Orientation quaternion
        self.orientaion_x = 0.0
        self.orientaion_y = 0.0
        self.orientaion_z = 0.0
        self.orientaion_w = 0.0

        # Linear velocity
        self.linear_velo_x = 0.0
        self.linear_velo_y = 0.0
        self.linear_velo_z = 0.0

        # Angular velocity
        self.angular_velo_x = 0.0
        self.angular_velo_y = 0.0
        self.angular_velo_z = 0.0

        self.get_logger().info('Odom Receiver Started')


    def clbk(self, msg):
        self.odom_received = True
        # Position
        self.pos_x = msg.pose.pose.position.x
        self.pos_y = msg.pose.pose.position.y
        self.pos_z = msg.pose.pose.position.z

        # Orientation quaternion
        self.orientaion_x = msg.pose.pose.orientation.x
        self.orientaion_y = msg.pose.pose.orientation.y
        self.orientaion_z = msg.pose.pose.orientation.z
        self.orientaion_w = msg.pose.pose.orientation.w

        self.roll, self.pitch, self.yaw = (
            self.quaternion_to_euler(self.orientaion_w, self.orientaion_x, self.orientaion_y, self.orientaion_z)
        )

        # Linear velocity
        self.linear_velo_x = msg.twist.twist.linear.x
        self.linear_velo_y = msg.twist.twist.linear.y
        self.linear_velo_z = msg.twist.twist.linear.z

        # Angular velocity
        self.angular_velo_x = msg.twist.twist.angular.x
        self.angular_velo_y = msg.twist.twist.angular.y
        self.angular_velo_z = msg.twist.twist.angular.z

        # self.get_logger().info(f'Position X: {self.pos_x} \n Position Y: {self.pos_y} \n Position Z: {self.pos_z}')


    def quaternion_to_euler(self, x, y, z, w):
    # Roll
        sin_roll_cos_pitch = 2.0 * (
            w * x + y * z
        )

        cos_roll_cos_pitch = 1.0 - 2.0 * (
            x * x + y * y
        )

        roll = math.atan2(
            sin_roll_cos_pitch,
            cos_roll_cos_pitch
        )

        # Pitch
        sin_pitch = 2.0 * (
            w * y - z * x
        )

        if abs(sin_pitch) >= 1:
            pitch = math.copysign(
                math.pi / 2,
                sin_pitch
            )
        else:
            pitch = math.asin(sin_pitch)

        # Yaw
        sin_yaw_cos_pitch = 2.0 * (
            w * z + x * y
        )

        cos_yaw_cos_pitch = 1.0 - 2.0 * (
            y * y + z * z
        )

        yaw = math.atan2(
            sin_yaw_cos_pitch,
            cos_yaw_cos_pitch
        )

        return roll, pitch, yaw



class MainWindow(QMainWindow):
    def __init__(self, ros_node):
        super().__init__()

        self.ros_node = ros_node

        self.setWindowTitle('Drone Telemetry')
        self.setFixedSize(480, 600)

        main_layout = QVBoxLayout()

        title_label = QLabel('X3 QUADROTOR TELEMETRY')

        title_label.setStyleSheet(
            """
            font-size: 20px;
            font-weight: bold;
            padding: 10px;
            """
        )
        self.telemetry_box = QPlainTextEdit()
        self.telemetry_box.setReadOnly(True)
        self.telemetry_box.setPlainText(
            'SYSTEM STATUS: WAITING FOR ODOMETRY'
        )

        self.telemetry_box.setStyleSheet(
            """
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #eeeeee;
                border: 2px solid #555555;
                border-radius: 6px;
                padding: 15px;
                font-family: monospace;
                font-size: 15px;               
            }
            """
        )

        main_layout.addWidget(title_label)
        main_layout.addWidget(self.telemetry_box)

        container = QWidget()
        container.setLayout(main_layout)

        self.setCentralWidget(container)

        self.display_timer = QTimer()

        self.display_timer.timeout.connect(self.update_display)
        self.display_timer.start(200)


    def update_display(self):
        if not self.ros_node.odom_received:
            self.telemetry_box.setPlainText(
                'SYSTEM STATUS: WAITING FOR ODOMETRY'
            )

            return

        roll_degrees = math.degrees(
            self.ros_node.roll
        )

        pitch_degrees = math.degrees(
            self.ros_node.pitch
        )

        yaw_degrees = math.degrees(
            self.ros_node.yaw
        )

        telemetry_text = (
            'SYSTEM STATUS: CONNECTED\n'
            '\n'
            'POSITION\n'
            '------------------------------\n'
            f'X: {self.ros_node.pos_x:8.3f} m\n'
            f'Y: {self.ros_node.pos_y:8.3f} m\n'
            f'Z: {self.ros_node.pos_z:8.3f} m\n'
            '\n'
            'ORIENTATION\n'
            '------------------------------\n'
            f'Roll:  {roll_degrees:8.2f}°\n'
            f'Pitch: {pitch_degrees:8.2f}°\n'
            f'Yaw:   {yaw_degrees:8.2f}°\n'
            '\n'
            'LINEAR VELOCITY\n'
            '------------------------------\n'
            f'X: {self.ros_node.linear_velo_x:8.3f} m/s\n'
            f'Y: {self.ros_node.linear_velo_y:8.3f} m/s\n'
            f'Z: {self.ros_node.linear_velo_z:8.3f} m/s\n'
            '\n'
            'ANGULAR VELOCITY\n'
            '------------------------------\n'
            f'X: {self.ros_node.angular_velo_x:8.3f} rad/s\n'
            f'Y: {self.ros_node.angular_velo_y:8.3f} rad/s\n'
            f'Z: {self.ros_node.angular_velo_z:8.3f} rad/s'
        )

        self.telemetry_box.setPlainText(
            telemetry_text
        )



def main(args=None):
    rclpy.init(args=args)

    node = OdomReceiverNode()

    app = QApplication([])

    window = MainWindow(node)
    window.show()

    ros_timer = QTimer()

    ros_timer.timeout.connect(
        lambda: rclpy.spin_once(
            node,
            timeout_sec=0.0
        )
    )

    ros_timer.start(20)

    try:
        app.exec()

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
