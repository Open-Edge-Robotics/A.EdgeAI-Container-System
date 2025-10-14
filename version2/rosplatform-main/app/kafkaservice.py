from asyncio import queues
from kafka import KafkaConsumer, KafkaProducer
from json import loads, dumps
import socket
import threading
from time import sleep
import os
import time
import random
import datetime
from .kafkamessage import KafkaMessage, KafkaStatus, ClusterStatusMessage
import asyncio
from .scheduler import request_kube_api, response_kube_api, set_kafka_api
from .database import MongoDB


#request_queue = asyncio.Queue()



def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip
 
def get_hostname():
    hostname = socket.gethostname()
    return hostname

def create_consumer(topic, group_id, kafka_server='localhost:9092'):
    return KafkaConsumer(
        topic,
        api_version=(0,11,5),
        bootstrap_servers=[kafka_server],
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id=group_id,
        value_deserializer=lambda x: loads(x.decode('utf-8')),
        consumer_timeout_ms=1000
    )


class KafkaAPI:
    def __init__(self, server, isManager=False):
        self.server = server
        self.name = f"{get_hostname()}-{threading.current_thread().name}-{time.time()}"
        self.ip = get_local_ip()
        self.producer = KafkaProducer(bootstrap_servers=[self.server],
                                      api_version=(0,11,5),             
                                      value_serializer=lambda x: dumps(x).encode('utf-8'))
        
        self.consumers = []
        self.clusters = {}
        self.ros_bridge = {}
        
    def create_consumer(self, topic):
        consumer = create_consumer(topic, self.name, kafka_server=self.server)
        #print(consumer.config)
        #print(consumer.bootstrap_connected())
        try:
            consumer.poll(timeout_ms=3000)
            b = consumer.assignment()

            for cc in b:
                (topic, partition) = cc
                if partition != 0: 
                    consumer.seek_to_end()
                    consumer.position(consumer.assignment().pop())
                    break

        except Exception as e:
            print(f"Error Occur in create_consumer {e}", flush=True)

        self.consumers.append(consumer)
        return consumer

    def send(self, topic, data):
        self.producer.send(topic, value=data)
        self.producer.flush()


    def run_alive(self):
        pass

    def close(self):

        self.producer.close()
        
        for consumer in self.consumers:
            consumer.close()

    def process_msg(self, msg):
        try:
            message = KafkaMessage.model_validate(msg.value)
        
            match message.type:
                case 'status':
                    self.process_status(msg.value)
                case 'cluster':
                    self.process_cluster_info(msg.value)
                case _:
                    print(f"Unknown topic {msg}", flush=True)

        except Exception as e:
            print(f"Error Occur in process_msg {msg}: {e}", flush=True)

    def process_ros_info(self, msg):
        data = msg.value

        data['received_time'] = time.time()
        self.ros_bridge[data['bridge_name']] = data


    def process_status(self, value):
        status = KafkaStatus.model_validate(value)
        print(status)

        if value['cluster_name'] not in self.clusters:
            self.clusters[value['cluster_name']] = {'cluster_name': value['cluster_name'], 'status': 'dead', 'timestamp': value['timestamp']}

        if value['status'] == 'alive':
            self.clusters[value['cluster_name']]['status'] = 'alive'
            self.clusters[value['cluster_name']]['timestamp'] = value['timestamp']
        else:
            self.clusters.pop(value['cluster_name'])

    def process_cluster_info(self, value):
        self.clusters[value['cluster_name']] = value


    async def process_started(self, value):
        
        bridge_name = value['bridge_name']

        _connections = await MongoDB.get_all('connections', {'$or': [{'from_bridge': bridge_name}, {'to_bridge': bridge_name}]})

        for _connection in _connections:
            self.send('connect_bridge', {'no': _connection['id'], 'from_bridge': _connection['from_bridge'], 'to_bridge': _connection['to_bridge'], 'type': _connection['type'], 'name': _connection['name'], 'types': _connection['types'], 'from_zeromq': _connection['from_zeromq'], 'to_zeromq': _connection['to_zeromq']})

    async def start_action(self):

        _connections = await MongoDB.get_all('connections', {})
        for _connection in _connections:
            self.send('connect_bridge', {'no': _connection['id'], 'from_bridge': _connection['from_bridge'], 'to_bridge': _connection['to_bridge'], 'type': _connection['type'], 'name': _connection['name'], 'types': _connection['types'], 'from_zeromq': _connection['from_zeromq'], 'to_zeromq': _connection['to_zeromq']})




