$(function(){
//This is used to edit the amount due in invoice
function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 2500);
}

  //This is when system loads
  payment_mode =  $("#payment_mode").find(':selected').data('id');
  if (payment_mode == "Cash"){
    $(".Cheque_RTGS").hide();
  }


  //This is for change of payment mode by user
  $("#payment_mode").on("change", function(){
      payment_mode =  $("#payment_mode").find(':selected').data('id');
      if (payment_mode != "Cash"){
        $(".Cheque_RTGS").show();
      }
      else{
        $(".Cheque_RTGS").hide();
      }
  });


$( ".save" ).confirm({
  title: 'Confirm!',
  icon: 'fa fa-spinner fa-spin',
  theme: 'black',
  backgroundDismiss: true,
  content: 'Are you sure to update?',
  confirmButton: 'Yes!',
  cancelButton: 'No!',
  autoClose: 'cancel|6000',
  confirmButtonClass: 'btn-success',
  cancelButtonClass: 'btn-danger',
  animation: 'rotateY',
  closeAnimation: 'rotateXR',
  animationSpeed: 750,
  confirm: function(){	
  	var proceed = -1;
  	//Ajax function sending data to backend if amount paid <= amount due
  	cells = document.querySelectorAll('table.balance td:last-child span:last-child');
  	amount_paid = Number(cells[5].innerHTML.replace(/[^0-9\.]+/g,""));
    number = cells[7].innerHTML;
    //net_total = Number(cells[2].innerHTML.replace(/[^0-9\.]+/g,""));
    proceed= balance-amount_paid
    var payment_mode =  $("#payment_mode").find(':selected').data('id');

    if (amount_paid > 0){
      proceed= balance-amount_paid;
      var payment_mode =  $("#payment_mode").find(':selected').data('id');
    } 

    else{
      proceed = -1;
      bootbox.alert({
        size: "small",
        title: "Minimum Amount Error",
        message: "Amount cannot be zero or negative.",
        onEscape: true });
    }
    //Send ajax function to back-end
      if (proceed >= 0){
        (function() {
  		    $.ajax({
            url : "", 
         	  type: "POST",
            data:{ amount_paid: amount_paid,
            payment_mode: payment_mode,
            number: number,
            calltype: 'save',
      		  csrfmiddlewaretoken: csrf_token},
            dataType: 'json',    			
            // handle a successful response
            success : function(jsondata) {
              //alert("Sales Invoice updated successfully");
              //console.log(jsondata)
              location.href = redirect_url;
              
            },
            // handle a non-successful response
            error : function() {
              bootbox.alert({
                size: "small",
                message: "Sales Invoice updation failed.",
                onEscape: true });
              clearmodal();
            }
      	  });
  	    }());
      }

      else if (proceed < 0){
          bootbox.alert({
            size: "small",
            title: "Maximum Amount Error",
            message: "Amount received cannot be more than invoice amount.",
            onEscape: true });
          clearmodal();
      }

  }
});

});