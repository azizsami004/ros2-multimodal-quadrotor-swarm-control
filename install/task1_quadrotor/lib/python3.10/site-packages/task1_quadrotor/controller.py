import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class QuadrotorController(Node):
    def __init__(self):
        super().__init__('quadrotor_controller')
        self.sub = self.create_subscription(Twist, 'command_sender', self.clbk, 10)
        self.pub = self.create_publisher(Twist, '/X3/cmd_vel', 10)

        self.command = Twist()

        
    def clbk(self, msg):
        self.get_logger().info(f"Data received: Linear.x = {msg.linear.x} linear.z = {msg.linear.z} angular.z = {msg.angular.z}")

        self.command.linear.x = msg.linear.x
        self.command.linear.z = msg.linear.z
        self.command.angular.z = msg.angular.z

        self.pub.publish(self.command)


def main(args=None):
    rclpy.init(args=args)
    node = QuadrotorController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()




    