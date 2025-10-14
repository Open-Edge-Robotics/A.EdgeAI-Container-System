class UsageRenderer  {
    eGui;

    // Optional: Params for rendering. The same params that are passed to the cellRenderer function.
    init(params) {

        const progress = document.createElement('progress');
        progress.setAttribute('class', 'usage-progress');
        progress.setAttribute('value', params.value);
        progress.setAttribute('max', 100);

        if(params.value > 70 && params.value < 90) {
            progress.setAttribute('class', 'usage-progress-warning');
        } else if(params.value > 90) {
            progress.setAttribute('class', 'usage-progress-danger');
        } 

        const span = document.createElement('span');
        span.setAttribute('class', 'usage-span');
        span.innerHTML = "(" + params.value.toFixed(2) + "%)";

        this.eGui = document.createElement('div');
        this.eGui.setAttribute('class', 'usage-div');
        this.eGui.appendChild(progress);
        this.eGui.appendChild(span);
    }

    // Required: Return the DOM element of the component, this is what the grid puts into the cell
    getGui() {
        return this.eGui;
    }

    // Required: Get the cell to refresh.
    refresh(params) {
        return false;
    }
}


class StatusRenderer  {
    eGui;

    // Optional: Params for rendering. The same params that are passed to the cellRenderer function.
    init(params) {
        const span = document.createElement('span');
        span.setAttribute('class', 'status-span');
        span.innerHTML = params.value;

        const div = document.createElement('div');
        div.setAttribute('class', 'status-in-div');

        const lower = params.value.toLowerCase();

        if(lower == "active") {
            div.style.backgroundColor = "#A2FF30";
        }else if(lower == "alive") {
            div.style.backgroundColor = "#30E0FF";
        }else if(lower == "available") {
            div.style.backgroundColor = "#FFF830";
        }else if(lower == "running") {
            div.style.backgroundColor = "#55E395";
        }else if(lower == "succeeded") {
            div.style.backgroundColor = "#00CEEB";
        }else if(lower == "ready") {
            div.style.backgroundColor = "#ADF204";
        } 
        
        div.appendChild(span);


        this.eGui = document.createElement('div');
        this.eGui.setAttribute('class', 'status-div');
        this.eGui.appendChild(div);
    }

    // Required: Return the DOM element of the component, this is what the grid puts into the cell
    getGui() {
        return this.eGui;
    }

    // Required: Get the cell to refresh.
    refresh(params) {
        return false;
    }
}

class UserTypeRenderer  {
    eGui;

    // Optional: Params for rendering. The same params that are passed to the cellRenderer function.
    init(params) {
        const span = document.createElement('span');
        span.setAttribute('class', 'user-span');
        span.innerHTML = "- "+params.value;

        if(params.value == "super") {
            span.style.color = "#30A9FF";
        } else {
            span.style.color = "#FF8630";
        }

        const div = document.createElement('div');
        div.setAttribute('class', 'user-in-div');

        if(params.value == "active") {
            div.style.backgroundColor = "#A2FF30";
        } 

        div.appendChild(span);


        this.eGui = document.createElement('div');
        this.eGui.setAttribute('class', 'status-div');
        this.eGui.appendChild(div);
    }

    // Required: Return the DOM element of the component, this is what the grid puts into the cell
    getGui() {
        return this.eGui;
    }

    // Required: Get the cell to refresh.
    refresh(params) {
        return false;
    }
}


class ClusterTypeRenderer  {
    eGui;

    // Optional: Params for rendering. The same params that are passed to the cellRenderer function.
    init(params) {
        const span = document.createElement('span');
        span.setAttribute('class', 'user-span');
        span.innerHTML = "- "+params.value;

        if(params.value == "baremetal") {
            span.style.color = "#A2FF30";
        } else {
            span.style.color = "#FF8630";
        }

        const div = document.createElement('div');
        div.setAttribute('class', 'user-in-div');

        if(params.value == "active") {
            div.style.backgroundColor = "#A2FF30";
        } 

        div.appendChild(span);


        this.eGui = document.createElement('div');
        this.eGui.setAttribute('class', 'status-div');
        this.eGui.appendChild(div);
    }

    // Required: Return the DOM element of the component, this is what the grid puts into the cell
    getGui() {
        return this.eGui;
    }

    // Required: Get the cell to refresh.
    refresh(params) {
        return false;
    }
}



class HostRenderer  {
    eGui;

    // Optional: Params for rendering. The same params that are passed to the cellRenderer function.
    init(params) {
        const host_info = params.value.split("/");
        const host_name = host_info[0].trim();
        const host_ip = host_info[1].trim();
        
        const span = document.createElement('span');
        span.setAttribute('class', 'host-span');
        span.innerHTML = host_name;

        const div = document.createElement('div');
        div.setAttribute('class', 'host-div');
        div.appendChild(span);


        const span2 = document.createElement('span');
        span2.setAttribute('class', 'host-span');
        span2.innerHTML = host_ip;

        div.appendChild(span2);


        this.eGui = document.createElement('div');
        this.eGui.setAttribute('class', 'status-div');
        this.eGui.appendChild(div);
    }

    // Required: Return the DOM element of the component, this is what the grid puts into the cell
    getGui() {
        return this.eGui;
    }

    // Required: Get the cell to refresh.
    refresh(params) {
        return false;
    }
}


class RosTypeRenderer  {
    eGui;

    // Optional: Params for rendering. The same params that are passed to the cellRenderer function.
    init(params) {
        const span = document.createElement('span');
        span.setAttribute('class', 'user-span');
        span.innerHTML = "- "+params.value;

        if(params.value == "topic") {
            span.style.color = "#30E0FF";
        } else if(params.value == "serivce") {
            span.style.color = "#FFF830";
        } else if(params.value == "action") {
            span.style.color = "#FF8630";
        }

        const div = document.createElement('div');
        div.setAttribute('class', 'user-in-div');

        if(params.value == "active") {
            div.style.backgroundColor = "#A2FF30";
        } 

        div.appendChild(span);


        this.eGui = document.createElement('div');
        this.eGui.setAttribute('class', 'status-div');
        this.eGui.appendChild(div);
    }

    // Required: Return the DOM element of the component, this is what the grid puts into the cell
    getGui() {
        return this.eGui;
    }

    // Required: Get the cell to refresh.
    refresh(params) {
        return false;
    }
}


class ServiceNameTypeRenderer  {
    eGui;

    // Optional: Params for rendering. The same params that are passed to the cellRenderer function.
    init(params) {

        if(params.data.type == 'NodePort') {
            const a_tag = document.createElement('a');
            a_tag.setAttribute('href',params.data.url);
            a_tag.setAttribute('target', '_blank');
            a_tag.innerHTML = params.value;
    
            const span = document.createElement('span');
            span.setAttribute('class', 'user-span');
            span.appendChild(a_tag);
    
            this.eGui = document.createElement('div');
            this.eGui.setAttribute('class', 'status-div');
            this.eGui.appendChild(span);

        } else {
            const span = document.createElement('span');
            span.setAttribute('class', 'user-span');
            span.innerHTML = params.value;

            this.eGui = document.createElement('div');
            this.eGui.setAttribute('class', 'status-div');
            this.eGui.appendChild(span);
        }
       

        
    }

    // Required: Return the DOM element of the component, this is what the grid puts into the cell
    getGui() {
        return this.eGui;
    }

    // Required: Get the cell to refresh.
    refresh(params) {
        return false;
    }
}