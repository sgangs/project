$(function(){

var classid=0, month="";

//This is called after the class is entered
$( ".class" ).change(function() {
    classid=$('.class').find(':selected').data('id');
});

$( ".date" ).change(function() {
    month=$('.date').find(':selected').data('id');
    $('.details').attr('disabled',false);
});


//This is for the reset button to work

$( ".details" ).click(function() {
    // console.log(parseInt(date.split("-")[0]));
    // console.log(date.split("-")[1]);
    // date.split("/").reverse().join("-"),
    (function() {
        $.ajax({
            url : "", 
            type: "POST",
            data:{ classid: classid,
                month: month,                
                csrfmiddlewaretoken: csrf_token},
            dataType: 'json',               
            // handle a successful response
            success : function(jsondata) {
                console.log(jsondata);
                // $('.details').attr('hidden', false);
                // $(".feeview .data").remove();
                // $.each(jsondata, function(){
                //     $('.feeview').append("<tr class='data' style='text-align: center'>"+
                //     "<td>" + this.year + "</td>"+
                //     "<td>" + this.month + "</td>"+
                //     "<td>" + this.paid_on + "</td>"+
                //     "<td>" + this.amount + "</td></tr>");                    
                // });
            },
            // handle a non-successful response
            error : function() {
                swal("Oops..", "There was an error!", "error");
                student="";
                }
            });
        }());    
});

});