from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum

import datetime

from .models import retail_invoice
from django.db.models import Sum
# from distributor_master.models import Product, Unit

def new_sales_invoice(tenant, request):
	
	customer_phone = request.data.get('customer_phone')
	customer_name = request.data.get('customer_name')
	customer_address = request.data.get('customer_address')
	customer_email = request.data.get('customer_email')
	customer_gender = request.data.get('customer_gender')
	customer_dob = request.data.get('customer_dob')
	
	warehouse_id=request.data.get('warehouse')
	
	subtotal=Decimal(request.data.get('subtotal'))
	total=Decimal(request.data.get('total'))
	warehouse = Warehouse.objects.for_tenant(this_tenant).get(id=warehouse_id)


	ware_address=warehouse.address_1+", "+warehouse.address_2
	ware_state=warehouse.state
	ware_city=warehouse.city
	ware_pin=warehouse.pin
	
	new_receipt=retail_invoice()
	new_receipt.tenant=tenant

	new_receipt.date = datetime.date.today()
	
	new_receipt.customer_name=customer_name
	new_receipt.customer_phone_no=customer_phone
	new_receipt.customer_address=customer_address
	new_receipt.customer_email=customer_email
	new_receipt.customer_gender=customer_gender
	new_receipt.customer_dob=customer_dob
	
	new_receipt.warehouse=warehouse
	new_receipt.warehouse_address=ware_address
	new_receipt.warehouse_state=ware_state
	new_receipt.warehouse_city=ware_city
	new_receipt.warehouse_pin=ware_pin
	
	new_receipt.subtotal=subtotal
	new_receipt.taxtotal=taxtotal
	new_receipt.total = total
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

def retail_sales_day_wise(start, end, tenant):
	sales_values=retail_invoice.objects.for_tenant(tenant).filter(date__range=(start,end)).\
			order_by('date').values('date').annotate(total=Sum('total'))
	response_data=[]
	for item in sales_values:
		response_data.append({'date':item['date'],'total':str(item['total'])})
	return response_data

# # def sales_raised_value(start, end, tenant):
# # 	invoice_value=sales_invoice.objects.for_tenant(tenant).filter(date__range=(start,end)).aggregate(Sum('total'))
# # 	print (invoice_value['total__sum'])
# # 	return invoice_value['total__sum']

# # def sales_collected_value(start, end, tenant):
# # 	payment_value=sales_payment.objects.for_tenant(tenant).filter(paid_on__range=(start,end)).aggregate(Sum('amount_received'))
# # 	print (payment_value['amount_received__sum'])
# 	return payment_value['amount_received__sum']