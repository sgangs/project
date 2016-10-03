from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import F, Sum
import json
from datetime import datetime
from decimal import *

from .models import salesInvoice,salesLineItem, salesPayment
from distribution_master.models import Manufacturer, Product, Zone, Customer, Vendor, Unit, Warehouse
from distribution_accounts.models import accountChart, Journal, journalEntry, paymentMode
from distribution_inventory.models import Inventory


@login_required
#Purchase Invoice Base
def sales_base(request):
	return render(request, 'bill/base/sales_base.html')

@login_required
#Lists all sales invoice
def sales_list(request, type):
	items = salesInvoice.objects.for_tenant(request.user.tenant).all()
	return render(request, 'master/sales/sales_list.html',{'items':items, 'type': type})

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
		
		#getting Customer Data
		if (calltype == 'customer'):
			customerkey = request.POST.get('customer_code')
			response_data['name'] = Customer.objects.for_tenant(request.user.tenant).get(key__iexact=customerkey).name
					
		#getting item data
		elif (calltype == 'item'):
			productkey = request.POST.get('item_code')
			product=Product.objects.for_tenant(request.user.tenant).get(key__iexact=productkey)
			response_data['name'] = product.name
			if(product.vat_type == 'No VAT'):
				response_data['vat_percent']=0
			else:
				response_data['vat_percent'] = float(product.vat_percent)
			response_data['vat_type']=product.vat_type
		
		#getting subitem data
		elif (calltype == 'subitem'):
			subitem = request.POST.get('subitem_code')
			productkey = request.POST.get('item_code')
			product = Product.objects.for_tenant(request.user.tenant).get(key__iexact=productkey)
			subproducts=product.subProduct_master_master_product.all()
			for subproduct in subproducts:
				if (subitem==subproduct.sub_key):
					response_data['salesprice'] = float(subproduct.selling_price)
					response_data['discount1'] = float(subproduct.discount1)
					response_data['discount2'] = float(subproduct.discount2)	

			#saving the invoice
		if (calltype == 'save'):
			with transaction.atomic():
				bill_data = json.loads(request.POST.get('bill_details'))
				proceed=True
				change_warehouse=request.POST.get('change_warehouse')
				if (change_warehouse == "true"):
					warehousekey = request.POST.get('warehouse')
				warehouse_object = Warehouse.objects.for_tenant(request.user.tenant).get(key__iexact=warehousekey)
				#Checking available inventory by warehouse
				for data in bill_data:
					invoiceQuantity=int(data['itemQuantity'])
					item=Product.objects.for_tenant(request.user.tenant).get(key__iexact=data['itemCode'])
					subitem=item.subProduct_master_master_product.get(sub_key__iexact=data['subitemCode'])
					productQuantity=subitem.inventory_inventory_master_subproduct.get(warehouse=warehouse_object).quantity
					if productQuantity < invoiceQuantity:
						proceed= False
				if proceed:
					try:
						Invoice=salesInvoice()
						payment=salesPayment()
						total= request.POST.get('total')
						grand_discount=request.POST.get('grand_discount')
						Invoice.tenant=request.user.tenant
						customerkey = request.POST.get('customer')	
						Invoice.customer = Customer.objects.for_tenant(request.user.tenant).get(key__iexact=customerkey)
						Invoice.warehouse=warehouse_object
						Invoice.total = total
						Invoice.grand_discount = grand_discount
						Invoice.date = date
						Invoice.save()
						payment.invoice_no=Invoice
						payment.amount_paid=0
						payment.save()
						journal=Journal()
						journal.tenant=request.user.tenant
						journal.date=date
						journal.journal_type="sales_invoice"
						journal.key=Invoice.invoice_id
						journal.save()
						i=4
						while (i>0):
							entry=journalEntry()
							entry.tenant=request.user.tenant
							entry.journal=journal
							entry.value=Decimal(total) - Decimal(grand_discount)
							if (i==4):
								entry.account= accountChart.objects.for_tenant(request.user.tenant).\
											get(name__exact="Accounts Receivable")
								entry.transaction_type = "Debit"
							elif (i==3):
								entry.account= accountChart.objects.for_tenant(request.user.tenant).\
											get(name__exact="Sales")
								entry.transaction_type = "Credit"
							elif (i==2):
								entry.account= accountChart.objects.for_tenant(request.user.tenant).\
											get(name__exact="Cost of Goods Sold")
								entry.transaction_type = "Debit"
							elif (i==1):
								entry.account= accountChart.objects.for_tenant(request.user.tenant).\
											get(name__exact="Inventory")
								entry.transaction_type = "Credit"
							entry.save()						
							i=i-1						
						debit = journal.journalEntry_journal.filter(transaction_type="Debit").aggregate(Sum('value'))
						credit = journal.journalEntry_journal.filter(transaction_type="Debit").aggregate(Sum('value'))
						if (debit != credit):
							raise IntegrityError
						#saving the salesLineItem and linking them with foreign key to invoice
						for data in bill_data:
							LineItem = salesLineItem()
							LineItem.invoice_no = Invoice
							itemcode=data['itemCode']
							subitemcode=data['subitemCode']
							LineItem.key= itemcode
							LineItem.sub_key= subitemcode
							item=Product.objects.for_tenant(request.user.tenant).get(key__iexact=itemcode)
							subitem=item.subProduct_master_master_product.get(sub_key__iexact=subitemcode)
							LineItem.name=item.name
							LineItem.unit=item.unit
							LineItem.discount1=subitem.discount1
							LineItem.discount2=subitem.discount2
							LineItem.quantity=int(data['itemQuantity'])
							LineItem.free=int(data['itemFree'])
							LineItem.manufacturer=item.manufacturer.key
							LineItem.mrp=subitem.mrp
							LineItem.selling_price=subitem.selling_price
							LineItem.vat_type=item.vat_type
							LineItem.vat_percent=item.vat_percent
							LineItem.save()
							inventory=Inventory.objects.filter(warehouse=warehouse_object).get(item=subitem)
							invoiceQuantity=int(data['itemQuantity'])
							inventory.quantity=F('quantity') - invoiceQuantity
							inventory.save()
					except:
						transaction.rollback()
				else:
					response_data['name']= "Sufficient stcok not available"
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'bill/sales/sales.html', {'date':date,'type': type, 'warehouse':warehouse})

