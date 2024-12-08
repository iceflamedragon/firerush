import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy

from sensor_msgs.msg import JointState
from std_msgs.msg import String, Float64MultiArray

import json
import serial
import numpy as np

ser = serial.Serial("/dev/ttyUSB0", 115200)


class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('serial_ctrl')
        
        self.position = []
        
        self.x=0
        self.y=0
        self.z=0
        # 定义 QoS 策略
        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            depth=10
        )
        
        # # 订阅 joint_states 话题
        # self.subscription = self.create_subscription(
        #     JointState,
        #     'joint_states',
        #     self.listener_callback,
        #     qos_profile)
        # self.subscription  # prevent unused variable warning
        
        # 订阅 depth_info 话题
        self.custom_subscription = self.create_subscription(
            Float64MultiArray,  # 修改消息类型为 Float64MultiArray
            'depth_info',
            self.custom_topic_callback,
            qos_profile)
        self.custom_subscription  # prevent unused variable warning
    
    def posGet(self, radInput, direcInput, multiInput):
        if radInput == 0:
            return 2047
        else:
            getPos = int(2047 + (direcInput * radInput / 3.1415926 * 2048 * multiInput) + 0.5)
            return getPos

        

    def custom_topic_callback(self, msg):
        # 处理 depth_info 话题的消息
        
        x, y, z = msg.data  # 获取三个数字
        # self.get_logger().info(f'Received custom values: x={x}, y={y}, z={z}')
        
        # # 你可以在这里添加更多的逻辑来处理 x, y, z
        
        # print("x是"+str(x))
        # print("x是"+str(y))
        # print("x是"+str(z))
        # 进行逆运动学解算
        joint_angles = self.inverse_kinematics(x, y, z)
        
        # 将关节角度转换为机械臂控制所需的格式
        join1 = self.posGet(joint_angles[0],  1, 1)
        join2 = self.posGet(joint_angles[1],  1, 3)
        join3 = self.posGet(joint_angles[2],  1, 1)
        join4 = self.posGet(joint_angles[3], -1, 1)
        join5 = self.posGet(joint_angles[4], -1, 1)
        
        data = json.dumps({'T':3,'P1':join1,'P2':join2,'P3':join3,'P4':join4,'P5':join5,'S1':0,'S2':0,'S3':0,'S4':0,'S5':0,'A1':60,'A2':60,'A3':60,'A4':60,'A5':60})
        
        ser.write(data.encode())
        print(data)


    def inverse_kinematics(self, x, y, z):
        # 机械臂参数
        L1 = 115.74  # 基座到第一个关节的长度
        L2 = 168.86  # 第一个关节到第二个关节的长度
        L3 = 127.92  # 第二个关节到第三个关节的长度
        L4 = 108.54  # 第三个关节到第四个关节的长度

        # 逆运动学解算
        theta1 =  np.arctan2(y, x)
        r = np.sqrt(x**2 + y**2)
        s = z - L1
        
        # 使用几何法求解
        D = (r**2 + s**2 - L2**2 - L3**2 - L4**2) / (2 * L2 * L3 * L4)
        
        # 检查 D 是否在有效范围内
        if D < -1 or D > 1:
            raise ValueError("Invalid D value: D must be between -1 and 1")
        
        # 计算 theta3
        theta3 = np.arctan2(np.sqrt(1 - D**2), D)
        
        # 计算 K1 和 K2
        K1 = L2 + L3 * np.cos(theta3) + L4 * np.cos(theta3)
        K2 = L3 * np.sin(theta3) + L4 * np.sin(theta3)
        
        # 计算 theta2
        theta2 = np.arctan2(s, r) - np.arctan2(K2, K1)
        
        # 计算 theta4
        theta4 = np.arctan2(np.sin(theta3), np.cos(theta3))
        
        # 假设第五个关节的角度为0
        theta5 = 0
        
        return [theta1, theta2, theta3, theta4, theta5]

def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()