$(function(){


//get address of customer from database

var customer='';
$( "#customer-code" ).change(function() {

//	alert( "Handler for .change() called." );
	customer = $("#customer-code").val();
	(function() {
		$.ajax({
        	url : "", 
        	type : "POST", 
        	data : { customer_code: customer,
        			 calltype: 'customer',
        			 csrfmiddlewaretoken: csrf_token}, // data sent with the post request
        	dataType: 'json',

        			// handle a successful response
        	success : function(jsondata) {
        		$("#customer-code").val(jsondata['name']);
                $("#customer-code").attr("disabled","True");
        		//console.log(jsondata); // log the returned json to the console
        	    //console.log("success"); // another sanity check
        	},

        			 //handle a non-successful response
        	error : function() {
            		alert("Customer does not exist"); // provide a bit more info about the error to the user
        	}
    	});
	}());

});

var warehouse='';
var change_warehouse=false
$( "#warehouse-code" ).change(function() {
    warehouse = $("#warehouse-code").val();
    change_warehouse=true
    (function() {
        $.ajax({
            url : "", 
            type : "POST", 
            data : { warehouse_code: warehouse,
                     calltype: 'warehouse',
                     csrfmiddlewaretoken: csrf_token}, // data sent with the post request
            dataType: 'json',

                    // handle a successful response
            success : function(jsondata) {
                $("#warehouse-code").val(jsondata['name']);
                $("#warehouse-code").attr("disabled","True");
                console.log(jsondata); // log the returned json to the console
                console.log("success"); // another sanity check
            },

                     //handle a non-successful response
            error : function() {
                    alert("Warehouse does not exist"); // provide a bit more info about the error to the user
            }
        });
    }());

});

//The following function(s) - on click and on blur pair gets data from the server regarding the item code entered.

$("#inventory_table").on("focus", ".itemcode", function(){
    $(this).data("initialText", $(this).html());
    /*alert( "On focus for table inventory called." );*/  

});


$("#inventory_table").on("blur", ".itemcode", function(){
    /*alert( "On blur for table inventory called." );*/
	var input = $(this).html();		
    if ($(this).data("initialText") !== $(this).html()) {
    	var el = this;    	
    	(function() {
			$.ajax({
        		url : "", 
        		type : "POST", 
        		data : { item_code: input,
        				 calltype: 'item',
        				 csrfmiddlewaretoken: csrf_token}, // data sent with the post request
        		dataType: 'json',
        			// handle a successful response
        		success : function(jsondata) {  
        			$(el).closest('tr').find('td:nth-child(3) span').html(jsondata['name'])
                    $(el).closest('tr').find('td:nth-child(1) span').attr("contenteditable",false);
        			//$(el).closest('tr').find('td:nth-child(4) span').html(jsondata['purchaseprice'])
        			$(el).closest('tr').find('td:nth-child(9) span').html(jsondata['vat_type'])
        			$(el).closest('tr').find('td:nth-child(10) span').html(jsondata['vat_percent'])
        	    	//console.log(jsondata); // log the returned json to the console
        	    	//alert(jsondata['sellingprice']);
        	    },

        				// handle a non-successful response
        			error : function() {
            			alert("Item does not exist"); // provide a bit more info about the error to the user
        			}
    		});
		}());    	    	
	}
});


/*This is used to get the subproduct*/

$("#inventory_table").on("focus", ".subitemcode", function(){
    $(this).data("initialsubID", $(this).closest('tr').find('td:nth-child(1) span').html());
    /*alert( "On focus for table inventory called." );*/  

});


$("#inventory_table").on("blur", ".subitemcode", function(){
    /*alert( "On blur for table inventory called." );*/
    var input = $(this).html();  
    var el = this;   
    item=$(el).closest('tr').find('td:nth-child(1) span').html();
    //var item= ".itemcode".html();
    if ($(this).data("initialsubID") !== $(this).html() && item !='') {
              
        (function() {
            $.ajax({
                url : "", 
                type : "POST", 
                data : { subitem_code: input,
                         item_code:item,   
                         calltype: 'subitem',
                         csrfmiddlewaretoken: csrf_token}, // data sent with the post request
                dataType: 'json',
                    // handle a successful response
                success : function(jsondata) {  
                    $(el).closest('tr').find('td:nth-child(4) span').html(jsondata['salesprice'])
                    $(el).closest('tr').find('td:nth-child(6) span').html(jsondata['discount1'])
                    $(el).closest('tr').find('td:nth-child(7) span').html(jsondata['discount2'])
                    //console.log(jsondata);
                    //console.log("Salesprice: "+jsondata['salesprice']); // log the returned json to the console
                },

                        // handle a non-successful response
                    error : function() {
                        alert("Item does not exist"); // provide a bit more info about the error to the user
                    }
            });
        }());               
    }
});

//The following function works as the save button is clicked - 
//sending the item code and quantity pair along with other bill details to back-end
//NOTE: DISCOUNT AND VAT IS NOT TAKEN CARE OF

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
			alert("Quantity has to be a positive number");
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
                        alert("Sufficient stock not available");
                    }
                    else{
                        alert("Sales Invoice generated successfully");
                        location.href = redirect_url;
                        //console.log(jsondata);
                    }        			
        		},

        		// handle a non-successful response
        		error : function() {
            		alert("Sales Invoice generation failed"); // provide a bit more info about the error to the user
        		}
    		});
		}());
	}

	else{
		alert ("Please check customer and warehouse details & whether all quantities are positive or not")
		location.reload(true);
	}
	

});

});