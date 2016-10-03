from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import F, Sum
from decimal import *
import json
from datetime import datetime

from .models import purchaseInvoice, purchaseLineItem, purchasePayment
from distribution_master.models import Manufacturer, Product, Zone, Customer, Vendor, Unit, Warehouse
from distribution_inventory.models import Inventory
from distribution_accounts.models import accountChart, Journal, journalEntry, paymentMode
from distribution_user.models import Tenant

#Purchase Invoice Base
@login_required
def purchase_base(request):
		return render(request, 'bill/base/purchase_base.html')


@login_required
#Returns list of all purchase invoices
def purchase_list(request, type):
	items = purchaseInvoice.objects.for_tenant(request.user.tenant).all()
	return render(request, 'master/purchase/purchase_list.html',{'items':items, 'type': type})

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
		
		#getting Customer Data
		if (calltype == 'vendor'):
			vendorkey = request.POST.get('vendor_code')
			response_data['name'] = Vendor.objects.for_tenant(request.user.tenant).get(key__iexact=vendorkey).name

		elif (calltype == 'warehouse'):
			warehousekey = request.POST.get('warehouse_code')
			response_data['name'] = Warehouse.objects.for_tenant(request.user.tenant).get(key__iexact=warehousekey).address
					
		#getting item data
		elif (calltype == 'item'):
			productkey = request.POST.get('item_code')
			item=Product.objects.for_tenant(request.user.tenant).get(key__iexact=productkey)
			response_data['name'] = item.name
			#response_data['purchaseprice'] = float(Product.objects.get(key__iexact=productkey).cost_price)
			if(item.vat_type == 'No VAT'):
				response_data['vat_percent']=0
			else:
				response_data['vat_percent'] = float(item.vat_percent)
			response_data['vat_type']=item.vat_type
		
		#getting subitem data
		elif (calltype == 'subitem'):
			subitem = request.POST.get('subitemcode')
			productkey = request.POST.get('item_code')
			product = Product.objects.for_tenant(request.user.tenant).get(key__iexact=productkey)
			subproducts=product.subProduct_master_master_product.all()
			for subproduct in subproducts:
				if (subitem==subproduct.sub_key):
					response_data['purchaseprice'] = float(subproduct.cost_price)
					response_data['discount1'] = float(subproduct.discount1)
					response_data['discount2'] = float(subproduct.discount2)			

		#saving the invoice
		if (calltype == 'save'):
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
					Invoice.tenant=request.user.tenant
					Invoice.vendor_key = Vendor.objects.for_tenant(request.user.tenant).get(key__iexact=vendorkey)
					warehouse_object = Warehouse.objects.for_tenant(request.user.tenant).get(key__iexact=warehousekey)
					Invoice.warehouse=warehouse_object
					Invoice.total = total
					Invoice.grand_discount = grand_discount
					Invoice.amount_paid = request.POST.get('amount_paid')
				#	Invoice.vendor_name = Vendor.object.get(key__iexact=vendorkey).name
				#	Invoice.address = Vendor.object.get(key__iexact=vendorkey).address
					Invoice.date = date
					Invoice.save()
					journal=Journal()
					journal.tenant=request.user.tenant
					journal.date=date
					journal.journal_type="purchase_invoice"
					journal.key=Invoice.invoice_id
					journal.save()
					i=2
					while (i>0):
						entry=journalEntry()
						entry.tenant=request.user.tenant
						entry.journal=journal
						entry.value=Decimal(total) - Decimal(grand_discount)
						if (i==2):
							entry.account= accountChart.objects.for_tenant(request.user.tenant).\
										get(name__exact="Inventory")
							entry.transaction_type = "Debit"
						elif (i==1):
							entry.account= accountChart.objects.for_tenant(request.user.tenant).\
										get(name__exact="Accounts Payable")
							entry.transaction_type = "Credit"
						entry.save()						
						i=i-1
						
					debit = journal.journalEntry_journal.filter(transaction_type="Debit").aggregate(Sum('value'))
					credit = journal.journalEntry_journal.filter(transaction_type="Debit").aggregate(Sum('value'))
					if (debit != credit):
						raise IntegrityError

			#saving the salesLineItem and linking them with foreign key to invoice
					for data in bill_data:
						LineItem = purchaseLineItem()
						LineItem.invoice_no = Invoice
						itemcode=data['itemCode']
						subitemcode=data['subitemcode']
						LineItem.product_key= itemcode
						LineItem.subproduct_key= subitemcode
						item=Product.objects.for_tenant(request.user.tenant).get(key__iexact=itemcode)
						subitem=item.subProduct_master_master_product.get(sub_key__iexact=subitemcode)
						LineItem.product_name=item.name
						LineItem.unit=item.unit
				#		LineItem.batch=Product.object.get(key__iexact=itemcode).batch
				#		LineItem.discount1=Product.object.get(key__iexact=itemcode).discount1
				#		LineItem.discount2=Product.object.get(key__iexact=itemcode).discount2
						LineItem.quantity=int(data['itemQuantity'])
						LineItem.free=int(data['itemFree'])
						LineItem.manufacturer=item.manufacturer.key
				#		LineItem.mrp=Product.object.get(key__iexact=itemcode).mrp
						LineItem.cost_price=subitem.cost_price
						LineItem.vat_type=item.vat_type
						LineItem.vat_percent=item.vat_percent
						LineItem.save()
						inventory=Inventory.objects.filter(warehouse=warehouse_object).get(item=subitem)
						invoiceQuantity=int(data['itemQuantity'])
						inventory.quantity=F('quantity') + invoiceQuantity
						inventory.save()
				except:
					transaction.rollback()


				#this part is just for checking
				#response_data['name'] = Product.object.get(key__iexact=itemcode).name

		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	#return render(request, 'bill/purchaseinvoice.html', {'date':date,'type': type})
	return render(request, 'bill/purchase/purchase.html', {'date':date,'type': type, 'default':warehouse})


