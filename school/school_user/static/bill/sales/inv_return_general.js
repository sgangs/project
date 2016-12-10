$(function(){

checked=true;

$('.tax').change(function(){
	if($(this).prop('checked'))
	{
		checked=true;
	}else{
		checked=false;
	}
})

});
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

function generateTableRow() {
	var emptyColumn = document.createElement('tr');

	emptyColumn.className ='data';	

	emptyColumn.innerHTML = '<td><a class="cut">-</a><span class="itemcode" contenteditable></span></td>' +
		'<td colspan="1"><span class="subitemcode" contenteditable></span></td>' +
		'<td colspan="2"><span></span></td>' +
		'<td colspan="1"><span class="unit"></span></td>' +
		'<td colspan="1"><span></span></td>' +
		'<td colspan="1"><span contenteditable></span></td>'+
		'<td colspan="1"><span></span></td>'+
		'<td colspan="1"><span></span></td>'+
		'<td colspan="1"><span></span></td>'+
		'<td colspan="2"><span>'+
		'<select id="inventory_type">'+
		'<option disabled selected hidden style="display: none" value>Select An Option</option>'+
  		'<option data-id="Reusable">Reusable</option>'+
  		'<option data-id="Returnable">Damaged, Returnable</option>'+
  		'<option data-id="Non-returnable">Damaged, Non-returnable</option> </select>'+  		
		'</span></td>';

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
	var vat_total = 0;
	var cells, price, total, a, i;

	// update inventory cells
	// ======================

	for (var a = document.querySelectorAll('table.inventory tbody tr'), i = 0; a[i]; ++i) {
		// get inventory row cells
		cells = a[i].querySelectorAll('span:last-child');

		// set price as cell[2] * cell[3]
		unitrate=parseFloatHTML(cells[4]);
		quantity=parseFloatHTML(cells[5]);
		vat_type=cells[6].innerHTML;
		vat_percent=parseFloatHTML(cells[7]);
		//console.log(vat_type);
		if (checked){
			if (vat_type == 'On Cost Price'){
				vat=vat_percent/100*unitrate;
				// console.log(vat);
			}else{
				vat=(unitrate*100)/(100+vat_percent)*(vat_percent/100);
			}
		}else{
			vat=0
		}		
		
		
		raw_price=(unitrate*quantity)+(vat*quantity);
		price=(Math.round(raw_price*100))/100;

		// add price to total
		total += price;
		vat_total += vat*quantity;

		// set row total
		cells[8].innerHTML = price;
	}

	// update balance cells
	// ====================

	// // get balance cells
	 cells = document.querySelectorAll('table.balance td:last-child span:last-child');

	// // set total
	 cells[0].innerHTML = total;
	 cells[1].innerHTML = vat_total;

	// //get grand discount
	// grand_discount = cells[1].innerHTML;

	// //get net total & set that to cell. If net total is negative, alert the customer
	// net_total = total-grand_discount;
	// if (net_total<0){
	// 	alert("Net total cannot be negative");
	// 	location.reload(true);
	// 	//location.reload(true);
	// }
	// cells[2].innerHTML = net_total;

	// // set balance and meta balance
	// cells[4].innerHTML = document.querySelector('table.meta tr:last-child td:last-child span:last-child').innerHTML = parsePrice(net_total - parseFloatHTML(cells[3]));

	// update prefix formatting
	// ========================

	 //var prefix = document.querySelector('#prefix').innerHTML;
	 //for (a = document.querySelectorAll('[data-prefix]'), i = 0; a[i]; ++i) a[i].innerHTML = prefix;

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

	//function onFileInput(e) {
		//image.classList.remove('hover');

	//	var
	//	reader = new FileReader(),
	//	files = e.dataTransfer ? e.dataTransfer.files : e.target.files,
	//	i = 0;

	//	reader.onload = onFileLoad;

	//	while (files[i]) reader.readAsDataURL(files[i++]);
	//}

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
	}
}

window.addEventListener && document.addEventListener('DOMContentLoaded', onContentLoad);

