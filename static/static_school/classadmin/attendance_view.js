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
    var date=$(".date").val();
    var classid=parseInt($(".classsection").find(':selected').data('id'));
    if (date != '' && classid != ''){
        (function() {
            $.ajax({
                url : "", 
                type : "POST", 
                data : { date: date,
                    classid: classid,
                    calltype: 'details',
                    csrfmiddlewaretoken: csrf_token}, // data sent with the post request
                dataType: 'json',
                // handle a successful response
                success : function(jsondata){
                    console.log(jsondata);
                    $.each(jsondata, function(){
                        present="Not Present";
                        if (this.is_present=="True"){
                            present="Present";
                        }
                        $('#student_table').append("<tr class='data'>"+
                        "<td class='key' hidden='true'>"+this.id+"</td>"+
                        "<td class='key'>"+this.key+"</td>"+
                        "<td class='local_id'>"+this.local_id+"</td>"+
                        "<td>"+this.first_name+"</td>"+
                        "<td>"+this.last_name+"</td>"+
                        "<td>"+present+"</td>"+
                        "<td>"+this.remarks+"</td>"+
                        "</tr>");                    
                    })
                },
                // handle a non-successful response
                error : function() {
                    bootbox.alert({
                        message: "Class and date combination doesn't have any attendance.", 
                        onEscape: true }); // provide a bit more info about the error to the user
                    clearmodal();
                }
            });
        }());
    }
    else{
        bootbox.alert({
            message: "Class or date cannot be blank.", 
            onEscape: true }); // provide a bit more info about the error to the user
        clearmodal();
    }
});

});