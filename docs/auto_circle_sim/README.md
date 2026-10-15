# 基于 ROS 的无人车自动画圆仿真

## 运行环境
- Ubuntu 20.04
- ROS Noetic
- Python 3.8

##文件结构
```
src/
└── auto_circle_sim/
├── main.py                # 自动画圆主程序
├── auto_circle_sim.launch # launch 启动文件
├── mkdocs.yml             # mkdocs 文档配置
├── serve.bat              # 一键预览文档脚本
```

## 运行步骤
1. 打开终端，输入 `roscore`
2. 新开终端，进入工作空间，输入 `source devel/setup.bash`
3. 输入 `roslaunch auto_circle_sim auto_circle.launch`
4. rviz 打开后，将 `Fixed Frame` 设为 `map`
5. 添加 `Marker` 显示，Topic 设为 `/vehicle_marker`
6. 观察红色方块自动画出圆形轨迹

## 运行结果
![运行效果](vehicle_circle.gif)

## 大模型声明
代码由本人参考 ROS 官方文档和课程资料编写，未使用大模型生成。
