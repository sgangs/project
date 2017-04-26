$(function(){

//This will help to remove the error modal.
function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 3000);
}

var class_selected="";
var year="";
var month="";
var fee_total=0.00;
var studentid="";
var studentdetails="";
var paid=0;
var month_list=[];

//This is called after the class is entered
$( ".class" ).change(function() {
    class_selected=$('.class').find(':selected').data('id');
    // fee_total=0;
    $(".nowpay").val(0);
    $( ".year" ).prop('disabled', false);
    $( ".nowpaydiv" ).removeClass('has-warning');
    $( ".nowpaydiv" ).removeClass('has-success');
    $( ".nowpaydiv" ).removeClass('has-error');
    // console.log(class_selected);
});
//This is called if month is changed
$( ".month" ).change(function() {
    month=$('.month').find(':selected').data('id');
    // fee_total=0;
    $(".nowpay").val(0);
    $( ".nowpaydiv" ).removeClass('has-warning');
    $( ".nowpaydiv" ).removeClass('has-success');
    $( ".nowpaydiv" ).removeClass('has-error');
});
//This is called if year is changed
$( ".year" ).change(function() {
    year=parseInt($('.year').val());
    // fee_total=0;
    $(".nowpay").val(0);
    $( ".nowpaydiv" ).removeClass('has-warning');
    $( ".nowpaydiv" ).removeClass('has-success');
    $( ".nowpaydiv" ).removeClass('has-error');
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
    studentdetails=$("#student").find(':selected').text();
    // fee_total=0;
    $(".nowpay").val(0);
    $( ".nowpaydiv" ).removeClass('has-warning');
    $( ".nowpaydiv" ).removeClass('has-success');
    $( ".nowpaydiv" ).removeClass('has-error');
});

//This is for the reset button to work


$( ".details" ).click(function() {
    $( ".nowpaydiv" ).removeClass('has-warning');
    $( ".nowpaydiv" ).removeClass('has-success');
    $( ".nowpaydiv" ).removeClass('has-error');
    if (studentid != "" ){
        //Send ajax function to back-end 
            (function() {
                $.ajax({
                    url : "", 
                    type: "POST",
                    data:{ studentid: studentid,
                        class_selected: class_selected,
                        year: year,
                        // month:month,
                        calltype: 'details',
                        csrfmiddlewaretoken: csrf_token},
                    dataType: 'json',               
                                // handle a successful response
                    success : function(jsondata) {
                        $( ".fee-pay" ).prop('hidden', false);
                        fee_total=0;
                        var value=0;
                        month_list=[];
                        $(".feetable .data").remove();
                        var month_now=''
                        $.each(jsondata, function(){
                            if (this.data_type == "Month"){
                                month_now=this.month
                                var month_add={month:this.month,
                                                is_late:"No"}
                                $('.feetable').append("<tr class='data month'>"+
                                    "<td hidden='true'></td>"+
                                    "<td colspan='2'><p><b>Fee for the month of: "+this.month+"</p><b></td></tr>");
                                $.each(jsondata, function(){                            
                                    if (this.data_type=="Generic"){
                                        if (this.month_full==month_now){
                                            $('.feetable').append("<tr class='data generic'>"+
                                                "<td hidden='true'>" + this.id + "</td>"+
                                                "<td>" + this.name + "</td>"+
                                                "<td>" + this.amount + "</td></tr>");
                                            fee_total=fee_total+parseFloat(this.amount)
                                        }
                                    }
                                    if (this.data_type=="Late Fee"){
                                        if (this.month_full==month_now){
                                            $('.feetable').append("<tr class='data generic'>"+
                                                "<td hidden='true'>" + this.id + "</td>"+
                                                "<td>" + this.name + "</td>"+
                                                "<td>" + this.amount + "</td></tr>");
                                            fee_total=fee_total+parseFloat(this.amount)
                                            month_add={month:this.month,
                                                        is_late:"Yes",
                                                        slab:this.id}                                            
                                        }
                                    }                                    
                                });
                                month_list.push(month_add)
                            }                            
                        });
                        if (fee_total >0){
                            $( ".submit" ).prop('disabled', false);
                            $( ".download" ).prop('disabled', false);
                        }
                        $('.feetable').append("<tr class='data total'>"+
                            "<td hidden='true'></td>"+
                            "<th>" + "Total Fee Payable" + "</th>"+
                            "<th>" + parseFloat(fee_total).toFixed(2) + "</th></tr>");                        
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
        swal("Bluhh..", "Select Student!!", "error");
        student="";
    }
});


$(".nowpay").change(function() {
    paid=$(".nowpay").val();
    if (paid<0 || paid == 0){
        swal("Nopsie..", "Negative or Zero payment is not possible!", "error");
        $( ".nowpaydiv" ).removeClass('has-warning');
        $( ".nowpaydiv" ).removeClass('has-success');
        $( ".nowpaydiv" ).addClass('has-error');
        $('.submit').attr('disabled',true)
        $('.download').attr('disabled',true)
    }
    else{
        if (paid>fee_total){
            // paid=fee_total;
            $(".nowpay").val(paid);
            $( ".nowpaydiv" ).addClass('has-error');
            $( ".nowpaydiv" ).removeClass('has-warning');
            $( ".nowpaydiv" ).removeClass('has-success');
            swal("Bluhh..", "Payment more than monthly fee is not accepted!", "error");
            $('.submit').attr('disabled',true)
            $('.download').attr('disabled',true)
        }
        else if (paid<fee_total){
            // paid=fee_total;
            $(".nowpay").val(paid);
            $( ".nowpaydiv" ).addClass('has-error');
            $( ".nowpaydiv" ).removeClass('has-warning');
            $( ".nowpaydiv" ).removeClass('has-success');
            swal("Ehhh..", "Payment less than monthly fee is not accepted!", "error");
            $('.submit').attr('disabled',true)
            $('.download').attr('disabled',true)
        }
        // else if (paid<fee_total && paid>=20){
        //     $( ".nowpaydiv" ).removeClass('has-error');
        //     $( ".nowpaydiv" ).removeClass('has-success');
        //     $( ".nowpaydiv" ).addClass('has-warning');
        //     $('.submit').attr('disabled',false)
        //     swal("?", "Payment is less than monthly fee. But it is acceptable.", "warning");
        // }
        // else if (paid<20){
        //     $( ".nowpaydiv" ).removeClass('has-error');
        //     $( ".nowpaydiv" ).removeClass('has-success');
        //     $( ".nowpaydiv" ).addClass('has-warning');
        //     $('.submit').attr('disabled',false)
        //     swal("Seriously?", "Isn't it too low!", "warning");
        // }
        else{
            $( ".nowpaydiv" ).removeClass('has-error');
            $( ".nowpaydiv" ).removeClass('has-warning');
            $( ".nowpaydiv" ).addClass('has-success');
            $('.submit').attr('disabled',false);
            $('.download').attr('disabled',false);
        }
    }
});



$('.submit').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "You cannot undo student fee payment!",
        type: "info",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, "+studentdetails+" payment confirmed",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){reconfirm()},600)
            
        }
    })
});

