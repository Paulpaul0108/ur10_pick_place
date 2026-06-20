#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from builtin_interfaces.msg import Duration

class RobotiqGripperClient(Node):
    def __init__(self):
        super().__init__('robotiq_gripper_client')
        # Build an action client to communicate with the gripper controller's FollowJointTrajectory action server, which is defined in controllers.yaml and will be loaded when we launch the Gazebo simulation
        self._action_client = ActionClient(
            self, 
            FollowJointTrajectory, 
            '/gripper_controller/follow_joint_trajectory'
        )

    def send_gripper_goal(self, position):
        self.get_logger().info('Waiting for gripper Action Server to be available...')
        self._action_client.wait_for_server()

        # Build the goal message
        goal_msg = FollowJointTrajectory.Goal()
        # The unique actuator name for your Robotiq gripper
        goal_msg.trajectory.joint_names = ['robotiq_85_left_knuckle_joint']

        # Set the target position for the gripper (0.0 for fully open, 0.8 for fully closed based on the URDF limits)
        point = JointTrajectoryPoint()
        point.positions = [position]
        # Set the time to reach the target position (e.g., 1 second)
        point.time_from_start = Duration(sec=1, nanosec=0)

        goal_msg.trajectory.points.append(point)

        self.get_logger().info(f'Sending gripper target position: {position}...')
        self._send_goal_future = self._action_client.send_goal_async(goal_msg)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Gripper rejected the action command!')
            return
        self.get_logger().info('Gripper accepted the command, moving...')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info('Gripper action completed!')
        # Action completed, shutdown the node
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    gripper_client = RobotiqGripperClient()
    
    # Set the target position for the gripper (0.0 for fully open, 0.8 for fully closed based on the URDF limits)
    target_position = 0.5
    
    gripper_client.send_gripper_goal(target_position)
    
    # Keep the node alive until the action is completed and the result callback shuts down the node
    rclpy.spin(gripper_client)

if __name__ == '__main__':
    main()