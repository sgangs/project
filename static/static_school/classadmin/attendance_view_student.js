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
    var studentid=parseInt($(".student").find(':selected').data('id'));
    if (startdate != '' && enddate != '' && studentid != ''){
        (function() {
            $.ajax({
                url : "", 
                type : "POST", 
                data : { start: startdate,
                    end: enddate,
                    studentid: studentid,
                    calltype: 'details',
                    csrfmiddlewaretoken: csrf_token}, // data sent with the post request
                dataType: 'json',
                // handle a successful response
                success : function(jsondata){
                    $("#student_table .data").remove();
                    $("#no_report .data").remove();
                    $("#holiday .data").remove();
                    $.each(jsondata, function(){
                        if (this.data_type == "Report"){
                            $('.student_table').prop('hidden',false);
                            present="Not Present";
                            if (this.is_present=="True"){
                                present="Present";
                            }
                            $('#student_table').append("<tr class='data'>"+
                            // "<td class='key' hidden='true'>"+this.id+"</td>"+
                            "<td class='key'>"+this.date+"</td>"+
                            "<td>"+present+"</td>"+
                            "<td>"+this.remarks+"</td>"+
                            "</tr>");
                        }
                        else if(this.data_type == "No Report"){
                            $('.no_report').prop('hidden',false);
                            $('#no_report').append("<tr class='data'>"+
                            "<td>"+this.date+"</td>"+
                            "</tr>");
                        }
                        else if(this.data_type == "Holiday"){
                            $('.holiday').prop('hidden',false);
                            $('#holiday').append("<tr class='data'>"+
                            "<td>"+this.date+"</td>"+
                            "</tr>");
                        }
                    })
                },
                // handle a non-successful response
                error : function() {
                    bootbox.alert({
                        message: "Student and date range combination doesn't have any attendance.", 
                        onEscape: true }); // provide a bit more info about the error to the user
                    clearmodal();
                }
            });
        }());
    }
    else{
        bootbox.alert({
            message: "Student or date range cannot be blank.", 
            onEscape: true }); // provide a bit more info about the error to the user
        clearmodal();
    }
});

});