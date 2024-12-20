import rclpy
from rclpy.node import Node
from std_msgs.msg import String


'''
현재 상대 클러스터의 zeromq 서버로 부터 수신하고 토픽을 현재 클러스터 내로 송신하는 노드
'''
class Publisher(Node):

    def __init__(self, topic, qos_profile=10):
        super().__init__('publisher')
        self.topic = topic
        self.publisher = self.create_publisher(String, topic, qos_profile)

    def destroy(self):
        self.destroy_node()