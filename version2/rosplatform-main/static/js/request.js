

let user_projects = [];

function get_projects(username, callback) {
    zfetch("/projects/?user_name=" +username, "GET", null).then(data => {
        callback(data);
    });
}



function onCreateDeploymentClicked() {

    clearModal();

    $("#modal-title").html("Deployment");
    $(".form-resource-show").hide();
    $(".form-deployment").show();

    get_projects(get_current_user().username, (data) => {
        user_projects = data;
        var options = "";
        for(var i = 0; i < data.length; i++) {
            if(data[i].status == "active") {    
                options += "<option value='" + data[i].name + "'>" + data[i].name + "</option>";
            }
        }
        $("#select-project").html(options);
        $("#create_modal").show();
        onProjectChanged();
        onPriorityChanged();
    });


}

function onDeleteDeploymentClicked() {
   
}

var used_clusters = [];

function onProjectChanged() {
    var value = $("#select-project").val();
    used_clusters = [];
    
    var project = user_projects.find(project => project.name == value);
    if(project) {
        var options = "";
        for(var i = 0; i < project.clusters.length; i++) {
            options += "<option value='" + project.clusters[i] + "'>" + project.clusters[i] + "</option>";
            used_clusters.push(project.clusters[i]);
        }
        $("#target-cluster").html(options);
        $("#source-cluster").html(options);

        var inputs = "";
        for(var i = 0; i < project.clusters.length; i++) {
            inputs += `<input type='checkbox' id='${project.clusters[i]}' name='${project.clusters[i]}' onchange='onTargetClusterChanged(this)' /><span class='cluster-item-name'>${project.clusters[i]}</span>`;
        }
        $("#target-clusters").html(inputs);
    }

    onSourceClusterChanged();
}

function onPriorityChanged() {
    var value = $("#priority").val();

    $(".form-all-show").hide();
    if(value == "selectedcluster") {
        $(".form-selectedcluster").show();
    } else if(value == "lowlatency") {
        $(".form-lowlatency").show();
    } else if(value == "mostrequested") {
        $(".form-mostrequested").show();
    } else if(value == "setcluster") {
        $(".form-setcluster").show();
    }
}



function onTargetClusterChanged(checkbox) {

    var name = $(checkbox).attr("name");

    var last_level = $(".level-item").last();

    var names_str = last_level.html().trim();

    var names = names_str.split(",");

    if(names_str.length == 0) {
        names = [];
    }

    var is_checked = $(checkbox).prop("checked");

    if(is_checked) {
        names.push(name);
        last_level.html(names.join(","));
    }else{

        $(".level-item").each(function() {
            var level_names = $(this).html().split(",");
            level_names = level_names.filter(n => n !== name);
            $(this).html(level_names.join(","));
        });
    }

    onPresentClustersChanged();
}

function addLevel() {
    init_Level();

    $('#drag-clusters').show();
    /*
    var last_level = $(".level-item").last();
    var names_str = last_level.html().trim();

    if(names_str.length == 0) {
        return;
    }

    var new_level = $("<div class='level-item'></div>");
    $(".level-list").append(new_level);
    */
}


function removeLevel() {

    if($(".level-item").length == 1) {
        return;
    }

    var last_level = $(".level-item").last();

    var names_str = last_level.html().trim();

    if(names_str.length != 0) {
        var names = names_str.split(",");

        $("#target-clusters input").each(function() {
            var name = $(this).attr("name");
            var is_checked = $(this).prop("checked");
    
            if(names.includes(name)) {
                $(this).prop("checked", false);
            }
        });
    }

    $(".level-item").last().remove();

    onPresentClustersChanged();
}

function onPresentClustersChanged() {
    var present_clusters = $("#present-clusters").val();
    
    var present_levels = [];

    $(".level-item").each(function() {
        var names_str = $(this).html().trim();

        var names = names_str.split(",");

        if(names_str.length == 0) {
            return;
        }

        present_levels.push(names);
    });

    var present_levels_str = JSON.stringify(present_levels);

    if(present_levels.length == 1) {
        present_levels_str = JSON.stringify(present_levels[0]);
    }else if(present_levels.length == 0) {
        present_levels_str = "";
    }

    $("#present-clusters").val(present_levels_str);
}


