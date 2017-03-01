from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import F, Sum
from decimal import *
import json
from datetime import datetime

from distributor.journalentry import journal_entry, new_journal
from distribution_master.models import Manufacturer, Product, Zone, Customer, Vendor, Unit, Warehouse
from distribution_inventory.models import Inventory, returnableInventory
from distribution_accounts.models import accountChart, Journal, journalEntry, paymentMode, journalGroup
from distribution_user.models import Tenant
from .models import purchaseInvoice, purchaseLineItem, purchasePayment, debitNote, debitNoteLineItem
from .utils import new_purchase_invoice, new_debit_note, item_call, subitem_call, unit_call

#Purchase Invoice Base
@login_required
def purchase_base(request):
		return render(request, 'bill/base/purchase_base.html')


@login_required
#Returns list of all purchase invoices
def purchase_list(request, type):
	if (type == "List"):
		items = purchaseInvoice.objects.for_tenant(request.user.tenant).all()
		return render(request, 'master/purchase/purchase_list.html',{'items':items, 'type': type})
	else:
		items = debitNote.objects.for_tenant(request.user.tenant).all()
		return render(request, 'master/purchase/debit_note_list.html',{'items':items, 'type': type})

@login_required
#To display list of purchase invoices with payment pending
def purchase_due(request, type):
	invoices=purchaseInvoice.objects.for_tenant(request.user.tenant)\
		.annotate(balance_due=F('total')-F('grand_discount')-F('amount_paid'))
	items=invoices.exclude(balance_due=0)
	return render(request, 'master/purchase/purchase_list.html',{'items':items, 'type': type})

@login_required
#This view helps in creating & thereafter saving a purchase invoice
def purchaseinvoice(request, type):
	date=datetime.now()	
	warehouse=Warehouse.objects.for_tenant(request.user.tenant).get(default="Yes")
	warehousekey=warehouse.key
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		this_tenant=request.user.tenant

		#getting Customer Data
		if (calltype == 'vendor'):
			vendorkey = request.POST.get('vendor_code')
			response_data['name'] = Vendor.objects.for_tenant(this_tenant).get(key__iexact=vendorkey).name

		#getting Watrehouse Data
		elif (calltype == 'warehouse'):
			warehousekey = request.POST.get('warehouse_code')
			response_data['name'] = Warehouse.objects.for_tenant(this_tenant).get(key__iexact=warehousekey).address
					
		#getting item data
		elif (calltype == 'item'):
			productkey = request.POST.get('item_code')
			response_data=item_call(this_tenant, productkey)
				
		#getting subitem data
		elif (calltype == 'subitem'):
			subitem = request.POST.get('subitemcode')
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
				try:
					bill_data = json.loads(request.POST.get('bill_details'))
					total=request.POST.get('total')
					grand_discount=request.POST.get('grand_discount')
					Invoice=purchaseInvoice()
					vendorkey = request.POST.get('vendor')
					change_warehouse=request.POST.get('change_warehouse')
					if (change_warehouse == "true"):
						warehousekey = request.POST.get('warehouse')
					vendor_key = Vendor.objects.for_tenant(this_tenant).get(key__iexact=vendorkey)
					warehouse_object = Warehouse.objects.for_tenant(this_tenant).get(key__iexact=warehousekey)
					Invoice=new_purchase_invoice(this_tenant, vendor_key,warehouse_object, total, grand_discount, date, 0)
					journal=new_journal(this_tenant, date,"Purchase Invoice",Invoice.invoice_id)
					i=2
					value=Decimal(total) - Decimal(grand_discount)
					while (i>0):
						if (i==2):
							account= accountChart.objects.for_tenant(this_tenant).\
										get(name__exact="Inventory")
							journal_entry(this_tenant, journal, value, account, "Debit")
						elif (i==1):
							account= accountChart.objects.for_tenant(this_tenant).\
										get(name__exact="Accounts Payable")
							journal_entry(this_tenant, journal, value, account, "Credit")
						i=i-1
						
					debit = journal.journalEntry_journal.filter(transaction_type="Debit").aggregate(Sum('value'))
					credit = journal.journalEntry_journal.filter(transaction_type="Debit").aggregate(Sum('value'))
					if (debit != credit):
						raise IntegrityError

			#saving the purchaseLineItem and linking them with foreign key to invoice
					for data in bill_data:
						itemcode=data['itemCode']
						subitemcode=data['subitemcode']
						unit_entry=data['unit']
						item=Product.objects.for_tenant(request.user.tenant).get(key__iexact=itemcode)
						subitem=item.subProduct_master_master_product.get(sub_key__iexact=subitemcode)
						unit=Unit.objects.for_tenant(this_tenant).get(symbol__iexact=unit_entry)
						multiplier=unit.multiplier
						invoiceQuantity=int(data['itemQuantity'])*multiplier
						LineItem = purchaseLineItem()
						LineItem.invoice_no = Invoice
						LineItem.product_key= itemcode
						LineItem.subproduct_key= subitemcode						
						LineItem.product_name=item.name						
						LineItem.unit=unit.symbol						
						LineItem.quantity=invoiceQuantity
						LineItem.free=int(data['itemFree'])*multiplier
						LineItem.manufacturer=item.manufacturer.key
						LineItem.cost_price=subitem.cost_price
						LineItem.vat_type=item.vat_type
						LineItem.vat_percent=item.vat_percent
						LineItem.save()
						inventory=Inventory.objects.filter(warehouse=warehouse_object).get(item=subitem)
						inventory.quantity=F('quantity') + invoiceQuantity
						inventory.save()
				except:
					transaction.rollback()

		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	return render(request, 'bill/purchase/purchase.html', {'date':date,'type': type, 'default':warehouse})

