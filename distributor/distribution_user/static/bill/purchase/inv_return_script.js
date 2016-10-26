$(function(){
$('html').bind('keypress', function(e){
    if(e.keycode == 13){
        return false;
    }
})


//This will help parse quantity to proper float value.
function parseFloatHTML(item) {
    return parseFloat(item.replace(/[^\d\.\-]+/g, ''));
}

//Add tooltip to this webpage
$('.table-extra').tooltip({animation: true, container: 'body'});

//This is used to auto-clear the alert modal after 2.5 secs
function clearmodal(){
    window.setTimeout(function(){
        bootbox.hideAll();
    }, 2500);
}

//This is used to check of note will be taxed or not
checked=true;
$('.tax').change(function(){
    if($(this).prop('checked'))
    {
        checked=true;
    }else{
        checked=false;
    }
});

//save invoice id
var invoice_id=""
$( "#invoice-id" ).change(function() {
    invoice_id=$(this).val();
});

//get address of vendor from database
var vendor='';
$( "#vendor-code" ).change(function() {
    vendor = $("#vendor-code").val();
    (function() {
        $.ajax({
            url : "", 
            type : "POST", 
            data : { vendor_code: vendor,
                	calltype: 'vendor',
                	csrfmiddlewaretoken: csrf_token}, // data sent with the post request
            dataType: 'json',
                	// handle a successful response
            success : function(jsondata) {
                $("#vendor-code").val(jsondata['name']);
                $("#vendor-code").attr("disabled","True");
                	//console.log("success"); // another sanity check
            },
                //handle a non-successful response
            error : function() {
                bootbox.alert({
                    message: "Vendor does not exist",
                    onEscape: true }); // provide a bit more info about the error to the user
                    clearmodal();
            }
        });
    }());
});

//get warehouse details from backend
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
                    //console.log("success"); // another sanity check
            },
            //handle a non-successful response
            error : function() {
                bootbox.alert({
                    message: "Warehouse does not exist. Please enter proper <b>warehouse code/key<b>.",
                    onEscape: true }); // provide a bit more info about the error to the user
                    clearmodal();
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
                    $(el).closest('tr').find('td:nth-child(1) span').attr("contenteditable",false);
                	$(el).closest('tr').find('td:nth-child(3) span').html(jsondata['name'])
                	//$(el).closest('tr').find('td:nth-child(4) span').html(jsondata['purchaseprice'])
                	$(el).closest('tr').find('td:nth-child(7) span').html(jsondata['vat_type'])
                	$(el).closest('tr').find('td:nth-child(8) span').html(jsondata['vat_percent'])
                },
                // handle a non-successful response
                error : function() {
                    bootbox.alert({
                    message: "Item does not exist", 
                        onEscape: true }); // provide a bit more info about the error to the user
                        clearmodal();
                	}
            });
        }());    	    	
    }
});

//This will get the subproduct details
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
    if (item!=''){
        if ($(this).data("initialsubID") !== $(this).html() && item !='') {              
            (function() {
                $.ajax({
                    url : "", 
                    type : "POST", 
                    data : { subitemcode: input,
                            item_code:item,   
                            calltype: 'subitem',
                            csrfmiddlewaretoken: csrf_token}, // data sent with the post request
                    dataType: 'json',
                    // handle a successful response
                    success : function(jsondata) {  
                        $(el).closest('tr').find('td:nth-child(2) span').attr("contenteditable",false);
                        $(el).closest('tr').find('td:nth-child(4) span').html(jsondata['unit']);
                        $(el).closest('tr').find('td:nth-child(4) span').attr("contenteditable",true);
                        $(el).closest('tr').find('td:nth-child(5) span').html(jsondata['purchaseprice']);
                        //$(el).closest('tr').find('td:nth-child(6) span').html(jsondata['discount1'])
                        //$(el).closest('tr').find('td:nth-child(7) span').html(jsondata['discount2'])
                    },
                        // handle a non-successful response
                    error : function() {
                        bootbox.alert({
                            message: "Sub-item does not exist", 
                            onEscape: true }); // provide a bit more info about the error to the user
                            clearmodal();
                        }
                });
            }());               
        }
    }
    else{
        bootbox.alert({
            size: "small",
            message: "Please enter parent-code first", 
            onEscape: true }); // provide a bit more info about the error to the user
        clearmodal();
    }
});

//This is used to get unit details
$("#inventory_table").on("focus", ".unit", function(){
    $(this).data("initialunit", $(this).closest('tr').find('td:nth-child(4) span').html());
    /*alert( "On focus for table inventory called." );*/  
});
$("#inventory_table").on("blur", ".unit", function(){
    /*alert( "On blur for table inventory called." );*/
    var input = $(this).html();  
    var el = this;   
    revised_unit=$(this).html()
    item=$(el).closest('tr').find('td:nth-child(1) span').html();
    subitem=$(el).closest('tr').find('td:nth-child(2) span').html();
    if ($(this).data("initialunit") !== $(this).html() && subitem !='') {        
        rate=$(el).closest('tr').find('td:nth-child(5) span').html();
        (function() {
            $.ajax({
                url : "", 
                type : "POST", 
                data : { unit:revised_unit,
                        item_code:item,
                        subitem_code:subitem,
                        calltype: 'unit',
                        csrfmiddlewaretoken: csrf_token}, // data sent with the post request
                dataType: 'json',
                // handle a successful response
                success : function(jsondata) {  
                    $(el).closest('tr').find('td:nth-child(4) span').attr("contenteditable",false);
                    //$(el).closest('tr').find('td:nth-child(4) span').html(jsondata['unit'])
                    old_multiplier=parseFloat(jsondata['old_multiplier']);
                    new_multiplier=parseFloat(jsondata['new_multiplier']);
                    new_rate=rate/old_multiplier*new_multiplier;
                    $(el).closest('tr').find('td:nth-child(5) span').html(new_rate)
                },
                // handle a non-successful response
                error : function() {
                    bootbox.alert({
                        message: "Unit does not exist", 
                        onEscape: true }); // provide a bit more info about the error to the user
                        clearmodal();
                }
            }); 
        }());               
    }
});

