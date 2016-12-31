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
                "<td>"+this.first_name+"</td>"+
                "<td>"+this.last_name+"</td>"+
                "<td><input type='checkbox' class='is_present'/></td>"+
                "<td><input type='text' class='reason'  /></td>"+
            "</tr>");                    
                })
                $(".datediv").attr('hidden', false);
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

//Check why is this not working, even after the class is getting added - Bootstrap issue
$( "#student_table" ).on("change",".is_present",function() {
    if ($(this).is(":checked")){
        $(this).parent().parent().addClass("table-success");
    }
});


$( ".submit" ).confirm({
    title: 'Confirm!',
    icon: 'fa fa-spinner fa-spin',
    theme: 'black',
    backgroundDismiss: true,
    content: 'Are you sure to record the attendances?',
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
        var date=$(".date").val();
        if (date != ""){
        console.log("Date: "+date);
            $("tr.data").each(function() {
                var student_id = $(this).find('td:nth-child(1)').html();
                var is_present = $(this).find('td:nth-child(6) input').is(":checked");
                var remarks = $(this).find('td:nth-child(7) input').val();
                var item = {
                    student_id : student_id,
                    is_present: is_present,
                    remarks: remarks,
                    };
                items.push(item);        
                });
        console.log(items);
        
        //Send ajax function to back-end 
        (function() {
            $.ajax({
                url : "", 
                type: "POST",
                data:{ details: JSON.stringify(items),
                    date: date,
                    classid: classid,
                    year: year,
                    calltype: 'save',
                    csrfmiddlewaretoken: csrf_token},
                    dataType: 'json',               
                    // handle a successful response
                success : function(jsondata) {
                    //alert("Attendance registered successfully");
                    location.href = redirect_url;
                    //console.log(jsondata);
                },
                    // handle a non-successful response
                error : function() {
                    bootbox.alert({
                        size: "medium",
                        message: "Attendance entry failed", 
                        onEscape: true });
                    clearmodal();
                }
            });
        }());
        }
        else{
            bootbox.alert({
                size: "small",
                message: "Please enter the date.",
                onEscape: true });
            clearmodal();
        }
    
    }, //bracket for confirm closing
});




});