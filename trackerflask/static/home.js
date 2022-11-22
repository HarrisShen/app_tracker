function handler_stop_prop(event) {
    event.stopPropagation();
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

    let searchBox = document.getElementById("search-box");
    searchBox.addEventListener("change", () => {
        if(searchBox.value) {
        postData(searchBox.getAttribute("target"), {text: searchBox.value})
            .then((data) => {
                console.log(data);
                let dropdown = document.createElement("span"); // TODO: dropdown list for search results
            });
        }
    });
});