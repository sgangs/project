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


//This is called after the class is entered
$( ".class" ).change(function() {
    class_selected=$('.class').find(':selected').data('id');
    console.log(class_selected);
});
//This is called if month is changed
$( ".month" ).change(function() {
    month=$('.month').find(':selected').data('id');
    console.log(month);
});
//This is called if year is changed
$( ".year" ).change(function() {
    year=parseInt($('.year').val());
    console.log(year);
});

//This is for the reset button to work
$( ".reset" ).click(function() {
    location.reload(true);
});

$( ".details" ).click(function() {
    if (class_selected != "" && month !="" && year !=""){
        console.log("Proceed called");        
            //Send ajax function to back-end 
            (function() {
                $.ajax({
                    url : "", 
                    type: "POST",
                    data:{ class_selected: class_selected,
                        year: year,
                        month:month,
                        calltype: 'details',
                        csrfmiddlewaretoken: csrf_token},
                    dataType: 'json',               
                                // handle a successful response
                    success : function(jsondata) {
                        console.log(jsondata);
                        $( ".class" ).prop('disabled', true);
                        $( ".month" ).prop('disabled', true);
                        $( ".year" ).prop('disabled', true);
                        $( ".details" ).prop('disabled', true);
                        $.each(jsondata, function(){
                            if (this.data_type=="Student"){
                                $('#student').append($('<option>',{
                                    'text': this.first_name+" "+this.last_name+" "+this.key+" "+this.local_id
                                }));
                                $('#student').selectpicker('refresh')
                            }
                            else if (this.data_type=="Monthly"){
                                $('.feetable').append("<tr>"+
                                    "<td hidden='true'>" + this.id + "</td>"+
                                    "<td>" + this.name + "</td>"+
                                    "<td>" + this.amount + "</td>"+
                                    "<td><input type='number' step='1' class='form-control year' disabled='true'></td></tr>");
                                fee_total=fee_total+parseFloat(this.amount)
                                
                            }
                            else if (this.data_type=="Yearly"){
                                $('.feetable').append("<tr>"+
                                    "<td hidden='true'>" + this.id + "</td>"+
                                    "<td>" + this.name + "</td>"+
                                    "<td>" + this.amount + "</td>"+
                                    "<td><input type='number' step='1' class='form-control year' disabled='true'></td></tr>");
                                fee_total=fee_total+parseFloat(this.amount)
                            }
                        });
                        $('.feetable').append("<tr>"+
                            "<td hidden='true'></td>"+
                            "<th>" + "Total Fee" + "</th>"+
                            "<th>" + parseFloat(fee_total).toFixed(2) + "</th>"
                            +"<td><input type='number' step='1' class='form-control year' disabled='true'></td></tr>");
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
            message: "Please select class, month and enter yeat details.",
            onEscape: true });
        clearmodal();
    }
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
            
        if (class_selected != "" && month !="" && year !=""){
            console.log("Proceed called");
            //Send ajax function to back-end 
            // (function() {
            //     $.ajax({
            //         url : "", 
            //         type: "POST",
            //         data:{ details: JSON.stringify(items),
            //             feename: fee_name,
            //             month:month,
            //             csrfmiddlewaretoken: csrf_token},
            //         dataType: 'json',               
            //                     // handle a successful response
            //         success : function(jsondata) {
            //             //alert("Fee Structure registered successfully");
            //             location.href = redirect_url;
            //             //console.log(jsondata);
            //             },
            //         // handle a non-successful response
            //         error : function() {
            //             bootbox.alert({
            //                 size: "medium",
            //                 message: "Fee Structure entry failed", 
            //                 onEscape: true });
            //             clearmodal();
            //         }
            //     });
            // }());
        }
        else{
            bootbox.alert({
                size: "small",
                message: "Please select class, month and enter yeat details.",
                onEscape: true });
            clearmodal();
        }
        
    
    }, //bracket for confirm closing
});




});