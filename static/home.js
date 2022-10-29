function handler_stop_prop(event) {
    event.stopPropagation();
}

function getCurrTime() {
    function twoDigits(num) {return (num < 10 ? '0' : '') + num.toString();}
    const now = new Date();
    return (now.getFullYear() + '-' + twoDigits(now.getMonth() + 1) + '-' + twoDigits(now.getDay()) +
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

function revertTd(className) {
    // Turn a editted td element back to a normal text-only one
    let tdElement = document.body.getElementsByClassName(className);
    tdElement = Array.from(tdElement);
    tdElement = tdElement.filter(element => element.childElementCount > 0);
    if(tdElement.length === 0) return null;
    tdElement = tdElement[0];
    let newValue = tdElement.firstElementChild.value;
    tdElement.innerHTML = newValue;
    if(tdElement.getAttribute('data-prev') === newValue) return null;
    return tdElement;
}

function childElementSum(nodeList) {
    nodeList = Array.from(nodeList);
    return nodeList.map(
        (node) => node.childElementCount
    ).reduce((a,b) => a + b, 0);
}

$(document).ready(function(){
    $(document).click(function(){
        let text_box = $('.tdNote').find('textarea');
        let td_to_revert = text_box.parent();
        td_to_revert.html(text_box.val());
    })

    let tdStatus = document.body.getElementsByClassName('tdStatus');
    tdStatus = Array.from(tdStatus);
    tdStatus.forEach((element) => {
        element.addEventListener('click', handler_stop_prop);
    });
    tdStatus.forEach((element) => {
        element.addEventListener('dblclick', (event) => {
            event.stopPropagation();
            if(childElementSum(tdStatus) === 1) return;
            if(element.textContent === 'None') return;
            if(element.childElementCount === 0) {
                let selectBox = document.getElementsByClassName('div-update-status')[0].cloneNode(true);
                let curr_val = element.textContent;
                element.setAttribute('data-prev', curr_val);
                let opts = selectBox.getElementsByTagName('option');
                opts = Array.from(opts);
                selected = opts.filter((element) => element.getAttribute('value') === curr_val)[0];
                selected.setAttribute('selected', 'selected');
                element.innerHTML = selectBox.innerHTML;
            }
        });
    });
    // $tdStatus.dblclick(function(event) {
    //     event.stopPropagation();
    //     if($tdStatus.children().length === 1) return;
    //     if($(this).text() === "None") return;
    //     if($(this).children().length === 0){
    //         let sel_box = $('.div-update-status').clone();
    //         let curr_val = $(this).text();
    //         $(this).setAttribute('data-prev', curr_val);
    //         sel_box.find('select').children('option[value=' + curr_val + ']').attr("selected", "selected");
    //         $(this).html(sel_box.html());
    //         // let select_obj = $(this).find('select')
    //         // select_obj.one('change', function(){
    //         //     curr_val = select_obj.val();
    //         //     console.log(curr_val);
    //         //     // $.post("/api/update", {status: curr_val}, dataType="json");
    //         // });
    //     }
    // });

    let $tdNote = $('.tdNote');
    $tdNote.each(function() {
        $(this).click(handler_stop_prop);
    });
    $tdNote.dblclick(function(event) {
        event.stopPropagation();
        if($(this).children().length === 0){
            let text_box = $('.div-update-note').clone();
            let curr_val = $(this).text();
            text_box.find("textarea").text(curr_val);
            $(this).html(text_box.html());                
        }
    });
});