from pymongo import MongoClient
from kubernetes.client.rest import ApiException 
import pprint
from   kubernetes import client, config

config.load_kube_config()
v1 = client.CoreV1Api()
'''
[ { 'cluster_name':'c1', 'host_name':'c1', 'cluster_ip':'129.111.123.120', 
    'worker_nodes':[ {'worker_node_name':'w1','worker_node_ip','129.111.123.121'},
                     {'worker_node_name':'w2','worker_node_ip','129.111.123.122'}
                   ] 
  },

  { 'cluster_name':'c2', 'host_name':'c2', 'cluster_ip':'129.111.123.130', 
    'worker_nodes':[ {'worker_node_name':'w1','worker_node_ip','129.111.123.131'},
                     {'worker_node_name':'w2','worker_node_ip','129.111.123.132'}
                   ] 
  }
]
'''
def get_cluster_info():
    ready_nodes = []
    for n in v1.list_node().items:
        for status in n.status.conditions:
            #print("status",status)
            if status.status == "True" and status.type == "Ready":
                print("metadata.name",n.metadata.name)
                ready_nodes.append(n.metadata.name)
    print("ready_nodes : ", ready_nodes)
    
    worker_nodes_list = []
    master_node_dic = {}
    
    for node_name in ready_nodes :
        t_node_data = v1.read_node(node_name)
        print(t_node_data.metadata.labels)
        if 'node-role.kubernetes.io/master' in t_node_data.metadata.labels :
            print(node_name, 'is master node')
            master_node_dic['cluster_name'] = node_name 
            print(t_node_data.status.addresses)
            for addr in t_node_data.status.addresses :
                if addr.type ==  'InternalIP':
                    master_node_dic['cluster_ip'] = addr.address
                elif addr.type == 'Hostname' :
                    master_node_dic['host_name'] = addr.address
        else :
            print(node_name, 'is worker node')
            worker_node_dic = {}
            worker_node_dic['worker_node_name'] = node_name
            for addr in t_node_data.status.addresses :
                if addr.type ==  'InternalIP':
                    worker_node_dic['worker_node_ip'] = addr.address
            worker_nodes_list.append(worker_node_dic)
    master_node_dic['worker_nodes'] = worker_nodes_list

    print('master_node_dic',master_node_dic)
    return master_node_dic

client = MongoClient('129.254.202.111', 30017)
#client = MongoClient('mongodb://root:gm1324@129.254.202.111:30017/')
print('connect client')
print('client=',client)

#print(client.list_database_names())
print('==================')
db = client['mydb']
collection = db['myCol']

result2= get_cluster_info()


result = collection.insert_one({'name': 'John Doe', 'age': 29})
print(f'Inserted document ID: {result.inserted_id}')

# 데이터 조회
for doc in collection.find():
    print(doc)

collection.drop()


