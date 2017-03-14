$(function(){

$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "You cannot undo attendance recording!",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, record attendance!",
        closeOnConfirm: false,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            save_data()
        }
    })
});

function save_data(){
    var proceed=true;
    var items=[]
    $("tr.data").each(function(){
        $(this).removeClass('has-error');
    })
    $("tr.data").each(function() {       
        var id = $(this).find('td:nth-child(1)').html();
        console.log($(this).find('td:nth-child(9)').html());
        var authorize = $(this).find('td:nth-child(10) input').is(":checked");
        var reject = $(this).find('td:nth-child(11) input').is(":checked");
        if (authorize){
            if (reject){
                proceed=false;
                $(this).addClass('has-error')
            }
        }
        var item = {
            attendanceid : id,
            authorize: authorize,
            reject: reject,
        };
        items.push(item);        
    });
    if (proceed){
        (function() {
            $.ajax({
                url : "", 
                type : "POST", 
                data : { attendances: JSON.stringify(items),
                    calltype: 'save',
                    csrfmiddlewaretoken: csrf_token}, // data sent with the post request
                dataType: 'json',
                // handle a successful response
                success : function(jsondata) {
                    swal("Hooray..", "Staff attendance recorded successfully", "success");
                    setTimeout(location.reload(true),600);
                },
                //handle a non-successful response
                error : function() {
                    swal("Ehhh..", "There were some errors.", "error");
                }
            });
        }());
    }
    else{
        swal("Umm...", "In case attendance is authorized, please deselect reject.", "info");
    }
        
};

});