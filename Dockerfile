FROM osrf/ros:humble-desktop-full-jammy

ENV DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-c"]

# -------------------------------------------------------
# ROS 2, Gazebo, GUI, audio and rendering dependencies
# -------------------------------------------------------

RUN apt-get update && apt-get install -y \
    ros-humble-ros-gz \
    ros-humble-tf2-ros \
    python3-colcon-common-extensions \
    python3-pip \
    portaudio19-dev \
    libportaudio2 \
    alsa-utils \
    mesa-utils \
    libgl1 \
    libgl1-mesa-dri \
    libegl1 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxcb1 \
    libxkbcommon-x11-0 \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    && rm -rf /var/lib/apt/lists/*


# -------------------------------------------------------
# Python dependencies
# -------------------------------------------------------

RUN python3 -m pip install --no-cache-dir \
    PyQt6 \
    vosk \
    sounddevice


# -------------------------------------------------------
# ROS workspace
# -------------------------------------------------------

WORKDIR /task_1_ws

COPY src ./src


# -------------------------------------------------------
# Build workspace
# -------------------------------------------------------

RUN source /opt/ros/humble/setup.bash && \
    colcon build --symlink-install


# -------------------------------------------------------
# Run complete project
# -------------------------------------------------------

CMD ["bash", "-lc", \
     "source /opt/ros/humble/setup.bash && \
      source /task_1_ws/install/setup.bash && \
      ros2 launch task1_quadrotor task1.launch.py"]