kafka_hostname = os.getenv('KAFKA_HOST_NAME')

if kafka_hostname is None:
    kafka_hostname = '172.16.11.151:31031'

kafka_api = KafkaAPI(kafka_hostname, True)


set_kafka_api(kafka_api)

threads = []
consumers = []


def run_listener(kafka_api: KafkaAPI):
    # check broker status
    consumer = kafka_api.create_consumer('cluster_info')
    consumers.append(consumer)

    while True:
        try:
            for message in consumer:
                kafka_api.process_msg(message)
        except Exception as e:
            print(f"Error Occur in run_listener {e}", flush=True)
            break


def run_response(kafka_api: KafkaAPI):

    consumer = kafka_api.create_consumer('response')
    consumers.append(consumer)

    while True:
        try:
            for message in consumer:
                response_kube_api(message.value)
        except Exception as e:
            print(f"Error Occur in run_response {e}", flush=True)
            break


def run_ros2(kafka_api: KafkaAPI):
    consumer = kafka_api.create_consumer('ros_info')
    consumers.append(consumer)

    while True:
        try:
            for message in consumer:
                kafka_api.process_ros_info(message)
        except Exception as e:
            print(f"Error Occur in run_ros2 {e}", flush=True)
            break


async def ros_started(kafka_api: KafkaAPI):
    consumer = kafka_api.create_consumer('started')
    consumers.append(consumer)

    while True:
        try:
            for message in consumer:
                await kafka_api.process_started(message.value)
        except Exception as e:
            print(f"Error Occur in ros_started {e}", flush=True)
            break

'''
def run_status(kafka_api: KafkaAPI):
    consumer = kafka_api.create_consumer('status')
    consumers.append(consumer)

    while True:
        try:
            for message in consumer:
                kafka_api.process_status(message)
        except Exception as e:
            print(f"Error Occur in run_status {e}", flush=True)
            break
'''

def start_module():
    alive_thread = threading.Thread(target=run_listener, args=(kafka_api,))
    alive_thread.daemon = True
    alive_thread.start()
    threads.append(alive_thread)


    response_thread = threading.Thread(target=run_response, args=(kafka_api,))
    response_thread.daemon = True
    response_thread.start()
    threads.append(response_thread)


    ros2_thread = threading.Thread(target=run_ros2, args=(kafka_api,))
    ros2_thread.daemon = True
    ros2_thread.start()
    threads.append(ros2_thread)


    started_thread = threading.Thread(target=ros_started, args=(kafka_api,))
    started_thread.daemon = True
    started_thread.start()
    threads.append(started_thread)

    kafka_api.send('webserver_info', {'type': 'webserver_status', 'cluster_name': kafka_api.name, 'status': 'alive', 'timestamp': time.time()})



def stop_module():

    for consumer in consumers:
        consumer.close()

    for thread in threads:
        thread.join()


def get_clusters_info():
    return kafka_api.clusters

def get_ros_info():

    remove_keys = []

    for key, value in kafka_api.ros_bridge.items():
        date = value['received_time']
        if time.time() - date > 20:
            value['status'] = 'dead'

        if time.time() - date > (60):
            remove_keys.append(key)
        
    for key in remove_keys:
        kafka_api.ros_bridge.pop(key)

    #print(len(kafka_api.ros_bridge))
        
    return kafka_api.ros_bridge


def get_kafka_api():
    return kafka_api


