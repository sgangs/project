from datetime import datetime
from decimal import *
import json
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import F, Sum
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from distributor.journalentry import journal_entry, new_journal
from distribution_master.models import Manufacturer, Product, Zone, Customer, Vendor, Unit, Warehouse
from distribution_accounts.models import accountChart, Journal, journalEntry, paymentMode, journalGroup
from distribution_inventory.models import Inventory, returnableInventory, damagedInventory
from .models import salesInvoice,salesLineItem, creditNote, creditNoteLineItem
from .utils import new_credit_note, item_call, subitem_call, unit_call, new_sales_payment, new_sales_invoice


@login_required
#Purchase Invoice Base
def sales_base(request):
	return render(request, 'bill/base/sales_base.html')

@login_required
#Lists all sales invoice
def sales_list(request, type):
	if (type == "List"):
		items = salesInvoice.objects.for_tenant(request.user.tenant).all()
		return render(request, 'master/sales/sales_list.html',{'items':items, 'type': type})
	else:
		items = creditNote.objects.for_tenant(request.user.tenant).all()
		return render(request, 'master/sales/credit_note_list.html',{'items':items, 'type': type})

@login_required
#Lists sales invoice with pending/due collection
def sales_due(request, type):
	invoices=salesInvoice.objects.for_tenant(request.user.tenant)\
		.annotate(balance_due=F('total')-F('grand_discount')-F('amount_paid'))
	items=invoices.exclude(balance_due=0)
	return render(request, 'master/sales/sales_list.html',{'items':items, 'type': type})