@login_required
def sales_detail(request, type, detail):
	date=datetime.now()
	#search for the clicked item details then get the item details and get dues from customers
	#Note this line has an issue as annotate goes over all elements, instead on just the necessary one.
	if (type== 'Detail'):
		invoice_id=detail.split("-",1)[1]
		invoice=salesInvoice.objects.for_tenant(request.user.tenant).get(invoice_id__iexact=invoice_id)
		details=invoice.salesLineItem_sales_sales_salesInvoice.all()
		return render(request, 'bill/sales/sales_detail.html',{'items': details, 'invoice':invoice})
	elif (type== 'Due'):
		invoice_id=detail.split("-",1)[1]
		invoice=salesInvoice.objects.for_tenant(request.user.tenant)\
			.annotate(balance_due=F('total')-F('grand_discount')-F('amount_paid'))\
			.get(invoice_id__iexact=invoice_id)
		details=invoice.salesLineItem_sales_sales_salesInvoice.all()
		payment_mode=paymentMode.objects.for_tenant(request.user.tenant).filter(default="No")
		default_mode=paymentMode.objects.for_tenant(request.user.tenant).get(default="Yes")
		if request.method == 'POST':
			response_data = {}
			calltype = request.POST.get('calltype')
			current_amount_paid = Decimal(request.POST.get('amount_paid'))
			payment_mode=paymentMode.objects.for_tenant(request.user.tenant).\
						get(name__exact=request.POST.get('payment_mode'))
			payment_account=payment_mode.payment_account
			total_due=invoice.total-invoice.grand_discount-total_payment['paid']
			with transaction.atomic():
				try:
					#I forgor why I used the first filter in if, need to confirm this
					if(current_amount_paid>0 and current_amount_paid>total_due):
						response_data['name']= "Paid amount cannot be more than due amount"
					else:
						amount_already_paid=invoice.amount_paid
						invoice.amount_paid=amount_already_paid+current_amount_paid
						invoice.save()
						payment=salesPayment()
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
											get(name__exact="Accounts Receivable")
								entry.transaction_type = "Credit"
							elif (i==1):
								entry.account= payment_account
								entry.transaction_type = "Credit"
							entry.save()						
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