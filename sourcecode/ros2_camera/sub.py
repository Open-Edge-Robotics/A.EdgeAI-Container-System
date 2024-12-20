import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage


from detetions.main import mainMaster
from flask import Flask,render_template,Response
import cv2
import os 
import numpy as np
import cv2
import supervision as sv
from ultralytics import YOLO
import threading


app=Flask(__name__)

data = None

def generate_frames():
    global data

    while True:
        
        np_arr = np.frombuffer(data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        frame=mainMaster(frame)
        ret,buffer=cv2.imencode('.jpg',frame)
        frame=buffer.tobytes()
    
        yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

class Sub(Node):
    def __init__(self):
        super().__init__('camera_subscriber')
        self.subscription = self.create_subscription(
            CompressedImage,
            'image_process',
            self.listener_callback,
            10)
        
        t = threading.Thread(target=self.run)
        t.start()

    def listener_callback(self, msg):
        global data
        data = msg.data


    def run(self):
        while True:
            rclpy.spin_once(sub, timeout_sec=0.001)

rclpy.init(args=None)
sub = Sub()

 
if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port=80)