@login_required
def salesinvoice(request, type):
	date=datetime.now()
	warehouse=Warehouse.objects.for_tenant(request.user.tenant).get(default="Yes")
	warehousekey=warehouse.key
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		this_tenant=request.user.tenant
		
		#getting Customer Data
		if (calltype == 'customer'):
			customerkey = request.POST.get('customer_code')
			response_data['name'] = Customer.objects.for_tenant(request.user.tenant).get(key__iexact=customerkey).name

		#getting Warehouse Data
		elif (calltype == 'warehouse'):
			warehousekey = request.POST.get('warehouse_code')
			response_data['name']=Warehouse.objects.for_tenant(request.user.tenant).get(key__iexact=warehousekey).address
			#response_data['key'] = warehouse.key
					
		#getting item data
		elif (calltype == 'item'):
			productkey = request.POST.get('item_code')
			response_data=item_call(this_tenant, productkey)
			
					
		#getting subitem data
		elif (calltype == 'subitem'):
			subitem = request.POST.get('subitem_code')
			productkey = request.POST.get('item_code')
			response_data=subitem_call(this_tenant, productkey, subitem)
			

		#This is used to get data if unit changes
		elif (calltype == 'unit'):
			subitem = request.POST.get('subitem_code')
			productkey = request.POST.get('item_code')
			unit_entry= request.POST.get('unit')
			response_data=unit_call(this_tenant, productkey, subitem, unit_entry)
						
		#saving the invoice
		elif (calltype == 'save'):
			with transaction.atomic():
				bill_data = json.loads(request.POST.get('bill_details'))
				proceed=True
				change_warehouse=request.POST.get('change_warehouse')
				if (change_warehouse == "true"):
					warehousekey = request.POST.get('warehouse')
				warehouse_object = Warehouse.objects.for_tenant(this_tenant).get(key__iexact=warehousekey)
				cogs_value=0
				#Checking available inventory by warehouse
				for data in bill_data:
					unit_entry=data['unit']
					unit=Unit.objects.for_tenant(this_tenant).get(symbol__iexact=unit_entry)
					multiplier=unit.multiplier
					invoiceQuantity=(int(data['itemQuantity']) +int(data['itemFree']))*multiplier
					item=Product.objects.for_tenant(this_tenant).get(key__iexact=data['itemCode'])
					subitem=item.subProduct_master_master_product.get(sub_key__iexact=data['subitemCode'])
					productQuantity=subitem.inventory_inventory_master_subproduct.get(warehouse=warehouse_object).quantity
					if productQuantity < invoiceQuantity:
						proceed= False
				if proceed:
					try:
						#Invoice=salesInvoice()
						total= request.POST.get('total')
						grand_discount=request.POST.get('grand_discount')
						customerkey = request.POST.get('customer')
						customer = Customer.objects.for_tenant(this_tenant).get(key__iexact=customerkey)
						Invoice=new_sales_invoice(this_tenant, customer,\
								 warehouse_object, total, grand_discount, date, amount_paid=0)
						journal=new_journal(this_tenant, date,"Sales Invoice",Invoice.invoice_id)
						
						#saving the salesLineItem and linking them with foreign key to invoice
						for data in bill_data:							
							itemcode=data['itemCode']
							subitemcode=data['subitemCode']
							unit_entry=data['unit']
							unit=Unit.objects.for_tenant(this_tenant).get(symbol__iexact=unit_entry)
							item=Product.objects.for_tenant(request.user.tenant).get(key__iexact=itemcode)
							subitem=item.subProduct_master_master_product.get(sub_key__iexact=subitemcode)
							subitem_unit=subitem.unit
							multiplier=unit.multiplier
							invoiceQuantity=int(data['itemQuantity'])*multiplier
							total_quantity=invoiceQuantity+(int(data['itemFree'])*multiplier)
							LineItem = salesLineItem()
							LineItem.invoice_no = Invoice
							LineItem.key= itemcode
							LineItem.sub_key= subitemcode							
							LineItem.name=item.name
							LineItem.unit=unit.symbol
							LineItem.discount1=subitem.discount1
							LineItem.discount2=subitem.discount2
							LineItem.quantity=invoiceQuantity
							LineItem.free=int(data['itemFree'])
							LineItem.manufacturer=item.manufacturer.key
							LineItem.mrp=subitem.mrp
							LineItem.selling_price=subitem.selling_price
							LineItem.vat_type=item.vat_type
							LineItem.vat_percent=item.vat_percent
							item_cost=round((subitem.cost_price*total_quantity),2)
							LineItem.save()
							#This is used to calculated to COGS
							cogs_value=cogs_value+item_cost
							#This will help reduce the inventory
							inventory=Inventory.objects.filter(warehouse=warehouse_object).get(item=subitem)							
							inventory.quantity=F('quantity') - total_quantity
							inventory.save()

						#This is for journal entry
						i=4
						while (i>0):
							value=Decimal(total) - Decimal(grand_discount)
							if (i==4):
								account= accountChart.objects.for_tenant(this_tenant).\
										get(name__exact="Accounts Receivable")
								journal_entry(this_tenant, journal, value, account, "Debit")
							elif (i==3):
								account= accountChart.objects.for_tenant(this_tenant).\
										get(name__exact="Sales")
								journal_entry(this_tenant, journal, value, account, "Credit")
							elif (i==2):
								account= accountChart.objects.for_tenant(this_tenant).\
										get(name__exact="Cost of Goods Sold")
								journal_entry(this_tenant, journal, cogs_value, account, "Debit")
							elif (i==1):
								account= accountChart.objects.for_tenant(this_tenant).\
										get(name__exact="Inventory")
								journal_entry(this_tenant, journal, cogs_value, account, "Credit")
							i=i-1						
						debit = journal.journalEntry_journal.filter(transaction_type="Debit").aggregate(Sum('value'))
						credit = journal.journalEntry_journal.filter(transaction_type="Debit").aggregate(Sum('value'))
						if (debit != credit):
							raise IntegrityError
					except:
						transaction.rollback()
				else:
					response_data['name']= "Sufficient stcok not available"
		
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'bill/sales/sales.html', {'date':date,'type': type, 'warehouse':warehouse})

