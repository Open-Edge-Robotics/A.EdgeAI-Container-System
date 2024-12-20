import zmq
import time
import threading
from rclpy.executors import MultiThreadedExecutor

'''
Zero MQ 특성상 PUB에서 서버를 바인딩한다.
'''
class ZeroMQServer:
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://*:5555")
        self.isrunning = True
        self.subscribers = {}
        self.executor = MultiThreadedExecutor(num_threads=20)
        self.t = threading.Thread(target=self.run)
        self.t.start()
        
 
    def stop(self):
        self.isrunning = False
        self.t.join()
        self.socket.close()
        self.context.term()

    def add_ros_subscriber(self, subscriber):
        self.subscribers[subscriber.topic] = subscriber
        self.executor.add_node(subscriber)

    def remove_ros_subscriber(self, subscriber):
        self.executor.remove_node(subscriber)
        self.subscribers.pop(subscriber.topic)

    def send_message(self, topic, msg):
        self.socket.send_string(topic + " " + msg)

    def run(self):
        while self.isrunning:
            self.executor.spin_once(timeout_sec=0.001)
            if len(self.subscribers) == 0:
                time.sleep(0.1)



        

