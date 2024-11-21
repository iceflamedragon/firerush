import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import time

class JointStatePublisher(Node):
    def __init__(self):
        super().__init__('joint_state_publisher')
        self.publisher_ = self.create_publisher(JointState, 'joint_states', 10)
        self.timer = self.create_timer(0.5, self.publish_joint_states)  # 每0.5秒发布一次

        # 初始化关节状态
        self.joint_state_msg = JointState()
        self.joint_state_msg.name = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5']  # 替换为您的关节名称
        self.joint_state_msg.position = [0.0] * len(self.joint_state_msg.name)  # 初始位置

    def publish_joint_states(self):
        # 更新关节位置（可以根据需要进行更改）
        for i in range(len(self.joint_state_msg.position)):
            self.joint_state_msg.position[i] += 0.1  # 示例：每次增加 0.1

        # 设置时间戳
        self.joint_state_msg.header.stamp = self.get_clock().now().to_msg()
        
        # 发布消息
        self.publisher_.publish(self.joint_state_msg)
        self.get_logger().info(f'Publishing: {self.joint_state_msg.position}')

def main(args=None):
    rclpy.init(args=args)
    joint_state_publisher = JointStatePublisher()
    rclpy.spin(joint_state_publisher)

    # 清理
    joint_state_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
