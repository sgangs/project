from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import F, Sum
from decimal import *
import json
from datetime import datetime

from .models import purchaseInvoice, purchaseLineItem
from distribution_master.models import Manufacturer, Product, Zone, Customer, Vendor, Unit
from distribution_inventory.models import Inventory
from distribution_accounts.models import accountChart, Journal, journalEntry
from distribution_user.models import Tenant

#Purchase Invoice Base
def purchase_base(request):
		return render(request, 'bill/base/purchase_base.html')


@login_required
#Returns list of all purchase invoices
def purchase_list(request, type):
	items = purchaseInvoice.objects.for_tenant(request.user.tenant).all()
	return render(request, 'master/purchase/purchase_list.html',{'items':items, 'type': type})

@login_required
#This view helps in creating & thereafter saving a purchase invoice
def purchaseinvoice(request, type):
	date=datetime.now()	
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		
		#getting Customer Data
		if (calltype == 'vendor'):
			vendorkey = request.POST.get('vendor_code')
			response_data['name'] = Vendor.objects.for_tenant(request.user.tenant).get(key__iexact=vendorkey).name
					
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
					Invoice.tenant=request.user.tenant
					Invoice.vendor_key = Vendor.objects.for_tenant(request.user.tenant).get(key__iexact=vendorkey)
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
						inventory=Inventory.objects.get(item=subitem)
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
	return render(request, 'bill/purchase/purchase.html', {'date':date,'type': type})


@login_required
def purchase_detail(request, type, detail):
	#search for the clicked item details one after other and then get the item details and authorize or unauthorize them
	invoice_id=detail.split("-",1)[1]
	invoice=purchaseInvoice.objects.for_tenant(request.user.tenant).get(invoice_id__iexact=invoice_id)
	#The next line gets the lineitem details of the onvoice
	details=invoice.purchaseLineItem_purchaseInvoice.all()
	#vendorkey=str(invoice.vendor_key_id)
	#vendorname=Vendor.objects.get(key__iexact=vendorkey).name
	vendorname=invoice.vendor_key.name
	#if (type== 'Authorize'):
	#	if request.method == 'POST':
	#		calltype = request.POST.get('calltype')
	#		response_data = {}
	#		if (calltype == 'Authorized'):
	#			emr.status="Authorized"
	#			comment = request.POST.get('comment')
	#			if (comment!= ''):
	#				emr.comment=comment
	#				response_data['note']='EMR Authorized successfully'
	#				emr.save()
	#			else:
	#				response_data['note']="Comment cannot be blank"
	#		if (calltype == 'Not Authorized'):
	#			emr.status="Not Authorized"
	#			comment = request.POST.get('comment')
	#			if (comment!= ''):
	#				emr.comment=comment
	#				response_data['note']='EMR un-authorized request noted'
	#				emr.save()
	#			else:
	#				response_data['note']="Comment cannot be blank"
	#		jsondata = json.dumps(response_data)
	#		return HttpResponse(jsondata)
	#	return render(request, 'project/bill/emr_auth.html',{'items': details, 'emr':emr})
	if (type== 'Detail'):
		#status=emr.status
		return render(request, 'bill/purchase/purchase_detail.html',{'items': details, 'invoice':invoice, 'vendor': vendorname})


