/* Shivving (IE8 is not supported, but at least it won't look as awful)
/* ========================================================================== */
/*
(function (document) {
	var
	head = document.head = document.getElementsByTagName('head')[0] || document.documentElement,
	elements = 'article aside audio bdi canvas data datalist details figcaption figure footer header hgroup mark meter nav output picture progress section summary time video x'.split(' '),
	elementsLength = elements.length,
	elementsIndex = 0,
	element;

	while (elementsIndex < elementsLength) {
		element = document.createElement(elements[++elementsIndex]);
	}

	element.innerHTML = 'x<style>' +
		'article,aside,details,figcaption,figure,footer,header,hgroup,nav,section{display:block}' +
		'audio[controls],canvas,video{display:inline-block}' +
		'[hidden],audio{display:none}' +
		'mark{background:#FF0;color:#000}' +
	'</style>';

	return head.insertBefore(element.lastChild, head.firstChild);
})(document);

/* Prototyping
/* ========================================================================== */

var i=1;


(function (window, ElementPrototype, ArrayPrototype, polyfill) {
	function NodeList() { [polyfill] }
	NodeList.prototype.length = ArrayPrototype.length;

	ElementPrototype.matchesSelector = ElementPrototype.matchesSelector ||
	ElementPrototype.mozMatchesSelector ||
	ElementPrototype.msMatchesSelector ||
	ElementPrototype.oMatchesSelector ||
	ElementPrototype.webkitMatchesSelector ||
	function matchesSelector(selector) {
		return ArrayPrototype.indexOf.call(this.parentNode.querySelectorAll(selector), this) > -1;
	};

	ElementPrototype.ancestorQuerySelectorAll = ElementPrototype.ancestorQuerySelectorAll ||
	ElementPrototype.mozAncestorQuerySelectorAll ||
	ElementPrototype.msAncestorQuerySelectorAll ||
	ElementPrototype.oAncestorQuerySelectorAll ||
	ElementPrototype.webkitAncestorQuerySelectorAll ||
	function ancestorQuerySelectorAll(selector) {
		for (var cite = this, newNodeList = new NodeList; cite = cite.parentElement;) {
			if (cite.matchesSelector(selector)) ArrayPrototype.push.call(newNodeList, cite);
		}

		return newNodeList;
	};

	ElementPrototype.ancestorQuerySelector = ElementPrototype.ancestorQuerySelector ||
	ElementPrototype.mozAncestorQuerySelector ||
	ElementPrototype.msAncestorQuerySelector ||
	ElementPrototype.oAncestorQuerySelector ||
	ElementPrototype.webkitAncestorQuerySelector ||
	function ancestorQuerySelector(selector) {
		return this.ancestorQuerySelectorAll(selector)[0] || null;
	};
})(this, Element.prototype, Array.prototype);

/* Helper Functions
/* ========================================================================== */

function generatePurchaseTableRow() {
	var emptyColumn = document.createElement('tr');

	emptyColumn.className ='data';	

	emptyColumn.innerHTML = '<td><a class="cut">-</a><span class="itemcode" contenteditable></span></td>' +
		'<td colspan="2"><span contenteditable></span></td>' +
		'<td><span contenteditable></span></td>' +
		'<td><span contenteditable></span></td>' +
		'<td><span contenteditable></span></td>'+
		'<td><span contenteditable></span></td>' +
		'<td><span contenteditable>0</span></td>'+
		'<td><span contenteditable></span></td>' +
		'<td><span contenteditable></span></td>' +
		'<td><span contenteditable></span></td>' ;


	return emptyColumn;
}




function generateTableRow() {
	var emptyColumn = document.createElement('tr');

	emptyColumn.className ='data';	

	emptyColumn.innerHTML = '<td><a class="cut">-</a><span class="itemcode" contenteditable></span></td>' +
		'<td colspan="2"><span></span></td>' +
		'<td><span></span></td>' +
		'<td><span contenteditable></span></td>' +
		'<td><span></span></td>'+
		'<td><span></span></td>' +
		'<td><span contenteditable>0</span></td>'+
		'<td><span></span></td>' +
		'<td><span></span></td>' +
		'<td><span></span></td>' ;


	return emptyColumn;
}

function parseFloatHTML(element) {
	return parseFloat(element.innerHTML.replace(/[^\d\.\-]+/g, '')) || 0;
}

