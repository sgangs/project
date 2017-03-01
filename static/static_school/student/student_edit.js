$(function(){

//This variable will store the student list added via json

//This will help to remove the error modal.

var batchid=0;
var studentid=0;

$( ".batch" ).change(function() {
    batchid=$('.batch').find(':selected').data('id');
    console.log(batchid);
    (function() {
        $.ajax({
            url : "", 
            type: "POST",
            data:{ batchid:batchid,
                call_type:"sending_batch",
                csrfmiddlewaretoken: csrf_token},
            dataType: 'json',               
            // handle a successful response
            success : function(jsondata) {
                $.each(jsondata, function(){
                    $('#student').append($('<option>',{
                        'data-id': this.id,
                        'text': this.first_name+" "+this.last_name+" "+this.key+" "+this.local_id
                    }));
                });
                $('#student').selectpicker('refresh')
                console.log(jsondata);
            // 
            // location.reload(true);            
            },
            // handle a non-successful response
            error : function() {
                console.log("Error")
            }
        });
    }());
});


$( ".student" ).change(function() {
    studentid=$('.student').find(':selected').data('id');
    (function() {
        $.ajax({
            url : "", 
            type: "POST",
            data:{ studentid: studentid,
                call_type:'sending_student',
                csrfmiddlewaretoken: csrf_token},
            dataType: 'json',               
            // handle a successful response
            success : function(jsondata) {
                // location.href = redirect_url;
                console.log(jsondata[0]['dob']);
                $('.dob').val(jsondata[0]['dob']);
                $('.gender').val(jsondata[0]['gender']);
                $('.gender').selectpicker('refresh');
                $('.blood').val(jsondata[0]['blood']);
                $('.blood').selectpicker('refresh');
                $('.phone').val(jsondata[0]['contact']);
                $('.email').val(jsondata[0]['email']);
                $('.dob').val(jsondata[0]['dob']);
                $('.local_id').val(jsondata[0]['local_id']);
                $('.address1').val(jsondata[0]['address1']);
                $('.address2').val(jsondata[0]['address2']);
                $('.state').val(jsondata[0]['state']);
                $('.pincode').val(jsondata[0]['pincode']);
                // location.reload(true);            
            },
            // handle a non-successful response
            error : function() {
                console.log("Error")
            }
        });
    }());
});

//This is for the reset button to work
$( ".reset" ).click(function() {
    location.reload(true);
});


$( ".submit" ).confirm({
    title: 'Confirm!',
    icon: 'fa fa-spinner fa-spin',
    theme: 'black',
    backgroundDismiss: true,
    content: 'Are you sure to record the fee structure?',
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
    
    }, //bracket for confirm closing
});




});