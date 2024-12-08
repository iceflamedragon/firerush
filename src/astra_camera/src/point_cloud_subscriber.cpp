#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <sensor_msgs/point_cloud2_iterator.hpp>
#include <std_msgs/msg/string.hpp>               // 包含 String 消息类型
#include <std_msgs/msg/float64_multi_array.hpp>  // 包含 Float64MultiArray 消息类型
#include <limits>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>

class DepthSubscriber : public rclcpp::Node {
 public:
  DepthSubscriber() : Node("depth_subscriber") {
    // 设置 QoS 策略
    auto qos = rclcpp::QoS(rclcpp::KeepLast(10)).best_effort();

    // 订阅 PointCloud2 消息深度相机
    subscription_ = this->create_subscription<sensor_msgs::msg::PointCloud2>(
        "/camera/depth/points",  // 修改为正确的主题名称
        qos, std::bind(&DepthSubscriber::listener_callback, this, std::placeholders::_1));

    // 订阅 serial_data 消息openmv
    serial_subscription_ = this->create_subscription<std_msgs::msg::String>(
        "serial_data",  // 修改为正确的主题名称
        qos, std::bind(&DepthSubscriber::serial_callback, this, std::placeholders::_1));

    // 创建发布者，发布 std_msgs::msg::Float64MultiArray 类型的消息给串口节点
    publisher_ = this->create_publisher<std_msgs::msg::Float64MultiArray>("depth_info", qos);
  }

 private:
  void listener_callback(const sensor_msgs::msg::PointCloud2::SharedPtr msg) {
    // 输出图像的行数和列数
    // 使用PointCloud2Iterator遍历点云数据
    sensor_msgs::PointCloud2ConstIterator<float> iter_x(*msg, "x");
    sensor_msgs::PointCloud2ConstIterator<float> iter_y(*msg, "y");
    sensor_msgs::PointCloud2ConstIterator<float> iter_z(*msg, "z");

    // 假设我们想要打印图像坐标系中原点（0, 0）的z值
    int target_u = 1;
    int target_v = 1;

    // 计算目标点的索引
    int target_index = target_v * msg->width + target_u;

    // 遍历点云数据，找到目标点
    for (int i = 0; i < target_index; ++i) {
      ++iter_x;
      ++iter_y;
      ++iter_z;
      float x = *iter_x;
      float y = *iter_y;
      float z = *iter_z;

      // 检查是否为 NaN 值
      if (std::isnan(x) || std::isnan(y) || std::isnan(z)) {
        continue;
      }
    }

    // 打印目标点的z值
    RCLCPP_INFO(this->get_logger(), "Origin point z value: %f", *iter_z);
    auto depth_msg = std::make_shared<std_msgs::msg::Float64MultiArray>();
    depth_msg->data = {100, 0, 1500};  // 发布 x, y, z 三个数字
    publisher_->publish(*depth_msg);

    // for (size_t i = 0; i < msg->width * msg->height; ++i, ++iter_x, ++iter_y, ++iter_z) {
    //   float x = *iter_x;
    //   float y = *iter_y;
    //   float z = *iter_z;

    //   // 检查是否为 NaN 值
    //   if (std::isnan(x) || std::isnan(y) || std::isnan(z)) {
    //     continue;
    //   }

    //   // 计算 x 和 y 坐标
    //   int u = i % msg->width;
    //   int v = i / msg->width;

    //   输出图像左上角 (1, 1) 点的深度
    //   if (u == 0 && v == 0) {
    //     RCLCPP_INFO(this->get_logger(), "Depth at (1, 1): %.2f meters", z);
    //   }

    //   // 输出图像 (5, 10) 点的深度
    //   if (u == 5 && v == 10) {
    //     RCLCPP_INFO(this->get_logger(), "Depth at (5, 10): %.2f meters", z);
    //   }

    //   // 其他处理代码
    //   if (u == 108 && v == 117) {  // 假设你想获取 (1, 2) 点的深度

    //     // 创建并发布消息
    //     auto depth_msg = std::make_shared<std_msgs::msg::Float64MultiArray>();
    //     depth_msg->data = {100, 0, 1500};  // 发布 x, y, z 三个数字
    //     publisher_->publish(*depth_msg);

    //     break;
    //   }
    // }
  }

  void serial_callback(const std_msgs::msg::String::SharedPtr msg) {
    RCLCPP_INFO(this->get_logger(), "Received serial data: %s", msg->data.c_str());
  }

  rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr subscription_;
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr serial_subscription_;
  rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr publisher_;  // 修改发布者类型
};

int main(int argc, char* argv[]) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<DepthSubscriber>());
  rclcpp::shutdown();
  return 0;
}