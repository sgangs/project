$(function(){

//This variable will store the student list added via json

//This will help to remove the error modal.
function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 3000);
}

var fee_name="";
var month="";


$(".delete").on('click', function() {
    $('.case:checkbox:checked').parents("tr").remove();
    $('.check_all').prop("checked", false); 
});



$(".addmore").on('click',function(){
    count=$('table tr').length;
    var data="<tr class='data'>"+
    "<td><input type='checkbox' class='case'/></td>"+
    "<td style='text-align: center'><select class='form-control select account'>"+
      "<option disabled selected hidden style='display: none' value>Select Account Name</option>"+
    "</select></td>"+
    "<td style='text-align: center'><input type='text' class='name'/></td>"+
    "<td style='text-align: center'><input type='number' class='amount'/></td>"+"</tr>";
    $('table').append(data);
    
    $.each(accounts, function(){
        $('table').find('tr:eq('+count+')').find('.account').append($('<option>',{
        //$('.account').append($('<option>',{
            'data-id': this.id,
            'text': this.name
        }));
    });
});

//This is called after the fee structure name is entered
$( ".feename" ).change(function() {
    fee_name=$(".feename").val();
    $( ".submit" ).prop('disabled',false); 
});

//This is called if month is changed
$( ".month" ).change(function() {
    month=$('.month').find(':selected').data('id');
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
                var name = parseInt($(this).find('td:nth-child(3) input').val());
                var amount = parseInt($(this).find('td:nth-child(4) input').val());
                if (isNaN(amount) || typeof(account) == "undefined" || account == "" || name == "" ){
                    proceed=false;}
                var item = {
                    account : account,
                    amount: amount,
                    name: name,
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