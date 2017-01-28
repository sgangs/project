$(function(){

//This variable will store the student list added via json
var student_list=[];

//This will help to remove the error modal.
function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 2500);
}


//This is for the reset button to work
$( ".reset" ).click(function() {
    location.reload(true);
});

//This function gets called as year is entered.
$( ".check" ).click(function() {
    var feeid=parseInt($(".monthlyfee").find(':selected').data('id'));
    if (feeid != ''){
        (function() {
            $.ajax({
                url : "", 
                type : "POST", 
                data : {feeid: feeid,
                    //calltype: 'details',
                    csrfmiddlewaretoken: csrf_token}, // data sent with the post request
                dataType: 'json',
                // handle a successful response
                success : function(jsondata){
                    // console.log(jsondata);
                    $("#student_table .data").remove(); 
                    $.each(jsondata, function(){
                        $('#student_table').append("<tr class='data'>"+
                        "<td class='account'>"+this.account+"</td>"+
                        "<td class='amount'>"+this.amount+"</td></tr>");                    
                    })
                },
                // handle a non-successful response
                error : function() {
                    $("#student_table .data").remove(); 
                    bootbox.alert({
                        message: "Monthly Fee doesn't have any details./Error getting data.", 
                        onEscape: true }); // provide a bit more info about the error to the user
                    clearmodal();
                }
            });
        }());
    }
    else{
        bootbox.alert({
            message: "Monthly fee cannot be blank.", 
            onEscape: true }); // provide a bit more info about the error to the user
        clearmodal();
    }
});

});