function onSourceClusterChanged() {
    var value = $("#source-cluster").val();
    var clusters = current_clusters.filter(cluster => cluster.cluster_name == value);

    if(clusters.length == 0) {
        return;
    }

    var nodes = clusters[0].nodes;

    var options = "";
    for(var i = 0; i < nodes.length; i++) {
        options += `<option value='${nodes[i].metadata.name}'>${nodes[i].metadata.name}</option>`;
    }

    $("#source-node").html(options);
}

function addLable() {
    var lable = document.createElement('div');
    lable.className = 'label-item';
    lable.innerHTML = '<div class="insert-title"></div><div class="label-inputs"><input class="label-name-input" type="text1" placeholder="Please enter name"><input class="label-value-input" type="text1" placeholder="Please enter value"><div class="remove-label-btn" onclick="removeLable(this)"><i class="fa-solid fa-minus remove-label-icon"></i></div></div>';
    document.getElementById('create-lables').appendChild(lable);
   
}

function removeLable(item) {
    item.parentElement.parentElement.remove();
}

function addPort(parentElement) {
    var port = document.createElement('div');
    port.className = 'port-item';
    port.innerHTML = '<div class="insert-title"></div><div class="port-inputs"><select class="port-name-input" name="port-name" style="outline: none; background:#1C1C1C;outline: 0;border: 0;color: #fff;border-radius: 5px;padding: 5px;font-size: 14px;"> <option value="http">http</option><option value="https">https</option><option value="tcp">tcp</option><option value="udp">udp</option></select><input class="port-value-input" type="text1" placeholder="80" value="80"><div class="remove-port-btn" onclick="removePort(this)"><i class="fa-solid fa-minus remove-port-icon"></i></div></div>';
    
    $(parentElement).children('.create-ports').append(port);
}

function removePort(item) {
    item.parentElement.parentElement.remove();
}

function addVolumeMount(parentElement) {

    var volumeMount = document.createElement('div');
    volumeMount.className = 'volume-mount-item';
    volumeMount.innerHTML = '<div class="insert-title"></div><div class="volume-mount-inputs"><input class="volume-mount-name-input" type="text1" placeholder="Please enter name"><input class="volume-mount-mountpath-input" type="text1" placeholder="Please enter MountPath"><div class="remove-volume-mount-btn" onclick="removeVolumeMount(this)"><i class="fa-solid fa-minus remove-volume-mount-icon"></i></div></div>';
    $(parentElement).children('.create-volumemounts').append(volumeMount);
}

function removeVolumeMount(item) {
    item.parentElement.parentElement.remove();
}


function addEnv(parentElement) {
    var env = document.createElement('div');
    env.className = 'env-item';
    env.innerHTML = '<div class="insert-title"></div><div class="env-inputs"><input class="env-name-input" type="text1" placeholder="Please enter name"><input class="env-value-input" type="text1" placeholder="Please enter value"><div class="remove-env-btn" onclick="removeEnv(this)"><i class="fa-solid fa-minus remove-env-icon"></i></div></div>';
    $(parentElement).children('.create-envs').append(env);
}

function removeEnv(item) {
    item.parentElement.parentElement.remove();
}



function addContainer() {
    var container = document.createElement('div');
    container.className = 'container-item';
    container.innerHTML = `
        
                        <div class="form-row">
                            <div class="insert-title">Container Name: </div>
                            <div class="insert-input-box"> 
                                <input name="container-name" class="container-name-input" type="text" placeholder="Please enter container name">
                                
                            </div>
                            <div class="remove-label-btn" onclick="removeContainer(this)">
                                <i class="fa-solid fa-minus remove-label-icon"></i>
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="insert-title">Image: </div>
                            <div class="insert-input-box"> 
                                <input name="image" class="image-input" type="text" placeholder="Please enter image">
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="insert-title">Pull Policy: </div>
                            <div > 
                                <select name="pull-policy" style="outline: none; background:#1C1C1C;outline: 0;border: 0;color: #fff;width: 100%;border-radius: 5px;padding: 5px;font-size: 14px;">
                                    <option value="IfNotPresent">IfNotPresent</option>
                                    <option value="Always">Always</option>
                                <option value="Never">Never</option>
                                </select>
                            </div>
                        </div>
                        <div class="form-row-margin">
                            <div class="insert-title">Ports </div>
                            <div class="add-label-btn" onclick="addPort(this.parentElement.parentElement)"> 
                                Add Port
                            </div>
                        </div>
                        <div class="create-ports" >
                        </div>
                        <div class="form-row">
                            <div class="insert-title">Command: </div>
                            <div class="insert-input-box"> 
                                <input name="command" type="text">
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="insert-title">Env </div>
                            <div class="add-label-btn" onclick="addEnv(this.parentElement.parentElement)"> 
                                Add Env
                            </div>
                        </div>
                        <div class="create-envs" >
                        </div>
                        <div class="form-row">
                            <div class="insert-title">VolumeMount </div>
                            <div class="add-label-btn" style="width: 200px;" onclick="addVolumeMount(this.parentElement.parentElement)"> 
                                Add VolumeMount
                            </div>
                        </div>
                        <div class="create-volumemounts" >
                        </div>
                    
    
    `;
    document.getElementById('container-list').appendChild(container);
}

