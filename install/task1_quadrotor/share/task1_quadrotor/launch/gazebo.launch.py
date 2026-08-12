import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess

def generate_launch_description():
    package_share = get_package_share_directory('task1_quadrotor')

    world_path = os.path.join(
        package_share,
        'worlds',
        'task1_world.sdf'
    )

    gazebo_run = ExecuteProcess(
        cmd=[
            'ign',
            'gazebo',
            '-r',
            '-v',
            '4',
            world_path
        ],
        output='screen'
    )

    return LaunchDescription([
        gazebo_run,
    ])