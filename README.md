# ROS 2 Multimodal Quadrotor Control & TurtleBot3 Leader-Follower

A ROS 2 Humble project that controls an **X3 quadrotor in Ignition Gazebo** using a PyQt6 manual interface and offline voice commands, displays real-time telemetry, and implements a **TurtleBot3 Burger leader-follower system using TF2**.

---

## 🔗 Project Links

### GitHub Repository
https://github.com/azizsami004/ros2-multimodal-quadrotor-swarm-control

### Docker Hub
https://hub.docker.com/r/azizsami004/ros2-multimodal-quadrotor-swarm-control

### Docker Image

```bash
docker pull azizsami004/ros2-multimodal-quadrotor-swarm-control:latest
```

---

# Features

## 🚁 Quadrotor Control

The X3 quadrotor can be controlled through a PyQt6 GUI.

Available commands:

- Forward
- Backward
- Left
- Right
- Up
- Down
- Stop

The interface supports two control modes:

- **BUTTON mode**
- **VOICE mode**

---

## 🎙️ Offline Voice Control

Voice commands are processed locally using **Vosk** and `sounddevice`.

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

The speech-recognition system works offline and does not require an internet connection during operation.

Voice processing runs separately from the GUI so that microphone processing does not freeze the PyQt interface.

---

## 📊 Real-Time Telemetry Dashboard

A separate PyQt6 telemetry interface displays real-time quadrotor data.

Displayed information includes:

- Position X
- Position Y
- Position Z
- Orientation
- Linear velocity
- Angular velocity
- Odometry / system status

The telemetry node subscribes to:

```text
/model/X3/odometry
```

using:

```text
nav_msgs/msg/Odometry
```

---

# 🤖 TurtleBot3 Leader-Follower System

The bonus portion of the project adds a **TurtleBot3 Burger** to the same Gazebo environment.

The TurtleBot automatically follows the X3 quadrotor using **ROS 2 TF2**.

The follower calculates:

```text
Relative X position
Relative Y position
Horizontal distance
Heading angle
```

It then generates linear and angular velocity commands for the TurtleBot.

Commands are published to:

```text
/tb3/cmd_vel
```

The follower:

1. Determines the drone position using TF2.
2. Rotates toward the drone when necessary.
3. Moves toward the drone.
4. Corrects its heading while moving.
5. Stops after reaching the required following distance.

---

# System Architecture

```text
                ┌───────────────────────┐
                │   command_sender_ui   │
                │                       │
                │ Manual + Voice Input  │
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
                    │    Gazebo    │
                    └──────┬───────┘
                           │
                 /model/X3/odometry
                    ┌──────┴──────┐
                    │             │
                    ▼             ▼
                odom_gui    tf_broadcaster
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

# TF2 Architecture

The project creates a common TF structure for the quadrotor and TurtleBot.

```text
                 world
                /     \
           X3/odom    tb3/odom
              |           |
              |           |
       X3/base_link  tb3/base_footprint
```

The follower queries the transform:

```text
tb3/base_footprint → X3/base_link
```

This provides the position of the drone relative to TurtleBot3.

The follower calculates:

```python
distance = sqrt(x² + y²)

heading = atan2(y, x)
```

and generates the required TurtleBot velocity commands.

---

# Package Structure

```text
task_1_ws/
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
│
└── src/
    └── task1_quadrotor/
        │
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

# Node Description

## `controller.py`

Receives velocity commands from:

```text
/command_sender
```

and publishes the processed commands to:

```text
/X3/cmd_vel
```

This acts as the main control interface between manual/voice input and the quadrotor.

---

## `command_sender_ui.py`

Provides the PyQt6 user interface.

The interface contains:

### BUTTON Mode

Manual controls for:

```text
Forward
Backward
Left
Right
Up
Down
Stop
```

### VOICE Mode

Provides microphone ON/OFF control and receives recognized commands from the voice-control system.

Both modes use the same ROS 2 command pipeline.

---

## `voice_controller.py`

Handles microphone input and speech recognition.

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
Command Detection
     ↓
PyQt Signal
     ↓