#Displaying invoice & updating Collection
@login_required
def sales_detail(request, type, detail):
	date=datetime.now()
	#search for the clicked item details then get the item details and get dues from customers
	#Note this line has an issue as annotate goes over all elements, instead on just the necessary one.
	if (type== 'Detail'):
		call_id=detail.split("-",1)[1]
		if (call_id[:2] == "si"):
			invoice=salesInvoice.objects.for_tenant(request.user.tenant).select_related().get(invoice_id__iexact=call_id)
			details=invoice.salesLineItem_sales_sales_salesInvoice.all()
			return render(request, 'bill/sales/sales_detail.html',{'items': details, 'invoice':invoice})
		elif (call_id[:2] == "cn"):
			credit_note=creditNote.objects.for_tenant(request.user.tenant).select_related().get(note_id__iexact=call_id)
			details=credit_note.creditNoteLineItem_creditNote.all()
			return render(request, 'bill/sales/inventory_return_detail.html',{'items': details, 'invoice':credit_note})
	elif (type== 'Due'):
		this_tenant=request.user.tenant
		invoice_id=detail.split("-",1)[1]
		invoice=salesInvoice.objects.for_tenant(this_tenant)\
			.annotate(balance_due=F('total')-F('grand_discount')-F('amount_paid'))\
			.get(invoice_id__iexact=invoice_id)
		details=invoice.salesLineItem_sales_sales_salesInvoice.all()
		payment_mode=paymentMode.objects.for_tenant(this_tenant).filter(default="No")
		default_mode=paymentMode.objects.for_tenant(this_tenant).get(default="Yes")
		if request.method == 'POST':
			response_data = {}
			#calltype = request.POST.get('calltype')
			cheque_rtgs_number = request.POST.get('number')
			this_tenant=request.user.tenant
			current_amount_paid = Decimal(request.POST.get('amount_paid'))
			payment_mode=paymentMode.objects.for_tenant(this_tenant).\
						get(name__exact=request.POST.get('payment_mode'))
			payment_account=payment_mode.payment_account
			total_due=invoice.balance_due
			with transaction.atomic():
				try:
					#I forgor why I used the first filter in if, need to confirm this
					if(current_amount_paid>0 and current_amount_paid>total_due):
						response_data['name']= "Paid amount cannot be more than due amount"
					else:
						amount_already_paid=invoice.amount_paid
						invoice.amount_paid=amount_already_paid+current_amount_paid
						invoice.save()
						#payment=salesPayment()
						payment=new_sales_payment (invoice, current_amount_paid, payment_mode, cheque_rtgs_number)
						journal=new_journal(this_tenant, date,"Sales Collection",invoice.invoice_id)
						i=2
						while (i>0):
							if (i==2):
								account= accountChart.objects.for_tenant(request.user.tenant).\
											get(name__exact="Accounts Receivable")
								journal_entry(this_tenant, journal, current_amount_paid, account, "Credit")
							elif (i==1):
								journal_entry(this_tenant, journal, current_amount_paid, payment_account, "Debit")
							i=i-1						
				except:
					transaction.rollback()
			jsondata = json.dumps(response_data)
			return HttpResponse(jsondata)
		return render(request, 'bill/sales/sales_due.html',\
						{'items': details, 'invoice':invoice, 'payment_modes':payment_mode,\
						'default':default_mode,})

@login_required
#Lists all customer and payment details.
def customer_due(request, type):
	customers = Customer.objects.for_tenant(request.user.tenant).annotate(total=\
		Sum('salesInvoice_sales_master_customer__total')\
		-Sum('salesInvoice_sales_master_customer__grand_discount')
		-Sum('salesInvoice_sales_master_customer__amount_paid'))
	return render(request, 'bill/sales/customer_payment_list.html',\
		{'customers':customers, 'type': type})

