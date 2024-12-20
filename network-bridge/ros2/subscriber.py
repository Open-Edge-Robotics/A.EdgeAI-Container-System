import rclpy
from rclpy.node import Node
from std_msgs.msg import String


'''
현재 클러스터내의 토픽을 수신하여 ZeroMQ로 전송하는 노드
'''
class Subscriber(Node):
    
    def __init__(self, topic, qos_profile=10):
        super().__init__('subscriber')
        self.zeromq_server = None
        self.topic = topic
        self.subscription = self.create_subscription(String, topic, self.listener_callback, qos_profile)
        
    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.data)

        if self.zeromq_server is not None:
            self.zeromq_server.send_message(self.topic, msg.data)

    def setZeroMQServer(self, zeromq_server):
        self.zeromq_server = zeromq_server

    def destroy(self):
        self.destroy_node()