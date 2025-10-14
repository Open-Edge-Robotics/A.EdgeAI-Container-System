import asyncio
import time
import threading
import json
import copy

request_queue = asyncio.Queue()
request_thread_queue = asyncio.Queue()
request_number = 0
timeout = 5

kafka_api = None

def set_kafka_api(kafka_api_):
    global kafka_api
    kafka_api = kafka_api_

def get_kafka_api():
    global kafka_api
    return kafka_api


def get_list_count(list_data):

    count = 0

    for data in list_data:
        if isinstance(data, list):
            count += get_list_count(data)

    return count + len(list_data)


def get_cluster_list(list_data):
    clusters = []
    for data in list_data:
        if isinstance(data, list):
            clusters.extend(get_cluster_list(data))
        else:
            clusters.append(data)
    return clusters

async def request_kube_api(request_data): 
    global request_number, kafka_api
    


    priority = request_data.get('priority', 'setcluster')

    request_number += 1
    request_data['request_number'] = request_number

    in_request_number = request_number


    if priority == 'setcluster' or priority == 'simple':
        
        print(f"Request sent: {request_data['request_number']}")
        kafka_api.send('request', request_data)

        start_time = time.time()
        request_data['date'] = start_time


        while True:
            if time.time() - start_time > timeout:
                # Timeout reached
                return {"status": "error", "message": "Request timeout"}

            # Check queue for matching request
            try:
                response = request_queue.get_nowait()
                if response.get('request_number') == request_number:
                    return {"status": "success", "response": response, "cluster": request_data['target_cluster']}
                else:

                    if time.time() - request_data['date'] < 60:
                        request_queue.put_nowait(response)
            except asyncio.QueueEmpty:
                # Queue is empty, wait briefly before checking again
                await asyncio.sleep(0.1)
                
    else:
        present_clusters = request_data.get('present_clusters', [])
        present_clusters = json.loads(present_clusters)
        request_data['present_clusters'] = present_clusters

        cluster_count = len(get_cluster_list(present_clusters))

        thread = threading.Thread(target=run_scheduler, args=(request_data,))
        thread.start()

        start_time = time.time()

        request_data['date'] = start_time

        while True:
            if time.time() - start_time > timeout * cluster_count:
                print(f"Request timeout: {in_request_number}")
                break
            try:
                response = request_thread_queue.get_nowait()
                if response.get('request_number') == in_request_number:
                    return response
                else:
                    if time.time() - request_data['date'] < 60:
                        request_thread_queue.put_nowait(response)
            except asyncio.QueueEmpty:
                time.sleep(0.1)

        
        
        return {"status": "error", "message": f"Request timeout {in_request_number}"}
            



def response_kube_api(response_data):
    print(f"Response received: {response_data['request_number']}")
    request_queue.put_nowait(response_data)



