from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    controller_node = Node(
        package='task1_quadrotor',
        executable='controller',
        name='quadrotor_controller',
        output='screen',
        emulate_tty=True,
    )

    command_sender_ui_node = Node(
        package='task1_quadrotor',
        executable='command_sender_ui',
        name='command_sender_ui',
        output='screen',
        emulate_tty=True
    )

    return LaunchDescription([
        controller_node,
        command_sender_ui_node
    ])