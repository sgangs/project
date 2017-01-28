$(function(){

//This variable will store the student list added via json

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
var paid=0;

//This is called after the class is entered
$( ".class" ).change(function() {
    class_selected=$('.class').find(':selected').data('id');
    $( ".year" ).prop('disabled', false);
    // console.log(class_selected);
});
//This is called if month is changed
$( ".month" ).change(function() {
    month=$('.month').find(':selected').data('id');
    // console.log(month);
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

//This is for the reset button to work
$( ".reset" ).click(function() {
    location.reload(true);
});

$( ".details" ).click(function() {
    if (studentid != "" && month !=""){
        //Send ajax function to back-end 
            (function() {
                $.ajax({
                    url : "", 
                    type: "POST",
                    data:{ studentid: studentid,
                        year: year,
                        month:month,
                        calltype: 'details',
                        csrfmiddlewaretoken: csrf_token},
                    dataType: 'json',               
                                // handle a successful response
                    success : function(jsondata) {
                        fee_total=0;
                        // console.log(jsondata);
                        // $( ".class" ).prop('disabled', true);
                        // $( ".month" ).prop('disabled', true);
                        // $( ".year" ).prop('disabled', true);
                        $(".feetable .data").remove();
                        $.each(jsondata, function(){
                            if (this.data_type=="Monthly"){
                                $('.feetable').append("<tr class='data monthly'>"+
                                    "<td hidden='true'>" + this.id + "</td>"+
                                    "<td>" + this.name + "</td>"+
                                    "<td>" + this.amount + "</td></tr>");
                                fee_total=fee_total+parseFloat(this.amount)
                                
                            }
                            else if (this.data_type=="Yearly"){
                                $('.feetable').append("<tr class='data yearly'>"+
                                    "<td hidden='true'>" + this.id + "</td>"+
                                    "<td>" + this.name + "</td>"+
                                    "<td>" + this.amount + "</td></tr>");
                                fee_total=fee_total+parseFloat(this.amount)
                            }
                            else if (this.data_type=="Paid"){
                                var value = parseFloat(this.amount)
                                fee_total=fee_total-value
                                if (value>0){
                                    $('.alreadypaiddiv').attr(hidden,false);
                                    $('.alreadypaid').val(value)
                                }
                            }
                        });
                        if (fee_total >0){
                            $( ".submit" ).prop('disabled', false);
                        }
                        $('.feetable').append("<tr class='data total'>"+
                            "<td hidden='true'></td>"+
                            "<th>" + "Total Fee" + "</th>"+
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
        swal("Bluhh..", "Select Student and month!", "error");
        student="";
    }
});


$(".nowpay").change(function() {
    paid=$(".nowpay").val();
    console.log(paid);
    if (paid<0){
        swal("Nopsie..", "Negative payment is not possible!", "error");
        $( ".nowpaydiv" ).removeClass('has-warning');
        $( ".nowpaydiv" ).removeClass('has-success');
        $( ".nowpaydiv" ).addClass('has-error');
        $('.submit').attr('disabled',true)
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
        }
        else if (paid<fee_total){
            // paid=fee_total;
            $(".nowpay").val(paid);
            $( ".nowpaydiv" ).addClass('has-error');
            $( ".nowpaydiv" ).removeClass('has-warning');
            $( ".nowpaydiv" ).removeClass('has-success');
            swal("Ehhh..", "Payment less than monthly fee is not accepted!", "error");
            $('.submit').attr('disabled',true)
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
            $('.submit').attr('disabled',false)
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
        confirmButtonText: "Yes, pay fee!",
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

function reconfirm() {
    swal({
        title: "Please Reconfirm!",
        text: "Reconfirm fee payment!",
        type: "warning",
        showCancelButton: true,
      // confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, fee payment reconfirmed!",
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
}


function save_data(){
    if (studentid != "" && paid !=0 && month !="" && year != "" && paid<=fee_total){
            console.log("Successful entry");
            // Send ajax function to back-end 
            (function() {
                $.ajax({
                    url : "", 
                    type: "POST",
                    data:{ studentid: studentid,
                        month:month,
                        year:year,
                        amount:paid,
                        csrfmiddlewaretoken: csrf_token},
                    dataType: 'json',               
                                // handle a successful response
                    success : function(jsondata) {
                        swal("Hooray..", "Fees payment registered successfully!!", "success");
                        // location.href = redirect_url;
                        //console.log(jsondata);
                        },
                    // handle a non-successful response
                    error : function() {
                        swal("Oops..", "There were some errors!!", "error");
                        // bootbox.alert({
                        //     size: "medium",
                        //     message: "Fee Structure entry failed", 
                        //     onEscape: true });
                        // clearmodal();
                    }
                });
            }());
    }
    else{
        swal("Ehhh..", "Check these again: Year, Month, Student and Amount Paid ", "error");
            // bootbox.alert({
            //     size: "small",
            //     message: "Please select class, month and enter yeat details.",
            //     onEscape: true });
            // clearmodal();
    }
            
}

});