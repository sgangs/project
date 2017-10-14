from decimal import Decimal
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError, transaction
from django.db.models import Sum

import datetime

from .models import retail_invoice
from django.db.models import Sum

from distributor_master.models import Unit, Product, Customer, Warehouse, product_sales_rate
from distributor_inventory.models import Inventory
from distributor_account.models import Account, tax_transaction, account_inventory, account_year_inventory, accounting_period, Journal,journal_entry,\
								journal_inventory, journal_entry_inventory, account_year, payment_mode
from distributor_account.journalentry import new_journal, new_journal_entry
from distributor_inventory.models import Inventory, inventory_ledger, warehouse_valuation
from distributor.variable_list import small_large_limt

from .models import *

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

# def delete_inventory(request):
# 	response_data={}
# 	this_tenant = request.user.tenant
# 	with transaction.atomic():
# 		try:
# 			invoice_pk=request.GET.get('invoice_id')
# 			old_invoice=retail_invoice.objects.for_tenant(this_tenant).get(id=invoice_pk)
			
# 			all_line_items=invoice_line_item.objects.for_tenant(this_tenant).filter(retail_invoice=old_invoice)
			
# 			#Does this tenant maintain inventory?
# 			maintain_inventory=this_tenant.maintain_inventory
# 			total_purchase_price=0
# 			#saving the invoice_line_item and linking them with foreign key to receipt
# 			if maintain_inventory:
# 				for item in all_line_items:
# 					productid=item.product
# 					multiplier=item.unit_multi
# 					# print(multiplier)
# 					try:
# 						original_tentative_sales_price=item.tentative_sales_price
# 						tentative_sales_price=original_tentative_sales_price/multiplier
# 					except:
# 						tentative_sales_price=0
# 					try:
# 						original_mrp=item.mrp
# 						mrp=original_mrp/multiplier
# 					except:
# 						mrp=0
# 					product_items=json.loads(item.other_data)['detail']
# 					for each_item in product_items:
# 						total_purchase_price+=Decimal(each_item['quantity'])*Decimal(each_item['pur_rate'])
# 						inventory=Inventory()
# 						inventory.product=productid
# 						inventory.warehouse=old_invoice.warehouse
# 						inventory.purchase_quantity=Decimal(each_item['quantity'])
# 						inventory.quantity_available=Decimal(each_item['quantity'])
# 						inventory.purchase_date=each_item['date']
# 						inventory.purchase_price=Decimal(each_item['pur_rate'])
# 						inventory.tentative_sales_price=tentative_sales_price
# 						inventory.mrp=mrp
# 						inventory.tenant=this_tenant
# 						inventory.save()

# 				#Update Warehouse Valuation
# 				warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).get(warehouse=old_invoice.warehouse)
# 				warehouse_valuation_change.valuation+=total_purchase_price
# 				warehouse_valuation_change.save()
								
# 				# delete inventory_ledger() - only if you maintain inventory
# 				inventory_ledger.objects.for_tenant(this_tenant).filter(date=old_invoice.date,transaction_type=9,\
# 						transaction_bill_id=old_invoice.invoice_id).delete()
						
# 			# delete tax_transaction
# 			tax_transaction.objects.for_tenant(this_tenant).filter(date=old_invoice.date,transaction_type=5,\
# 						transaction_bill_id=old_invoice.id).delete()
# 			#delete old line items
# 			all_line_items.delete()

# 			#delete all journal entries
# 			old_journal=Journal.objects.for_tenant(this_tenant).get(trn_type=7, transaction_bill_id=old_invoice.id)
# 			# Update the current balance of all journal related accounts
# 			journal_line_items=journal_entry.objects.for_tenant(this_tenant).filter(journal=old_journal)
# 			acct_period = accounting_period.objects.for_tenant(this_tenant).get(start__lte=old_journal.date, end__gte=old_journal.date)
			
# 			for item in journal_line_items:
# 				trn_type = item.transaction_type
# 				account = item.account
# 				account_journal_year=account_year.objects.get(account=account, accounting_period = acct_period)
# 				if (trn_type == 1):
# 					account_journal_year.current_debit=account_journal_year.current_debit-item.value
# 				elif (trn_type == 2):
# 					account_journal_year.current_credit=account_journal_year.current_credit-item.value
# 				account_journal_year.save()
# 			old_journal.delete()
						
# 			#delete all inventory journal entries
# 			old_journal_inv=journal_inventory.objects.for_tenant(this_tenant).filter(trn_type=7, transaction_bill_id=old_invoice.id)
# 			# Update the current balance of all inventory journal related accounts
# 			journal_inv_line_items = journal_entry_inventory.objects.for_tenant(this_tenant).filter(journal__in=old_journal_inv)
# 			for item in journal_inv_line_items:
# 				inventory_acct = item.account
# 				account_journal_year=account_year_inventory.objects.get(account_inventory=inventory_acct, accounting_period = acct_period)
# 				if (trn_type == 1):
# 					account_journal_year.current_debit=account_journal_year.current_debit-item.value
# 				elif (trn_type == 2):
# 					account_journal_year.current_credit=account_journal_year.current_credit-item.value
# 				account_journal_year.save()
						
# 			old_journal_inv.delete()
# 			# raise IntegrityError

# 			old_invoice.delete()

# 			response_data['success'] = True
# 			return response_data
# 		except:
# 			transaction.rollback()