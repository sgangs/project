$(function(){

var leavetype=0, remarks="", date="", entry_type='';

$('.date').datepicker({
    autoclose: true,
    startDate: '-60d',
    // endDate: moment(),
    endDate: '0d',
    format: 'dd/mm/yyyy',    
    });


$( ".entry_type" ).change(function() {
    entry_type=$(".entry_type").find(':selected').data('id');
    if (entry_type == 'Mispunch'){
        $('.submit').attr('disabled', false);
        $('.mispunch').attr('hidden', false);
    }
    else{
        $('.leave').attr('hidden', false);
    }
});

$( ".leavetype" ).change(function() {
    leavetype=$(".leavetype").find(':selected').data('id');
    $('.submit').attr('disabled', false);
});

$( ".date" ).change(function() {
    date=$(".date").val();    
});

$( ".remarks" ).change(function() {
    remarks=$(".remarks").val();
});


$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "You cannot undo leave/regularization.!",
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
    if (entry_type == "Leave"){
        if (leavetype<1 || isNaN(leavetype) || ($.trim(remarks).length)<2 || date == '' || typeof(date)=='undefined'){
                proceed=false;
        }
        console.log("Here");
    }
    else{
        if (($.trim(remarks).length)<2 || date == '' || typeof(date)=='undefined'){
                proceed=false;
        }
        console.log("Here");
    }
    
    if (proceed){
        (function() {
            $.ajax({
                url : "", 
                type : "POST", 
                data : { date: date.split("/").reverse().join("-"),
                    leavetype: leavetype,
                    entry_type: entry_type,
                    remarks: remarks,
                    calltype: 'save',
                    csrfmiddlewaretoken: csrf_token}, // data sent with the post request
                dataType: 'json',
                // handle a successful response
                success : function(jsondata) {
                    console.log(jsondata);
                    if (jsondata == "Holiday"){
                        location.href = holiday_url;
                    }
                    else{
                        swal("Hooray..", "Teacher attendance recorded successfully", "success");
                        setTimeout(location.reload(true),600);
                    }
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
        swal("Oops...", "Please select leave type and add proper reason for leave/mispunch", "error");
    }
        
};

});