def run_scheduler(request_data):


    request_data = copy.deepcopy(request_data)

    priority = request_data.get('priority', 'setcluster')
    org_request_number = request_data['request_number']

    
    if priority == 'selectedcluster':
        present_clusters = request_data.get('present_clusters', [])

        clusters = get_cluster_list(present_clusters)
        

        response_date = None
        err_reason_response = []

        for cluster in clusters:
            start_time = time.time()

            req_request_number = f"{start_time}_{cluster}"

            request_data = copy.deepcopy(request_data)

            request_data['date'] = start_time
            
            request_data['request_number'] = req_request_number
            request_data['target_cluster'] = cluster

            print(f"Request sent: selectedcluster {request_data['request_number']} to {cluster}")
            kafka_api.send('request', request_data)

            while True:
                if time.time() - start_time > timeout:
                    print(f"Request timeout: {req_request_number}")
                    err_reason_response.append({"request_number": req_request_number, "status": "error", "message": "Request timeout", "cluster": request_data['target_cluster']})
                    break
                try:
                    response = request_queue.get_nowait()
                    if response.get('request_number') == req_request_number:
                        if response.get('status') == 200:
                            response_date = response
                            request_thread_queue.put_nowait({"request_number": org_request_number, "status": "success", "response": response_date, "cluster": request_data['target_cluster']})
                            return
                        else:
                            err_reason_response.append(response)
                        break
                    else:
                        if time.time() - request_data['date'] < 60:
                            request_queue.put_nowait(response)
                except asyncio.QueueEmpty:
                    # Queue is empty, wait briefly before checking again
                    time.sleep(0.1)

        if response_date is not None:
            request_thread_queue.put_nowait({"request_number": org_request_number, "status": "success", "response": response_date, "cluster": request_data['target_cluster']})
        else:
            request_thread_queue.put_nowait({"request_number": org_request_number, "status": "error", "message": err_reason_response})
    elif priority == 'lowlatency':
        if kafka_api is not None:

            present_clusters = request_data.get('present_clusters', [])
            clusters = get_cluster_list(present_clusters)

            print(f"check clusters lowlatency time for {clusters}")

            lowlatency_clusters = []

            for cluster in clusters:
                if cluster in kafka_api.clusters:
                    lowlatency_clusters.append(cluster)

            if len(lowlatency_clusters) == 0:
                print(f"No lowlatency clusters found for {clusters}")
                request_thread_queue.put_nowait({"request_number": org_request_number, "status": "error", "message": f"No lowlatency clusters found for {clusters}"})
                return

            ping_results = []

            for cluster in lowlatency_clusters:
                if cluster in kafka_api.clusters:
                    nodes = kafka_api.clusters[cluster]['nodes']
                    for node_name in nodes:
                        node = nodes[node_name]
                        ping_time = node['ping_time']
                        ping_results.append({"cluster": cluster, "node_name": node_name, "ping_time": ping_time})


            print("-------------------------------- start ping results --------------------------------")
            for ping_result in ping_results:
                print(f"ping_result: {ping_result}")
            print("-------------------------------- end ping results --------------------------------")


            ping_results.sort(key=lambda x: x['ping_time'])

            print("-------------------------------- start sorted ping results --------------------------------")
            for ping_result in ping_results:
                print(f"ping_result: {ping_result}")
            print("-------------------------------- end sorted ping results --------------------------------")


            best_clusters = []
            for ping_result in ping_results:
                if ping_result['cluster'] not in best_clusters:
                    best_clusters.append(ping_result['cluster'])


            print("-------------------------------- start best clusters --------------------------------")
            for best_cluster in best_clusters:
                print(f"best_cluster: {best_cluster}")
            print("-------------------------------- end best clusters --------------------------------")

            response_date = None
            err_reason_response = []

            for cluster in best_clusters:
                start_time = time.time()

                req_request_number = f"{start_time}_{cluster}"

                request_data = copy.deepcopy(request_data)

                request_data['date'] = start_time
                
                request_data['request_number'] = req_request_number
                request_data['target_cluster'] = cluster

                print(f"Request sent: lowlatency {request_data['request_number']} to {cluster}")
                kafka_api.send('request', request_data)

                while True:
                    if time.time() - start_time > timeout:
                        print(f"Request timeout: {req_request_number}")
                        err_reason_response.append({"request_number": req_request_number, "status": "error", "message": "Request timeout", "cluster": request_data['target_cluster']})
                        break
                    try:
                        response = request_queue.get_nowait()
                        if response.get('request_number') == req_request_number:
                            if response.get('status') == 200:
                                response_date = response
                                request_thread_queue.put_nowait({"request_number": org_request_number, "status": "success", "response": response_date, "cluster": request_data['target_cluster']})
                                print(f"Request success: lowlatency {request_data['request_number']} to {cluster}")
                                return
                            else:
                                print(f"Request error: lowlatency {request_data['request_number']} to {cluster}")
                                err_reason_response.append(response)
                            break
                        else:
                            if time.time() - request_data['date'] < 60:
                                request_queue.put_nowait(response)
                    except asyncio.QueueEmpty:
                        # Queue is empty, wait briefly before checking again
                        time.sleep(0.1)

                if len(err_reason_response) > 0:
                    request_thread_queue.put_nowait({"request_number": org_request_number, "status": "error", "message": err_reason_response})
               
        
            

    else:
        print(f"Not implemented: {priority}")

