#from datetime import datetime
from distribution_purchase.models import purchaseInvoice, debitNote
from distribution_master.models import Product, Unit

#def new_journal(tenant, date, group,journal_type = None, key=None):
def new_purchase_invoice(tenant, vendor_key, warehouse_object,total, grand_discount, date, amount_paid = 0):
	Invoice=purchaseInvoice()
	Invoice.tenant=tenant
	Invoice.vendor_key = vendor_key
	Invoice.warehouse=warehouse_object
	Invoice.total = total
	Invoice.grand_discount = grand_discount
	Invoice.amount_paid = 0
	Invoice.date = date
	Invoice.save()
	return Invoice

def new_debit_note(tenant, vendor_key, warehouse_object, total, tax_total, date, note_type):
	debit_note=debitNote()
	debit_note.tenant=tenant
	debit_note.vendor_key = vendor_key
	debit_note.warehouse=warehouse_object
	debit_note.total = total
	debit_note.tax = tax_total
	debit_note.date = date
	debit_note.note_type = note_type
	#debit_note.invoice_no=
	debit_note.save()
	return debit_note

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
	response_data['purchaseprice'] = float(round(subproduct.cost_price*multiplier,2))
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