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
        emulate_tty=True,
    )

    odom_gui_node = Node(
        package='task1_quadrotor',
        executable='odom_gui',
        name='odom_gui',
        output='screen',
        emulate_tty=True,
    )

    tf_broadcaster_node = Node(
        package='task1_quadrotor',
        executable='tf_broadcaster',
        name='robot_tf_broadcaster',
        output='screen',
        emulate_tty=True,
    )

    turtlebot_follower_node = Node(
        package='task1_quadrotor',
        executable='turtlebot_follower',
        name='turtlebot_follower',
        output='screen',
        emulate_tty=True,
    )

    return LaunchDescription([
        controller_node,
        command_sender_ui_node,
        # odom_gui_node,
        tf_broadcaster_node,
        turtlebot_follower_node,
    ])