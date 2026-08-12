import sys

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from task1_quadrotor.voice_controller import VoiceController


# ==========================================================
# ROS 2 NODE
# ==========================================================

class CommandSenderNode(Node):

    def __init__(self):
        super().__init__('command_sender_ui')

        self.publisher = self.create_publisher(
            Twist,
            'command_sender',
            10
        )

        self.get_logger().info('Command sender UI started')


    def publish_command(self, linear_x=0.0, linear_z=0.0, angular_z=0.0):
        message = Twist()

        message.linear.x = linear_x
        message.linear.z = linear_z
        message.angular.z = angular_z

        self.publisher.publish(message)


# ==========================================================
# PYQT6 MAIN WINDOW
# ==========================================================

class MainWindow(QMainWindow):

    def __init__(self, ros_node):
        super().__init__()

        self.ros_node = ros_node

        self.voice_thread = None
        self.voice_controller = None

        self.setWindowTitle('Quadrotor Controller')
        self.setFixedSize(600, 450)

        # The main vertical layout contains:
        #
        # 1. Button / Voice selector
        # 2. The selected control page

        main_layout = QVBoxLayout()

        # --------------------------------------------------
        # MODE SELECTION BUTTONS
        # --------------------------------------------------

        mode_layout = QHBoxLayout()

        self.button_mode_button = QPushButton('BUTTON')
        self.voice_mode_button = QPushButton('VOICE')

        self.button_mode_button.setCheckable(True)
        self.voice_mode_button.setCheckable(True)

        self.button_mode_button.setChecked(True)

        self.button_mode_button.setFixedSize(150, 50)
        self.voice_mode_button.setFixedSize(150, 50)

        self.button_mode_button.clicked.connect(
            self.show_button_page
        )

        self.voice_mode_button.clicked.connect(
            self.show_voice_page
        )

        mode_layout.addStretch()
        mode_layout.addWidget(self.button_mode_button)
        mode_layout.addWidget(self.voice_mode_button)
        mode_layout.addStretch()

        main_layout.addLayout(mode_layout)

        # --------------------------------------------------
        # STACKED LAYOUT
        # --------------------------------------------------

        self.stack_layout = QStackedLayout()

        self.button_page = self.create_button_page()
        self.voice_page = self.create_voice_page()

        self.stack_layout.addWidget(self.button_page)
        self.stack_layout.addWidget(self.voice_page)

        # Page 0 is the button-control page.
        self.stack_layout.setCurrentIndex(0)

        main_layout.addLayout(self.stack_layout)

        # --------------------------------------------------
        # CENTRAL WIDGET
        # --------------------------------------------------

        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        self.setCentralWidget(central_widget)


    # ======================================================
    # BUTTON-CONTROL PAGE
    # ======================================================

    def create_button_page(self):
        page = QWidget()

        page_layout = QHBoxLayout()

        # Left side:
        # forward, backward, left, right and stop.

        direction_layout = QGridLayout()

        self.forward_button = QPushButton('FORWARD\n▲')
        self.backward_button = QPushButton('BACKWARD\n▼')
        self.left_button = QPushButton('LEFT\n◀')
        self.right_button = QPushButton('RIGHT\n▶')
        self.stop_button = QPushButton('STOP')

        self.forward_button.setFixedSize(110, 65)
        self.backward_button.setFixedSize(110, 65)
        self.left_button.setFixedSize(110, 65)
        self.right_button.setFixedSize(110, 65)
        self.stop_button.setFixedSize(110, 65)

        direction_layout.addWidget(
            self.forward_button,
            0,
            1
        )

        direction_layout.addWidget(
            self.left_button,
            1,
            0
        )

        direction_layout.addWidget(
            self.stop_button,
            1,
            1
        )

        direction_layout.addWidget(
            self.right_button,
            1,
            2
        )

        direction_layout.addWidget(
            self.backward_button,
            2,
            1
        )

        # Right side:
        # altitude controls.

        altitude_layout = QVBoxLayout()

        self.up_button = QPushButton('UP\n↑')
        self.down_button = QPushButton('DOWN\n↓')

        self.up_button.setFixedSize(110, 65)
        self.down_button.setFixedSize(110, 65)

        altitude_layout.addStretch()
        altitude_layout.addWidget(self.up_button)
        altitude_layout.addSpacing(60)
        altitude_layout.addWidget(self.down_button)
        altitude_layout.addStretch()

        page_layout.addLayout(direction_layout)
        page_layout.addSpacing(40)
        page_layout.addLayout(altitude_layout)

        page.setLayout(page_layout)

        # --------------------------------------------------
        # CONNECT BUTTON SIGNALS TO METHODS
        # --------------------------------------------------

        self.forward_button.pressed.connect(
            self.move_forward
        )

        self.forward_button.released.connect(
            self.stop_drone
        )

        self.backward_button.pressed.connect(
            self.move_backward
        )

        self.backward_button.released.connect(
            self.stop_drone
        )

        self.left_button.pressed.connect(
            self.turn_left
        )

        self.left_button.released.connect(
            self.stop_drone
        )

        self.right_button.pressed.connect(
            self.turn_right
        )

        self.right_button.released.connect(
            self.stop_drone
        )

        self.up_button.pressed.connect(
            self.move_up
        )

        self.up_button.released.connect(
            self.stop_drone
        )

        self.down_button.pressed.connect(
            self.move_down
        )

        self.down_button.released.connect(
            self.stop_drone
        )

        self.stop_button.clicked.connect(
            self.stop_drone
        )

        return page


    # ======================================================
    # VOICE PAGE
    # ======================================================

    def create_voice_page(self):
        page = QWidget()

        voice_layout = QVBoxLayout()

        self.microphone_label = QLabel('🎤')
        self.microphone_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.microphone_label.setStyleSheet(
            'font-size: 100px;'
        )

        self.voice_status_label = QLabel(
            'Microphone off (Click to Toogle)'
        )

        self.voice_status_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.voice_status_label.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            """
        )

        self.recognized_text_label = QLabel(
            'Recognized text will appear here'
        )

        self.recognized_text_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.microphone_button = QPushButton(
            'MICROPHONE OFF'
        )

        self.microphone_button.setCheckable(True)
        self.microphone_button.setFixedSize(180, 55)

        self.microphone_button.toggled.connect(
            self.toggle_microphone
        )

        self.microphone_button.setStyleSheet(
            """
            QPushButton {
                background-color: #d9534f;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }

            QPushButton:checked {
                background-color: #2ecc71;
            }
            """
        )

        voice_layout.addStretch()
        voice_layout.addWidget(self.microphone_label)
        voice_layout.addWidget(self.voice_status_label)
        voice_layout.addWidget(self.recognized_text_label)
        voice_layout.addSpacing(20)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.microphone_button)
        button_layout.addStretch()

        voice_layout.addLayout(button_layout)
        voice_layout.addStretch()

        page.setLayout(voice_layout)

        return page

    def toggle_microphone(self, checked):
        if checked:
            self.start_voice_control()

        else:
            self.stop_voice_control()

    def start_voice_control(self):
        if (
            self.voice_thread is not None
            and self.voice_thread.isRunning()
        ):
            return

        self.microphone_button.setText(
            'MICROPHONE ON'
        )

        self.voice_status_label.setText(
            'Starting microphone...'
        )

        self.recognized_text_label.setText(
            'Waiting for voice command...'
        )

        # Create the thread.
        self.voice_thread = QThread(self)

        # Create the voice controller.
        self.voice_controller = VoiceController()

        # Move voice processing away from the GUI thread.
        self.voice_controller.moveToThread(
            self.voice_thread
        )

        # Start listening when the thread starts.
        self.voice_thread.started.connect(
            self.voice_controller.start_listening
        )

        # Receive information from VoiceController.
        self.voice_controller.status_changed.connect(
            self.update_voice_status
        )

        self.voice_controller.text_recognized.connect(
            self.show_recognized_text
        )

        self.voice_controller.command_recognized.connect(
            self.process_voice_command
        )

        self.voice_controller.error_occurred.connect(
            self.show_voice_error
        )

        # Stop the QThread when recognition ends.
        self.voice_controller.finished.connect(
            self.voice_thread.quit
        )

        self.voice_controller.finished.connect(
            self.voice_controller.deleteLater
        )

        self.voice_thread.finished.connect(
            self.voice_thread.deleteLater
        )

        self.voice_thread.finished.connect(
            self.voice_thread_finished
        )

        self.voice_thread.start()

    def stop_voice_control(self):
        self.microphone_button.setText(
            'MICROPHONE OFF'
        )

        self.voice_status_label.setText(
            'Stopping microphone...'
        )

        if self.voice_controller is not None:
            self.voice_controller.stop_listening()

        # Safety: stop the drone when the microphone is disabled.
        self.stop_drone()

    def update_voice_status(self, status):
        self.voice_status_label.setText(status)

    def show_recognized_text(self, text):
        self.recognized_text_label.setText(
            f'Heard: {text}'
        )

    def process_voice_command(self, command):
    # Ignore a late command if voice mode has already
    # been switched off.
        if not self.microphone_button.isChecked():
            return

        self.recognized_text_label.setText(
            f'Command: {command.upper()}'
        )

        if command == 'forward':
            self.move_forward()

        elif command == 'backward':
            self.move_backward()

        elif command == 'left':
            self.turn_left()

        elif command == 'right':
            self.turn_right()

        elif command == 'up':
            self.move_up()

        elif command == 'down':
            self.move_down()

        elif command == 'stop':
            self.stop_drone()

    def show_voice_error(self, error_message):
        self.voice_status_label.setText(
            'Voice-control error'
        )

        self.recognized_text_label.setText(
            error_message
        )

        self.stop_drone()

        # Change the button state without calling the
        # toggled handler a second time.
        self.microphone_button.blockSignals(True)
        self.microphone_button.setChecked(False)
        self.microphone_button.setText(
            'MICROPHONE OFF'
        )
        self.microphone_button.blockSignals(False)

    def voice_thread_finished(self):
        self.voice_thread = None
        self.voice_controller = None

        self.microphone_button.blockSignals(True)
        self.microphone_button.setChecked(False)
        self.microphone_button.setText(
            'MICROPHONE OFF'
        )
        self.microphone_button.blockSignals(False)

        self.voice_status_label.setText(
            'Microphone off'
        )

    # ======================================================
    # PAGE-SWITCHING METHODS
    # ======================================================

    def show_button_page(self):
        self.stop_drone()

        if self.microphone_button.isChecked():
            self.microphone_button.setChecked(False)

        self.stack_layout.setCurrentIndex(0)

        self.button_mode_button.setChecked(True)
        self.voice_mode_button.setChecked(False)

        self.ros_node.get_logger().info(
            'Button mode selected'
        )


    def show_voice_page(self):
        self.stop_drone()

        self.stack_layout.setCurrentIndex(1)

        self.button_mode_button.setChecked(False)
        self.voice_mode_button.setChecked(True)

        self.ros_node.get_logger().info(
            'Voice mode selected'
        )


    # ======================================================
    # MOVEMENT METHODS
    # ======================================================

    def move_forward(self):
        self.ros_node.publish_command(
            linear_x=1.0
        )


    def move_backward(self):
        self.ros_node.publish_command(
            linear_x=-1.0
        )


    def turn_left(self):
        self.ros_node.publish_command(
            angular_z=0.5
        )


    def turn_right(self):
        self.ros_node.publish_command(
            angular_z=-0.5
        )


    def move_up(self):
        self.ros_node.publish_command(
            linear_z=1.0
        )


    def move_down(self):
        self.ros_node.publish_command(
            linear_z=-1.0
        )


    def stop_drone(self):
        self.ros_node.publish_command()


    # ======================================================
    # WINDOW-CLOSING EVENT
    # ======================================================

    def closeEvent(self, event):
        self.stop_drone()

        if self.microphone_button.isChecked():
            self.microphone_button.setChecked(False)

        if (
            self.voice_thread is not None
            and self.voice_thread.isRunning()
        ):
            self.voice_thread.wait()

        event.accept()


# ==========================================================
# MAIN FUNCTION
# ==========================================================

def main(args=None):
    rclpy.init(args=args)

    ros_node = CommandSenderNode()

    # We are not using Qt command-line arguments,
    # so an empty list is enough.
    app = QApplication([])

    window = MainWindow(ros_node)
    window.show()

    app.exec()

    ros_node.publish_command()
    ros_node.destroy_node()

    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()