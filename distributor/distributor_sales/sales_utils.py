from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum

#from datetime import datetime
from distributor_sales.models import sales_invoice, sales_payment
from django.db.models import Sum
# from distributor_master.models import Product, Unit

def new_sales_invoice(tenant, customer, warehouse, date, duedate,
				grand_discount_type, grand_discount_value, subtotal, taxtotal, total, amount_paid = 0):
	
	customer_name=customer.name
	customer_address=customer.address_1+", "+customer.address_2
	customer_state=customer.state
	customer_city=customer.city
	customer_pin=customer.pin
	
	ware_address=warehouse.address_1+", "+warehouse.address_2
	ware_state=warehouse.state
	ware_city=warehouse.city
	ware_pin=warehouse.pin
	
	new_receipt=sales_invoice()
	new_receipt.tenant=tenant

	new_receipt.date = date
	
	new_receipt.customer=customer
	new_receipt.customer_name=customer_name
	new_receipt.customer_address=customer_address
	new_receipt.customer_state=customer_state
	new_receipt.customer_city=customer_city
	new_receipt.customer_pin=customer_pin
	new_receipt.customer_gst=customer.gst

	new_receipt.warehouse=warehouse
	new_receipt.warehouse_address=ware_address
	new_receipt.warehouse_state=ware_state
	new_receipt.warehouse_city=ware_city
	new_receipt.warehouse_pin=ware_pin
	
	new_receipt.grand_discount_type=grand_discount_type
	new_receipt.grand_discount_value=grand_discount_value
	new_receipt.subtotal=subtotal
	new_receipt.cgsttotal=cgsttotal
	new_receipt.sgsttotal=sgsttotal
	new_receipt.igsttotal=igsttotal
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

def sales_day_wise(start, end, tenant):
	sales_values=sales_invoice.objects.for_tenant(tenant).filter(date__range=(start,end)).\
			order_by('date').values('date').annotate(total=Sum('total'))
	response_data=[]
	for item in sales_values:
		response_data.append({'date':item['date'],'total':str(item['total'])})
	return response_data

def sales_raised_value(start, end, tenant):
	invoice_value=sales_invoice.objects.for_tenant(tenant).filter(date__range=(start,end)).aggregate(Sum('total'))
	print (invoice_value['total__sum'])
	return invoice_value['total__sum']

def sales_collected_value(start, end, tenant):
	payment_value=sales_payment.objects.for_tenant(tenant).filter(paid_on__range=(start,end)).aggregate(Sum('amount_received'))
	print (payment_value['amount_received__sum'])
	return payment_value['amount_received__sum']