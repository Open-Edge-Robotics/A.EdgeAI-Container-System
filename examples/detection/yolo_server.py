from collections import UserList
from yolo_interfaces.srv import DetectionObject   # CHANGE

import rclpy
from rclpy.node import Node
from ultralytics import YOLO
import cv2
import numpy as np
import os
import torch
import supervision as sv
from std_msgs.msg import String


device = "cuda" if torch.cuda.is_available() else "cpu"
model = YOLO('yolov8n.pt')


class YoloService(Node):

    def __init__(self):
        super().__init__('yolo_service')
        self.srv = self.create_service(DetectionObject, 'yolo_service_instance', self.add_three_ints_callback)

    def add_three_ints_callback(self, request, response):
        index = request.index
        data = request.data.tobytes()
        encoded_img = np.fromstring(data, dtype = np.uint8)
        frame = cv2.imdecode(encoded_img, cv2.IMREAD_COLOR)

        results = model.predict(conf=0.25,save=False, source=frame)
        detections = sv.Detections.from_ultralytics(results[0])

        labels = [
            model.model.names[class_id]
            for class_id
            in detections.class_id
        ]


        s = []

        for ss in labels:
            sss = String()
            sss.data = ss
            s.append(sss)

        response.index = index
        response.result = s
        self.get_logger().info(f"Incoming request\n index: {response.index}, results: {labels[0]}")

        return response

def main(args=None):
    rclpy.init(args=args)

    Yolo_service = YoloService()

    rclpy.spin(Yolo_service)

    rclpy.shutdown()

if __name__ == '__main__':
    main()