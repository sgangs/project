$(function(){

$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "The record(s) will be permanently deleted!",
        type: "info",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, delete record(s).",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){delete_data()},600)            
        }
        else{
            swal("Okay..", "Records are not deleted", "info");
        }
    })
});


function delete_data(){            
    var items = [];
    $("tr.data").each(function() {
        var item_id = $(this).find('td:nth-child(1)').html();
        if (calltype== 'Notice'){
            var will_delete = $(this).find('td:nth-child(5) input').is(":checked");
        }
        else{
            var will_delete = $(this).find('td:nth-child(4) input').is(":checked");
        }
        var item = {
            item_id : item_id,
        };
        if (will_delete){
            items.push(item);
        }
    });
    if (items.length > 0){
        // Get data function defined earlier gets the attendance.
        //Send ajax function to back-end 
        (function() {
            $.ajax({
                url : "", 
                type: "POST",
                data:{ details: JSON.stringify(items),
                    called_for: 'save',
                    csrfmiddlewaretoken: csrf_token},
                    dataType: 'json',               
                    // handle a successful response
                success : function(jsondata) {
                    //alert("Attendance registered successfully");
                    swal("Hooray..", "Records deleted successfully!!", "success");
                    setTimeout(location.reload(true),750);
                    location.href = redirect_url;
                    //console.log(jsondata);
                },
                    // handle a non-successful response
                error : function() {
                    swal("Oops..", "There were some errors.", "error");                    
                }
            });
        }());
    }
    else{
        swal("Oops..", "Please select atleast one item.", "error");
    }
};

});