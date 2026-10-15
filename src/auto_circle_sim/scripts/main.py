#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import String
import random

def autonomous_driving():
    rospy.init_node('autonomous_obstacle_avoidance', anonymous=True)
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    status_pub = rospy.Publisher('/vehicle_status', String, queue_size=10)
    rate = rospy.Rate(1)

    distance = 10.0

    while not rospy.is_shutdown():
        twist = Twist()
        distance = distance - random.uniform(0.5, 2.0)

        if distance > 3.0:
            twist.linear.x = 1.0
            twist.angular.z = 0.0
            status = "前方无障碍，继续直行（剩余距离: %.2f 米）" % distance
            rospy.loginfo(status)
        elif distance > 1.0:
            twist.linear.x = 0.5
            twist.angular.z = 0.5
            status = "检测到障碍物，向左转向避让（距离: %.2f 米）" % distance
            rospy.logwarn(status)
        else:
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            status = "距离过近，紧急停车！（距离: %.2f 米）" % distance
            rospy.logerr(status)
            break

        pub.publish(twist)
        status_pub.publish(status)
        rate.sleep()

if __name__ == '__main__':
    try:
        autonomous_driving()
    except rospy.ROSInterruptException:
        pass
