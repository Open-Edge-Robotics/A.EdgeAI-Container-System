import rclpy
from rclpy.node import Node
import cv2


from sensor_msgs.msg import CompressedImage



class Pub(Node):
    def __init__(self):
        super().__init__('camera_publisher')
        self.publisher_ = self.create_publisher(CompressedImage, 'image_process', 10)
        

    def run(self):
        camera=cv2.VideoCapture('test.mp4')
        msg = CompressedImage()


        msg.format = "jpeg"
        msg.header.frame_id = "camera"
        
        msg.data = b"Hello, world!"
        self.publisher_.publish(msg)

        while True:
            success,frame=camera.read()
            if not success:
                camera=cv2.VideoCapture('test.mp4')
                continue
            else:
                ret,buffer=cv2.imencode('.jpg',frame)
                frame=buffer.tobytes()
                msg.data = frame
                msg.header.stamp = self.get_clock().now().to_msg()
                self.publisher_.publish(msg)


rclpy.init(args=None)

pub = Pub()
pub.run()

