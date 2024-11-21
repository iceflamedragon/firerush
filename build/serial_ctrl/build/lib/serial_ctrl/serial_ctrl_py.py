import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import serial
import json

# 初始化串口连接
ser1 = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)
ser2 = serial.Serial("/dev/ttyACM0", 115200, timeout=1)

class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('serial_ctrl')
        
        self.position = []
        
        self.subscription = self.create_subscription(
            JointState,
            'joint_states',
            self.listener_callback,
            10)
        self.subscription  # 防止未使用的变量警告
    
    def posGet(self, radInput, direcInput, multiInput):
        if radInput == 0:
            return 2047
        else:
            getPos = int(2047 + (direcInput * radInput / 3.1415926 * 2048 * multiInput) + 0.5)
            return getPos

    def listener_callback(self, msg):
        try:
            a = msg.position
            
            # 数据验证
            if len(a) < 5:
                self.get_logger().warning("Received JointState message with insufficient data.")
                return
            
            # 第一个串口的数据
            join1_1 = self.posGet(a[0], -1, 1)
            join2_1 = self.posGet(a[1], -1, 3)
            join3_1 = self.posGet(a[2], -1, 1)
            join4_1 = self.posGet(a[3],  1, 1)
            join5_1 = self.posGet(a[4], -1, 1)
            
            # 准备第一个字节数据
            data1 = json.dumps({'T':0,'P1':5000,'P2':50,'P3':50,'P4':110,'P5':110,'S1':110,'S2':110,'S3':1111110,'S4':0,'S5':0,'A1':0,'A2':0,'A3':0,'A4':0,'A5':0})

            
            ser1.write(data1.encode())

            # 准备第二个字节数据
            data2 = bytearray([0x7B, 0x00, 0x00, 0x00, 0x30, 0x00, 0x00, 0x00, 0x00, 0x4B, 0x7D])
            
            ser2.write(data2)
            self.get_logger().info(f"Sent data to /dev/ttyACM0: {data2.hex()}")
        
        except Exception as e:
            self.get_logger().error(f"Error in listener_callback: {e}")

    def send_shutdown_data(self):
        try:
            # 发送关闭时的特定数据
            shutdown_data1 = json.dumps({'T':0,'P1':5000,'P2':50,'P3':50,'P4':110,'P5':110,'S1':110,'S2':110,'S3':1111110,'S4':0,'S5':0,'A1':0,'A2':0,'A3':0,'A4':0,'A5':0})
            ser1.write(shutdown_data1.encode())

            shutdown_data2 = bytearray([0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x7B, 0x7D])
            ser2.write(shutdown_data2)
            self.get_logger().info(f"Sent shutdown data to /dev/ttyACM0: {shutdown_data2.hex()}")
        except Exception as e:
            self.get_logger().error(f"Error sending shutdown data: {e}")

    def __del__(self):
        if ser1.is_open:
            ser1.close()
            self.get_logger().info("Serial connection to /dev/ttyUSB0 closed.")
        if ser2.is_open:
            ser2.close()
            self.get_logger().info("Serial connection to /dev/ttyACM0 closed.")

def main(args=None):
    rclpy.init(args=args)
    minimal_subscriber = MinimalSubscriber()
    try:
        rclpy.spin(minimal_subscriber)
    except KeyboardInterrupt:
        minimal_subscriber.get_logger().info("Node interrupted by user.")
        minimal_subscriber.send_shutdown_data()    
    finally:
        minimal_subscriber.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()


