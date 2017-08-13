from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum
from django.db.models import Sum

from distributor_account.models import Account, Journal, journal_entry, tax_transaction
from distributor_inventory.models import Inventory, inventory_ledger
from distributor_sales.models import sales_invoice, sales_payment
# from distributor_master.models import Product, Unit

def new_sales_invoice(tenant, customer, warehouse, date, duedate,
				grand_discount_type, grand_discount_value, subtotal, taxtotal, total, amount_paid = 0):
	
	customer_name=customer.name
	try:
		customer_address=customer.address_1+", "+customer.address_2
	except:
		customer_address=''
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
	return invoice_value['total__sum']

def sales_collected_value(start, end, tenant):
	payment_value=sales_payment.objects.for_tenant(tenant).filter(paid_on__range=(start,end)).aggregate(Sum('amount_received'))
	return payment_value['amount_received__sum']


def new_inventory_ledger_sales(product, warehouse, trn_type, date, quantity, pur_rate, sales_rate, invoice_id, this_tenant):
	new_inventory_ledger=inventory_ledger()
	new_inventory_ledger.product=product
	new_inventory_ledger.warehouse=warehouse
	new_inventory_ledger.transaction_type=trn_type
	new_inventory_ledger.date=date
	new_inventory_ledger.quantity=quantity
	new_inventory_ledger.actual_sales_price=sales_rate
	new_inventory_ledger.purchase_price=pur_rate
	new_inventory_ledger.transaction_bill_id=invoice_id
	new_inventory_ledger.tenant=this_tenant
	new_inventory_ledger.save()

def new_tax_transaction_sales(tax_type, trn_type, percent, value, invoice_pk, invoice_id,  date, this_tenant, is_registered):
	new_tax_transaction=tax_transaction()
	new_tax_transaction.transaction_type=trn_type
	new_tax_transaction.tax_type=tax_type
	new_tax_transaction.tax_percent=percent
	new_tax_transaction.tax_value=value
	new_tax_transaction.transaction_bill_id=invoice_pk
	new_tax_transaction.transaction_bill_no=invoice_id
	new_tax_transaction.date=date
	new_tax_transaction.tenant=this_tenant
	new_tax_transaction.is_registered = is_registered
	new_tax_transaction.save()

def paginate_data(page_no, total_per_page, objects):
	response_data={}
	paginator = Paginator(objects, total_per_page)
	object_paginated=paginator.page(page_no)
			
	objects_list=objects[(int(page_no)-1)*total_per_page:int(page_no)*total_per_page]
	index = paginator.page_range.index(object_paginated.number)
	max_index = len(paginator.page_range)
	start_index = index - 3 if index >= 3 else 0

	end_index = index + 3 if index <= max_index - 3 else max_index
		
	response_data['object']=objects_list
	response_data['start']=start_index
	response_data['end']=end_index
	# response_data['has_previous']=paginator.has_previous()
	# response_data['has_next']=paginator.has_next()
	return response_data 