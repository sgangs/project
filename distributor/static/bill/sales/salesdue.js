$(function(){

//This is used to edit the amount due in invoice
$( ".save" ).on("click", function(){
	
	var proceed = 1;


	//Ajax function sending data to backend if amount paid <= amount due
	cells = document.querySelectorAll('table.balance td:last-child span:last-child');

	amount_paid = Number(cells[5].innerHTML.replace(/[^0-9\.]+/g,""));
  //net_total = Number(cells[2].innerHTML.replace(/[^0-9\.]+/g,""));
  proceed= balance-amount_paid

  var payment_mode =  $("#payment_mode").find(':selected').data('id');
  alert (payment_mode)
  
      		
	//Send ajax function to back-end
    if (proceed >=0){
      (function() {
		    $.ajax({
          url : "", 
       	  type: "POST",
          data:{ amount_paid: amount_paid,
          calltype: 'save',
          payment_mode: payment_mode,
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
            alert("Sales Invoice updation failed"); // provide a bit more info about the error to the user
          }
    	  });
	    }());
    }

    else{
        alert("Amount received cannot be more than invoice amount");
    }

});

});