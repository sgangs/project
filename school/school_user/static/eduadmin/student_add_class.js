$(function(){

//This variable will store the student list added via json


var batch="";
var classselected="";
var year="";

$( ".batch" ).change(function() {
    batch=$(".batch").find(':selected').data('id');  
});

$( ".class" ).change(function() {
    classselected=$('.class').find(':selected').data('id');
});

//This is for the reset button to work
$( ".reset" ).click(function() {
    // location.reload(true);
    $('.student_add').attr('hidden',true);
    $('.fetch_data').attr('disabled',false);
    $(".student_add .data").remove();
});

$( ".year" ).change(function() {
    year=$(".year").val();    
});

$('.helpdiv').click(function(e){
    swal({
        type: "info",
        title: "How To",
        text: "<p>Select the batch from which the students nedd to be added. Select the class to add the students."+
        " Then enter the acaemic year.</p><p> Finally from the list of students that appears below,"
        +" select students to add to selected class. All selected student must have the roll number for the new class.</p>",
        html: true,
        timer: 15000,
        allowOutsideClick: true,
        showConfirmButton: true
    });
});

$('.fetch').click(function(e) {
    if (batch != '' && classselected != '' && year != '' && batch != undefined && classselected != undefined && year != undefined){
        console.log(batch);
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
                // location.href = redirect_url;
                    console.log(jsondata);
                    if (jsondata.length<1){
                        swal("Umm..", "There's no new admission student in the batch.", "error");    
                    }
                    else{
                        $('.student_add').attr('hidden',false);
                        $('.fetch_data').attr('disabled',true);
                        $.each(jsondata, function(){
                            if (this.data_type=="Student"){
                                $('.student').append("<tr class='data' >"+
                                    "<td hidden='true'>"+this.id+"</td>"+
                                    "<td style='height:20px;'>" + this.key + "</td>"+
                                    "<td style='height:20px;'>" + this.local_id + "</td>"+
                                    "<td style='height:20px;'>" + this.name + "</td>"+
                                    "<td style='height:20px;'><input type='checkbox' checked></td>"+
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
            setTimeout(function(){reconfirm()},600)
            
        }
    })
});

function save_data(){
            
    //get all itemcode & quantity pair
    console.log($('.month').is(":visible")); 
        var items = [];
        var proceed = true;
        var month_entered=true
        fee_name=$(".feename").val();
        if ($('.month').is(":visible")){
            if (month ==''){
                month_entered=false
            }
        }
        if (fee_name != "" && month_entered){
            //console.log("Date: "+date);
            $("tr.data").each(function() {
                var account = $(this).find('td:nth-child(2)').find(':selected').data('id');
                var amount = parseInt($(this).find('td:nth-child(3) input').val());
                if (isNaN(amount) || typeof(account) === "undefined" ){
                    proceed=false;}
                var item = {
                    account : account,
                    amount: amount,
                    };
                items.push(item);        
            });
            console.log(items);
            if (proceed){
        //Send ajax function to back-end 
                (function() {
                    $.ajax({
                        url : "", 
                        type: "POST",
                        data:{ details: JSON.stringify(items),
                            feename: fee_name,
                            month:month,
                            csrfmiddlewaretoken: csrf_token},
                            dataType: 'json',               
                            // handle a successful response
                        success : function(jsondata) {
                            //alert("Fee Structure registered successfully");
                            location.href = redirect_url;
                            //console.log(jsondata);
                        },
                            // handle a non-successful response
                        error : function() {
                            bootbox.alert({
                                size: "medium",
                                message: "Fee Structure entry failed", 
                                onEscape: true });
                            clearmodal();
                        }
                    });
                }());
            }
            else{
                bootbox.alert({
                    size: "small",
                    message: "Please select Account and enter values in all rows.",
                    onEscape: true });
                clearmodal();

            }
        }
        else if (month_entered==false){
            bootbox.alert({
                size: "small",
                message: "Please enter the name of fee structure or the month.",
                onEscape: true });
            clearmodal();
        }
        else{
            bootbox.alert({
                size: "small",
                message: "Please enter the name of fee structure.",
                onEscape: true });
            clearmodal();
        }
    
}

});