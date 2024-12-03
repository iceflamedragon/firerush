import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import serial

class SerialReaderNode(Node):
    def __init__(self):
        super().__init__('serial_reader_node')
        self.publisher_ = self.create_publisher(String, 'serial_data', 10)
        self.serial_port = '/dev/ttyTHS1'  # 修改为你的串口设备
        self.baud_rate = 9600  # 修改为你的波特率
        self.serial_conn = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
        self.timer = self.create_timer(0.1, self.read_serial)

    def read_serial(self):
        if self.serial_conn.in_waiting > 0:
            data = self.serial_conn.readline().decode('latin1').strip()
            self.get_logger().info(f'Received: {data}')
            msg = String()
            msg.data = data
            self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = SerialReaderNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()