
var draggingEle;
var placeholder;
var isDraggingStarted = false;

// 마우스 위치값을 위해 선언
var x = 0;
var y = 0;
const swap = function (nodeA, nodeB) {
    // 상위 컨테이너 요소를 가져옴
    const parentA = nodeA.parentNode;
    // nodeA에 형제(다음 요소)가 nodeB라면 nodeA, 아닌 경우 다음 요소를 담음
    // sibling에서 조건처리하는 이유는 placeholder와 drag element의 위치를 조정하기 위해서
    const siblingA = nodeA.nextSibling === nodeB ? nodeA : nodeA.nextSibling;

    // nodeA를 nodeB의 뒤로 삽입
    nodeB.parentNode.insertBefore(nodeA, nodeB);

    // nobeB를 nodeA에 형제(다음요소) 뒤에 넣음
    parentA.insertBefore(nodeB, siblingA);
};

  // nodeA가 nodeB 위에 존재하는지 확인하는 함수
const isAbove = function (nodeA, nodeB) {
    // 각 node의 위치정보를 가져옴
    const rectA = nodeA.getBoundingClientRect();
    const rectB = nodeB.getBoundingClientRect();

    // top을 기준으로 A가 B보다 작으면 화면 위치상 A는 B보다 상위에 존재함으로 above가 성립
    return rectA.top + rectA.height / 2 < rectB.top + rectB.height / 2;
};


const mouseDownHandler = function (e) {
    // 현재 이벤트가 발생한 element를 저장
    draggingEle = e.target;

    // 선택된 element의 위치를 중심으로 마우스 클릭 위치를 계산
    const rect = draggingEle.getBoundingClientRect();
    x = e.pageX - rect.left;
    y = e.pageY - rect.top;

    // mouse 움직임, 해제 이벤트 적용
    document.addEventListener('mousemove', mouseMoveHandler);
    document.addEventListener('mouseup', mouseUpHandler);
};

const mouseMoveHandler = function (e) {
    // 현재 이벤트가 발생한 element의 위치 정보 가져옴
    const draggingRect = draggingEle.getBoundingClientRect();

    // 첫 움직임인 경우 적용
    if (!isDraggingStarted) {
      isDraggingStarted = true;

      // 선택한 element가 움직이는 동안 표시할 placeholder element를 생성
      placeholder = document.createElement('div');
      placeholder.classList.add('placeholder');
      draggingEle.parentNode.insertBefore(placeholder, draggingEle.nextSibling);
      placeholder.style.height = `${draggingRect.height}px`;
    }

    // 드래그 하는 동안 element가 마우스 위치를 따라가도록 설정
    draggingEle.style.position = 'absolute';
    draggingEle.style.top = `${e.pageY - y}px`;
    draggingEle.style.left = `${e.pageX - x}px`;

    // 선택 element에 전 element와 다음 element를 선택함
    // placeholder가 들어가 있기 때문에 순서는 다음과 같음
    // 이전 element
    // drag 중인 element
    // placeholder element
    // 다음 element
    const prevEle = draggingEle.previousElementSibling;
    const nextEle = placeholder.nextElementSibling;

    // 이전 element가 존재하고 drag 중인 element가 이전 element 위에 존재하는 경우
    if (prevEle && isAbove(draggingEle, prevEle)) {
      // 서로의 위치를 바꿈
      // swap을 통해 place와 drag를 바꾸는 이유는 한번 움직이는게 아닌 연속적으로 상위요소로 올라갈 때, preEle 처리전 place와 drag의 위치를 정리하기 위해서임
      swap(placeholder, draggingEle);
      swap(placeholder, prevEle);
      return;
    }

    // 다음 element가 존재하고 drag 중인 element가 다음 element 위에 존재하는 경우
    if (nextEle && isAbove(nextEle, draggingEle)) {
      swap(nextEle, placeholder);
      swap(nextEle, draggingEle);
    }
};

