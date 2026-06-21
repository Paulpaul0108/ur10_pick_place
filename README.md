# UR10 Pick & Place — ROS 2 + MoveIt 2 + Gazebo

A simulated industrial pick-and-place robotic cell built with ROS 2 Humble, MoveIt 2, Gazebo Classic, and `ros2_control`.

The project features a Universal Robots UR10 manipulator, a Robotiq 2F-85 parallel gripper, MoveIt 2 motion planning, Gazebo simulation, RViz visualization, and controller-based gripper operation.

This project was developed as a self-directed robotics integration project to strengthen practical ROS 2, MoveIt 2, Gazebo, and robot control skills.

---

## Demo



https://github.com/user-attachments/assets/31cd3585-c3c4-40e8-b851-e1810e744fc7



---

## Tech Stack

| Component | Version / Tool |
|---|---|
| OS | Ubuntu 22.04 |
| ROS 2 | Humble |
| Simulator | Gazebo 11 Classic |
| Motion Planning | MoveIt 2 |
| Planner | OMPL / RRTConnect |
| Control | ros2_control |
| Arm | Universal Robots UR10 |
| Gripper | Robotiq 2F-85 |
| Visualization | RViz 2 |

---

## System Architecture

```text
ur10_cell.xacro
   ├── UR10 robot arm
   ├── Robotiq 2F-85 gripper
   ├── Table obstacle
   └── ros2_control hardware interfaces
            │
            ▼
        Gazebo Classic
            │
            ▼
 gazebo_ros2_control plugin
            │
            ▼
 joint_state_broadcaster
 joint_trajectory_controller
 gripper_controller
            │
            ▼
        MoveIt 2 move_group
            │
            ▼
        RViz 2 MotionPlanning
```

---

## Current Features

- UR10 robot model integrated through `ur_description`
- Robotiq 2F-85 gripper integration through `robotiq_description`
- Custom URDF/Xacro robot cell description
- Gazebo Classic simulation environment
- `ros2_control` integration
- Arm trajectory controller
- Gripper trajectory controller
- MoveIt 2 planning with OMPL
- RViz MotionPlanning panel support
- Static table obstacle with collision geometry
- Basic gripper control through a trajectory action client
- Initial pick-and-place sequence using predefined joint-space waypoints

---

## Current Status

The project currently supports two levels of operation:

### 1. Interactive MoveIt Planning

The robot can be controlled in RViz using the MoveIt 2 MotionPlanning panel.

This allows:

- setting end-effector pose goals
- planning collision-aware trajectories
- visualizing planned paths
- executing trajectories in Gazebo

### 2. Automated Joint-Space Demo

The current automated pick-and-place script executes a predefined sequence of joint-space waypoints through the `joint_trajectory_controller`.

The sequence follows this basic workflow:

```text
home
 → pre-grasp
 → open gripper
 → grasp
 → close gripper
 → lift
 → move to place
 → lower
 → open gripper
 → return home
```

This script is useful for testing controller communication, repeatable robot motion, and gripper sequencing.

However, the current automated script does not yet use MoveIt 2 for autonomous planning. It directly sends joint targets to the controller.

### 3. MoveIt-Based Automation

A MoveIt-based automated pick-and-place node is planned as the next development step.

The goal is to replace fixed joint-space waypoints with:

- end-effector pose goals
- MoveIt planning requests
- collision-aware trajectory generation
- planning result checking
- execution through MoveIt

---

## Repository Structure

```text
ur10_pick_place/
├── CMakeLists.txt
├── package.xml
├── README.md
├── config/
│   └── controllers.yaml
├── launch/
│   └── ur10_moveit_gazebo.launch.py
├── scripts/
│   ├── gripper_control.py
│   └── auto_pick_place.py
└── urdf/
    └── ur10_cell.xacro
```

If using a separate MoveIt configuration package, the workspace should include:

```text
ur10_ws/src/
├── ur10_pick_place/
└── ur10_pick_place_moveit_config/
```

The MoveIt configuration package is required for the current launch file and should be included in the workspace.

---

## Installation

### 1. Install dependencies

```bash
sudo apt update
sudo apt install ros-humble-moveit \
                 ros-humble-gazebo-ros2-control \
                 ros-humble-ros2-control \
                 ros-humble-ros2-controllers \
                 ros-humble-controller-manager \
                 ros-humble-joint-trajectory-controller \
                 ros-humble-joint-state-broadcaster \
                 ros-humble-ur-description \
                 ros-humble-robotiq-description \
                 ros-humble-xacro \
                 ros-humble-ompl
```

### 2. Create workspace

```bash
mkdir -p ~/ur10_ws/src
cd ~/ur10_ws/src
```

### 3. Clone repository

```bash
git clone https://github.com/Paulpaul0108/ur10_pick_place.git
```

If the MoveIt configuration package is separate, also place it inside:

```bash
~/ur10_ws/src
```

### 4. Build

```bash
cd ~/ur10_ws
colcon build
source install/setup.bash
```

---

## Usage

### Launch Gazebo + MoveIt 2 + RViz

```bash
ros2 launch ur10_pick_place ur10_moveit_gazebo.launch.py
```