#Displaying invoice & updating Payment
@login_required
def purchase_detail(request, type, detail):
	date=datetime.now()
	this_tenant=request.user.tenant
	if (type== 'Detail'):
		call_id=detail.split("-",1)[1]
		if (call_id[:2] == "pi"):
			invoice=purchaseInvoice.objects.for_tenant(this_tenant).select_related().get(invoice_id__iexact=call_id)
			details=invoice.purchaseLineItem_purchaseInvoice.all()
			return render(request, 'bill/purchase/purchase_detail.html',{'items': details, 'invoice':invoice})
		elif (call_id[:2] == "dn"):
			note=debitNote.objects.for_tenant(this_tenant).select_related().get(note_id__iexact=call_id)
			details=note.debitNoteLineItem_debitNote.all()
			return render(request, 'bill/purchase/inventory_return_detail.html',{'items': details, 'note':note})
	elif (type== 'Due'):
		invoice_id=detail.split("-",1)[1]
		invoice=purchaseInvoice.objects.for_tenant(this_tenant)\
			.annotate(balance_due=F('total')-F('grand_discount')-F('amount_paid'))\
			.get(invoice_id__iexact=invoice_id)
		details=invoice.purchaseLineItem_purchaseInvoice.all()
		payment_mode=paymentMode.objects.for_tenant(this_tenant).filter(default="No")
		default_mode=paymentMode.objects.for_tenant(this_tenant).get(default="Yes")
		if request.method == 'POST':
			response_data = {}
			#calltype = request.POST.get('calltype')
			cheque_rtgs_number = request.POST.get('number')
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
						payment=purchasePayment()
						payment.invoice_no=invoice
						payment.payment_mode=payment_mode
						payment.cheque_rtgs_number=cheque_rtgs_number
						payment.amount_paid=current_amount_paid
						payment.collected_on=datetime.now()
						payment.save()
						journal=new_journal(tenant=this_tenant,date=date,\
											journal_type=invoice.invoice_id,group="Purchase Collection")
						i=2
						value=current_amount_paid
						while (i>0):
							if (i==2):
								account= accountChart.objects.for_tenant(request.user.tenant).\
											get(name__exact="Accounts Payable")
								journal_entry(this_tenant, journal, value, account, "Debit")
							elif (i==1):
								journal_entry(this_tenant, journal, value, payment_account, "Credit")
							i=i-1						
				except:
					transaction.rollback()
			jsondata = json.dumps(response_data)
			return HttpResponse(jsondata)
		return render(request, 'bill/purchase/purchase_due.html',\
						{'items': details, 'invoice':invoice, 'payment_modes':payment_mode,\
						'default':default_mode,})

@login_required
#Lists all customer and payment details.
def vendor_due(request, type):
	vendors = Vendor.objects.for_tenant(request.user.tenant).annotate(total=\
		Sum('purchaseInvoice_purchase_master_vendor__total')\
		-Sum('purchaseInvoice_purchase_master_vendor__grand_discount')
		-Sum('purchaseInvoice_purchase_master_vendor__amount_paid'))
	return render(request, 'bill/purchase/vendor_payment_list.html',\
		{'vendors':vendors, 'type': type})

