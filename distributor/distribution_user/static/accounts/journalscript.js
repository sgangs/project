$(function(){

//he two functions are used to get and store journal_type & journal_group
var journal_type='';
$( "#journal-type" ).change(function() {
//  alert( "Handler for .change() called." );
    journal_type = $("#journal-type").val();
}());

var journal_group='';
$( "#journal-group" ).change(function() {
//  alert( "Handler for .change() called." );
    journal_group = $("#journal-group").val();
}());

//The following function(s) - on click and on blur pair 
//gets data from the server regarding the accounts key entered.
$("#journal_table").on("focus", ".accountskey", function(){
    $(this).data("initialText", $(this).html());
});
$("#journal_table").on("blur", ".accountskey", function(){
    var input = $(this).html();
    if ($(this).data("initialText") !== $(this).html()) {
        var el = this;
        (function() {
			$.ajax({
        		url : "", 
        		type : "POST", 
        		data : { account_code: input,
        				 calltype: 'account',
        				 csrfmiddlewaretoken: csrf_token}, // data sent with the post request
        		dataType: 'json',
        			// handle a successful response
        		success : function(jsondata) {  
        			$(el).closest('tr').find('td:nth-child(2) span').html(jsondata['name'])
                    $(el).closest('tr').find('td:nth-child(1) span').attr("contenteditable",false);
        			//console.log(jsondata); // log the returned json to the console
                    //alert(jsondata['sellingprice']);
        	    },
        				// handle a non-successful response
        			error : function() {
            			alert("Account does not exist"); // provide a bit more info about the error to the user
        			}
    		});
		}());    	    	
	}
});

//The following function works as the save button is clicked sneding data to backend for saving
$( ".save" ).on("click", function(){	
	var items = [];
    //These four variables are for checking user input and inform in case of error
    var debit=0;
    var credit=0;
	var value_identifier = 1;
    var trn_identifier=1;
    //get all journal entry details 
    $("tr.data").each(function() {
        var code = $(this).find('td:nth-child(1) span').html();
        var trn_type =  $(this).find('td:nth-child(3) span').find(':selected').data('id'); //trn_type is short for transaction type
        var value = $(this).find('td:nth-child(4) span').html();
        if (value<=0){
			value_identifier = 0;
		}
        if (code=="" || trn_type==""){
            trn_identifier=0;
        }
        if (trn_type=="Debit"){
            debit+=parseFloat(value);
        }
        else if (trn_type=="Credit"){
            credit+=parseFloat(value);
        }
		var item = {
			account_code: code,
            value: value,
 			transaction_type: trn_type       
		};
		items.push(item);        
	});
	if (debit==credit && value_identifier != 0 && trn_identifier !=0){
        (function() {
			$.ajax({
        		url : "", 
        		type: "POST",
    			data:{ journal_details: JSON.stringify(items),
    				journal_type: journal_type,
    				journal_group: journal_group,
    				calltype: 'save',
    				csrfmiddlewaretoken: csrf_token},
    			dataType: 'json',    			
    			success : function(jsondata) {  
        			alert("Journal entry successful");
                    location.href = redirect_url;
        		},
                error : function() {
            		alert("Journal entry failed.");
        		}
    		});
		}());
	}
	else{
        if (debit != credit){
            alert ("Your Debit: "+debit+", your Credit: "+credit+". They should be equal")
        }
        if (value_identifier==0){
            alert("Value cannot be zero.")
        }
        if (trn_identifier==0){
            alert("Please check your transaction type and account details entered.")
        }		
	}
});
});