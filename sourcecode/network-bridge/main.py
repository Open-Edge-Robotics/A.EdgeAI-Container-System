from typing import Union
import rclpy
from fastapi import FastAPI
import os
import sys
import threading
import time
from rclpy.node import Node
import datetime
from typing import List, Dict
from pydantic import BaseModel

base_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(base_dir)

sys.path.append(os.path.join(base_dir, '../utils'))

from kafka_api import KafkaAPI # type: ignore

from ros2.publisher import Publisher
from ros2.subscriber import Subscriber
from zeromq.zeromqserver import ZeroMQServer

                
rclpy.init(args=None)

kafka_api = KafkaAPI('172.16.11.151:31031')

#zeromq_server = ZeroMQServer()

publishers  = {}
subscribers = {}

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/publish/{topic}")
def publish(topic: str):
    if topic not in publishers:
        publishers[topic] = Publisher(topic)

    return {"published": topic}

@app.delete("/publish/{topic}")
def publish_delete(topic: str):
    if topic in publishers:
        publishers.pop(topic).destroy()
        
    return {"unpublished": topic} 
 
@app.post("/subscribe/{topic}")
def subscribe(topic: str):
    if topic not in subscribers:
        subscribers[topic] = Subscriber(topic)
        #subscribers[topic].setZeroMQServer(zeromq_server)
        #zeromq_server.add_ros_subscriber(subscribers[topic])
    return {"subscribed": topic}

@app.delete("/subscribe/{topic}")
def subscribe_delete(topic: str):
    if topic in subscribers:
        #zeromq_server.remove_ros_subscriber(subscribers[topic])
        subscribers.pop(topic).destroy()

    return {"unsubscribed": topic}


@app.get("/agent/status")
async def get_agent_status(agent_id: str):
    return {
        "agent_id": agent_id,
        "cpu_usage": 30,
        "memory_usage": 512,
        "battery": 40,
        "network_quality": "good"
    }

@app.get("/edge/status")
async def get_edge_status(edge_id: str):
    return {
        "edge_id": edge_id,
        "cpu_usage": 50,
        "memory_usage": 2048,
        "pending_tasks": 10
    }

# 서비스 분할 API
class ServiceRequest(BaseModel):
    name: str
    priority: int

class SplitRequest(BaseModel):
    agent_id: str
    services: List[ServiceRequest]
    constraints: Dict[str, int]

@app.post("/service/split")
async def split_service(request: SplitRequest):
    # Dummy logic for service split decision
    return {
        "decision": "split",
        "execution_plan": {
            "agent_services": ["route_planning"],
            "edge_services": ["object_detection"]
        }
    }

# 최적화 API
class OptimizationRequest(BaseModel):
    agent_id: str
    current_state: Dict[str, int]
    metrics: Dict[str, int]

@app.post("/service/optimize")
async def optimize_service(request: OptimizationRequest):
    # Dummy logic for optimization
    return {
        "optimization_suggestion": {
            "agent_services": ["route_planning"],
            "edge_services": ["object_detection"]
        }
    }

# 실행 결과 조회 API
@app.get("/service/status/{agent_id}")
async def get_service_status(agent_id: str):
    return {
        "agent_id": agent_id,
        "current_execution": {
            "agent_services": ["route_planning"],
            "edge_services": ["object_detection"]
        },
        "metrics": {
            "latency": 40,
            "battery": 35
        }
    }

def list_nodes(node):
    nodes = node.get_node_names()
    
    node_list = [{"node": node_name} for node_name in nodes]
    
    return node_list 

def list_topics(node):
    topics = node.get_topic_names_and_types()
    topic_list = [{"topic": topic, "types": types} for topic, types in topics]
    return topic_list

def list_publishers(node, topics):
    publishers = []
    for topic in topics:
        publishers_ = node.get_publishers_info_by_topic(topic['topic'])

        for publisher in publishers_:
            publishers.append({"node": publisher.node_name, "node_namespace": publisher.node_namespace, "topic":topic['topic'], "topic_type": publisher.topic_type})
    return publishers

def list_publishers2(node, nodes):
    publishers = []
    for node_ in nodes:
        publishers_ = node.get_publisher_names_and_types_by_node(node_['node'])

        for publisher in publishers_:
            publishers.append({"node": publisher.node_name, "node_namespace": publisher.node_namespace, "topic_type": publisher.topic_type})
    return publishers

def list_subscribers(node, topics):
    subscribers = []
    for topic in topics:
        subscribers_ = node.get_subscriptions_info_by_topic(topic['topic'])

        for subscriber in subscribers_:
            subscribers.append({"node": subscriber.node_name, "node_namespace": subscriber.node_namespace, "topic":topic['topic'], "topic_type": subscriber.topic_type})

    return subscribers


def list_services(node):
    services = node.get_service_names_and_types()
    service_list = [{"service": service, "types": types} for service, types in services]
    return service_list

def list_actions(node, publishers, subscribers):
    topics = node.get_topic_names_and_types()
    action_servers = []
    for topic, types in topics:
        if topic.endswith('/_action/feedback'):
            action_name = topic.rsplit('/', 2)[0]

            for p in publishers:
                if p['topic'] == topic:
                    action_servers.append({"node":p['node'], "action": action_name, "topic":topic, "types": types})

            for s in subscribers:
                if s['topic'] == topic:
                    action_servers.append({"node":s['node'], "action": action_name, "topic":topic, "types": types})
    return action_servers


def run_monitoring(kafka_api):

    node = Node("broker")

    while True:
        nodes = list_nodes(node)
        topics = list_topics(node)
        publishers = list_publishers(node, topics)
        #publishers_ = list_publishers2(node, nodes)

        subscribers = list_subscribers(node, topics)
        services = list_services(node)
        actions = list_actions(node, publishers, subscribers)

        kafka_api.send('ros_info', {
            'node': nodes,
            'topics': topics,
            'publishers': publishers,
            'subscribers': subscribers,
            'services': services,
            'actions' : actions,
            'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        time.sleep(1)

def start_module():
    alive_thread = threading.Thread(target=run_monitoring, args=(kafka_api,))
    alive_thread.daemon = True
    alive_thread.start()
    
start_module()