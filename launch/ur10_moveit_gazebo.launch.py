from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from moveit_configs_utils import MoveItConfigsBuilder
from launch_ros.actions import Node, SetParameter  # 🔥 記得加上 SetParameter
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # 1.read the robot description from the xacro file and set it as a parameter for the robot_state_publisher
    robot_description_content = ParameterValue(
        Command([
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution([
                FindPackageShare("ur10_pick_place"),
                "urdf",
                "ur10_cell.xacro"
            ]),
        ]),
        value_type=str
    )

    # 2. state publisher node to publish the robot's state to the rest of the ROS system, using the robot description we just read from the xacro file
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {"robot_description": robot_description_content},
            {"use_sim_time": True},
        ],
    )

    # 3. include the Gazebo launch file to start the Gazebo simulator with the appropriate world and settings for our UR10 robot
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("gazebo_ros"),
                "launch",
                "gazebo.launch.py"
            ])
        ])
    )

    # 4. spawn the robot into Gazebo and load the necessary controllers for both the arm and the gripper for 120 sec to ensure they are fully loaded before we start sending commands to them
    spawn_robot = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=["-topic", "robot_description", "-entity", "ur10"],
    )
    load_joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager-timeout", "120"],
    )
    load_joint_trajectory_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_trajectory_controller", "--controller-manager-timeout", "120"],
    )
    load_gripper_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["gripper_controller", "--controller-manager-timeout", "120"],
    )

    # 5.
    moveit_config = (
        MoveItConfigsBuilder("ur10_cell", package_name="ur10_pick_place_moveit_config")
        .robot_description(
            file_path=os.path.join(
                get_package_share_directory("ur10_pick_place"),
                "urdf",
                "ur10_cell.xacro"
            )
        )
        .planning_pipelines(pipelines=["ompl"])
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .to_moveit_configs()
    )

    moveit_params = moveit_config.to_dict()
    moveit_params["use_sim_time"] = True

    move_group = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[moveit_params],
    )
    
    rviz = Node(
        package="rviz2",
        executable="rviz2",
        output="screen",
        arguments=["-d", os.path.join(
            get_package_share_directory("ur10_pick_place_moveit_config"),
            "config",
            "moveit.rviz"
        )],
        parameters=[
            moveit_params, 
            {"use_sim_time": True}
        ],
    )

    #6. delayed the spawn of the robot and controllers to ensure Gazebo is fully up and running
    delayed_spawn = TimerAction(
        period=8.0, #8 seconds delay to ensure Gazebo is fully up and running
        actions=[
            spawn_robot,
            load_joint_state_broadcaster,
            load_joint_trajectory_controller,
            load_gripper_controller,
        ]
    )

    return LaunchDescription([
        SetParameter(name='use_sim_time', value=True), 
        robot_state_publisher,
        gazebo,
        delayed_spawn, 
        move_group,
        rviz,
    ])