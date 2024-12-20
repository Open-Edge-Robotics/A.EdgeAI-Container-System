import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node

from action_tutorials_interfaces.action import Fibonacci
import zmq
import threading

def zmq_listener(action_server):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    while True:
        msg = socket.recv()
        socket.send(b"World")
        action_server.publisher_.publish(msg)

class Ros2ActionServer(Node):

    def __init__(self):
        super().__init__('fibonacci_action_server')
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            self.execute_callback)

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')
        result = Fibonacci.Result()
        return result


def main(args=None):
    rclpy.init(args=args)

    action_server = Ros2ActionServer()

    thread = threading.Thread(target=zmq_listener, args=(action_server,))
    thread.start()

    rclpy.spin(action_server)


if __name__ == '__main__':
    main()