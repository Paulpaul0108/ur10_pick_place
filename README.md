# UR10 Pick & Place — ROS 2 + MoveIt 2 + Gazebo


https://github.com/user-attachments/assets/4fa2fe6e-c409-4239-b822-74dba1059c0f


A simulated industrial pick-and-place cell built from scratch in ROS 2, featuring a Universal Robots UR10 arm, a Robotiq 2F-85 parallel gripper, motion planning with collision avoidance, and a full Gazebo simulation environment.

This project was built independently to deepen hands-on ROS 2 / MoveIt 2 skills following working-student experience in robotic system integration at Moin Robotics GmbH.

---

## Tech Stack

| Component | Version |
|---|---|
| OS | Ubuntu 22.04 |
| ROS 2 | Humble |
| Simulator | Gazebo 11 (classic) |
| Motion Planning | MoveIt 2 (OMPL — RRTConnect) |
| Gripper | Robotiq 2F-85 |
| Arm | Universal Robots UR10 |

---

## System Architecture

```
ur10_cell.xacro (URDF)
   ├── UR10 arm (ur_description)
   ├── Robotiq 2F-85 gripper (robotiq_description)
   ├── Table obstacle (collision geometry)
   └── ros2_control hardware interfaces
            │
            ▼
   Gazebo (gazebo_ros2_control plugin)
            │
            ▼
   joint_trajectory_controller / gripper_controller
            │
            ▼
   MoveIt 2 (move_group) ──── OMPL motion planning
            │
            ▼
        RViz 2 (visualization + interactive planning)
```

Two ROS 2 packages:

- **`ur10_pick_place`** — robot description (URDF/Xacro), Gazebo integration, controller configs
- **`ur10_pick_place_moveit_config`** — MoveIt 2 configuration (SRDF, kinematics, planning pipelines)

---

## Features

- [x] UR10 arm simulated in Gazebo with full `ros2_control` integration
- [x] MoveIt 2 motion planning (OMPL / RRTConnect) with RViz interactive control
- [x] Static obstacle (table) with collision geometry — verified collision detection and automatic path planning around it
- [x] Robotiq 2F-85 gripper integration via `ur_to_robotiq` adapter, with mimic-joint Gazebo plugin for synchronized finger motion
- [x] Standalone gripper action client for open/close control
- [ ] Full automated pick-and-place sequence (in progress)
- [ ] Vision-based object detection (planned)

---

## Installation

```bash
# Dependencies
sudo apt install ros-humble-moveit ros-humble-gazebo-ros2-control \
                  ros-humble-ur-description ros-humble-robotiq-description \
                  ros-humble-ompl

# Clone into your workspace
cd ~/ur10_ws/src
git clone <this-repo-url>

# Build
cd ~/ur10_ws
colcon build --packages-select ur10_pick_place ur10_pick_place_moveit_config
source install/setup.bash
```

## Usage

Launch the full simulation stack (Gazebo + MoveIt 2 + RViz):

```bash
ros2 launch ur10_pick_place ur10_moveit_gazebo.launch.py
```

In RViz, use the **MotionPlanning** panel to drag the interactive marker and plan/execute arm trajectories. The table is registered in the MoveIt planning scene — try planning a path through it to see automatic collision avoidance.

Control the gripper independently:

```bash
ros2 run ur10_pick_place gripper_control.py open
ros2 run ur10_pick_place gripper_control.py close
```

---

## Debugging Notes

A selection of non-obvious issues encountered and resolved while building this on ROS 2 Humble:

- **OMPL library version mismatch** — MoveIt 2.7.4 required `libompl.so.17`, but apt only provided `.so.16`. Resolved with a manual symlink rather than waiting on a packaging fix.
- **`move_group` segfault on startup** — traced to `MoveItConfigsBuilder` auto-loading the CHOMP planner plugin, which wasn't installed. Fixed by explicitly restricting `planning_pipelines=["ompl"]`.
- **Sim/wall-clock desync** — MoveIt rejected joint states as "too old" because Gazebo's simulated clock and ROS's wall clock diverged. Fixed by propagating `use_sim_time: True` to every node in the launch file.
- **Gripper fingers crossing on close** — the Gazebo `mimic_joint` plugin multipliers didn't match the `<mimic>` tags already defined in the Robotiq URDF macro, causing both fingers to rotate in the same direction instead of mirroring. Fixed by aligning plugin multiplier signs with the macro's mimic definitions.
- **MoveIt unaware of URDF-defined obstacles** — adding a `<collision>` geometry to the URDF wasn't enough on its own; the Setup Assistant–generated SRDF needed explicit `disable_collisions` entries between the table and the robot base link to avoid a false "start state in collision" rejection.

---

## Project Background

Developed as a self-directed learning project to build practical depth in ROS 2, MoveIt 2, and Gazebo simulation, in preparation for industrial automation roles (UR/KUKA/ABB-class manipulators, robotic cell integration).

## License

MIT