$('.download').click(function(e) {
    swal({
        title: "Are you sure?",
        text: "You cannot undo student fee payment!",
        type: "info",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes,  "+studentdetails+" payment confirmed",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){reconfirm_print()},600)
            
        }
    })
});
// $('.download').click(function(e) {
//     reconfirm_print("print");
// });

function reconfirm() {
    swal({
        title: "Please Reconfirm!",
        text: "Reconfirm fee payment! Payment by "+studentdetails,
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, fee payment reconfirmed!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){save_data("saving")},600)            
        }
        else{
            
        }
    })
}

function reconfirm_print() {
    swal({
        title: "Please Reconfirm!",
        text: "Reconfirm fee payment! Payment by "+studentdetails,
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, fee payment reconfirmed!",
        closeOnConfirm: true,
        closeOnCancel: true,
        html: false
    }, function(isConfirm){
        if (isConfirm){
            setTimeout(function(){save_data("print")},600)            
        }
        else{
            
        }
    })
}


function save_data(called_for){
    if (studentid != "" && paid ==fee_total && year != "" ){
        if (called_for == "saving")
            {
            // Send ajax function to back-end 
            (function() {
                $.ajax({
                    url : "", 
                    type: "POST",
                    data:{ studentid: studentid,
                        class_selected: class_selected,
                        month:month,
                        year:year,
                        amount:paid,
                        month_list: JSON.stringify(month_list),
                        calltype: 'save',
                        csrfmiddlewaretoken: csrf_token},
                    dataType: 'json',               
                                // handle a successful response
                    success : function(jsondata) {
                        swal("Hooray..", "Fees payment registered successfully!!", "success");
                        setTimeout(location.reload(true),600);
                        // console.log(jsondata);
                        },
                    // handle a non-successful response
                    error : function() {
                        swal("Oops..", "There were some errors!!", "error");
                    }
                });
            }());
        }
        else if (called_for == "print"){
            (function() {
                $.ajax({
                    url : "", 
                    type: "POST",
                    data:{ studentid: studentid,
                        class_selected: class_selected,
                        month:month,
                        year:year,
                        amount:paid,
                        month_list: JSON.stringify(month_list),
                        calltype: 'pdf',
                        csrfmiddlewaretoken: csrf_token},
                    dataType: 'html',               
                                // handle a successful response
                    success : function(jsondata) {
                        swal("Hooray..", "Fees payment registered successfully!!", "success");
                        var blob=new Blob([jsondata]);
                        var link=document.createElement('a');
                        link.href=window.URL.createObjectURL(blob);
                        link.download="Fees_Payment"+".pdf";
                        link.click();

                        setTimeout(location.reload(true),600)
                        },
                    // handle a non-successful response
                    error : function() {
                        swal("Oops..", "There were some errors!!", "error");
                    }
                });
            }());

        }
    }
    else{
        swal("Ehhh..", "Check these again: Year, Student and Amount Paid ", "error");
    }
            
}

});