from yolo_interfaces.srv import DetectionObject

import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from std_msgs.msg import String
import zmq




context = zmq.Context()
print("Connecting to hello world server…")
socket = context.socket(zmq.REQ)
#socket.connect("tcp://172.16.11.151:30309")
socket.connect("tcp://172.16.11.151:31067")


class YoloService(Node):

    def __init__(self):
        super().__init__('yolo_service')
        self.srv = self.create_service(DetectionObject, 'yolo_service_instance', self.yolo_service_callback)

    def yolo_service_callback(self, request, response):
        index = request.index
        data = request.data.tobytes()
        b = (str(index)+":").encode()
        s_data = b+data

        socket.send(s_data)
        message = socket.recv()
        colon_index = message.find(b':')
        index_ = int(message[:colon_index].decode('utf-8'))
        result =  message[colon_index+1:].decode('utf-8')

        s = String()
        s.data = result
        ss = [s]

        response.index = index_
        response.result = ss

        return response

def main(args=None):
    rclpy.init(args=args)

    Yolo_service = YoloService()

    rclpy.spin(Yolo_service)

    rclpy.shutdown()

if __name__ == '__main__':
    main()