const mouseUpHandler = function () {
    // placeholder가 존재하면 지워줌
    placeholder && placeholder.parentNode.removeChild(placeholder);

    // Get the element at the current mouse position
    const mouseX = draggingEle.style.left.replace('px', '');
    const mouseY = draggingEle.style.top.replace('px', '');
    const elementsAtPoint = document.elementsFromPoint(mouseX, mouseY);
    const targetElement = elementsAtPoint.find(element => element.classList.contains('level_item'));
    const targetList = elementsAtPoint.find(element => element.classList.contains('list-clusters'));

    if(targetElement) {
        targetElement.appendChild(draggingEle);
    }else if(targetList) {
        targetList.appendChild(draggingEle);
    }

    // absolute로 움직이던 속성을 다 제거
    draggingEle.style.removeProperty('top');
    draggingEle.style.removeProperty('left');
    draggingEle.style.removeProperty('position');

    // 위치와 element 관련 date를 초기화
    x = null;
    y = null;
    draggingEle = null;
    isDraggingStarted = false;

    // 이벤트 해제
    document.removeEventListener('mousemove', mouseMoveHandler);
    document.removeEventListener('mouseup', mouseUpHandler);
};

  // 모든 draggable 요소에 mouseDown 이벤트 적용
  
function add_Level() {
    const html = `
    <div class="level_parent">
        <div class="level_item" style="width: 100%; height: 100%;"></div>
        <div class="ok-button" style="bottom: 10px; margin-bottom: 0;background: #D30F0F;" onclick="remove_Level(this)">Remove</div>
    </div>
    `;

    $('#levels').append(html);
    //document.getElementById('levels').innerHTML += html;
}


function remove_all_Level() {

    document.querySelectorAll('.level_parent').forEach(function(item) {
        item.remove();
    });
}

function init_Level() {
    remove_all_Level();
    add_Level();

    document.querySelectorAll('.draggable').forEach(function(item) {
        item.remove();
    });

    document.getElementById('list-clusters').innerHTM = '';

    used_clusters.forEach(function(name) {
        add_draggable(name);
    });

    [].slice.call(document.getElementById('list-clusters').querySelectorAll('.draggable')).forEach(function (item) {
        item.addEventListener('mousedown', mouseDownHandler);
    });
}


function add_draggable(name) {
    const html = `
    <div class="draggable">${name}</div>
    `;

    document.getElementById('list-clusters').innerHTML += html;
}

function remove_Level(button) {

    // Get count of level_parent elements
    const levelParentCount = document.getElementsByClassName('level_parent').length;
    if(levelParentCount <= 1) {
        alert('Last level cannot be removed');
        return; // Don't remove if it's the last level
    }

    const levelItems = button.parentElement.querySelectorAll('.draggable');
    levelItems.forEach(function(item) {
        document.getElementById('list-clusters').appendChild(item);
    });

    button.parentElement.remove();
}


function okLevel() {


    const draggableCount = document.getElementById('list-clusters').getElementsByClassName('draggable').length;
    if(draggableCount > 0) {
        alert('Remind to add clusters to the level');
        return;
    }

    $('#drag-clusters').hide();

    var level_items = [];

    document.querySelectorAll('.level_item').forEach(function(item) {
        var names = [];

        item.querySelectorAll('.draggable').forEach(function(draggable) {
            names.push(draggable.textContent);
        });

        if(names.length > 0) {
            if(names.length == 1) {
                names = names[0];
            }
            
            level_items.push(names);
        }
    });

    var present_levels_str = JSON.stringify(level_items);

    if(level_items.length == 1) {
        present_levels_str = JSON.stringify(level_items[0]);
    }else if(level_items.length == 0) {
        present_levels_str = "";
    }

    $("#present-clusters").val(present_levels_str);
}


function closeLevel() {
    $('#drag-clusters').hide();
}



const list = document.getElementById('list-clusters');


[].slice.call(list.querySelectorAll('.draggable')).forEach(function (item) {
    item.addEventListener('mousedown', mouseDownHandler);
});

$('#drag-clusters').hide();