//The following function works as the save button is clicked - 
//sending the item code and quantity pair along with other bill details to back-end
//NOTE: DISCOUNT AND VAT IS NOT TAKEN CARE OF

//If debit note is of debit type
$( ".debit" ).confirm({
    title: 'Confirm!',
    icon: 'fa fa-spinner fa-spin',
    theme: 'black',
    backgroundDismiss: true,
    content: 'Are you sure to generate invoice?',
    confirmButton: 'Yes!',
    cancelButton: 'No!',
    autoClose: 'cancel|6000',
    confirmButtonClass: 'btn-success',
    cancelButtonClass: 'btn-danger',
    animation: 'rotateY',
    closeAnimation: 'rotateXR',
    animationSpeed: 750,
    confirm: function(){
    save_note("debit")}
});

//If debit note is of cash refund type
$( ".refund" ).confirm({
    title: 'Confirm!',
    icon: 'fa fa-spinner fa-spin',
    theme: 'black',
    backgroundDismiss: true,
    content: 'Are you sure to generate invoice?',
    confirmButton: 'Yes!',
    cancelButton: 'No!',
    autoClose: 'cancel|6000',
    confirmButtonClass: 'btn-success',
    cancelButtonClass: 'btn-danger',
    animation: 'rotateY',
    closeAnimation: 'rotateXR',
    animationSpeed: 750,
    confirm: function(){
    save_note("refund")}
});


function save_note(call_details){
    //get all itemcode & quantity pair 
    var items = [];
    var quantity_identifier = 1;
    var inventory=1;
    if (warehouse =='' && change_warehouse == false){
        warehouse = $("#warehouse-code").val();
    }
    $("tr.data").each(function() {
        var code = $(this).find('td:nth-child(1) span').html();
        var subcode = $(this).find('td:nth-child(2) span').html();
        var unit= $(this).find('td:nth-child(4) span').html();
        var quantity = parseFloatHTML($(this).find('td:nth-child(6) span').html());
        var inventory_type = $(this).find('td:nth-child(10) span').find(':selected').data('id');
        if (quantity<=0){
            quantity_identifier = 0;
            // bootbox.alert({
            //     size: "small",
            //     message: "Quantity has to be a positive number", 
            //     onEscape: true });
            // clearmodal();
        }
        if (inventory_type == undefined){
            inventory=0;
        }
        var item = {
            itemCode : code,
            subitemcode: subcode,
            itemQuantity : quantity,
            unit: unit,
            inventory_type: inventory_type
        };
        items.push(item);        
    });
    //Ajax function sending data to backend if customer is not blank, else request user to enter customer details
    if (vendor != '' && warehouse != '' && inventory !=0 && quantity_identifier != 0){

        //get other bill details
        //Step 1: get reference to all balance-id cells
        cells = document.querySelectorAll('table.balance td:last-child span:last-child');
        //Step 2: get total
        total=Number(cells[0].innerHTML.replace(/[^0-9\.]+/g,""));
        vat_total = Number(cells[0].innerHTML.replace(/[^0-9\.]+/g,""));
        
        //Send ajax function to back-end 
        (function() {
            $.ajax({
                url : "", 
                type: "POST",
                data:{ note_details: JSON.stringify(items),
                    vendor: vendor,
                    warehouse: warehouse,
                    change_warehouse:change_warehouse,
                    invoice_id:invoice_id,
                    total: total,
                    vat_total: vat_total,
                    call_details:call_details,
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
                    //alert("Purchase Invoice generated successfully");
                    else{
                        console.log (jsondata)
                        location.href = redirect_url;
                    }
                },
                    // handle a non-successful response
                error : function() {
                    bootbox.alert({
                        size: "small",
                        message: "Debit Note generation failed",
                        onEscape: true });
                    clearmodal();
                    //alert("Purchase Invoice generation failed"); // provide a bit more info about the error to the user
                }
            });
        }());
    }
    else if (vendor == '' || warehouse == ''){
        bootbox.alert({
            size: "small",
            message: "Please check vendor & warehouse details.",
            onEscape: true });
        clearmodal();
        //location.reload(true);
    }
    else if (inventory == 0){
        bootbox.alert({
            size: "small",
            message: "Please check. Return inventory type is not selected in atleast one item.",
            onEscape: true });
        clearmodal();
        //alert ();
    }

    else if (quantity_identifier == 0){
        bootbox.alert({
            size: "small",
            message: "Check item quantity for all items. Item quantity cannot be zero or negative.",
            onEscape: true });
        clearmodal();
        //alert ("Check item quantity. Item quantity cannot be zero.")
    }
};


});



