#!/usr/bin/env python3
import rospy
import math
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from visualization_msgs.msg import Marker

class LidarAvoidance:
    def __init__(self):
        rospy.init_node('lidar_avoidance_sim')
        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.scan_pub = rospy.Publisher('/scan', LaserScan, queue_size=10)
        self.car_pub = rospy.Publisher('/car_visual', Marker, queue_size=10)
        self.wall_pub = rospy.Publisher('/wall_visual', Marker, queue_size=10)
        
        self.rate = rospy.Rate(10)
        
        # 车从正中间出生
        self.x = 2.5
        self.y = 0.0
        self.theta = 0.0

        # 四面墙，彻底封死
        self.obstacles = [
            (5.0, 0.0, 0.5, 8.0),   # 右墙
            (0.0, 0.0, 0.5, 8.0),   # 左墙
            (2.5, 4.0, 5.5, 0.5),   # 上墙
            (2.5, -4.0, 5.5, 0.5)   # 下墙
        ]

    def draw_obstacles(self):
        for i, (x, y, sx, sy) in enumerate(self.obstacles):
            wall = Marker()
            wall.header.frame_id = "map"
            wall.header.stamp = rospy.Time.now()
            wall.ns = "walls"
            wall.id = i
            wall.type = Marker.CUBE
            wall.action = Marker.ADD
            wall.pose.position.x = x
            wall.pose.position.y = y
            wall.pose.position.z = 0.5
            wall.scale.x = sx
            wall.scale.y = sy
            wall.scale.z = 1.0
            wall.color.r = 0.5
            wall.color.g = 0.5
            wall.color.b = 0.5
            wall.color.a = 1.0
            self.wall_pub.publish(wall)

    def draw_car(self):
        car = Marker()
        car.header.frame_id = "map"
        car.header.stamp = rospy.Time.now()
        car.ns = "car"
        car.id = 0
        car.type = Marker.CUBE
        car.action = Marker.ADD
        car.pose.position.x = self.x
        car.pose.position.y = self.y
        car.pose.position.z = 0.2
        car.pose.orientation.z = math.sin(self.theta / 2)
        car.pose.orientation.w = math.cos(self.theta / 2)
        car.scale.x = 1.0
        car.scale.y = 0.6
        car.scale.z = 0.4
        car.color.r = 0.0
        car.color.g = 0.5
        car.color.b = 1.0
        car.color.a = 1.0
        self.car_pub.publish(car)

    def check_collision(self, nx, ny):
        # 严密的碰撞检测，提前 0.6 米预判
        for ox, oy, sx, sy in self.obstacles:
            if (abs(nx - ox) < (sx / 2.0 + 0.6)) and (abs(ny - oy) < (sy / 2.0 + 0.6)):
                return True
        return False

    def run(self):
        print("仿真启动，小车在封闭房间内进行碰撞检测与自主避障...")
        while not rospy.is_shutdown():
            self.draw_obstacles()
            self.draw_car()

            # 发雷达数据
            scan = LaserScan()
            scan.header.frame_id = "map"
            scan.header.stamp = rospy.Time.now()
            scan.angle_min = -1.57
            scan.angle_max = 1.57
            scan.angle_increment = 3.14 / 10
            scan.range_min = 0.1
            scan.range_max = 10.0
            scan.ranges = [1.0] * 10
            self.scan_pub.publish(scan)

            twist = Twist()
            
            # 默认往前走
            twist.linear.x = 0.6
            twist.angular.z = 0.0

            # 计算下一步位置
            dt = 0.1
            nx = self.x + twist.linear.x * math.cos(self.theta) * dt
            ny = self.y + twist.linear.x * math.sin(self.theta) * dt
            
            # 如果下一步会撞墙，就原地强行转向
            if self.check_collision(nx, ny):
                twist.linear.x = 0.0
                twist.angular.z = 1.5  # 疯狂打方向盘
                nx = self.x
                ny = self.y

            self.x = nx
            self.y = ny
            self.theta += twist.angular.z * dt

            self.cmd_pub.publish(twist)
            self.rate.sleep()

if __name__ == '__main__':
    try:
        node = LidarAvoidance()
        node.run()
    except rospy.ROSInterruptException:
        pass