function removeContainer(item) {
    item.parentElement.parentElement.remove();
}

function addVolume() {
    var volume = document.createElement('div');
    volume.className = 'volume-item';
    volume.innerHTML = `
                        <div class="form-row">
                            <div class="insert-title">Volume Name:</div>
                            <div class="insert-input-box" style="width: auto;flex: 1;">
                                <input name="volume-name" class="volume-name-input" type="text" placeholder="Please enter name">
                            </div> 
                            <div class="insert-input-box"  style="width: auto;flex: 1; margin-left: 10px;">
                                <input name="volume-claimname" class="volume-claimname-input" type="text" placeholder="Please enter PVC claimName">
                            </div>
                            <div class="remove-volume-btn" onclick="removeVolume(this)"><i class="fa-solid fa-minus remove-volume-icon"></i></div>
                        </div>
        `;
    
    document.getElementById('volume-list').appendChild(volume);
}

function removeVolume(item) {
    item.parentElement.parentElement.remove();
}



function closeModal() {
    $("#create_modal").hide();
}

function getValue(name)
{
    return $(`#create_modal ${name}`).val();
}


function getValues(name, names)
{
    const _names = [];

    $(`#create_modal ${name} ${names}`).each(function() {
        _names.push($(this).val());
    });

    return _names;
}

function addServicePort() {

    var servicePort = document.createElement('div');
    servicePort.className = 'service-port-item';
    servicePort.innerHTML = `
        <div class="insert-title">Port: </div>
        <div class="label-inputs"> 
            <input class="service-port-input" type="text1" placeholder="Please enter port">
            <input class="service-target-port-input" type="text1" placeholder="Please enter target port">
            <div class="remove-label-btn" onclick="removeServicePort(this)"><i class="fa-solid fa-minus remove-label-icon"></i></div>
        </div>
    `;

    $('#service-ports').append(servicePort);
}

function removeServicePort(item) {
    item.parentElement.parentElement.remove();
}

function clearModal() {
    $("#create-name").val("");
    $("#replicas").val("1");
    $("#present-clusters").val("");
    $("#create-lables").html("");
    $("#container-list").html("");
    $("#volume-list").html("");
    //$("#select-pod").html("");
    //$("#select-cluster").html("");

    var index = 0;
    $(".level-item").each(function() {
        if(index == 0) {
            $(this).html("");
        }else{
            $(this).remove();
        }
        index++;
    });

    $("#service-name").val("");
    $("#service-ports").html("");
}


