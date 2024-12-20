import rclpy
from rclpy.node import Node

from std_msgs.msg import String
import zmq
import threading


class Ros2Publisher(Node):

    def __init__(self, node_name, topic_name):
        super().__init__(node_name)
        self.publisher_ = self.create_publisher(String, topic_name, 10)


def zmq_listener(ros2Publisher):
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.bind("tcp://*:5555")
    while True:
        msg = socket.recv()
        print("Received request: %s" % msg)
        ros2Publisher.publisher_.publish(msg)


def main(args=None):
    

    rclpy.init(args=args)

    ros2Publisher = Ros2Publisher('test_publisher', 'chatter')

    thread = threading.Thread(target=zmq_listener, args=(ros2Publisher,))
    thread.start()

    rclpy.spin(ros2Publisher)

    

    ros2Publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()