@login_required
#Checks Sales Inventory Return and saves item
def inventory_return(request):
	date=datetime.now()
	warehouse=Warehouse.objects.for_tenant(request.user.tenant).get(default="Yes")
	warehousekey=warehouse.key
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		this_tenant=request.user.tenant
		#getting Customer Data
		if (calltype == 'customer'):
			customerkey = request.POST.get('customer_code')
			response_data['name'] = Customer.objects.for_tenant(this_tenant).get(key__iexact=customerkey).name

		#getting Warehouse Data
		elif (calltype == 'warehouse'):
			warehousekey = request.POST.get('warehouse_code')
			response_data['name'] = Warehouse.objects.for_tenant(this_tenant).get(key__iexact=warehousekey).address
					
		#getting item data
		elif (calltype == 'item'):
			productkey = request.POST.get('item_code')
			response_data=item_call(this_tenant, productkey)
					
		#getting subitem data
		elif (calltype == 'subitem'):
			subitem = request.POST.get('subitem_code')
			productkey = request.POST.get('item_code')
			response_data=subitem_call(this_tenant, productkey, subitem)			

		#This is used to get data if unit changes
		elif (calltype == 'unit'):
			subitem = request.POST.get('subitem_code')
			productkey = request.POST.get('item_code')
			unit_entry= request.POST.get('unit')
			response_data=unit_call(this_tenant, productkey, subitem, unit_entry)
			
		#Save Credit Note
		elif (calltype == 'save'):
			with transaction.atomic():
				note_data = json.loads(request.POST.get('note_details'))
				change_warehouse=request.POST.get('change_warehouse')
				if (change_warehouse == "true"):
					warehousekey = request.POST.get('warehouse')
				warehouse_object = Warehouse.objects.for_tenant(this_tenant).get(key__iexact=warehousekey)
				cogs_value=0
				cogs_waste=0
				try:
					total= request.POST.get('total')
					call_details = request.POST.get('call_details')
					tax_total= request.POST.get('vat_total')
					#credit_note.tenant=this_tenant
					customerkey = request.POST.get('customer')	
					customer=Customer.objects.for_tenant(this_tenant).get(key__iexact=customerkey)
					credit_note=new_credit_note(this_tenant, customer,\
								warehouse_object, total, tax_total, date, "Goods Return" )
					#The journal type needs to change to credit note
					journal=new_journal(this_tenant, date,"Credit Note",credit_note.note_id)
					
					#saving the creditnoteLineItem and linking them with foreign key to credit note
					for data in note_data:
						itemcode=data['itemCode']
						subitemcode=data['subitemCode']
						unit_entry=data['unit']
						inventory_type=data['inventory_type']
						item=Product.objects.for_tenant(request.user.tenant).get(key__iexact=itemcode)
						subitem=item.subProduct_master_master_product.get(sub_key__iexact=subitemcode)
						unit=Unit.objects.for_tenant(this_tenant).get(symbol__iexact=unit_entry)
						multiplier=unit.multiplier
						invoiceQuantity=int(data['itemQuantity'])*multiplier
						LineItem = creditNoteLineItem()
						LineItem.creditnote_no = credit_note												
						LineItem.key= itemcode
						LineItem.sub_key= subitemcode						
						LineItem.name=item.name
						LineItem.unit=unit.symbol					
						LineItem.quantity=invoiceQuantity
						LineItem.selling_price=subitem.selling_price
						LineItem.vat_type=item.vat_type
						LineItem.vat_percent=item.vat_percent
						LineItem.inventory_type = inventory_type
						LineItem.save()
						#This is used to calculated to COGS
						item_cost=round((subitem.cost_price*invoiceQuantity),2)
						if (inventory_type == "Waste"):
							cogs_waste=cogs_waste+item_cost
						else:
							cogs_value=cogs_value+item_cost
						#This will help reduce the inventory, after selecting which inventory to reduce
						if (inventory_type == "Reusable"):
							inventory=Inventory.objects.filter(warehouse=warehouse_object).get(item=subitem)
						elif (inventory_type == "Returnable"):
							inventory=returnableInventory.objects.filter(warehouse=warehouse_object).get(item=subitem)
						elif (inventory_type == "Waste"):
							inventory=damagedInventory.objects.filter(warehouse=warehouse_object).get(item=subitem)
						inventory.quantity=F('quantity') + invoiceQuantity
						inventory.save()
						#This is for journal entry
					i=6
					while (i>0):
						value=Decimal(total)
						if (i==6):
							#Checls if call is from credit or cash refund and acts accordingly
							if (call_details == "credit"):
								account= accountChart.objects.for_tenant(this_tenant).\
									get(name__exact="Accounts Receivable")
							elif (call_details == "refund"):
								account= accountChart.objects.for_tenant(this_tenant).\
									get(name__exact="Cash")
							journal_entry(this_tenant, journal, value, account, "Credit")	
						elif (i==5):
							account= accountChart.objects.for_tenant(this_tenant).\
									get(name__exact="Sales Contra")
							journal_entry(this_tenant, journal, value, account, "Debit")
						elif (i==4):
							account= accountChart.objects.for_tenant(this_tenant).\
								get(name__exact="Cost of Goods Sold Contra")
							total_value= cogs_waste+cogs_value
							journal_entry(this_tenant, journal, total_value, account, "Credit")
						elif (i==3):
							if (cogs_value > 0):
								account= accountChart.objects.for_tenant(this_tenant).\
									get(name__exact="Inventory")
								#journal_entry(this_tenant, journal, cogs_value, account, "Debit")
							if (cogs_waste > 0):
								account= accountChart.objects.for_tenant(this_tenant).\
									get(name__exact="Inventory Wastage")
							journal_entry(this_tenant, journal, cogs_value, account, "Debit")
						i=i-1						
					debit = journal.journalEntry_journal.filter(transaction_type="Debit").aggregate(Sum('value'))
					credit = journal.journalEntry_journal.filter(transaction_type="Debit").aggregate(Sum('value'))
					if (debit != credit):
						raise IntegrityError
				except:
					transaction.rollback()
				
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'bill/sales/inventory_return.html', {'warehouse': warehouse})

