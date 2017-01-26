$(function(){

//This variable will store the student list added via json

//This will help to remove the error modal.
function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 2500);
}

var classid="";
var year = 1;
var date="";

//This is called after the class option is selected
$( ".classsection" ).change(function() {
    classid=parseInt($(".classsection").find(':selected').data('id'));
    console.log(classid);
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
                    // $('.student').html('<option data-tokens='+this.id+'>'+this.first_name+" "
                    //     +this.last_name+" "+this.key+" "+this.local_id+'</option>').selectpicker('refresh');
                    $('#student').append($('<option>',{
                        'data-id': this.id,
                        'text': this.first_name+" "+this.last_name+" "+this.key+" "+this.local_id
                    }));
                    $('#student').selectpicker('refresh')
                })
                $(".datediv").attr('hidden', false);
                $(".studentdiv").attr('hidden', false);
                $(".submit").attr('disabled', false); 
                $(".year").attr('disabled', true);
                
            },
            // handle a non-successful response
            error : function() {
                bootbox.alert({
                    message: "Class and year combination doesn't exist.", 
                    onEscape: true }); // provide a bit more info about the error to the user
                clearmodal();
            }
        });
    }());
});
$( ".date" ).change(function(){
    date=$(this).val();
    console.log(date);
    $( "#student" ).attr('disabled',false);
    $('#student').selectpicker('refresh');
});

$( "#student" ).change(function() {
    studentid=parseInt($("#student").find(':selected').data('id'));
    (function() {
        $.ajax({
            url : "", 
            type : "POST", 
            data : { date: date,
                classid: classid,
                studentid: studentid,
                calltype: 'attendance',
                csrfmiddlewaretoken: csrf_token}, // data sent with the post request
            dataType: 'json',
            // handle a successful response
            success : function(jsondata){
                console.log(jsondata);
                console.log(jsondata[0]['is_present']);
                $('.presentdiv').attr('hidden',false);
                if (jsondata[0]['is_present']){
                    $('.is_present').prop('checked', true);
                }
                else{
                    $('.is_present').prop('checked', false);
                }
                //$('.is_present').prop('checked', true);
                $('.remarks').val(jsondata[0]['remarks']);
                $('.attendance_data').val(jsondata[0]['id']);
            },
            // handle a non-successful response
            error : function() {
                bootbox.alert({
                    message: "Class, Student and date matching attendance data doesn't exist.", 
                    onEscape: true }); // provide a bit more info about the error to the user
                clearmodal();
            }
        });
    }());
    
});






$( ".submit" ).confirm({
    title: 'Confirm!',
    icon: 'fa fa-spinner fa-spin',
    theme: 'black',
    backgroundDismiss: true,
    content: 'Are you sure to record the edited attendances?',
    confirmButton: 'Yes!',
    cancelButton: 'No!',
    autoClose: 'cancel|6000',
    confirmButtonClass: 'btn-success',
    cancelButtonClass: 'btn-danger',
    animation: 'rotateY',
    closeAnimation: 'rotateXR',
    animationSpeed: 750,
    confirm: function(){
            
    //get all itemcode & quantity pair 
        var items = [];
        console.log("Date: "+date);
        is_present=$('.is_present').is(":checked")
        remarks=$('.remarks').val()
        console.log("Present: "+is_present+" Remarks: "+remarks)
        
        //Send ajax function to back-end 
        // (function() {
        //     $.ajax({
        //         url : "", 
        //         type: "POST",
        //         data:{ details: JSON.stringify(items),
        //             date: date,
        //             classid: classid,
        //             year: year,
        //             calltype: 'save',
        //             csrfmiddlewaretoken: csrf_token},
        //             dataType: 'json',               
        //             // handle a successful response
        //         success : function(jsondata) {
        //             //alert("Attendance registered successfully");
        //             location.href = redirect_url;
        //             //console.log(jsondata);
        //         },
        //             // handle a non-successful response
        //         error : function() {
        //             bootbox.alert({
        //                 size: "medium",
        //                 message: "Attendance entry failed", 
        //                 onEscape: true });
        //             clearmodal();
        //         }
        //     });
        // }());
                
    }, //bracket for confirm closing
});




});