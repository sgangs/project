$(function(){

//This variable will store the student list added via json
var student_list=[];

//This will help to remove the error modal.
function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 2500);
}

var year='',day=8, period='', subject='';

//This function gets called as year is entered.
$( ".year" ).change(function() {
    year = $(this).val();
    //alert (year)
    (function() {
        $.ajax({
            url : "", 
            type : "POST", 
            data : { year: year,
                calltype: 'year',
                csrfmiddlewaretoken: csrf_token}, // data sent with the post request
            dataType: 'json',
            // handle a successful response
            success : function(jsondata) {  
                $.each(jsondata, function(){
                    if (this.data_type=="Teacher"){
                        $('.classteacher').append(this.first_name+" "+this.last_name);
                        $('.classteacherdiv').attr('hidden',false);
                    }
                    else if (this.data_type=="Syllabus"){
                        $('.classsubjectdiv').attr('hidden',false);
                        $('#subject_table').append("<tr>"+
                        "<td>" + this.subject + "</td>"+
                        "<td>" + this.topics + "</td></tr>");
                        $('.selectsubject').append($('<option>',{
                        'data-id': this.id,
                        'text': this.subject
                        }));
                    }
                    else if (this.data_type=="Period"){
                        console.log(this)
                        $('tr.'+this.period).find('.'+this.day+'').html('<p>'+this.subject +'<//p><p>'+this.teacher+'</p>')
                    }
                    else if (this.data_type=="Error"){
                        bootbox.alert({
                            message: this.message, 
                            onEscape: true }); // provide a bit more info about the error to the user
                        clearmodal();
                    }
                });
                $('.addperiod').prop('disabled', false);
                $('.year').prop('disabled', true);
            },
            // handle a non-successful response
            error : function() {
                bootbox.alert({
                    message: "Data not available for selected year.", 
                    onEscape: true }); // provide a bit more info about the error to the user
                clearmodal();
            }
        });
    }());
});

$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Add period to database?",
        type: "info",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, Add Period!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        // swal("Deleted!",
        // "Your imaginary file has been deleted.",
        // "success");
        if (isConfirm){
            setTimeout(function(){save_data()},600)
            
        }
    })
});


function save_data(){
    day=$('.day').find(':selected').data('id');
    period=$('.period').find(':selected').data('id');
    subject=$('.selectsubject').find(':selected').data('id');
    if (day >6 || period =="" || subject =="" || day == undefined || period == undefined || subject ==undefined){
        swal("Ehhh..", "All three data: Day, Period and Subject must be entered ", "error");
    }
    else{
            // Send ajax function to back-end 
            (function() {
                $.ajax({
                    url : "", 
                    type: "POST",
                    data:{ day: day,
                        period:period,
                        year:year,
                        subject: subject,
                        calltype: 'save',
                        csrfmiddlewaretoken: csrf_token},
                    dataType: 'json',               
                                // handle a successful response
                    success : function(jsondata) {
                        console.log(jsondata);
                        // if (jsondata=="Error"){
                        //     swal("Oops..", "There were some errors. Rechek your data!!", "error");    
                        // }
                        if (jsondata== null){
                        swal("Hooray..", "Period added successfully!!", "success");
                        location.reload();
                        }
                        else{
                         swal("Oops..", jsondata, "error");   
                        }                        
                        //console.log(jsondata);
                    },
                    // handle a non-successful response
                    error : function() {
                        swal("Oops..", "There were some errors. Maybe the period is not free!!", "error");
                    }
                });
            }());
    }
           
}

});//end of function load.
