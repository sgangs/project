$(function(){

var ispresent="", leavetype=0, remarks="";

$( ".ispresent" ).change(function() {
    ispresent=$(".ispresent").find(':selected').data('id');
    $('.submit').attr('disabled',false);
    if (!ispresent){
        $('.leave').attr('hidden',false);
    }
    else{
        $('.leave').attr('hidden',true);
    }
});

$( ".leavetype" ).change(function() {
    leavetype=$(".leavetype").find(':selected').data('id');
});

$( ".remarks" ).change(function() {
    remarks=$(".remarks").val();
});


$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "You cannot undo attendance recording!",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
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
    var proceed = true;
    if (!ispresent){
        if (leavetype<1 || isNaN(leavetype) || ($.trim(remarks).length)<2){
            proceed=false;
        }
    }
    if (proceed){
        (function() {
            $.ajax({
                url : "", 
                type : "POST", 
                data : { ispresent: ispresent,
                    leavetype: leavetype,
                    remarks: remarks,
                    calltype: 'save',
                    csrfmiddlewaretoken: csrf_token}, // data sent with the post request
                dataType: 'json',
                // handle a successful response
                success : function(jsondata) {
                    swal("Hooray..", "Teacher attendance recorded successfully", "success");
                    setTimeout(location.reload(true),600);
                },
                //handle a non-successful response
                error : function() {
                    swal("Ehhh..", "There were some errors.", "error");
                }
            });
        }());
        
        // }
    }
    else{
        swal("Oops...", "Please select leave type and add proper reason for leave", "error");
    }
        
};

});