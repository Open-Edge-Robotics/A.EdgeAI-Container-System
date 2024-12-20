from yolo_interfaces.srv import DetectionObject

import rclpy
from rclpy.node import Node
import zmq
import threading
from time import sleep
import cv2
import numpy
import zmq
from datetime import datetime
import time


def current_milli_time():
    return round(time.time() * 1000)

cap = cv2.VideoCapture(0)
if cap.isOpened() == 0:
    exit(-1)

# Set the video resolution to HD720 (2560*720)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)



class JetsonClientAsync(Node):

    def __init__(self):
        super().__init__('jetson_client_async')
        self.cli = self.create_client(DetectionObject, 'yolo_service_instance')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = DetectionObject.Request()

    def send_request(self, index, data):
        self.req.index = index
        self.req.data =  data
        self.future = self.cli.call_async(self.req)


def main(args=None):
    rclpy.init(args=args)
    down_width = 640
    down_height = 180
    down_points = (down_width, down_height)

    detection_client = JetsonClientAsync()
    times = {}
    index = 1
    while True:
        retval, frame = cap.read()
        resized_down = cv2.resize(frame, down_points, interpolation= cv2.INTER_LINEAR)
        retval, buf = cv2.imencode('.webp',resized_down, [cv2.IMWRITE_WEBP_QUALITY, 100])
        times[index] = current_milli_time()
        detection_client.send_request(index, buf.tobytes())
        while rclpy.ok():
            rclpy.spin_once(detection_client)

            if detection_client.future.done():
                try:
                    response = detection_client.future.result()
                except Exception as e:
                    detection_client.get_logger().info(
                        'Service call failed %r' % (e,))
                else:
                    #r = f"{response.index}:{response.result[0].data}"
                    print(f"({response.index}:{response.result[0].data})Time taken: {current_milli_time()-times[response.index]} ms")
                break

        index += 1

    rclpy.shutdown()

if __name__ == '__main__':
    main()