function okModal(resource_type) {
    const name = getValue("#create-name");
    const replicas = getValue("#replicas");

    const lables_names = getValues("#create-lables", ".label-name-input");
    const lables_values = getValues("#create-lables", ".label-value-input");

    const target_cluster = getValue("#target-cluster");
    const source_cluster = getValue("#source-cluster");
    const source_node = getValue("#source-node");
    const pull_secret = getValue("#pull-secret");
    var priority = getValue("#priority");
    const present_clusters = getValue("#present-clusters");
    const project = getValue("#select-project");
    const service_name = getValue("#service-name");
    const service_port = getValues("#service-ports", ".service-port-input");
    const service_type = getValue("#service-type");
    const service_target_port = getValues("#service-ports", ".service-target-port-input");
    const select_pod = getValue("#select-pod");
    const select_cluster = getValue("#select-cluster");
   

    var is_check = true;

    if(resource_type == "service") {
        is_check = false;
    }

    if(is_check && name == "") {
        alert(`Please fill in ${resource_type} Name.`);
        $("#create-name").focus();
        return;
    }

    if(is_check && replicas == "" && resource_type == "deployment") {
        alert("Please fill in Replicas.");
        $("#replicas").focus();
        return;
    }

    if(is_check && priority == "") {
        alert("Please fill in Priority.");
        $("#priority").focus();
        return;
    }

    if (is_check && resource_type == "deployment" && (isNaN(replicas) || parseInt(replicas) != replicas || parseInt(replicas) < 1)) {
        alert("Replicas must be a positive integer.");
        $("#replicas").focus();
        return;
    }

    if(is_check && lables_names.length == 0) {
        alert("Please fill in Lables.");
        $("#create-lables").focus();
        return;
    }

    lables_names.forEach(name => {
        if(name == "") {
            alert("Please fill in Lables.");
            $("#create-lables").focus();
            return;
        }
    });

    lables_values.forEach(name => {
        if(name == "") {
            alert("Please fill in Lables.");
            $("#create-lables").focus();
            return;
        }
    });

    if(priority == "lowlatency" || priority == "selectedcluster") {
        if(present_clusters.length == 0) {
            alert("Please select Target Cluster.");
            $("#present-clusters").focus();
            return;
        }
    }

    var containers = [];




    //conatainers

    if(is_check) {
        $("#container-list").children(".container-item").each(function() {
            const container_name = $(this).find(".container-name-input").val();
            const image = $(this).find(".image-input").val();
            const pull_policy = $(this).find(".pull-policy-input").val();
            const command = $(this).find(".command-input").val();
            const ports_names = getValues(".create-ports", ".port-name-input");
            const ports_values = getValues(".create-ports", ".port-value-input");
            const envs_names = getValues(".create-envs", ".env-name-input");
            const envs_values = getValues(".create-envs", ".env-value-input");
            const volume_mounts_names = getValues(".create-volumemounts", ".volume-mount-name-input");
            const volume_mounts_mountpaths = getValues(".create-volumemounts", ".volume-mount-mountpath-input");

            if(container_name == "") {
                alert("Please fill in Container Name.");
                $("#container-list").focus();
                return;
            }

            if(image == "") {
                alert("Please fill in Image.");
                $("#container-list").focus();
                return;
            }

            ports_names.forEach(name => {
                if(name == "") {
                    alert("Please fill in Port.");
                    $("#container-list").focus();
                    return;
                }
            });

            ports_values.forEach(value => {
                if(value == "") {
                    alert("Please fill in Port.");
                    $("#container-list").focus();
                    return;
                }
            });

            envs_names.forEach(name => {
                if(name == "") {
                    alert("Please fill in Env.");
                    $("#container-list").focus();
                    return;
                }
            });

            envs_values.forEach(value => {  
                if(value == "") {
                    alert("Please fill in Env.");
                    $("#container-list").focus();
                    return;
                }
            });

            volume_mounts_names.forEach(name => {
                if(name == "") {
                    alert("Please fill in VolumeMount.");
                    $("#container-list").focus();
                    return;
                }
            });

            volume_mounts_mountpaths.forEach(mountpath => {
                if(mountpath == "") {
                    alert("Please fill in VolumeMount.");
                    $("#container-list").focus();
                    return;
                }
            });


            containers.push({
                container_name: container_name,
                image: image,
                pull_policy: pull_policy,
                command: command,
                ports: ports_names,
                ports_values: ports_values,
                envs: envs_names,
                envs_values: envs_values,
                volume_mounts: volume_mounts_names,
                volume_mounts_mountpaths: volume_mounts_mountpaths
            });
            
        });

        if(containers.length == 0) {
            alert("Please fill in Container.");
            $("#container-list").focus();
            return;
        }
    }


    var volumes = [];

    if(is_check) {

        $("#volume-list").children(".volume-item").each(function() {
            const volume_name = $(this).find(".volume-name-input").val();
            const volume_claimname = $(this).find(".volume-claimname-input").val();
            
            volumes.push({
                volume_name: volume_name,
                volume_claimname: volume_claimname
            });
        });
    }

    if(service_name != "") {
        if(service_port.length == 0) {
            alert("Please fill in Service Port.");
            $("#service-ports").focus();
            return;
        }

        service_port.forEach(port => {
            if(port == "") {
                alert("Please fill in Service Port.");
                $("#service-ports").focus();
                return;
            }
        });

        service_target_port.forEach(target_port => {    
            if(target_port == "") {
                alert("Please fill in Service Target Port.");
                $("#service-ports").focus();
                return;
            }
        });
    }

    var service_ports = [];

    service_port.forEach((port, index) => {
        service_ports.push({
            port: port,
            target_port: service_target_port[index]
        });
    });


    if(resource_type == "service") {

        if(select_cluster.length == 0){
            alert("Please select a cluster.");
            $("#select-cluster").focus();
            return;
        }

        if(select_pod.length == 0){
            alert("Please select a pod.");
            $("#select-pod").focus();
            return;
        }


        const pod_labels = get_selected_pod_labels();

        for(pod_label in pod_labels){
            if(pod_label.startsWith("pod-template-hash")) {
                continue;
            }
            lables_names.push(pod_label);
            lables_values.push(pod_labels[pod_label]);
        }
        
         
    }


    const project_ = user_projects.find(project__ => project__.name == project);
    

    var deployment = {
        type: resource_type,
        username: get_current_user().username,
        workspace: project_.workspace_name,
        project: project,
        name: name,
        replicas: replicas,
        lables: lables_names,
        lables_values: lables_values,
        target_cluster: target_cluster,
        source_cluster: source_cluster,
        source_node: source_node,
        pull_secret: pull_secret,
        priority: priority,
        present_clusters: present_clusters,
        containers: containers,
        volumes: volumes,
        service_name: service_name,
        service_ports: service_ports,
        service_type: service_type,
        select_cluster: select_cluster,
        select_pod: select_pod
    }

    zfetch("/requst_kube_api", "POST", deployment).then(data => {
        const is_success = error_handler(data);
        if(!is_success) {
            return;
        }

        closeModal();
        get_clusters_info();
    });
}