command_sender_ui
```

---

## `odom_gui.py`

Subscribes to:

```text
/model/X3/odometry
```

and displays live telemetry including:

```text
Position
Orientation
Linear velocity
Angular velocity
System status
```

---

## `tf_broadcaster.py`

Creates the TF2 relationships required for the leader-follower system.

It receives:

```text
/model/X3/odometry
```

and:

```text
/tb3/odom
```

and publishes the required dynamic and static transforms.

---

## `turtlebot_follower.py`

Uses:

```python
tf2_ros.Buffer
```

and:

```python
tf2_ros.TransformListener
```

to determine the position of the quadrotor relative to TurtleBot3.

The calculated distance and heading are used to publish:

```text
/tb3/cmd_vel
```

and automatically follow the quadrotor.

---

# ROS 2 Topics

## Quadrotor

```text
/command_sender
/X3/cmd_vel
/model/X3/odometry
```

## TurtleBot3

```text
/tb3/cmd_vel
/tb3/odom
/tb3/tf
```

---

# ROS-Gazebo Bridge

`ros_gz_bridge` is used for communication between ROS 2 and Ignition Gazebo.

Main bridges:

```text
ROS 2 → Gazebo

/X3/cmd_vel
/tb3/cmd_vel
```

```text
Gazebo → ROS 2

/model/X3/odometry
/tb3/odom
```

---

# Gazebo World

The simulation world is located at:

```text
worlds/task1_world.sdf
```

The environment contains:

- X3 quadrotor
- TurtleBot3 Burger
- Ground plane
- Gazebo velocity-control systems
- Odometry systems

The ground plane was enlarged to provide enough space for the TurtleBot leader-follower demonstration.

---

# Requirements

The project was developed using:

```text
Ubuntu 22.04
ROS 2 Humble
Ignition Gazebo Fortress
Python 3
PyQt6
Vosk
sounddevice
TF2
ros_gz_bridge
ros_gz_sim
```

---

# Running From Source

Clone the repository:

```bash
git clone https://github.com/azizsami004/ros2-multimodal-quadrotor-swarm-control.git
```

Enter the workspace:

```bash
cd ros2-multimodal-quadrotor-swarm-control
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

Run the complete project:

```bash
ros2 launch task1_quadrotor task1.launch.py
```

---

# 🐳 Docker

A Docker image containing the ROS 2 workspace and its dependencies is available on Docker Hub.

## Docker Hub Repository

https://hub.docker.com/r/azizsami004/ros2-multimodal-quadrotor-swarm-control

## Pull Docker Image

```bash
sudo docker pull \
azizsami004/ros2-multimodal-quadrotor-swarm-control:latest
```

---

# Running With Docker Compose

Because the application uses:

- Gazebo GUI
- PyQt6 GUI
- Microphone input
- X11 display

the included `docker-compose.yml` provides the necessary host configuration.

First allow the Docker container to access the X11 display:

```bash
xhost +si:localuser:root
```

Build and run directly from the repository:

```bash
sudo docker compose build
sudo docker compose up
```

To stop the project:

```bash
Ctrl+C
```

then:

```bash
sudo docker compose down
```

---

# Complete Launch

Only one ROS 2 launch command is required:

```bash
ros2 launch task1_quadrotor task1.launch.py
```

The launch hierarchy is:

```text
task1.launch.py
│
├── gazebo.launch.py
│   ├── Ignition Gazebo
│   ├── X3 Quadrotor
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

# Manual Control Flow

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
X3 Quadrotor
```

---

# Voice Control Flow

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
X3 Quadrotor
```

---

# Leader-Follower Flow

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

# Testing

## Check Quadrotor Odometry

```bash
ros2 topic echo /model/X3/odometry
```

## Check TurtleBot Odometry

```bash
ros2 topic echo /tb3/odom
```

## Check Quadrotor Commands

```bash
ros2 topic echo /X3/cmd_vel
```

## Check TurtleBot Commands

```bash
ros2 topic echo /tb3/cmd_vel
```

## Check TF2

```bash
ros2 run tf2_ros tf2_echo \
tb3/base_footprint \
X3/base_link
```

A valid continuously updating transform confirms that TF2 can determine the position of the quadrotor relative to TurtleBot3.

---

# Future Improvements

Possible improvements include:

- Maintaining a fixed target point directly behind the quadrotor
- Configurable following distance
- PID-based follower controller
- Obstacle avoidance
- Integrated telemetry and control dashboard
- Improved voice feedback
- Additional failsafe mechanisms
- Navigation integration

---

# Author

**Abdul Aziz**

Developed for the **BUET Mars Rover Team – Interplanetar 2026 Recruitment Software Assignment, Task 1**.

---

# Docker Hub

🐳 **Pre-built Docker image:**

https://hub.docker.com/r/azizsami004/ros2-multimodal-quadrotor-swarm-control

```bash
docker pull azizsami004/ros2-multimodal-quadrotor-swarm-control:latest
```