function parsePrice(number) {
	return number.toFixed(2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1,');
}

/* Update Number
/* ========================================================================== */

function updateNumber(e) {
	var
	activeElement = document.activeElement,
	value = parseFloat(activeElement.innerHTML),
	wasPrice = activeElement.innerHTML == parsePrice(parseFloatHTML(activeElement));

	if (!isNaN(value) && (e.keyCode == 38 || e.keyCode == 40 || e.wheelDeltaY)) {
		e.preventDefault();

		value += e.keyCode == 38 ? 1 : e.keyCode == 40 ? -1 : Math.round(e.wheelDelta * 0.025);
		value = Math.max(value, 0);

		activeElement.innerHTML = wasPrice ? parsePrice(value) : value;
	}

	updateInvoice();
}

/* Update Invoice
/* ========================================================================== */

function updateInvoice() {
	var total = 0;
	var cells, price, total, a, i;

	// update inventory cells
	// ======================

	for (var a = document.querySelectorAll('table.inventory tbody tr'), i = 0; a[i]; ++i) {
		// get inventory row cells
		cells = a[i].querySelectorAll('span:last-child');

		// set price as cell[2] * cell[3]
		unitrate=parseFloatHTML(cells[2]);
		quantity=parseFloatHTML(cells[3]);
		discount1=parseFloatHTML(cells[4]);
		discount2=parseFloatHTML(cells[5]);
		free=parseFloatHTML(cells[6]);
		vat_type=parseFloatHTML(cells[7]);
		vat_percent=parseFloatHTML(cells[8]);
		if (vat_type == 'on Cost Price'){
			vat=vat_percent/100*unitrate;
		}
		else{
			vat=(unitrate*100)/(100+vat_percent)*(vat_percent/100);
		}
		
		raw_price=(unitrate-discount1/100*unitrate-discount2)*quantity+vat*(quantity+free);
		price=(Math.round(raw_price*100))/100;

		// add price to total
		total += price;

		// set row total
		cells[9].innerHTML = price;
	}

	// update balance cells
	// ====================

	// get balance cells
	cells = document.querySelectorAll('table.balance td:last-child span:last-child');

	// set total
	cells[0].innerHTML = total;

	//get grand discount
	grand_discount = cells[1].innerHTML;

	//get net total & set that to cell. If net total is negative, alert the customer
	net_total = total-grand_discount;
	if (net_total<0){
		alert("Net total cannot be negative");
		location.reload(true);
		//location.reload(true);
	}
	cells[2].innerHTML = net_total;

	// set balance and meta balance
	cells[4].innerHTML = document.querySelector('table.meta tr:last-child td:last-child span:last-child').innerHTML = parsePrice(net_total - parseFloatHTML(cells[3]));

	// update prefix formatting
	// ========================

	var prefix = document.querySelector('#prefix').innerHTML;
	for (a = document.querySelectorAll('[data-prefix]'), i = 0; a[i]; ++i) a[i].innerHTML = prefix;

	// update price formatting
	// =======================

	for (a = document.querySelectorAll('span[data-prefix] + span'), i = 0; a[i]; ++i) if (document.activeElement != a[i]) a[i].innerHTML = parsePrice(parseFloatHTML(a[i]));
}

/* On Content Load
/* ========================================================================== */

function onContentLoad() {
	updateInvoice();

	var
	input = document.querySelector('input'),
	image = document.querySelector('img');

	function onClick(e) {
		var element = e.target.querySelector('[contenteditable]'), row;

		element && e.target != document.documentElement && e.target != document.body && element.focus();

		if (e.target.matchesSelector('.add')) {
			document.querySelector('table.inventory tbody').appendChild(generateTableRow());
		}
		else if (e.target.className == 'cut') {
			row = e.target.ancestorQuerySelector('tr');

			row.parentNode.removeChild(row);
		}
		else if (e.target.matchesSelector('.purchaseadd')) {
			document.querySelector('table.inventory tbody').appendChild(generatePurchaseTableRow());
		}

		updateInvoice();
	}

	function onEnterCancel(e) {
		e.preventDefault();

		//image.classList.add('hover');
	}

	function onLeaveCancel(e) {
		e.preventDefault();

		//image.classList.remove('hover');
	}

	function onFileInput(e) {
		//image.classList.remove('hover');

		var
		reader = new FileReader(),
		files = e.dataTransfer ? e.dataTransfer.files : e.target.files,
		i = 0;

		reader.onload = onFileLoad;

		while (files[i]) reader.readAsDataURL(files[i++]);
	}

	function onFileLoad(e) {
		var data = e.target.result;

		image.src = data;
	}

	if (window.addEventListener) {
		document.addEventListener('click', onClick);

		document.addEventListener('mousewheel', updateNumber);
		document.addEventListener('keydown', updateNumber);

		document.addEventListener('keydown', updateInvoice);
		document.addEventListener('keyup', updateInvoice);

		input.addEventListener('focus', onEnterCancel);
		input.addEventListener('mouseover', onEnterCancel);
		input.addEventListener('dragover', onEnterCancel);
		input.addEventListener('dragenter', onEnterCancel);

		input.addEventListener('blur', onLeaveCancel);
		input.addEventListener('dragleave', onLeaveCancel);
		input.addEventListener('mouseout', onLeaveCancel);

		input.addEventListener('drop', onFileInput);
		input.addEventListener('change', onFileInput);
	}
}

window.addEventListener && document.addEventListener('DOMContentLoaded', onContentLoad);



//get address of customer from database

var customer='';

$( "#customer-code" ).change(function() {

	/*alert( "Handler for .change() called." );*/
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
        		$('#companyname').html(jsondata['name'])
        		$('#companyaddress').html(jsondata['address'])
        	    console.log(jsondata); // log the returned json to the console
        	    console.log("success"); // another sanity check
        	},

        			 //handle a non-successful response
        	error : function() {
            		alert("Customer does not exist"); // provide a bit more info about the error to the user
        	}
    	});
	}());

});

