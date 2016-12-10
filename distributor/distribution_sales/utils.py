from datetime import datetime
from distribution_master.models import Product, Unit
from .models import salesInvoice, creditNote, salesPayment, creditNoteLineItem, salesLineItem


def new_sales_invoice(tenant, customer, warehouse_object,total, grand_discount, date, amount_paid = 0):
	item=salesInvoice()
	item.tenant=tenant
	item.customer = customer
	item.warehouse=warehouse_object
	item.total = total
	item.grand_discount = grand_discount
	item.amount_paid = amount_paid
	item.date = date
	item.save()
	return item

def new_credit_note(tenant, customer, warehouse_object, total, tax_total, date, note_type):
	credit_note=creditNote()
	credit_note.tenant=tenant
	credit_note.customer = customer
	credit_note.warehouse=warehouse_object
	credit_note.total = total
	credit_note.tax = tax_total
	credit_note.date = date
	credit_note.note_type = note_type
	credit_note.save()
	return credit_note

def new_sales_payment(invoice, current_amount_paid, payment_mode, cheque_rtgs_number ):
	payment=salesPayment()
	payment.invoice_no=invoice
	payment.amount_paid=current_amount_paid
	payment.collected_on=datetime.now()
	payment.payment_mode=payment_mode
	payment.cheque_rtgs_number=cheque_rtgs_number
	payment.save()
	return payment

def item_call(tenant, productkey):
	response_data={}
	product=Product.objects.for_tenant(tenant).get(key__iexact=productkey)
	response_data['name'] = product.name
	if(product.vat_type == 'No VAT'):
		response_data['vat_percent']=0
	else:
		response_data['vat_percent'] = float(product.vat_percent)
	response_data['vat_type']=product.vat_type
	return response_data
	
def subitem_call(tenant, productkey, subitem):
	response_data={}
	product = Product.objects.for_tenant(tenant).get(key__iexact=productkey)
	subproduct=product.subProduct_master_master_product.get(sub_key=subitem)
	unit=subproduct.unit
	multiplier=unit.multiplier
	response_data['unit'] = unit.symbol
	response_data['salesprice'] = float(round(subproduct.selling_price*multiplier,2))
	response_data['discount1'] = float(subproduct.discount1)
	response_data['discount2'] = float(round(subproduct.discount2*multiplier,2))
	return response_data
	
def unit_call(tenant, productkey, subitem, unit_entry):
	response_data={}
	product = Product.objects.for_tenant(tenant).get(key__iexact=productkey)
	subproduct=product.subProduct_master_master_product.get(sub_key=subitem)
	initial_multiplier=subproduct.unit.multiplier
	revised_unit= Unit.objects.for_tenant(tenant).get(symbol__iexact=unit_entry)
	response_data['unit'] = revised_unit.symbol
	response_data['old_multiplier'] = str(initial_multiplier)
	response_data['new_multiplier'] = str(revised_unit.multiplier)
	return response_data

def note_new_line_item(credit_note, itemcode, subitemcode, item, symbol, invoiceQuantity, selling_price, inventory_type):
	LineItem = creditNoteLineItem()
	LineItem.creditnote_no = credit_note												
	LineItem.key= itemcode
	LineItem.sub_key= subitemcode						
	LineItem.name=item.name
	LineItem.unit=symbol					
	LineItem.quantity=invoiceQuantity
	LineItem.selling_price=subitem.selling_price
	LineItem.vat_type=item.vat_type
	LineItem.vat_percent=item.vat_percent
	LineItem.inventory_type = inventory_type
	LineItem.save()
	return LineItem

def invoice_new_line_item(Invoice, itemcode, subitemcode, item, symbol, subitem, invoiceQuantity, free):
	LineItem = salesLineItem()
	LineItem.invoice_no = Invoice
	LineItem.key= itemcode
	LineItem.sub_key= subitemcode							
	LineItem.name=item.name
	LineItem.unit=symbol
	LineItem.discount1=subitem.discount1
	LineItem.discount2=subitem.discount2
	LineItem.quantity=invoiceQuantity
	LineItem.free=free
	LineItem.manufacturer=item.manufacturer.key
	LineItem.mrp=subitem.mrp
	LineItem.selling_price=subitem.selling_price
	LineItem.vat_type=item.vat_type
	LineItem.vat_percent=item.vat_percent							
	LineItem.save()