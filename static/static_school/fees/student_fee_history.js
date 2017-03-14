$(function(){

var class_selected=0, student=0, start_date, end_date;

//This is called after the class is entered
$( ".class" ).change(function() {
    class_selected=$('.class').find(':selected').data('id');
    
    selectlist=$('#student')
    selectlist.find("option:gt(0)").remove();
    $('#student').selectpicker('refresh');

    // console.log(year);
    (function() {
        $.ajax({
            url : "", 
            type: "POST",
            data:{ class_selected: class_selected,
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

// $('.date').daterangepicker({
//     'showDropdowns': true,
//     'locale': {
//         format: 'DD/MM/YYYY',
//     },
//     'autoApply':true,
//     // 'minDate': moment(min),
//     // 'maxDate': moment(max)      
//     },
//     function(start, end, label) {
//         startdate=start.format('YYYY-MM-DD');
//         enddate=end.format('YYYY-MM-DD');        
// });

//This is for the reset button to work

$( ".details" ).click(function() {
    (function() {
        $.ajax({
            url : "", 
            type: "POST",
            data:{ studentid: studentid,
                class_selected: class_selected,
                // start:start_date,
                // end:end_date,
                calltype: 'details',
            csrfmiddlewaretoken: csrf_token},
            dataType: 'json',               
            // handle a successful response
            success : function(jsondata) {
                console.log(jsondata);
                $('.details').attr('hidden', false);
                $(".feeview .data").remove();
                $.each(jsondata, function(){
                    $('.feeview').append("<tr class='data' style='text-align: center'>"+
                    "<td>" + this.year + "</td>"+
                    "<td>" + this.month + "</td>"+
                    "<td>" + this.paid_on + "</td>"+
                    "<td>" + this.amount + "</td></tr>");                    
                });
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