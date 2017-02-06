$(function(){

var class_selected="";
var year="";
var studentid="";

//This is called after the class is entered
$( ".class" ).change(function() {
    class_selected=$('.class').find(':selected').data('id');
    $( ".year" ).prop('disabled', false);
    // console.log(class_selected);
});

//This is called if year is changed
$( ".year" ).change(function() {
    year=parseInt($('.year').val());
    selectlist=$('#student')
    selectlist.find("option:gt(0)").remove();
    $('#student').selectpicker('refresh');
    // console.log(year);
    (function() {
        $.ajax({
            url : "", 
            type: "POST",
            data:{ class_selected: class_selected,
                year: year,
                calltype: 'student',
                csrfmiddlewaretoken: csrf_token},
            dataType: 'json',               
                                // handle a successful response
            success : function(jsondata) {
                // var jsondata = JSON.parse(data);                
                if(Object.keys(jsondata).length != 0){
                    $.each(jsondata, function(){
                        if (this.data_type=="Student"){
                            $('#student').append($('<option/>',{
                                'data-id': this.id,
                                'text': this.first_name+" "+this.last_name+" "+this.key+" "+this.local_id
                            }));
                            $('#student').selectpicker('refresh')
                        }                    
                    });
                }
                else{
                    swal("Bluhh..", "Student doesn't exist!", "error");
                    year="";
                    studentid="";
                }
            },
            // handle a non-successful response
            error : function() {
                swal("Oops..", "There was an error!", "error");
                year="";
                studentid="";
            }
        });
    }());
});


$( "#student" ).change(function() {
    studentid=$("#student").find(':selected').data('id');
});


$( ".details" ).click(function() {
    if (studentid != ""){
        //Send ajax function to back-end 
            (function() {
                $.ajax({
                    url : "", 
                    type: "POST",
                    data:{ studentid: studentid,
                        year: year,
                        calltype: 'payment_history',
                        csrfmiddlewaretoken: csrf_token},
                    dataType: 'json',               
                    // handle a successful response
                    success : function(jsondata) {
                        $(".feeview .data").remove();
                        $(".fee-view").attr('hidden', false);
                        console.log(jsondata);
                        $.each(jsondata, function(){
                            if (this.data_type=="payment"){
                                date=new Date(this.paid_on)
                                $('.feeview').append("<tr class='data monthly'>"+
                                    "<td hidden='true'></td>"+
                                    "<td>" + this.month + "</td>"+
                                    "<td>" + this.amount + "</td>"+
                                    "<td>" + date.getDate()+"-"+date.getMonth()+"-"+date.getFullYear() + "</td></tr>");
                                console.log(typeof(this.paid_on))
                            }
                        });
                    },
                    // handle a non-successful response
                    error : function() {
                        swal("Oops..", "There was an error!", "error");
                        student="";
                    }
                });
            }());
        }
    else{
        swal("Bluhh..", "Select Student!", "error");
        student="";
    }
});

});