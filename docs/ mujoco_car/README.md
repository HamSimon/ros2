# 基于 Mujoco 的两轮小车运动仿真

## 任务说明
本人选择任务（1）：车辆运动仿真，使用 Mujoco 物理引擎对两轮小车进行运动仿真，通过 launch 启动仿真程序。

## 运行环境
- Windows 10/11 或 Ubuntu 20.04
- Python 3.8+
- Mujoco 3.15.0
- ROS Noetic（用于 launch 启动）

## 依赖安装
1. 安装 Mujoco：
   pip install mujoco
2. 安装 ROS Noetic（Ubuntu 环境）。

## 运行步骤
1. 打开终端，输入 `roscore`
2. 新开终端，输入 `roslaunch mujoco_sim mujoco_sim.launch`
3. 观察 Mujoco 窗口中红色小车在灰色地面上向前移动

## 运行结果
![运行效果](mujoco_car.gif)

## 大模型声明
代码由本人参考 Mujoco 官方文档和课程资料编写，未使用大模型生成。
