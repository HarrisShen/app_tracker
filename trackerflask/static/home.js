function handler_stop_prop(event) {
    event.stopPropagation();
}

function getCurrTime() {
    function twoDigits(num) {return (num < 10 ? '0' : '') + num.toString();}
    const now = new Date();
    return (now.getFullYear() + '-' + twoDigits(now.getMonth() + 1) + '-' + twoDigits(now.getDate()) +
        'T' + now.getHours() + ':' + now.getMinutes());
}

async function postData(url = '', data = {}) {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    return response.json();
  }

function getEditingTd(className) {
    let tdElement = document.body.getElementsByClassName(className);
    tdElement = Array.from(tdElement);
    tdElement = tdElement.filter(element => element.childElementCount > 0);
    if(tdElement.length === 0) return null;
    tdElement = tdElement[0];
    return tdElement; 
}

function updateTd(className) {
    let tdElement = getEditingTd(className);
    if(tdElement === null) return null;
    let inputs = tdElement.getElementsByClassName('update');
    let updateData = {};
    inputs = Array.from(inputs);
    inputs.forEach((element) => {
        updateData[element.getAttribute('name')] = element.value;
    });
    let newValue = tdElement.firstElementChild.value;
    tdElement.innerHTML = newValue;
    if(tdElement.getAttribute('data-prev') === newValue) return null;
    postData(get_url_update(), updateData)
        .then((data) => alert(data['message']));
    return tdElement;
}

function revertTd(className) {
    // Turn a editing td element back to a normal text-only one
    let tdElement = getEditingTd(className);
    if(tdElement === null) return null;
    const prevValue = tdElement.getAttribute('data-prev');
    tdElement.innerHTML = prevValue;
    return tdElement;
}

function childElementSum(nodeList) {
    nodeList = Array.from(nodeList);
    return nodeList.map(
        (node) => node.childElementCount
    ).reduce((a,b) => a + b, 0);
}

function addEditableEvent() {
    let editButton = document.createElement("button");
    editButton.setAttribute("type", "button");
    editButton.setAttribute("class", "bt bt-outline-second");
    let icon = document.createElement("i");
    icon.setAttribute("class", "bi bi-pencil-square");
    editButton.appendChild(icon);
    let tdEditable = document.body.getElementsByClassName('td-editable');
    tdEditable = Array.from(tdEditable);
    tdEditable.forEach((element) => {
        element.addEventListener('onmouseover', () => {
            element.appendChild(editButton);
        });
        element.addEventListener('onmouseout', () => {
            element.removeChild(editButton);
        })
    })
}

function clearEditBtn(){
    let infoTable = document.getElementById("tableAppInfo");
    let currEditBtn = infoTable.getElementsByTagName("button");
    if(currEditBtn.length) {
        currEditBtn = currEditBtn[0];
        let tdCurrEdit = currEditBtn.parentElement;
        tdCurrEdit.removeChild(currEditBtn);
        return true;
    }
    return false;
}

$(document).ready(function(){
    // $(document).click(function(){
    //     let text_box = $('.tdNote').find('textarea');
    //     let td_to_revert = text_box.parent();
    //     td_to_revert.html(text_box.val());
    // })

    document.addEventListener('click', () => {
        clearEditBtn();
    });

    let editButton = document.getElementById("div-edit-button").children[0].cloneNode(true);
    let tdEditable = document.body.getElementsByClassName('td-editable');
    tdEditable = Array.from(tdEditable);
    tdEditable.forEach((element) => {
        element.addEventListener('click', () => {
            event.stopPropagation();
            console.log("clicked");
            if(!clearEditBtn() && element.childElementCount == 0) {
                element.appendChild(editButton);
            }
        });
    })

    // let tdStatus = document.body.getElementsByClassName('tdStatus');
    // tdStatus = Array.from(tdStatus);
    // tdStatus.forEach((element) => {
    //     element.addEventListener('click', handler_stop_prop);
    // });
    // tdStatus.forEach((element) => {
    //     element.addEventListener('dblclick', (event) => {
    //         event.stopPropagation();
    //         if(childElementSum(tdStatus) === 1) return;
    //         // if(element.textContent === 'None') return;
    //         if(element.childElementCount === 0) {
    //             let updateDiv = document.getElementsByClassName('div-update-status')[0].cloneNode(true);
    //             let selectBox = updateDiv.getElementsByTagName('select')[0];
    //             let curr_val = element.textContent;
    //             element.setAttribute('data-prev', curr_val);
    //             let opts = selectBox.getElementsByTagName('option');
    //             opts = Array.from(opts);
    //             selected = opts.filter((element) => element.getAttribute('value') === curr_val);
    //             if(selected.length === 1){
    //                 selected = selected[0];
    //                 selected.setAttribute('selected', 'selected');                    
    //             }
    //             let currRow = element.parentElement;
    //             const compName = currRow.getElementsByClassName('tdComp')[0].textContent;
    //             updateDiv.getElementsByClassName('update-company-auto')[0].setAttribute('value', compName);
    //             const posName = currRow.getElementsByClassName('tdPos')[0].textContent;
    //             updateDiv.getElementsByClassName('update-position-auto')[0].setAttribute('value', posName);
    //             element.innerHTML = updateDiv.innerHTML;
    //             element.getElementsByClassName('update-time')[0].value = getCurrTime();
    //         }
    //     });
    // });

    // let $tdNote = $('.tdNote');
    // $tdNote.each(function() {
    //     $(this).click(handler_stop_prop);
    // });
    // $tdNote.dblclick(function(event) {
    //     event.stopPropagation();
    //     if($(this).children().length === 0){
    //         let text_box = $('.div-update-note').clone();
    //         let curr_val = $(this).text();
    //         text_box.find("textarea").text(curr_val);
    //         $(this).html(text_box.html());                
    //     }
    // });
});