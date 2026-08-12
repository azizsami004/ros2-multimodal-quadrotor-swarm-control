from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='quadrotor_bridge',
        output='screen',
        arguments=[
            (
                'X3/cmd_vel'
                '@geometry_msgs/msg/Twist'
                ']ignition.msgs.Twist'
            ),
            (
                '/model/X3/odometry'
                '@nav_msgs/msg/Odometry'
                '[ignition.msgs.Odometry'
            ),
            (
                '/tb3/cmd_vel'
                '@geometry_msgs/msg/Twist'
                ']ignition.msgs.Twist'
            ),
            (
                '/tb3/odom'
                '@nav_msgs/msg/Odometry'
                '[ignition.msgs.Odometry'
            ),
            
        ],
    )

    return LaunchDescription([
        bridge,
    ])