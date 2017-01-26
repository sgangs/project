$(function(){

//This variable will store the student list added via json
var student_list=[];

//This will help to remove the error modal.
function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 2500);
}

var classid="";
var year = 1;

//This is called after the class option is selected
$( ".classsection" ).change(function() {
    classid=parseInt($(".classsection").find(':selected').data('id'));
    $( ".classsection" ).prop('disabled',true); 
    $( ".year" ).prop('disabled',false);
});

//This is for the reset button to work
$( ".reset" ).click(function() {
    location.reload(true);
});

//This function gets called as year is entered.
$( ".year" ).change(function() {
    year =parseInt($(this).val());
    (function() {
        $.ajax({
            url : "", 
            type : "POST", 
            data : { year: year,
                classid: classid,
                calltype: 'details',
                csrfmiddlewaretoken: csrf_token}, // data sent with the post request
            dataType: 'json',
            // handle a successful response
            success : function(jsondata){
                console.log(jsondata);
                $.each(jsondata, function(){
                    $('#student_table').append("<tr class='data'>"+
                "<td hidden='true' class='pk'>"+this.id+"</td>"+
                "<td class='key'>"+this.key+"</td>"+
                "<td class='local_id'>"+this.local_id+"</td>"+
                "<td>"+this.roll_no+"</td>"+
                "<td>"+this.first_name+"</td>"+
                "<td>"+this.last_name+"</td>"+
                "</tr>");
                })
                $(".btn").attr('disabled', false); 
                $(".year").attr('disabled', true);
            },
            // handle a non-successful response
            error : function() {
                bootbox.alert({
                    message: "Class and year cimbination doesn't exist.", 
                    onEscape: true }); // provide a bit more info about the error to the user
                clearmodal();
            }
        });
    }());
});





});