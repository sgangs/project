$(function(){

function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 2500);
}

//The functions is used to get and store journal_type 
var journal_type='';
$( "#journal-type" ).change(function() {
//  alert( "Handler for .change() called." );
    journal_type = $("#journal-type").val();
}());

$('#group_select').selectpicker({
  size: 4
});



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
                        bootbox.alert({
                            size: "small",
                            message: "Account does not exist.",
                            onEscape: true });// provide a bit more info about the error to the user
                        clearmodal();
        			}
    		});
		}());    	    	
	}
});

//The following function works as the save button is clicked sneding data to backend for saving
$('[data-toggle="confirmation"]').confirmation();

$( ".save" ).on("click", function(){	
    var group = $("#journal_group").find(':selected').data('id');
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
    if ($("#group_select")[0].selectedIndex<=0){
        bootbox.alert({
                size: "small",
                message: "Plese select a Journal Group",
                onEscape: true });// provide a bit more info about the error to the user
            clearmodal();
    }
    else{
	   if (debit==credit && value_identifier != 0 && trn_identifier !=0){
            (function() {
                $.ajax({
                    url : "", 
                    type: "POST",
                    data:{ journal_details: JSON.stringify(items),
                    journal_type: journal_type,
                    group: group,
                    calltype: 'save',
                    csrfmiddlewaretoken: csrf_token},
                    dataType: 'json',
                    success : function(jsondata) {
                        bootbox.alert({
                            size: "small",
                            message: "Journal entry successful.",
                            onEscape: true });// provide a bit more info about the error to the user
                        clearmodal();
                        location.href = redirect_url;
        		},
                    error : function() {
                        bootbox.alert({
                            size: "small",
                            message: "Journal entry failed.",
                            onEscape: true });// provide a bit more info about the error to the user
                        clearmodal();
                    }
                });
            }());
        }
	   else{
            if (debit != credit){
                bootbox.alert({
                    size: "small",
                    message: "Your Debit: "+debit+", your Credit: "+credit+". They should be equal",
                    onEscape: true });// provide a bit more info about the error to the user
                clearmodal();
            }
            if (value_identifier==0){
                bootbox.alert({
                    size: "small",
                    message: "Value cannot be zero.",
                    onEscape: true });// provide a bit more info about the error to the user
                clearmodal();
            }
            if (trn_identifier==0){
                bootbox.alert({
                    size: "small",
                    message: "Please check your transaction type and account details entered.",
                    onEscape: true });// provide a bit more info about the error to the user
                clearmodal();
            }
        }
    }
});
});