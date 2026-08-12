import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable

from launch.actions import (
    ExecuteProcess,
    SetEnvironmentVariable,
    TimerAction
)

from launch_ros.actions import Node

def generate_launch_description():
    package_share = get_package_share_directory('task1_quadrotor')
    turtlebot_model = os.path.join(
        package_share,
        'models',
        'turtlebot3_burger',
        'model.sdf'
    )

    models_path = os.path.join(
        package_share,
        'models'
    )

    old_resource_path = os.environ.get(
        'IGN_GAZEBO_RESOURCE_PATH',
        ''
    )

    if old_resource_path:
        resource_path = models_path + ':' + old_resource_path
    else:
        resource_path = models_path

    world_path = os.path.join(
        package_share,
        'worlds',
        'task1_world.sdf'
    )

    set_resource_path = SetEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH',
        value=resource_path
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

    spawn_turtlebot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'tb3_burger',
            '-file', turtlebot_model,
            '-x', '-2.0',
            '-y', '0.0',
            '-z', '0.05',
        ],
        output='screen'
    )

    delayed_turtlebot_spawn = TimerAction(
        period=3.0,
        actions=[
            spawn_turtlebot
        ]
    )

    return LaunchDescription([
        set_resource_path,
        gazebo_run,
        delayed_turtlebot_spawn,
    ])