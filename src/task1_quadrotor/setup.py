from setuptools import find_packages, setup

import os
from glob import glob

package_name = 'task1_quadrotor'


def install_directory(source_directory, destination_directory):
    data_files = []

    for current_path, directories, filesnames in os.walk(source_directory):

        if not filesnames:
            continue

        relative_path = os.path.relpath(current_path, source_directory)

        install_path = os.path.join('share', package_name, destination_directory)

        if relative_path != '.':
            install_path = os.path.join(install_path, relative_path)

        source_files = [
            os.path.join(current_path, filename)
            for filename in filesnames
        ]
        data_files.append((install_path, source_files))

    return data_files

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.sdf')),
    ] + install_directory('models/vosk-model-small-en-us-0.15', 'models/vosk-model-small-en-us-0.15'),

    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='abdul',
    maintainer_email='abdul@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'controller = task1_quadrotor.controller:main',
            'command_sender_ui = task1_quadrotor.command_sender_ui:main',
            'odom_gui = task1_quadrotor.odom_gui:main'
        ],
    },
)