@login_required
def purchase_detail(request, type, detail):
	date=datetime.now()
	if (type== 'Detail'):
		invoice_id=detail.split("-",1)[1]
		invoice=purchaseInvoice.objects.for_tenant(request.user.tenant).get(invoice_id__iexact=invoice_id)
		details=invoice.purchaseLineItem_purchaseInvoice.all()
		return render(request, 'bill/purchase/purchase_detail.html',{'items': details, 'invoice':invoice})
	elif (type== 'Due'):
		invoice_id=detail.split("-",1)[1]
		invoice=purchaseInvoice.objects.for_tenant(request.user.tenant)\
			.annotate(balance_due=F('total')-F('grand_discount')-F('amount_paid'))\
			.get(invoice_id__iexact=invoice_id)
		details=invoice.purchaseLineItem_purchaseInvoice.all()
		payment_mode=paymentMode.objects.for_tenant(request.user.tenant).filter(default="No")
		default_mode=paymentMode.objects.for_tenant(request.user.tenant).get(default="Yes")
		if request.method == 'POST':
			response_data = {}
			calltype = request.POST.get('calltype')
			current_amount_paid = Decimal(request.POST.get('amount_paid'))
			payment_mode=paymentMode.objects.for_tenant(request.user.tenant).\
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
						payment.amount_paid=current_amount_paid
						payment.collected_on=datetime.now()
						payment.save()
						journal=Journal()
						journal.tenant=request.user.tenant
						journal.date=date
						journal.journal_type="sales_collection invoice: " + invoice.invoice_id
						journal.save()
						i=2
						while (i>0):
							entry=journalEntry()
							entry.tenant=request.user.tenant
							entry.journal=journal
							entry.value=current_amount_paid
							if (i==2):
								entry.account= accountChart.objects.for_tenant(request.user.tenant).\
											get(name__exact="Accounts Payable")
								entry.transaction_type = "Debit"
							elif (i==1):
								entry.account= payment_account
								entry.transaction_type = "Debit"
							entry.save()						
							i=i-1						
						#debit = journal.journalEntry_journal.filter(transaction_type="Debit").aggregate(Sum('value'))
						#credit = journal.journalEntry_journal.filter(transaction_type="Credit").aggregate(Sum('value'))
						#if (debit != credit):
						#	raise IntegrityError
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