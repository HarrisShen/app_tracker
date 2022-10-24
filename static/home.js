function handler_stop_prop(event) {
    event.stopPropagation();
}

$(document).ready(function(){
    $(document).click(function(){
        let sel_box = $('.tdStatus').find('select');
        let td_to_revert = sel_box.parent();
        td_to_revert.html(sel_box.val());
    })
    $(document).click(function(){
        let text_box = $('.tdNote').find('textarea');
        let td_to_revert = text_box.parent();
        td_to_revert.html(text_box.val());
    })

    let $tdStatus = $('.tdStatus');
    $tdStatus.each(function() {
        $(this).click(handler_stop_prop);
    });
    $tdStatus.dblclick(function(event) {
        event.stopPropagation();
        if($(this).text() === "None") return;
        if($(this).children().length === 0){
            let sel_box = $('.div-update-status').clone();
            let curr_val = $(this).text();
            sel_box.find('select').children('option[value=' + curr_val + ']').attr("selected", "selected");
            $(this).html(sel_box.html());
            let select_obj = $(this).find('select')
            select_obj.one('change', function(){
                curr_val = select_obj.val();
                console.log(curr_val);
                // $.post("/api/update", {status: curr_val}, dataType="json");
                $(this).html(curr_val);
            });
        }
    });

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