$(function(){

var date=0;
var proceed=true;

$( ".date" ).change(function() {
    date=$(".date").val();
    $('.submit').attr('disabled', false)
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
    var items = [], proceed = true, info=false;
    if (date == undefined || date==''){
        proceed=false;
    }
    $("tr.data").each(function(){
        $(this).removeClass('has-error');
    })
    $("tr.data").each(function() {       
        var id = $(this).find('td:nth-child(1)').html();
        var ispresent = $(this).find('td:nth-child(5) input').is(":checked");
        var absenttype = $(this).find('td:nth-child(6)').find(':selected').data('id');
        if (absenttype == undefined){
            absenttype=''
        }
        if (ispresent == undefined){
            ispresent=''
        }
        var remarks = $(this).find('td:nth-child(7) input').val();
        if (ispresent == undefined || ispresent=='' || ispresent == false){
            if (absenttype == undefined || absenttype=='' || absenttype=='Dont'){
                proceed=false;
                $(this).addClass('has-error')
            }
        }
        else{
            if (absenttype != undefined && absenttype !='' && absenttype !='Dont'){
                info=true;
                proceed=false
                $(this).addClass('has-error')
            }   
        }
        var item = {
            teacherid : id,
            ispresent: ispresent,
            absenttype: absenttype,
            remarks : remarks,    
        };
        items.push(item);        
    });
    console.log(items)
    if (proceed){
        (function() {
            $.ajax({
                url : "", 
                type : "POST", 
                data : { date: date,
                    attendances: JSON.stringify(items),
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
        if (info){
            swal("Umm...", "In case teacher is present, please remove the reason for absence", "info");
        }
        else{
            swal("Oops...", "Select type of absence, in case the teacher is absent.", "error");
        }
    }
        
};

});