function onCreate_Pod() {
    clearModal();

    $(".form-resource-show").hide();
    $(".form-pod").show();

    $("#modal-title").html("Pod");

    get_projects(get_current_user().username, (data) => {
        user_projects = data;
        var options = "";
        for(var i = 0; i < data.length; i++) {
            if(data[i].status == "active") {    
                options += "<option value='" + data[i].name + "'>" + data[i].name + "</option>";
            }
        }
        $("#select-project").html(options);
        $("#create_modal").show();
        onProjectChanged();
        onPriorityChanged();
    });

}


function onCreate_Service() {
    clearModal();

    $(".form-resource-show").hide();
    $(".form-service").show();

    $("#modal-title").html("Service");

    get_projects(get_current_user().username, (data) => {
        user_projects = data;
        var options = "";
        for(var i = 0; i < data.length; i++) {
            if(data[i].status == "active") {    
                options += "<option value='" + data[i].name + "'>" + data[i].name + "</option>";
            }
        }
        $("#select-project").html(options);
        $("#create_modal").show();
       
    });
}

function check_status(data) {
    if(data.status == "error") {
        alert(data.message);
        return false;
    }else if(data.status == "success") {
        return true;
    }

    if(data.status != 200 || data.status != 201) {
        try {
            const r = JSON.parse(data.body);
            alert(r.status + "(" + r.code + ") : " + r.message);
        } catch(e) {
            // Keep as string if parsing fails
        }

        return false;
    }
    return true;
}




function get_ros_info() {
   return zfetch("/bridges/ros_info", "GET", {});
}


function error_handler(data) {
    console.log(data);
    if(data.status == "error") {
        if (Array.isArray(data.message)) {
            data.message.forEach(message => {
                alert(`${message.status} in ${message.cluster}: ${message.body}`);
            });
        }else{
            alert(data.message);
        }
       
        return false;
    }else if(data.status == "success") {
        
        if(data.response.status != 200) {
            alert(data.response.body);
            return false;
        }
    }else if(data.status != 200) {
        try {
            const r = JSON.parse(data.body);
            alert(r.status + "(" + r.code + ") : " + r.message);
        } catch(e) {
            // Keep as string if parsing fails
        }
    
        return false;
    }


    return true;
}


// Call get_ros_info every second
//setInterval(get_ros_info, 1000);