//get address of vendor from database

var vendor='';

$( "#vendor-code" ).change(function() {

	/*alert( "Handler for .change() called." );*/
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
        		$('#companyname').html(jsondata['name'])
        		console.log(jsondata); // log the returned json to the console
        	    console.log("success"); // another sanity check
        	},

        			 //handle a non-successful response
        	error : function() {
            		alert("Vendor does not exist"); // provide a bit more info about the error to the user
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
        			$(el).closest('tr').find('td:nth-child(2) span').html(jsondata['name'])
        			$(el).closest('tr').find('td:nth-child(3) span').html(jsondata['sellingprice'])
        			$(el).closest('tr').find('td:nth-child(8) span').html(jsondata['vat_type'])
        			$(el).closest('tr').find('td:nth-child(9) span').html(jsondata['vat_percent'])
        	    	console.log(jsondata); // log the returned json to the console
        	    	alert(jsondata['sellingprice']);
        	    },

        				// handle a non-successful response
        			error : function() {
            			alert("Item does not exist"); // provide a bit more info about the error to the user
        			}
    		});
		}());    	    	
	}
});



//The following function works as the save button in sales bill is clicked - sending the item code and quantity pair along with other bill details to back-end

$( ".save" ).on("click", function(){
	
	//get all itemcode & quantity pair 
	var items = [];
	var quantity_identifier = 1;

	$("tr.data").each(function() {
		
		var code = $(this).find('td:nth-child(1) span').html();
		var quantity = $(this).find('td:nth-child(4) span').html();
		var free =  $(this).find('td:nth-child(7) span').html();
		if (quantity<=0){
			quantity_identifier = 0;
			alert("Quantity has to be a positive number");
		}

		var item = {
			itemCode : code,
 			itemQuantity : quantity,
 			itemFree: free       
		};
		items.push(item);        
	});



	//Ajax function sending data to backend if customer is not blank, else request user to enter customer details
	if (customer != '' && quantity_identifier != 0){

		//get other bill details
		//Step 1: get reference to all balance-id cells
		cells = document.querySelectorAll('table.balance td:last-child span:last-child');

		//Step 2: get total
		total=Number(cells[0].innerHTML.replace(/[^0-9\.]+/g,""));
		alert(total)

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
    				total: total,
    				grand_discount: grand_discount,
    				amount_paid: amount_paid,
    				calltype: 'save',
    				csrfmiddlewaretoken: csrf_token},
    			dataType: 'json',    			
    			// handle a successful response
        		success : function(jsondata) {  
        			console.log(jsondata['name']); // log the returned json to the console
        			if (jsondata['name']=="Sufficient stock not available") {
        				console.log(jsondata['name'])
        				alert("Sufficient stock not available");
        			}
        			else{
        				alert("Invoice generated successfully");
        			}
        	    },

        		// handle a non-successful response
        		error : function() {
            		alert("Invoice generation failed"); // provide a bit more info about the error to the user
        		}
    		});
		}());
	}

	else{
		alert ("Please check customer details & whether all quantities are positive or not")
		location.reload(true);
	}
	

});

//The following function works as the save button in purchase is clicked - sending the item code and quantity pair along with other bill details to back-end

$( ".purchasesave" ).on("click", function(){
	
	//get all itemcode & quantity pair 
	var items = [];
	var quantity_identifier = 1;

	$("tr.data").each(function() {
		
		var code = $(this).find('td:nth-child(1) span').html();
		var quantity = $(this).find('td:nth-child(4) span').html();
		var free =  $(this).find('td:nth-child(7) span').html();
		if (quantity<=0){
			quantity_identifier = 0;
			alert("Quantity has to be a positive number");
		}

		var item = {
			itemCode : code,
 			itemQuantity : quantity,
 			itemFree: free       
		};
		items.push(item);        
	});



	//Ajax function sending data to backend if customer is not blank, else request user to enter customer details
	if (vendor != '' && quantity_identifier != 0){

		//get other bill details
		//Step 1: get reference to all balance-id cells
		cells = document.querySelectorAll('table.balance td:last-child span:last-child');

		//Step 2: get total
		total=Number(cells[0].innerHTML.replace(/[^0-9\.]+/g,""));
		alert(total)

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
    				vendor: vendor,
    				total: total,
    				grand_discount: grand_discount,
    				amount_paid: amount_paid,
    				calltype: 'save',
    				csrfmiddlewaretoken: csrf_token},
    			dataType: 'json',    			
    			// handle a successful response
        		success : function(jsondata) {  
        			console.log(jsondata); // log the returned json to the console
        			alert("Invoice generated successfully");
        	    },

        		// handle a non-successful response
        		error : function() {
            		alert("Invoice generation failed"); // provide a bit more info about the error to the user
        		}
    		});
		}());
	}

	else{
		alert ("Please check vendor details & whether all quantities are positive or not")
		location.reload(true);
	}
	
});
