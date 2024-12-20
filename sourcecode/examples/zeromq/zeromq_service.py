import rclpy
from rclpy.node import Node

from std_msgs.msg import String
import zmq
import threading
from example_interfaces.srv import AddTwoInts

class MinimalService(Node):

    def __init__(self):
        super().__init__('minimal_service')
        self.srv = self.create_service(AddTwoInts, 'add_two_ints', self.add_two_ints_callback)

    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info('Incoming request\na: %d b: %d' % (request.a, request.b))

        return response


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