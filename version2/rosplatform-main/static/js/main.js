let currnet_user = null;
let current_clusters = [];
let ros_info = null;


function set_current_user(user) {
    currnet_user = user;
}

function get_current_user() {
    return currnet_user;
}

const id_debug = true;


function zfetch(url, method, data) {

    var token = localStorage.getItem("access_token");
    var token_type = localStorage.getItem("token_type");

    var body = null;

    if(method === "GET") {
        body = null;
    }else{
        body = JSON.stringify(data);
    }

    return fetch(url, {
        method: method,
        headers: {
            "Authorization": token_type+" " + token,
            "Content-Type": "application/json"
        },
        body: body
    }).then(
        async response =>{
            if(response.status == 200 || response.status == 201) {
                return response.json();
            }else{
                const data = await response.json();

                if(checkProperty(data, "detail")) {

                    if (Array.isArray(data.detail)) {
                        data.detail.forEach(error => {
                            console.log(error);
                            alert(error.loc[1] + " : " + error.msg);
                        });
                    }else{
                        if(checkProperty(data, "detail")) {
                            alert(data.detail);
                        }else{
                            alert("Failed to fetch data : " + response.status);
                        }
                    }
                    
                }

                if(id_debug == false) {
                    clear_local_storage();
                }

                throw new Error("Unknown Error");
            }
        }
    )
    .then(data =>{
        return data;
    }).catch((error) => {
        if(id_debug == false) {
            clear_local_storage();
        }
        throw new Error(error);
    });
}


function fetchData(element, event, url) {

    document.querySelectorAll('.sidebar-toggle img').forEach(img => {
        img.classList.remove('sidebar-active');
    });
    

    if(element) {
        element.querySelector('img').classList.add('sidebar-active');
    }
    
    if(event) {
        event.target.classList.add('active');
    }

    var token = localStorage.getItem("access_token");
    var token_type = localStorage.getItem("token_type");
    fetch(url,
        {
            method: "GET",
            headers: {
                "Authorization": token_type+" " + token
            }
        })
    .then(response => response.text())
    .then(data =>{
        $( "#main-content" ).html(data );
    });
}

function fetchData2(element, event, url) {

    document.querySelectorAll('.sidebar-toggle2 img').forEach(img => {
        img.classList.remove('sidebar-active');
    });

    document.querySelectorAll('.sidebar-menu img').forEach(img => {
        img.classList.remove('sidebar-active');
    });
    

    if(element) {
        element.querySelector('img').classList.add('sidebar-active');
    }
    
    if(event) {
        event.target.classList.add('active');
    }

    var token = localStorage.getItem("access_token");
    var token_type = localStorage.getItem("token_type");
    fetch(url,
        {
            method: "GET",
            headers: {
                "Authorization": token_type+" " + token
            }
        })
    .then(response => response.text())
    .then(data =>{
        $( "#main-content" ).html(data );
    });
}



function check_user() {
    var token = localStorage.getItem("access_token");
    var token_type = localStorage.getItem("token_type");
    var user_type = localStorage.getItem("user_type");
    var user_id = localStorage.getItem("user_id");

    if(token) {

        $("#user-info-txt2").text(user_id);
       
    } else {
        window.location.href = "/";
    }
}


function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("token_type");
    localStorage.removeItem("user_id");
    localStorage.removeItem("user_type");
    window.location.href = "/";
}


var clusters_info = {};

function get_clusters_info2() {
    var token = localStorage.getItem("access_token");
    var token_type = localStorage.getItem("token_type");

    $.ajax({
        type: "GET",
        url: "/clusters/info",
        beforeSend: function (xhr) {
            xhr.setRequestHeader("Authorization",token_type+" " + token);
        },
        success: function (res) {
            clusters_info = res;
            //console.log(clusters_info);
            debugger;
        }
    });
}

function get_clusters_info() {

    const url = "/clusters/info";


    zfetch(url, "GET", {}).then(data => {
        const clusters = [];


        for(const cluster in data) {
            const cluster_info = data[cluster];

            const nodes = [];

            for(const node in cluster_info.nodes) {
                const node_info = cluster_info.nodes[node];
                nodes.push(node_info);
            }

            const pods = [];

            for(const pod in cluster_info.pods) {
                const pod_info = cluster_info.pods[pod];
                pods.push(pod_info);
            }

            const services = [];

            for(const service in cluster_info.services) {
                const service_info = cluster_info.services[service];
                services.push(service_info);
            }

            cluster_info.pods = pods;
            cluster_info.nodes = nodes;
            cluster_info.services = services;


            clusters.push(cluster_info);
        }

        current_clusters = clusters;

        update_clusters_info(clusters);
    });
}

function clear_local_storage() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("token_type");
    localStorage.removeItem("user_id");
    localStorage.removeItem("user_type");
    window.location.href = "/";
}



function convertUTCToSeoul(utcTimeStr) {
    // UTC 시간을 Date 객체로 파싱
    const utcDate = new Date(utcTimeStr);
    
    // 서울 시간으로 변환 (KST = UTC+9)
    const seoulTime = new Date(utcDate.getTime() + (9 * 60 * 60 * 1000));
    return seoulTime.toISOString().replace('T', ' ').replace(/\.\d+Z?$/, '');
}

// 방법 2: Intl.DateTimeFormat 사용 (더 정확한 시간대 처리)
function convertUTCToSeoulModern(utcTimeStr) {
    const utcDate = new Date(utcTimeStr);
    
    // 서울 시간대 옵션
    const options = {
        timeZone: 'Asia/Seoul',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    };
    
    return new Intl.DateTimeFormat('ko-KR', options).format(utcDate);
}

// 방법 3: moment.js 사용 (라이브러리 필요)
function convertUTCToSeoulMoment(utcTimeStr) {
    // moment.js가 설치되어 있다면:
    // const moment = require('moment-timezone');
    // return moment(utcTimeStr).tz('Asia/Seoul').format('YYYY-MM-DD HH:mm:ss Z');
    
    // 또는 CDN으로 moment.js를 사용할 수 있습니다
    console.log("moment.js 라이브러리가 필요합니다");
}


function checkProperty(obj, propertyName) {
    return obj.hasOwnProperty(propertyName);
}


function formatPythonTimestamp(timestamp) {
    const date = new Date(timestamp * 1000);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hour = String(date.getHours()).padStart(2, '0');
    const minute = String(date.getMinutes()).padStart(2, '0');
    const second = String(date.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
}


function showConnectBridge() {
    $("#connect_bridge_modal").show();
}

function closeConnectBridge() {
    $("#connect_bridge_modal").hide();
}