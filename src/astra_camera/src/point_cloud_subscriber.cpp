#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <sensor_msgs/point_cloud2_iterator.hpp>
#include <limits>

class DepthSubscriber : public rclcpp::Node {
 public:
  DepthSubscriber() : Node("depth_subscriber") {
    // 设置 QoS 策略
    auto qos = rclcpp::QoS(rclcpp::KeepLast(10)).best_effort();

    subscription_ = this->create_subscription<sensor_msgs::msg::PointCloud2>(
        "/camera/depth/points",  // 修改为正确的主题名称
        qos, std::bind(&DepthSubscriber::listener_callback, this, std::placeholders::_1));
  }

 private:
  void listener_callback(const sensor_msgs::msg::PointCloud2::SharedPtr msg) {
    // 打印点云数据的字段信息
    // RCLCPP_INFO(this->get_logger(), "PointCloud2 fields:");
    // for (const auto& field : msg->fields) {
    //   RCLCPP_INFO(this->get_logger(), "  name: %s, offset: %d, datatype: %d, count: %d",
    //               field.name.c_str(), field.offset, field.datatype, field.count);
    // }

    sensor_msgs::PointCloud2ConstIterator<float> iter_x(*msg, "x");
    sensor_msgs::PointCloud2ConstIterator<float> iter_y(*msg, "y");
    sensor_msgs::PointCloud2ConstIterator<float> iter_z(*msg, "z");

    for (size_t i = 0; i < msg->width * msg->height; ++i, ++iter_x, ++iter_y, ++iter_z) {
      float x = *iter_x;
      float y = *iter_y;
      float z = *iter_z;

      // 检查是否为 NaN 值
      if (std::isnan(x) || std::isnan(y) || std::isnan(z)) {
        continue;
      }

      // 计算 x 和 y 坐标
      int u = i % msg->width;
      int v = i / msg->width;

      if (u == 108 && v == 117) {  // 假设你想获取 (1, 2) 点的深度
        RCLCPP_INFO(this->get_logger(), "Depth at (1, 2): %.2f meters", z);
        break;
      }
    }
  }

  rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr subscription_;
};

int main(int argc, char* argv[]) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<DepthSubscriber>());
  rclcpp::shutdown();
  return 0;
}