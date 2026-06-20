#!/usr/bin/env python3
import rclpy
import math
from rclpy.node import Node
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from builtin_interfaces.msg import Duration

class PickAndPlaceNode(Node):
    def __init__(self):
        super().__init__('auto_pick_place_node')
        
        #create action clients for both the arm and the gripper, connecting to the respective action servers defined in controllers.yaml
        self.arm_client = ActionClient(self, FollowJointTrajectory, '/joint_trajectory_controller/follow_joint_trajectory')
        self.gripper_client = ActionClient(self, FollowJointTrajectory, '/gripper_controller/follow_joint_trajectory')

        # define joint names (must match those in controllers.yaml)
        self.arm_joint_names = [
            'shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
            'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint'
        ]
        self.gripper_joint_names = ['robotiq_85_left_knuckle_joint']

    def wait_for_servers(self):
        self.get_logger().info('Waiting for brain and nervous system connection...')
        self.arm_client.wait_for_server()
        self.gripper_client.wait_for_server()
        self.get_logger().info('System connection successful! Ready to execute task.')

    def move_arm(self, positions, duration_sec=3):
        """Control the arm to move to the specified angles"""
        # prepare the goal message including joint names, target positions and the time to reach the target
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory.joint_names = self.arm_joint_names
        
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(sec=duration_sec, nanosec=0)
        goal_msg.trajectory.points.append(point)

        # force the robot to execute the trajectory by sending the goal message to the action server and waiting for the result 
        future = self.arm_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()
        
        # check if the action server accepted the goal 
        if not goal_handle.accepted:
            self.get_logger().error('Arm rejected the motion command!')
            return False
        
        # wait for the action to complete and return the result
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        return True

    def move_gripper(self, position, duration_sec=1):
        """Control the gripper to open or close"""
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory.joint_names = self.gripper_joint_names
        
        point = JointTrajectoryPoint()
        point.positions = [position]
        point.time_from_start = Duration(sec=duration_sec, nanosec=0)
        goal_msg.trajectory.points.append(point)

        future = self.gripper_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()
        
        if not goal_handle.accepted:
            self.get_logger().error('Gripper rejected the motion command!')
            return False
            
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        return True

def main(args=None):
    rclpy.init(args=args)
    node = PickAndPlaceNode()
    node.wait_for_servers()

    # ========================================================
    # 🎯 Define the key poses for the task (using degrees, the program will automatically convert them)
    # Array order: [Base, Shoulder, Elbow, Wrist1, Wrist2, Wrist3]
    # ========================================================
    
    # A utility function to convert degrees to radians
    def deg2rad(degrees):
        return [math.radians(d) for d in degrees]

    # 1. Default standby position (hand pointing up)
    pos_home       = deg2rad([0.0, -90.0, 90.0, -90.0, -90.0, 0.0])  

    # 2. Pre-grasp position above the box (just above the cup, ready to descend and grasp)
    pos_pre_grasp  = deg2rad([-13.3, -90.0, 85.0, -85.0, -90.0, 0]) 

    # 3. Grasp position (the perfect coordinates you copied from the RViz screenshot!)
    pos_grasp      = deg2rad([-13.3, -90.0, 95.0, -95.0, -90.0, 0])  

    # 4. Place position above (we rotate the base to the left by 45 degrees, from -15 to 30)
    pos_place_pre  = deg2rad([30.0, -90.0, 95.0, -95.0, -90.0, 0]) 

    # 5. lowered place position (the same as the grasp position but with the base rotated, ready to release the cup)
    pos_place      = deg2rad([30.0, -94.0, 98.0, -91.0, -92.0, 0])  

    # Gripper control values (Radian)
    gripper_open = 0.0
    gripper_close = 0.27

    try:
        node.get_logger().info('▶️ Task started: Returning to Home position')
        node.move_arm(pos_home, 3)

        node.get_logger().info('1️⃣ Arm moved to above the box (Pre-grasp)')
        node.move_arm(pos_pre_grasp, 3)

        node.get_logger().info('2️⃣ Gripper opened')
        node.move_gripper(gripper_open, 1)

        node.get_logger().info('3️⃣ Arm descended to grasp position (Grasp)')
        node.move_arm(pos_grasp, 2)

        node.get_logger().info('4️⃣ Gripper closed (grasped the cup)')
        node.move_gripper(gripper_close, 1)

        node.get_logger().info('5️⃣ Arm lifted (lifting the cup)')
        node.move_arm(pos_pre_grasp, 2)

        node.get_logger().info('6️⃣ Arm moved to the placement position')
        node.move_arm(pos_place_pre, 3)

        node.get_logger().info('7️⃣ Arm descended to the placement position')
        node.move_arm(pos_place, 2)

        node.get_logger().info('8️⃣ Gripper opened (releasing the cup)')
        node.move_gripper(gripper_open, 1)

        node.get_logger().info('9️⃣ Arm lifted (moving away)')
        node.move_arm(pos_place_pre, 2)

        node.get_logger().info('🔟 Arm returned to Home position')
        node.move_arm(pos_home, 3)

        node.get_logger().info('✅ Task completed successfully!')

    except KeyboardInterrupt:
        node.get_logger().info('Task manually interrupted.')

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()