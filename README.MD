source install/setup.bash
sudo chmod 777 /dev/ttyUSB0
ros2 launch roarm roarm.launch.py
ros2 run serial_ctrl serial_ctrl

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

point_cloud_subscriber是处理节点