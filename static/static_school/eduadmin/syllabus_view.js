$(function(){

//This variable will store the student list added via json


var classselected="";

$( ".class" ).change(function() {
    classselected=$(".class").find(':selected').data('id');  
    (function(){
        $.ajax({
            url : "", 
            type: "POST",
            data:{classselected:classselected,
                csrfmiddlewaretoken: csrf_token},
            dataType: 'json',
            // handle a successful response
            success : function(jsondata) {
                console.log(jsondata);
                $("#syllabus_table .data").remove();
                if (jsondata.length<1){
                    $('.syllabus').attr('hidden',true);
                    swal("Umm..", "There's no syllabus created for the selection.", "error");    
                }
                else{
                    $('.syllabus').attr('hidden',false);
                    $.each(jsondata, function(){
                        $('#syllabus_table').append("<tr class='data' style='text-align: center' >"+
                            "<td>"+this.subject+"</td>"+
                            "<td>"+this.topics+"</td>"+
                            "<td>" + this.month + "</td></tr>");
                    });
                }
            },
                // handle a non-successful response
            error : function() {
                $('.syllabus').attr('hidden',true);
                swal("Umm..", "Syllabus not updated for selected class in the current academic year", "error");
            }
        });
    }());
});

//This is for the reset button to work
$( ".reset" ).click(function() {
    // location.reload(true);
    $('.student_add').attr('hidden',true);
    $('.fetch_data').attr('disabled',false);
    $(".student_add .data").remove();
});

$('.fetch').click(function(e) {
    if (batch != '' && classselected != '' && year != '' && batch != undefined && classselected != undefined && year != undefined){
        (function(){
            $.ajax({
                url : "", 
                type: "POST",
                data:{batchid:batch,
                    classselected:classselected,
                    year:year,
                    calltype: 'student',
                    csrfmiddlewaretoken: csrf_token},
                dataType: 'json',
                // handle a successful response
                success : function(jsondata) {
                    var i=0;
                    if (jsondata.length<1){
                        swal("Umm..", "There's no new admission student in the batch.", "error");    
                    }
                    else{
                        $('.student_add').attr('hidden',false);
                        $('.fetch_data').attr('disabled',true);
                        $.each(jsondata, function(){
                            if (this.data_type=="Student"){
                                i++;
                                $('.student').append("<tr class='data' >"+
                                    "<td hidden='true'>"+this.id+"</td>"+
                                    "<td style='height:20px;'>" + i + "</td>"+
                                    "<td style='height:20px;'>" + this.key + "</td>"+
                                    "<td style='height:20px;'>" + this.local_id + "</td>"+
                                    "<td style='height:20px;'>" + this.name + "</td>"+
                                    "<td style='height:20px;'><input type='checkbox'></td>"+
                                    "<td style='height:20px;'><input class='form-control' type='number'></td></tr>");
                            }
                        });
                    }
                },
                // handle a non-successful response
                error : function() {
                    swal("Umm..", "Student doesn't exist or all students of the batch & year combination already has class ", "error");
                }
            });
        }());
    }
    else{
        swal("Oops..", "All the three fields must be filled.", "error");
    }
})


$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "Please confirm adding student(s) to class for selected academic year!",
        type: "info",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, add student(s)!",
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
    var proceed = true;        
    var items = [];    
    if (year != 0 && typeof(year) != "undefined" && classselected!= "" && typeof(classselected) != "undefined"){
        $("tr.data").each(function() {
            var student_id = parseInt($(this).find('td:nth-child(1)').html());
            var is_added = $(this).find('td:nth-child(6) input').is(":checked");
            var roll_no = parseInt($(this).find('td:nth-child(7) input').val());
            if (is_added){
                if (isNaN(roll_no) || typeof(roll_no) === "undefined" ){  
                    proceed=false;
                    console.log("Here");
                }
                var item = {
                    student_id : student_id,
                    roll_no: roll_no
                };
                items.push(item);
            }
        });
        // console.log(proceed);
        if (proceed){
        //Send ajax function to back-end 
            (function() {
                $.ajax({
                    url : "", 
                    type: "POST",
                    data:{ class_selected:classselected,
                        year:year,
                        details: JSON.stringify(items),
                        calltype: 'save',
                        csrfmiddlewaretoken: csrf_token},
                        dataType: 'json',               
                        // handle a successful response
                    success : function(jsondata) {
                        // console.log(jsondata);
                        swal("Hooray..", "Data recorder successfully.", "success");
                        setTimeout(function(){location.reload(true);},750);
                    },
                    // handle a non-successful response
                    error : function() {
                        swal("Oops..", "There were some errors.", "error");                            
                    }
                });
            }());
        }
        else{
            swal("Oops..", "All added students must have a roll no.", "error");
        }
    }        
    else{
        swal("Oops..", "Please select class and academic year before clicking submit", "error");
    }
    
}

});