$(function(){

function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 2500);
}


$('.input-group.date').datepicker({
    format: 'dd/mm/yyyy',
    autoclose: true,
    todayBtn: "linked",
});

//get address of customer from database


$('[data-toggle="confirmation"]').confirmation();

$( ".save" ).on("click", function(){
	
	//get all itemcode & quantity pair 
	var items = [];
	var quantity_identifier = 1;

	$("tr.data").each(function() {
		
		var code = $(this).find('td:nth-child(1) span').html();
        var subcode = $(this).find('td:nth-child(2) span').html();
		var quantity = $(this).find('td:nth-child(5) span').html();
        var discount1 = $(this).find('td:nth-child(6) span').html();
        var discount2 = $(this).find('td:nth-child(7) span').html();
		var free =  $(this).find('td:nth-child(8) span').html();
		if (quantity<=0){
			quantity_identifier = 0;
            bootbox.alert({
                size: "small",
                title: "Invoicing Error",
                message: "Quantity has to be a positive number", 
                onEscape: true });
            clearmodal();
		}

		var item = {
			itemCode : code,
            subitemCode: subcode,
 			itemQuantity : quantity,
 			itemFree: free       
		};
		items.push(item);        
	});



	//Ajax function sending data to backend if customer is not blank, else request user to enter customer details
	if (customer != '' && warehouse !='' && quantity_identifier != 0){

		//get other bill details
		//Step 1: get reference to all balance-id cells
		cells = document.querySelectorAll('table.balance td:last-child span:last-child');

		//Step 2: get total
		total=Number(cells[0].innerHTML.replace(/[^0-9\.]+/g,""));
		//alert(total)

		//Step 3: get grand discount
		grand_discount = cells[1].innerHTML;

		//Step 4: get net total
		net_total = Number(cells[2].innerHTML.replace(/[^0-9\.]+/g,""));
		amount_paid = Number(cells[3].innerHTML.replace(/[^0-9\.]+/g,""));
		
		//Send ajax function to back-end 
		(function() {
			$.ajax({
        		url : "", 
        		type: "POST",
    			data:{ bill_details: JSON.stringify(items),
    				customer: customer,
                    warehouse: warehouse,
                    change_warehouse:change_warehouse,
    				total: total,
    				grand_discount: grand_discount,
    				amount_paid: amount_paid,
    				calltype: 'save',
    				csrfmiddlewaretoken: csrf_token},
    			dataType: 'json',    			
    			// handle a successful response
        		success : function(jsondata) {
                    if (jsondata['name']=="Sufficient stcok not available") {
                        //console.log(jsondata['name'])
                        bootbox.alert({
                            size: "small",
                            title: "Stocking Error",
                            message: "Sufficient stock not available", 
                            onEscape: true });
                        clearmodal();
                    }
                    else{
                        //alert("Sales Invoice generated successfully");
                        location.href = redirect_url;
                        //console.log(jsondata);
                    }        			
        		},

        		// handle a non-successful response
        		error : function() {
                    bootbox.alert({
                            size: "small",
                            message: "Sales Invoice generation failed", 
                            onEscape: true });
                        clearmodal();
            	}
    		});
		}());
	}

	else if (customer != '' && warehouse != ''){
        bootbox.alert({
            size: "small",
            title: "Invoicing Error",
            message: "Please check customer and warehouse details.",
            onEscape: true });
        clearmodal();
            //location.reload(true);
	}
	

});

});