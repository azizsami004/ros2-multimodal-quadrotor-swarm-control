# ROS 2 Multimodal Quadrotor Control & TurtleBot3 Leader-Follower

A ROS 2 Humble project for controlling an X3 quadrotor in Ignition Gazebo using a **PyQt6 manual interface** and **offline voice commands**, while displaying real-time telemetry. The project also implements the bonus **TurtleBot3 Burger leader-follower system using TF2**.

## Features

### Quadrotor Control

* Manual control using a PyQt6 GUI
* Forward / backward movement
* Left / right yaw rotation
* Up / down movement
* Stop command
* Button and Voice mode switching

### Voice Control

* Real-time microphone input using `sounddevice`
* Offline speech recognition using Vosk
* Supported commands:

  * `forward`
  * `backward`
  * `left`
  * `right`
  * `up`
  * `down`
  * `stop`
* Voice recognition runs separately from the PyQt6 GUI to prevent the interface from freezing

### Telemetry Dashboard

Real-time display of:

* Position: X, Y, Z
* Orientation
* Linear velocity
* Angular velocity
* Odometry connection status

### Bonus: TurtleBot3 Leader-Follower

* TurtleBot3 Burger spawned in the same Gazebo world as the X3 quadrotor
* Separate TurtleBot command and odometry topics
* TF2-based tracking between the quadrotor and TurtleBot3
* TurtleBot automatically turns toward and follows the quadrotor
* Maintains a minimum following distance

---

## System Architecture

```text
                     ┌───────────────────────┐
                     │   command_sender_ui   │
                     │                       │
                     │  PyQt6 Manual Control │
                     │  + Voice Mode         │
                     └───────────┬───────────┘
                                 │
                         /command_sender
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │      controller       │
                     └───────────┬───────────┘
                                 │
                           /X3/cmd_vel
                                 │
                                 ▼
                         ┌──────────────┐
                         │ X3 Quadrotor │
                         │   Gazebo     │
                         └──────┬───────┘
                                │
                      /model/X3/odometry
                         ┌──────┴───────┐
                         │              │
                         ▼              ▼
                    odom_gui      tf_broadcaster
                                       │
                                       │ TF2
                                       ▼
                              turtlebot_follower
                                       │
                                  /tb3/cmd_vel
                                       │
                                       ▼
                               TurtleBot3 Burger
```

---

## Package Structure

```text
task_1_ws/
└── src/
    └── task1_quadrotor/
        ├── launch/
        │   ├── gazebo.launch.py
        │   ├── bridge.launch.py
        │   ├── control.launch.py
        │   └── task1.launch.py
        │
        ├── models/
        │   ├── turtlebot3_burger/
        │   ├── turtlebot3_common/
        │   └── vosk-model-small-en-us-0.15/
        │
        ├── worlds/
        │   └── task1_world.sdf
        │
        ├── task1_quadrotor/
        │   ├── __init__.py
        │   ├── controller.py
        │   ├── command_sender_ui.py
        │   ├── voice_controller.py
        │   ├── odom_gui.py
        │   ├── tf_broadcaster.py
        │   └── turtlebot_follower.py
        │
        ├── package.xml
        ├── setup.cfg
        └── setup.py
```

---

## Node Description

### `controller.py`

Receives velocity commands from:

```text
/command_sender
```

and publishes them to:

```text
/X3/cmd_vel
```

The node acts as the interface between the user-control system and the quadrotor.

---

### `command_sender_ui.py`

PyQt6-based control interface.

It contains two modes:

#### Button Mode

Provides buttons for:

```text
Forward
Backward
Left
Right
Up
Down
Stop
```

#### Voice Mode

Provides microphone ON/OFF control and receives recognized commands from `VoiceController`.

Both manual and voice commands use the same command publishing system.

---

### `voice_controller.py`

Handles the speech-recognition system.

Pipeline:

```text
Microphone
    ↓
sounddevice
    ↓
Audio Queue
    ↓
Vosk
    ↓
Recognized Text
    ↓
Command Extraction
    ↓
PyQt Signal
    ↓
command_sender_ui
```

Vosk allows the voice-control system to work offline without requiring an internet connection.

---

### `odom_gui.py`

Subscribes to:

```text
/model/X3/odometry
```

using:

```text
nav_msgs/msg/Odometry
```

It displays the quadrotor's real-time telemetry including position, orientation, linear velocity, and angular velocity.

---

### `tf_broadcaster.py`

Creates the TF relationship between the quadrotor and TurtleBot3.

The TF tree is approximately:

```text
                world
               /     \
          X3/odom    tb3/odom
             |           |
             |           |
      X3/base_link  tb3/base_footprint
```

The quadrotor transform is generated from:

```text
/model/X3/odometry
```

and the TurtleBot transform is generated from:

```text
/tb3/odom
```

---

### `turtlebot_follower.py`

Uses a TF2 `Buffer` and `TransformListener` to determine the position of the quadrotor relative to TurtleBot3.

It calculates:

```text
Horizontal distance to quadrotor
Heading angle to quadrotor
```

The TurtleBot then:

1. Rotates toward the quadrotor if the heading error is large.
2. Moves toward the quadrotor.
3. Corrects its heading while moving.
4. Stops when it reaches the desired following distance.

Commands are published to:

```text
/tb3/cmd_vel
```

---

## Gazebo World

The project uses:

```text
worlds/task1_world.sdf
```

The world contains:

* X3 quadrotor
* Large ground plane
* TurtleBot3 Burger
* Required Gazebo systems and plugins

The ground plane was enlarged to provide sufficient space for TurtleBot3 leader-follower movement.

---

## ROS 2 / Gazebo Topics

### Quadrotor

```text
/command_sender
/X3/cmd_vel
/model/X3/odometry
```

### TurtleBot3

```text
/tb3/cmd_vel
/tb3/odom
/tb3/tf
```

---

## ROS-Gazebo Bridge

The project uses `ros_gz_bridge` to communicate between ROS 2 and Ignition Gazebo.

The main bridges are:

```text
ROS 2 → Gazebo
/X3/cmd_vel
/tb3/cmd_vel

Gazebo → ROS 2
/model/X3/odometry
/tb3/odom
```

---

## Requirements

Tested with:

```text
Ubuntu 22.04
ROS 2 Humble
Ignition Gazebo Fortress
Python 3
PyQt6
Vosk
sounddevice
ros_gz_bridge
ros_gz_sim
tf2_ros
```

Install the main ROS dependencies:

```bash
sudo apt update

sudo apt install \
    ros-humble-ros-gz-bridge \
    ros-humble-ros-gz-sim \
    ros-humble-tf2-ros \
    python3-pyqt6 \
    portaudio19-dev
```

Install the Python voice-control libraries:

```bash
python3 -m pip install --user vosk sounddevice
```

---

## Building the Workspace

Clone the repository and enter the workspace:

```bash
cd task_1_ws
```

Source ROS 2:

```bash
source /opt/ros/humble/setup.bash
```

Build:

```bash
colcon build --symlink-install
```

Source the workspace:

```bash
source install/setup.bash
```

---

## Running the Complete Project

The entire system can be started using:

```bash
ros2 launch task1_quadrotor task1.launch.py
```

This launches:

```text
task1.launch.py
│
├── gazebo.launch.py
│   ├── Ignition Gazebo
│   ├── X3 quadrotor
│   └── TurtleBot3 Burger
│
├── bridge.launch.py
│   ├── X3 velocity bridge
│   ├── X3 odometry bridge
│   ├── TurtleBot velocity bridge
│   └── TurtleBot odometry bridge
│
└── control.launch.py
    ├── controller
    ├── command_sender_ui
    ├── odom_gui
    ├── tf_broadcaster
    └── turtlebot_follower
```

---

## Manual Control

Launch the project and select:

```text
BUTTON
```

from the control GUI.

The available controls are:

```text
Forward    → Move quadrotor forward
Backward   → Move quadrotor backward
Left       → Rotate left
Right      → Rotate right
Up         → Increase altitude
Down       → Decrease altitude
Stop       → Stop movement
```

---

## Voice Control

Select:

```text
VOICE
```

and enable the microphone.

Supported commands:

```text
forward
backward
left
right
up
down
stop
```

Example:

```text
User: "forward"

Microphone
    ↓
Vosk recognizes "forward"
    ↓
GUI processes command
    ↓
/command_sender
    ↓
controller.py
    ↓
/X3/cmd_vel
    ↓
Quadrotor moves forward
```

---

## TurtleBot3 Leader-Follower

The TurtleBot automatically follows the quadrotor using TF2.

The follower queries:

```text
tb3/base_footprint → X3/base_link
```

and calculates the relative horizontal position of the drone.

The controller uses:

```text
distance = sqrt(x² + y²)
heading  = atan2(y, x)
```

to determine the required linear and angular velocity.

The current implementation uses a proportional follower controller with limited linear and angular speeds for stable movement.

---

## Testing Individual Components

### Quadrotor velocity

```bash
ros2 topic echo /X3/cmd_vel
```

### Quadrotor odometry

```bash
ros2 topic echo /model/X3/odometry
```

### TurtleBot velocity

```bash
ros2 topic echo /tb3/cmd_vel
```

### TurtleBot odometry

```bash
ros2 topic echo /tb3/odom
```

### Check TF relationship

```bash
ros2 run tf2_ros tf2_echo \
    tb3/base_footprint \
    X3/base_link
```

---

## Control Flow

### Manual Mode

```text
PyQt Button
    ↓
command_sender_ui
    ↓
/command_sender
    ↓
controller
    ↓
/X3/cmd_vel
    ↓
X3
```

### Voice Mode

```text
Microphone
    ↓
VoiceController
    ↓
Vosk
    ↓
Recognized Command
    ↓
command_sender_ui
    ↓
/command_sender
    ↓
controller
    ↓
/X3/cmd_vel
    ↓
X3
```

### Leader-Follower

```text
X3 Odometry ──────┐
                  │
TB3 Odometry ─────┤
                  ▼
            TF Broadcaster
                  ↓
                TF2
                  ↓
         TurtleBot Follower
                  ↓
           /tb3/cmd_vel
                  ↓
           TurtleBot3 Burger
```

---

## Future Improvements

Possible improvements include:

* Maintaining a fixed target point directly behind the quadrotor
* Configurable follower distance
* Better PID-based follower controller
* Obstacle avoidance
* Combined control and telemetry dashboard
* Improved voice-recognition feedback
* Additional safety and command timeout handling

---

## Author

Developed as part of the **BUET Mars Rover Team – Interplanetar 2026 Recruitment Assignment, Task 1**.

