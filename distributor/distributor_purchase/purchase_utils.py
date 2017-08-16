#from datetime import datetime
from distributor_purchase.models import purchase_receipt
# from distributor_master.models import Product, Unit

def new_purchase_receipt(tenant, supplier_invoice, vendor, warehouse, date, duedate,
				subtotal, cgsttotal, sgsttotal, igsttotal, round_value, total, amount_paid = 0):

	vendor_name=vendor.name
	ven_address=vendor.address_1+", "+vendor.address_2
	ven_state=vendor.state
	ven_city=vendor.city
	ven_pin=vendor.pin
	ven_gst=vendor.gst


	ware_address=warehouse.address_1+", "+warehouse.address_2
	ware_state=warehouse.state
	ware_city=warehouse.city
	ware_pin=warehouse.pin
	
	new_receipt=purchase_receipt()
	new_receipt.tenant=tenant

	new_receipt.supplier_invoice = supplier_invoice
	new_receipt.date = date
	
	new_receipt.vendor=vendor
	new_receipt.vendor_name=vendor_name
	try:
		new_receipt.vendor_address=ven_address
	except:
		new_receipt=''
	new_receipt.vendor_state=ven_state
	new_receipt.vendor_city=ven_city
	new_receipt.vendor_pin=ven_pin
	new_receipt.vendor_gst=ven_gst

	if (ven_gst):
		new_receipt.gst_type=1
	else:
		new_receipt.gst_type=2

	new_receipt.warehouse=warehouse
	new_receipt.warehouse_address=ware_address
	new_receipt.warehouse_state=ware_state
	new_receipt.warehouse_city=ware_city
	new_receipt.warehouse_pin=ware_pin
	
	# new_receipt.grand_discount_type=grand_discount_type
	# new_receipt.grand_discount_value=grand_discount_value
	new_receipt.subtotal=subtotal
	new_receipt.cgsttotal=cgsttotal
	new_receipt.sgsttotal=sgsttotal
	new_receipt.igsttotal=igsttotal
	new_receipt.roundoff=round_value
	new_receipt.total = total
	new_receipt.duedate = duedate
	new_receipt.amount_paid = 0
	new_receipt.save()
	return new_receipt

# def new_debit_note(tenant, vendor_key, warehouse_object, total, tax_total, date, note_type):
# 	debit_note=debitNote()
# 	debit_note.tenant=tenant
# 	debit_note.vendor_key = vendor_key
# 	debit_note.warehouse=warehouse_object
# 	debit_note.total = total
# 	debit_note.tax = tax_total
# 	debit_note.date = date
# 	debit_note.note_type = note_type
# 	#debit_note.invoice_no=
# 	debit_note.save()
# 	return debit_note
