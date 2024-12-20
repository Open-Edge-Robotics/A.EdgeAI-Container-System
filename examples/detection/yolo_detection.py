from yolo_interfaces.srv import DetectionObject

import rclpy
from rclpy.node import Node
import zmq
import threading
from time import sleep

def zmq_listener(detection_client):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    while True:
        msg = socket.recv()
        detection_client.send_request(msg)
        while rclpy.ok():
            rclpy.spin_once(detection_client)

            if detection_client.future.done():
                try:
                    response = detection_client.future.result()
                except Exception as e:
                    detection_client.get_logger().info(
                        'Service call failed %r' % (e,))
                else:
                    r = f"{response.index}:{response.result[0].data}"
                    socket.send(r.encode('utf-8'))
                break

class DetectionClientAsync(Node):

    def __init__(self):
        super().__init__('detection_client_async')
        self.cli = self.create_client(DetectionObject, 'yolo_service_instance')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = DetectionObject.Request()

    def send_request(self, msg):

        colon_index = msg.find(b':')
        self.req.index = int(msg[:colon_index].decode('utf-8'))
        self.req.data =  msg[colon_index+1:]
        self.future = self.cli.call_async(self.req)


def main(args=None):
    rclpy.init(args=args)

    detection_client = DetectionClientAsync()

    thread = threading.Thread(target=zmq_listener, args=(detection_client,))
    thread.start()

    while True:
        sleep(1)

    rclpy.shutdown()

if __name__ == '__main__':
    main()