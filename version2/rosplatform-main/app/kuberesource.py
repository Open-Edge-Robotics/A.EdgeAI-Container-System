
from kubernetes.utils.quantity import parse_quantity

def create_deployment_yaml(data):
    containers = []
    for i in range(len(data.get("containers", []))):
        c = data["containers"][i]
        envs = []
        for name, value in zip(c.get("envs", []), c.get("envs_values", [])):
            if name and value:
                envs.append({"name": name, "value": value})
        ports = []
        for name, value in zip(c.get("ports", []), c.get("ports_values", [])):
            if name and value:
                try:
                    port = int(value)
                except Exception:
                    port = value
                ports.append({"name": name, "containerPort": port})
        volume_mounts = []
        for name, value in zip(c.get("volume_mounts", []), c.get("volume_mounts_mountpaths", [])):
            if name and value:
                volume_mounts.append({"name": name, "mountPath": value})
        container = {
            "name": c.get("container_name", f"container-{i}"),
            "image": c.get("image", ""),
            "imagePullPolicy": c.get("pull_policy", "IfNotPresent"),
        }
        if c.get("command"):
            container["command"] = [c["command"]]
        if ports:
            container["ports"] = ports
        if envs:
            container["env"] = envs
        if volume_mounts:
            container["volumeMounts"] = volume_mounts
        containers.append(container)

    labels = {}
    for k, v in zip(data.get("lables", []), data.get("lables_values", [])):
        if k and v:
            labels[k] = v

    volumes = []
    for v in data.get("volumes", []):
        if v.get("volume_name") and v.get("volume_claimname"):
            volumes.append({
                "name": v["volume_name"],
                "persistentVolumeClaim": {
                    "claimName": v["volume_claimname"]
                }
            })

    deployment = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": data.get("name", "deployment"),
            "namespace": data.get("username", "default"),
            "labels": labels,
            "annotations": {
                "username" : data.get("username", ""),
                "workspace" : data.get("workspace", ""),
                "project" : data.get("project", "")
            }
        },
        "spec": {
            "replicas": int(data.get("replicas", 1)),
            "selector": {
                "matchLabels": labels
            },
            "template": {
                "metadata": {
                    "labels": labels,
                    "annotations": {
                        "username" : data.get("username", ""),
                        "workspace" : data.get("workspace", ""),
                        "project" : data.get("project", "")
                    }
                },
                "spec": {
                    "containers": containers,
                    "volumes": volumes
                }
            }
        }
    }
    # Optionally add imagePullSecrets
    if data.get("pull_secret"):
        deployment["spec"]["template"]["spec"]["imagePullSecrets"] = [
            {"name": data["pull_secret"]}
        ]
    return deployment

def create_pod_yaml(data):

    containers = []
    for i in range(len(data.get("containers", []))):
        c = data["containers"][i]
        envs = []
        for name, value in zip(c.get("envs", []), c.get("envs_values", [])):
            if name and value:
                envs.append({"name": name, "value": value})
        ports = []
        for name, value in zip(c.get("ports", []), c.get("ports_values", [])):
            if name and value:
                try:
                    port = int(value)
                except Exception:
                    port = value
                ports.append({"name": name, "containerPort": port})
        volume_mounts = []
        for name, value in zip(c.get("volume_mounts", []), c.get("volume_mounts_mountpaths", [])):
            if name and value:
                volume_mounts.append({"name": name, "mountPath": value})
        container = {
            "name": c.get("container_name", f"container-{i}"),
            "image": c.get("image", ""),
            "imagePullPolicy": c.get("pull_policy", "IfNotPresent"),
        }
        if c.get("command"):
            container["command"] = [c["command"]]
        if ports:
            container["ports"] = ports
        if envs:
            container["env"] = envs
        if volume_mounts:
            container["volumeMounts"] = volume_mounts
        containers.append(container)

    labels = {}
    for k, v in zip(data.get("lables", []), data.get("lables_values", [])):
        if k and v:
            labels[k] = v

    volumes = []
    for v in data.get("volumes", []):
        if v.get("volume_name") and v.get("volume_claimname"):
            volumes.append({
                "name": v["volume_name"],
                "persistentVolumeClaim": {
                    "claimName": v["volume_claimname"]
                }
            })

    pod = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": data.get("name", "pod"),
            "namespace": data.get("username", "default"),
            "labels": labels,
            "annotations": {
                "username" : data.get("username", ""),
                "workspace" : data.get("workspace", ""),
                "project" : data.get("project", "")
            }
        },
        "spec": {
            "containers": containers,
            "volumes": volumes
        }
    }

    # Optionally add imagePullSecrets
    if data.get("pull_secret"):
        pod["spec"]["template"]["spec"]["imagePullSecrets"] = [
            {"name": data["pull_secret"]}
        ]

    return pod

def create_service_yaml(data):
    labels = {}
    for k, v in zip(data.get("lables", []), data.get("lables_values", [])):
        if k and v:
            labels[k] = v

    ports = []
    for p in data.get("service_ports", []):
        if p.get("port") and p.get("target_port"):
            ports.append({"port": int(p.get("port")), "targetPort": int(p.get("target_port"))})

    service = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": data.get("service_name", "service"),
            "namespace": data.get("username", "default"),
            "labels": labels,
            "annotations": {
                "username" : data.get("username", ""),
                "workspace" : data.get("workspace", ""),
                "project" : data.get("project", "")
            }
        },
        "spec": {
            "selector": labels,
            "ports": ports,
            "type": data.get("service_type", "ClusterIP"),
        }
    }
    return service
