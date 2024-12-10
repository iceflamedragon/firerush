source install/setup.bash
sudo chmod 777 /dev/ttyUSB0
sudo chmod 777 /dev/ttyTHS1
ros2 launch roarm roarm.launch.py
ros2 run serial_ctrl serial_ctrl
openmv的图像x(-80,80),y(-60,60)

ros2 run astra_camera point_cloud_subscriber
##Starting the camera

● In terminal 1

```bash
source /opt/ros/humble/setup.bash 
source ./install/setup.bash 
ros2 launch astra_camera astra_mini.launch.py
```

● In terminal 2

```bash
source /opt/ros/humble/setup.bash 
source ./install/setup.bash 
rviz2 -d src/ros2_astra_camera/astra_camera/rviz/pointcloud.rviz

point_cloud_subscriber是处理节点，订阅深度相机，串口接受信息(openmv),给机械臂传数据 （连上之后取消gui，只用普通程序）
jetson已接受到串口信息，是ttyTHS1，
新建立了一个节点读取串口信息
激光雷达     
深度图480rows，640cols