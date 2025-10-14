const grafana_hash1 = '8b7a8b326d7a6f1f04244066368c67af';
const grafana_hash2 = '200ac8fdbfbb74b39aff88118e4d1c2c';
const grafana_hash3 = 'efa86fd1d0c121a26444b636a3f509a8';

var grafana_source_name = null;
var grafana_node_name = null;
var grafana_type = null;

function getGrafanaDataSouceName(name){
    switch(name){
        case 'zento-master':
            return 'prometheus';
        case 'ms-master':
            return 'ms-master';
        case 'edge-master':
            return 'edge-master';
        default:
            return 'prometheus';
    }
}

function getGrafanaHash(type){
    if(type == 'kubernetes-compute-resources-node-pods'){
        return grafana_hash2;
    }else if(type == 'kubernetes-compute-resources-cluster'){
        return grafana_hash3;
    }
    return grafana_hash1;
}

function openGrafana() {
    if(grafana_source_name == null || grafana_type == null){
        return;
    }

    const grafana_hash = getGrafanaHash(grafana_type);

    var title_name = grafana_source_name;

    if(grafana_node_name != null){
        title_name = grafana_source_name + ' - ' + grafana_node_name;
    }

    document.querySelector('.show-grafana').style.display = 'flex';
    document.querySelector('#grafana-title').textContent = title_name;
    document.querySelector('#grafana-iframe').src = `/d/${grafana_hash}/${grafana_type}?orgId=1&refresh=10s&var-datasource=${getGrafanaDataSouceName(grafana_source_name)}&kiosk&var-node=${grafana_node_name}`;
}

function closeGrafana() {
    document.querySelector('.show-grafana').style.display = 'none';
    document.querySelector('#grafana-iframe').src = '';
}