@login_required
#Checks Purchase Inventory Return and saves item
def inventory_return(request):
	date=datetime.now()	
	warehouse=Warehouse.objects.for_tenant(request.user.tenant).get(default="Yes")
	warehousekey=warehouse.key
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		this_tenant=request.user.tenant

		#getting Customer Data
		if (calltype == 'vendor'):
			vendorkey = request.POST.get('vendor_code')
			response_data['name'] = Vendor.objects.for_tenant(this_tenant).get(key__iexact=vendorkey).name

		#getting Watrehouse Data
		elif (calltype == 'warehouse'):
			warehousekey = request.POST.get('warehouse_code')
			response_data['name'] = Warehouse.objects.for_tenant(this_tenant).get(key__iexact=warehousekey).address
					
		#getting item data
		elif (calltype == 'item'):
			productkey = request.POST.get('item_code')
			response_data=item_call(this_tenant, productkey)
			
		#getting subitem data
		elif (calltype == 'subitem'):
			subitem = request.POST.get('subitemcode')
			productkey = request.POST.get('item_code')
			response_data=subitem_call(this_tenant, productkey, subitem)
			
		#This is used to get data if unit changes
		elif (calltype == 'unit'):
			subitem = request.POST.get('subitem_code')
			productkey = request.POST.get('item_code')
			unit_entry= request.POST.get('unit')
			response_data=unit_call(this_tenant, productkey, subitem, unit_entry)
		
		#saving the debi note
		elif (calltype == 'save'):
			with transaction.atomic():
				note_data = json.loads(request.POST.get('note_details'))
				proceed=True
				change_warehouse=request.POST.get('change_warehouse')
				if (change_warehouse == "true"):
					warehousekey = request.POST.get('warehouse')
				warehouse_object = Warehouse.objects.for_tenant(this_tenant).get(key__iexact=warehousekey)
				#Checking available inventory by warehouse
				for data in note_data:
					unit_entry=data['unit']
					inventory_type=data['inventory_type']
					unit=Unit.objects.for_tenant(this_tenant).get(symbol__iexact=unit_entry)
					multiplier=unit.multiplier
					invoiceQuantity=int(data['itemQuantity'])*multiplier
					item=Product.objects.for_tenant(this_tenant).get(key__iexact=data['itemCode'])
					subitem=item.subProduct_master_master_product.get(sub_key__iexact=data['subitemcode'])
					if (inventory_type == "Reusable"):
						productQuantity=subitem.inventory_inventory_master_subproduct.\
										get(warehouse=warehouse_object).quantity
					elif (inventory_type == "Returnable"):
						productQuantity=subitem.returnableinventory_inventory_master_subproduct.\
										get(warehouse=warehouse_object).quantity
					if productQuantity < invoiceQuantity:
						proceed= False
				if proceed:
					try:
						total=request.POST.get('total')
						tax_total=request.POST.get('vat_total')
						call_details = request.POST.get('call_details')
						vendorkey=request.POST.get('vendor')
						vendor_key=Vendor.objects.for_tenant(this_tenant).get(key__iexact=vendorkey)
						debit_note=new_debit_note(this_tenant, vendor_key,\
								warehouse_object, total, tax_total, date, "Goods Return" )
						#The journal type needs to change to Debit Note
						journal=new_journal(this_tenant, date,"Debit Note",debit_note.note_id)
						i=2
						value=Decimal(total)
						while (i>0):
							if (i==2):
								account= accountChart.objects.for_tenant(this_tenant).\
											get(name__exact="Inventory")
								journal_entry(this_tenant, journal, value, account, "Credit")
							elif (i==1):
								if (call_details == "debit"):
									account= accountChart.objects.for_tenant(this_tenant).\
											get(name__exact="Accounts Payable")
								elif (call_details == "refund"):
									account= accountChart.objects.for_tenant(this_tenant).\
											get(name__exact="Cash")
								journal_entry(this_tenant, journal, value, account, "Debit")
							i=i-1
						
						debit = journal.journalEntry_journal.filter(transaction_type="Debit").aggregate(Sum('value'))
						credit = journal.journalEntry_journal.filter(transaction_type="Debit").aggregate(Sum('value'))
						if (debit != credit):
							raise IntegrityError

						#saving the debitnoteLineItem and linking them with foreign key to debit note
						for data in note_data:
							itemcode=data['itemCode']
							subitemcode=data['subitemcode']
							unit_entry=data['unit']
							inventory_type=data['inventory_type']
							item=Product.objects.for_tenant(request.user.tenant).get(key__iexact=itemcode)
							subitem=item.subProduct_master_master_product.get(sub_key__iexact=subitemcode)
							unit=Unit.objects.for_tenant(this_tenant).get(symbol__iexact=unit_entry)
							multiplier=unit.multiplier
							invoiceQuantity=int(data['itemQuantity'])*multiplier
							LineItem = debitNoteLineItem()
							LineItem.debitnote_no = debit_note
							LineItem.product_key= itemcode
							LineItem.subproduct_key= subitemcode						
							LineItem.product_name=item.name						
							LineItem.unit=unit.symbol					
							LineItem.quantity=invoiceQuantity
							LineItem.cost_price=subitem.cost_price
							LineItem.vat_type=item.vat_type
							LineItem.vat_percent=item.vat_percent
							LineItem.inventory_type = inventory_type
							LineItem.save()
							#This will help reduce the inventory, after selecting which inventory to reduce
							if (inventory_type == "Reusable"):
								inventory=Inventory.objects.filter(warehouse=warehouse_object).get(item=subitem)
							elif (inventory_type == "Returnable"):
								inventory=returnableInventory.objects.filter(warehouse=warehouse_object).get(item=subitem)
							inventory.quantity=F('quantity') - invoiceQuantity
							inventory.save()
					except:
						transaction.rollback()
				else:
					response_data['name']= "Sufficient stcok not available"

		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	
	return render(request, 'bill/purchase/inventory_return.html', {'date':date,'type': type, 'warehouse':warehouse})