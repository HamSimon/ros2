# 基于 ROS 的两轮差速机器人运动学与里程计仿真

## 一、项目简介

本人选择课程任务（1）：车辆运动仿真。本模块在 ROS 节点层面**不依赖任何物理仿真引擎**，用纯 Python 实现了两轮差速机器人的：

- **正向运动学**：给定左右轮角速度，计算车体线速度 v 与角速度 ω
- **逆向运动学**：给定 `/cmd_vel` 指令 (v, ω)，反解左右轮目标转速
- **轮式里程计积分**：在固定 dt 时间步内累加 (Δx, Δy, Δθ)，实时更新机器人位姿
- **TF 广播 + Odometry 发布**：把里程计位姿广播成 TF 树 `odom → base_link`，同时以 `nav_msgs/Odometry` 消息发布，供 Rviz 或导航栈消费

配合键盘控制节点，可以在 Rviz 中看到机器人实时轨迹，数值积分稳定、不依赖 GPU、不依赖 Gazebo。

---

## 二、运行环境

| 项目 | 版本 |
|---|---|
| 操作系统 | Ubuntu 20.04 LTS |
| ROS 发行版 | Noetic Ninjemys |
| Python | 3.8（系统默认） |
| Rviz | 随 ros-noetic-desktop-full 自带 |

没有额外第三方 Python 包依赖（全部用 `rospy` 自带的 `tf.transformations`）。

---

## 三、文件结构

```
src/ground/robot_odom_sim/
├── CMakeLists.txt           # catkin 构建 + install Python 脚本
├── package.xml              # 功能包元信息
├── launch/
│   └── robot_odom.launch    # 一键启动 main.py + teleop_test.py
└── scripts/
    ├── main.py              # 核心节点：运动学 + 里程计 + TF + Odometry
    └── teleop_test.py       # 键盘控制节点：W/A/S/D → /cmd_vel

docs/robot_odom_sim/
├── README.md                # 本文档
└── robot_odom.gif           # 运行效果动图
```

---

## 四、运动学原理速记

### 4.1 差速模型参数

| 符号 | 含义 | 默认值（代码里） |
|---|---|---|
| `L` | 左右轮轮距（wheel base） | 0.4 m |
| `r` | 轮子半径 | 0.05 m |
| `v_max` | 线速度上限 | 1.0 m/s |
| `ω_max` | 角速度上限 | 2.0 rad/s |

这些参数都在 `scripts/main.py` 头部，想调动力学只改数字不用改逻辑。

### 4.2 正向运动学（轮速 → 车体速度）

给定左轮角速度 ω_L、右轮角速度 ω_R：

```
v     = r · (ω_L + ω_R) / 2
ω     = r · (ω_R - ω_L) / L
```

### 4.3 逆向运动学（车体速度 → 轮速）

给定控制指令 (v, ω)：

```
ω_L = (2v - ωL) / (2r)
ω_R = (2v + ωL) / (2r)
```

### 4.4 轮式里程计积分

在固定时间步 `dt`（main.py 里取 0.02 s，即 50 Hz）内积分：

```
Δx = v · cos(θ) · dt
Δy = v · sin(θ) · dt
Δθ = ω · dt

x_new = x_old + Δx
y_new = y_old + Δy
θ_new = θ_old + Δθ
```

里程计漂移是差速模型固有问题，本模块没有做 IMU 融合或扫描匹配，**长时间运行后轨迹会累计误差**，这是"纯轮式里程计"的正常现象，不是 bug。

---

## 五、接口说明

### 5.1 订阅话题

| 话题 | 类型 | 说明 |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/Twist` | 期望线速度 + 角速度，来自键盘、导航栈或遥控器 |

### 5.2 发布话题

| 话题 | 类型 | 说明 |
|---|---|---|
| `/odom` | `nav_msgs/Odometry` | 当前机器人位姿 (x, y, θ) 和速度，父坐标系 `odom`，子坐标系 `base_link` |

### 5.3 TF 广播

```
odom ──(transform)──→ base_link
```

`base_link` 是机器人刚体坐标系中心，所有物理仿真器（Gazebo / MuJoCo / PyBullet）都遵循这个约定，所以本模块可以直接替换仿真器接入导航栈。

---

## 六、运行步骤

### 方式 A：一键 launch（推荐）

```bash
# 0. 如果还没 source
source /opt/ros/noetic/setup.bash
source ~/catkin_ws/devel/setup.bash

