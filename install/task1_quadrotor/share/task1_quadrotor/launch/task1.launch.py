import os

from ament_index_python.packages import get_package_share_directory

from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import (
    PythonLaunchDescriptionSource,
)


def generate_launch_description():
    package_share = get_package_share_directory(
        'task1_quadrotor'
    )

    launch_directory = os.path.join(
        package_share,
        'launch'
    )

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                launch_directory,
                'gazebo.launch.py'
            )
        )
    )

    bridge_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                launch_directory,
                'bridge.launch.py'
            )
        )
    )

    control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                launch_directory,
                'control.launch.py'
            )
        )
    )

    odom_gui_node = Node(
        package='task1_quadrotor',
        executable='odom_gui',
        name='odom_gui',
        output='screen',
        emulate_tty=True
    )

    return LaunchDescription([
        gazebo_launch,
        bridge_launch,
        control_launch,
        odom_gui_node
    ])