This launch file starts:

- Gazebo Classic
- robot state publisher
- UR10 model spawning
- controller spawners
- MoveIt `move_group`
- RViz 2

---

## RViz Motion Planning

After launching the system:

1. Open the MotionPlanning panel in RViz.
2. Select the planning group.
3. Move the interactive marker.
4. Click `Plan`.
5. If the trajectory is valid, click `Execute`.

The table is included as collision geometry, so MoveIt can be used to test collision-aware motion planning.

---

## Gripper Control

The Robotiq 2F-85 gripper is controlled through the `gripper_controller` using a `FollowJointTrajectory` action client.

In the current project, gripper motion is mainly used as part of the automated pick-and-place sequence.

The gripper target position is defined inside the control script, for example:

```python
target_position = 0.5
```

The gripper can be commanded programmatically during the task sequence, such as:

```text
open gripper
move to grasp pose
close gripper
lift object
move to place pose
open gripper
```

This design keeps gripper control integrated with the pick-and-place workflow instead of requiring separate command-line open/close commands.

---

## Automated Pick-and-Place Demo

Run the current joint-space demo:

```bash
ros2 run ur10_pick_place auto_pick_place.py
```

This script sends predefined joint targets to the `joint_trajectory_controller`.

It is useful for testing:

- controller communication
- basic robot motion
- gripper sequencing
- repeatable motion execution

Current limitation:

> The automated demo does not yet use MoveIt 2 planning. It directly sends joint trajectories to the controller.

---

## Planned MoveIt-Based Automation

The next version will introduce a MoveIt-based automation node.

Planned execution flow:

```text
MoveIt plan to home
MoveIt plan to pre-grasp pose
open gripper
MoveIt plan to grasp pose
close gripper
MoveIt plan to lift pose
MoveIt plan to place pre-pose
MoveIt plan to place pose
open gripper
MoveIt plan back to home
```

This will replace fixed joint-space waypoints with pose-based planning.

Expected improvements:

- collision-aware automated motion
- easier object position adjustment
- better demonstration of MoveIt planning
- more realistic industrial pick-and-place workflow

---

## Known Issues and Debugging Notes

During development, several non-trivial ROS 2, MoveIt 2, and Gazebo integration issues were encountered and resolved.

### OMPL Library Mismatch

MoveIt expected a different OMPL shared library version than the one available through the installed packages.

This was resolved by adjusting the local OMPL library setup.

### MoveIt Loading Unwanted Planning Pipelines

`MoveItConfigsBuilder` may load additional planning plugins automatically.

To avoid startup issues, the launch file explicitly restricts the planning pipeline to OMPL:

```python
.planning_pipelines(pipelines=["ompl"])
```

### Sim Time Mismatch

MoveIt may reject joint states if Gazebo simulation time and ROS wall time are not synchronized.

The solution is to ensure that all relevant nodes use:

```python
{"use_sim_time": True}
```

### Gripper Mimic Joints

The Robotiq gripper uses mimic joints. Incorrect mimic joint multiplier signs can cause the fingers to move in the wrong direction.

The Gazebo mimic joint plugin settings must match the mimic behavior defined in the gripper URDF.

### MoveIt Collision Scene

URDF collision geometry alone is not always sufficient for correct MoveIt behavior.

The SRDF and allowed collision matrix may need to be adjusted to prevent false start-state collision errors.

---

## Roadmap

- [x] UR10 model integration
- [x] Robotiq 2F-85 gripper integration
- [x] Gazebo simulation
- [x] `ros2_control` controller setup
- [x] MoveIt 2 planning in RViz
- [x] Basic gripper action client
- [x] Joint-space automated pick-and-place demo
- [ ] MoveIt-based automated pick-and-place node
- [ ] Add collision object for grasp target
- [ ] Add Cartesian approach and retreat motion
- [ ] Add object attach/detach in MoveIt planning scene
- [ ] Add CI build test
- [ ] Add demo GIF/video
- [ ] Add detailed setup troubleshooting section

---

## Future Improvements

### MoveIt Planning Scene Object

Add the target object as a collision object in the MoveIt planning scene.

This will allow the robot to:

- avoid the object before grasping
- attach the object to the gripper after closing
- move the object safely
- detach it at the place location

### Cartesian Approach Motion

For grasping, a Cartesian path can be used for the final approach:

```text
pre-grasp pose
   ↓
straight-line Cartesian descent
   ↓
grasp pose
```

This is more realistic than planning every motion as a general pose-to-pose path.

### Real Robot Extension

The project is currently simulation-only.

A future real-robot version would require:

- UR robot driver
- real controller configuration
- safety limits
- tool calibration
- gripper hardware interface
- emergency stop and workspace safety validation

---

## Project Motivation

This project was built to develop practical skills in robot system integration, including:

- ROS 2 package structure
- URDF/Xacro robot modeling
- Gazebo simulation
- MoveIt 2 motion planning
- `ros2_control`
- controller configuration
- gripper integration
- debugging multi-node robotic systems

The project is intended as a robotics portfolio project for industrial automation, robot integration, and ROS 2 development roles.

---

## License

MIT License