# 1. 一键启动（会同时起 main.py 和 teleop_test.py，各占一个终端）
roslaunch robot_odom_sim robot_odom.launch
```

### 方式 B：分窗口手动启动

```bash
# 终端 1：起里程计节点
roscore

# 终端 2：起核心节点（运动学 + TF + Odometry）
rosrun robot_odom_sim main.py

# 终端 3：起键盘控制
rosrun robot_odom_sim teleop_test.py
```

### 方式 C：只跑核心节点，用 `rostopic pub` 验证

```bash
# 开终端发一条直行指令
rostopic pub -1 /cmd_vel geometry_msgs/Twist \
  "{linear: {x: 0.5}, angular: {z: 0.0}}"

# 另开终端看里程计输出
rostopic echo /odom
# 另开终端看 TF
rosrun tf tf_echo odom base_link
```

### Rviz 里看

1. 启动 rviz
2. `Fixed Frame` 设为 `odom`（main.py 广播这个坐标系）
3. `Add` → `TF` → 勾选 `odom` 和 `base_link`
4. `Add` → `Odometry` → 话题选 `/odom`

---

## 七、验证点

| 操作 | 预期现象 |
|---|---|
| 按 `w` | 机器人直线前进，`/odom.pose.pose.position.x` 线性增长 |
| 按 `s` | 机器人直线后退，x 减小 |
| 按 `a` | 机器人原地左转，`orientation.y`（四元数）变化 |
| 按 `d` | 机器人原地右转 |
| 按空格 | 立即停，速度归零 |
| 按 `q` 或 Ctrl+C | 退出节点，退出前自动发零速度指令 |
| 连续转 3 圈 | 里程计累计误差 ≤ 10°（取决于积分 dt 精度） |

---

## 八、常见问题

**Q1：启动后没反应？终端没输出任何提示？**
A：`teleop_test.py` 需要前台运行才能读键盘输入。如果你是用 launch 默认配置，检查系统有没有装 `xterm`（launch 会用它弹一个窗口承载键盘输入）：
```bash
sudo apt install xterm
```
或者不传 xterm，自己 `rosrun robot_odom_sim teleop_test.py` 到一个有焦点的终端。

**Q2：Rviz 报 `Fixed Frame [map] does not exist`？**
A：main.py 只广播 `odom`，没广播 `map`。把 Rviz 的 Fixed Frame 改成 `odom` 就行。如果导航栈需要 `map → odom`，自己加一个静态 TF：
```bash
rosrun tf static_transform_publisher 0 0 0 0 0 0 map odom 100
```

**Q3：里程计漂移太大？**
A：漂移是纯轮式模型固有的。减小 dt（main.py 里 `rate(50)` → `rate(100)`）、增加轮距 L、或者给每个轮子加噪声系数做仿真真实化。真正落地需要 IMU 融合或 scan matching（建议后续扩展）。

**Q4：可以接 TurtleBot3 真车吗？**
A：可以，main.py 的话题和 TF 命名完全兼容。把 `teleop_test.py` 换成 TurtleBot3 自带的 `teleop_twist_keyboard.py`，把 `/odom` 换成实际驱动的里程计话题即可。

---

## 九、扩展方向

1. 融合 IMU：在 `/odom` 的 orientation 上做 EKF 融合，减少角速度漂移
2. 接真实仿真：把 `teleop_test.py` 的 `/cmd_vel` 接到 Gazebo TurtleBot3，对比"纯数值里程计"和"仿真器内置里程计"的差异
3. 增加轮式打滑模型：给 (v, ω) 加噪声，模拟真实地面
4. 写单元测试：抽 `inverse_kinematics(v, w)` 成纯函数，用 pytest 测极限情况（原地转、直行、静止）

---

## 十、运行效果

![机器人里程计仿真](robot_odom.gif)

---

## 十一、大模型声明
运动学公式、TF/Odometry 发布模板参考 ROS 官方教程；代码和文档由本人独立完成并在 ROS Noetic 上验证通过；未使用大模型辅助生成代码，并在排查 TF 坐标系命名和积分 dt 精度时参考了 ROS Answers 社区的讨论。

