import datetime as date_first
from decimal import Decimal
import json
import csv

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError, transaction
from django.db.models import Sum, Count
from django.shortcuts import render, redirect
from django.http import HttpResponse


from rest_framework.decorators import api_view
from rest_framework.response import Response

from distributor_master.models import Unit, Service, Customer, Warehouse, service_sales_rate
from distributor_user.models import User
from distributor_inventory.models import Inventory
from distributor_account.models import Account, tax_transaction, account_inventory, account_year_inventory, accounting_period, Journal,journal_entry,\
								journal_inventory, journal_entry_inventory, account_year, payment_mode
from distributor_account.journalentry import new_journal, new_journal_entry
from distributor_inventory.models import Inventory, inventory_ledger, warehouse_valuation
from distributor.variable_list import small_large_limt

from distributor.global_utils import paginate_data, new_tax_transaction_register
# from .sales_utils import *
from .models import *

TWOPLACES = Decimal(10) ** -2

@api_view(['GET',],)
def new_sales_invoice(request):
	return render(request,'service_sales/invoice.html', {'extension': 'base.html'})


@api_view(['GET',],)
def get_payment_mode(request):
	payment_modes=list(payment_mode.objects.for_tenant(request.user.tenant).exclude(name__in=["Vendor Debit", "Customer Credit"]).\
				values('id','name', 'default').order_by('-default'))
	jsondata = json.dumps(payment_modes,  cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

@api_view(['GET',],)
def service_sales_user(request):
	this_tenant = request.user.tenant
	users = list(User.objects.filter(tenant = this_tenant, user_type__contained_by=['service_sales', 'service_sales_lead']).\
		values('id', 'username', 'first_name', 'last_name'))
	jsondata = json.dumps(users,  cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)


@api_view(['GET','POST'],)
def get_product(request):
	this_tenant=request.user.tenant
	if request.method == "GET":
		q = request.GET.get('term', '')
		services = Service.objects.for_tenant(this_tenant).filter(name__icontains  = q )[:10].select_related('default_unit', \
			'cgst', 'sgst')
		response_data = []
		for item in services:
			item_json = {}
			item_json['id'] = item.id
			item_json['label'] = item.name
			item_json['unit_id'] = item.default_unit.id
			item_json['unit'] = item.default_unit.symbol
			item_json['unit_multiplier'] = item.default_unit.multiplier
			# item_json['inventory'] = this_tenant.maintain_inventory
			# item_json['vat_type'] = item.vat_type
			try:
				item_json['cgst'] = item.cgst.percentage
			except:
				item_json['cgst'] = 0
			try:
				item_json['sgst'] = item.sgst.percentage
			except:
				item_json['sgst'] = 0
			response_data.append(item_json)
		data = json.dumps(response_data, cls=DjangoJSONEncoder)
	else:
		data = 'fail'
	mimetype = 'application/json'
	return HttpResponse(data, mimetype)

@api_view(['GET'],)
def get_product_rate(request):
	this_tenant=request.user.tenant
	response_data={}
	if request.method == "GET":
		service_id = request.GET.get('product_id')
		warehouse_id = request.GET.get('warehouse_id')
		# product_quantity=Inventory.objects.for_tenant(this_tenant).filter(quantity_available__gt=0,product=product_id,\
		# 		warehouse=warehouse_id).aggregate(Sum('quantity_available'))['quantity_available__sum']
		service_rate=list(service_sales_rate.objects.for_tenant(this_tenant).filter(service=service_id).\
					values('tentative_sales_rate', 'is_tax_included'))
		service = Service.objects.for_tenant(this_tenant).get(id=service_id)
		try:
			cgst = service.cgst.percentage
		except:
			cgst = 0
		try:
			sgst = service.sgst.percentage
		except:
			sgst = 0

		response_data['rate']=service_rate
		response_data['cgst']=cgst
		response_data['sgst']=sgst
		
	jsondata = json.dumps(response_data,  cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

@api_view(['GET'],)
def get_product_data(request):
	this_tenant=request.user.tenant
	response_data={}
	if request.method == "GET":
		try:
			product_id = request.GET.get('product_id')
			warehouse_id = request.GET.get('warehouse_id')
			
			product_data=Product.objects.for_tenant(this_tenant).get(id=product_id)
			product_quantity=Inventory.objects.for_tenant(this_tenant).filter(quantity_available__gt=0,product=product_data,\
					warehouse=warehouse_id).aggregate(Sum('quantity_available'))['quantity_available__sum']
			product_rate=list(product_sales_rate.objects.for_tenant(this_tenant).filter(product=product_data).\
						values('tentative_sales_rate', 'is_tax_included'))
			

			response_data['quantity']=product_quantity
			response_data['rate']=product_rate
			response_data['product_id']=product_data.id
			response_data['product_name']=product_data.name
			response_data['product_hsn']=product_data.hsn_code
			response_data['unit_id']=product_data.default_unit.id
			response_data['unit']=product_data.default_unit.symbol

			try:
				response_data['cgst'] = product_data.cgst.percentage
			except:
				response_data['cgst'] = 0
			try:
				response_data['sgst'] = product_data.sgst.percentage
			except:
				response_data['sgst'] = 0
		except:
			#Check if json response has any error. If so, display error.
			response_data['error']='Product Does not exist'
	
	jsondata = json.dumps(response_data,  cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)


@api_view(['POST'],)
def sales_invoice_save(request):
	if request.method == 'POST':
		calltype = request.data.get('calltype')
		response_data = {}
		this_tenant=request.user.tenant
		if (calltype == 'save' or calltype == 'mobilesave'):
			try:
				with transaction.atomic():
					date = date_first.date.today()
					if (calltype == 'save'):
						bill_data = json.loads(request.data.get('bill_details'))
					else:
						bill_data = request.data.get('bill_details')
					
					# customer_phone = request.data.get('customer_phone')
					# customer_name = request.data.get('customer_name')
					# customer_address = request.data.get('customer_address')
					# customer_email = request.data.get('customer_email')
					# customer_gender = request.data.get('customer_gender')
					# customer_dob = request.data.get('customer_dob')
					
					warehouse_id=request.data.get('warehouse')
					paymentmode_id=request.data.get('paymentmode')

					if (paymentmode_id):
						payment_mode_selected=payment_mode.objects.for_tenant(this_tenant).get(id=paymentmode_id)
					else:
						payment_mode_selected=payment_mode.objects.for_tenant(this_tenant).get(default=True)
					
					subtotal=Decimal(request.data.get('subtotal')).quantize(TWOPLACES)
					cgsttotal=Decimal(request.data.get('cgsttotal')).quantize(TWOPLACES)
					sgsttotal=Decimal(request.data.get('sgsttotal')).quantize(TWOPLACES)
					total=Decimal(request.data.get('total')).quantize(TWOPLACES)
					try:
						roundoff=Decimal(request.data.get('roundoff')).quantize(TWOPLACES)
					except:
						roundoff = 0
					sum_total = subtotal+cgsttotal+sgsttotal
					
					# round_value = 0
					# if (abs(sum_total - total) <0.90 ):
					# 	round_value = sum_total - total
					
					warehouse = Warehouse.objects.for_tenant(this_tenant).get(id=warehouse_id)
					ware_address=warehouse.address_1+", "+warehouse.address_2
					ware_state=warehouse.state
					ware_city=warehouse.city
					ware_pin=warehouse.pin
					
					new_invoice=service_invoice()
					new_invoice.tenant=this_tenant

					new_invoice.date = date
					
					# new_invoice.customer_name=customer_name
					# new_invoice.customer_phone_no=customer_phone
					# new_invoice.customer_address=customer_address
					# new_invoice.customer_email=customer_email
					# new_invoice.customer_gender=customer_gender
					# new_invoice.customer_dob=customer_dob
					
					new_invoice.warehouse=warehouse
					new_invoice.warehouse_address=ware_address
					new_invoice.warehouse_state=ware_state
					new_invoice.warehouse_city=ware_city
					new_invoice.warehouse_pin=ware_pin
					new_invoice.payment_mode_id=payment_mode_selected.id
					new_invoice.payment_mode_name=payment_mode_selected.name
					
					new_invoice.subtotal=subtotal
					new_invoice.cgsttotal=cgsttotal
					new_invoice.sgsttotal=sgsttotal
					# new_invoice.taxtotal=taxtotal
					
					#This will provide the details, whether this is B2CL or B2CS
					# if (subtotal<small_large_limt):
					# 	new_invoice.gst_type=3
					# else:
					# 	new_invoice.gst_type=2
					

					new_invoice.total = total
					new_invoice.roundoff = roundoff
					new_invoice.amount_paid = total
					new_invoice.save()
					
					# products_cost=0
					
					cgst_paid={}
					sgst_paid={}
					
					cgst_total=0
					sgst_total=0
					
					#Does this tenant maintain inventory?
					maintain_inventory=this_tenant.maintain_inventory
					total_purchase_price=0
					#saving the invoice_line_item and linking them with foreign key to receipt
					for data in bill_data:
						serviceid=data['product_id']
						unitid=data['unit_id']
						
						discount_amount=data['discount_amount']
						line_taxable_total=Decimal(data['taxable_total']).quantize(TWOPLACES)
						line_total=Decimal(data['line_total']).quantize(TWOPLACES)

						cgst_p=Decimal(data['cgst_p']).quantize(TWOPLACES)
						cgst_v=Decimal(data['cgst_v']).quantize(TWOPLACES)
						sgst_p=Decimal(data['sgst_p']).quantize(TWOPLACES)
						sgst_v=Decimal(data['sgst_v']).quantize(TWOPLACES)

						is_tax=data['is_tax']
						if (is_tax == 'true'):
							is_tax = True
						elif(is_tax == 'false' or is_tax == ''):
							is_tax = False

						cgst_total+=cgst_v
						sgst_total+=sgst_v

						service=Service.objects.for_tenant(this_tenant).select_related('cgst', 'sgst').get(id=serviceid)
								
						unit=Unit.objects.for_tenant(this_tenant).get(id=unitid)
						multiplier=unit.multiplier
						
						# original_actual_sales_price=Decimal(data['sales'])
						original_actual_sales_price = Decimal(data['sales_before_tax']).quantize(TWOPLACES)
						actual_sales_price=Decimal(original_actual_sales_price/multiplier)
						
						original_quantity=Decimal(data['quantity']).quantize(TWOPLACES)
						quantity=original_quantity*multiplier
						salespersons_raw = data['salespersons']
						salespersons = {}
						for i in salespersons_raw:
							salesperson = User.objects.get(tenant = this_tenant, id = i['id'])
							# salespersons.append({'id': salesperson.id, salesperson.id : i['cont'], salesperson.id : i['cont'], \
							# 				'name': salesperson.first_name+" "+salesperson.last_name,})
							salespersons[str(salesperson.id)] = i['cont']
							salespersons[str(salesperson.id)+"_name"] = salesperson.first_name+" "+salesperson.last_name

						LineItem = invoice_line_item()
						LineItem.service_invoice = new_invoice
						LineItem.service= service
						LineItem.service_name= service.name
						LineItem.service_sku=service.sku
						LineItem.service_hsn=service.hsn_code
						LineItem.date = date
						LineItem.cgst_percent=cgst_p
						LineItem.cgst_value=cgst_v
						LineItem.sgst_percent=sgst_p
						LineItem.sgst_value=sgst_v
						LineItem.is_tax_included=is_tax
						
						LineItem.unit=unit.symbol
						LineItem.unit_id = unitid
						LineItem.unit_multi=unit.multiplier
						LineItem.quantity=original_quantity
						
						LineItem.sales_price=original_actual_sales_price
						
						LineItem.discount_amount=discount_amount
						
						LineItem.line_before_tax=line_taxable_total
						LineItem.line_total=line_total
						LineItem.user_details = salespersons
						LineItem.tenant=this_tenant
						LineItem.save()

						if (cgst_p in cgst_paid):
							[cgst_p][0]+=cgst_v
							cgst_paid[cgst_p][1]=total
							cgst_paid[cgst_p][2]+=line_taxable_total
						else:
							cgst_paid[cgst_p]=[cgst_v, total, line_taxable_total]
						if (sgst_p in sgst_paid):
							sgst_paid[sgst_p][0]+=sgst_v
							sgst_paid[sgst_p][1]=total
							sgst_paid[sgst_p][2]+=line_taxable_total
						else:
							sgst_paid[sgst_p]=[sgst_v, total, line_taxable_total]
						

					for k,v in cgst_paid.items():
						try:
							if v[2]>0:
								new_tax_transaction_register("CGST",7, k, v[0],v[1],v[2], new_invoice.id, \
									new_invoice.invoice_id, date, this_tenant, False, customer_gst=None, customer_state=ware_state)
						except:
							pass

					for k,v in sgst_paid.items():
						try:
							if v[2]>0:
								new_tax_transaction_register("SGST",7, k, v[0],v[1],v[2], new_invoice.id,\
									new_invoice.invoice_id, date, this_tenant, False, customer_gst=None, customer_state=ware_state)
						except:
							pass

					#One more journal entry for COGS needs to be done
					remarks="Retail Invoice No: "+str(new_invoice.invoice_id)
					journal=new_journal(this_tenant, date,"Sales",remarks, trn_id=new_invoice.id, trn_type=10)
					account= Account.objects.for_tenant(this_tenant).get(name__exact="Sales")
					new_journal_entry(this_tenant, journal, subtotal, account, 2, date)
					if (cgst_total>0):
						account= Account.objects.for_tenant(this_tenant).get(name__exact="CGST Output")
						new_journal_entry(this_tenant, journal, cgst_total, account, 2, date)

					if (sgst_total>0):
						account= Account.objects.for_tenant(this_tenant).get(name__exact="SGST Output")
						new_journal_entry(this_tenant, journal, sgst_total, account, 2, date)

					if (roundoff != 0):
						account= Account.objects.for_tenant(this_tenant).get(name__exact="Rounding Adjustment")
						new_journal_entry(this_tenant, journal, roundoff, account, 2, date)

					# account= Account.objects.for_tenant(this_tenant).get(name__exact="Cash")
					account = payment_mode_selected.payment_account
					new_journal_entry(this_tenant, journal, total, account, 1, date)
					
					debit = journal.journalEntry_journal.filter(transaction_type=1).aggregate(Sum('value'))
					credit = journal.journalEntry_journal.filter(transaction_type=2).aggregate(Sum('value'))

					if (debit != credit):
						if ((debit['value__sum'] - credit['value__sum'])>0.98):
							raise IntegrityError (('Credit and Debit not matching'))


					response_data['pk']=new_invoice.id
					response_data['id']=new_invoice.invoice_id
			except Exception as err:
				response_data  = err.args 
				transaction.rollback()

		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)


@login_required
def invoice_product_detail_view(request, pk):
	return render(request,'service_sales/invoice_product_detail.html', {'extension': 'base.html', 'pk':pk})

@api_view(['GET', 'POST'],)
def invoice_product_details(request, pk):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		invoice=service_invoice.objects.for_tenant(this_tenant).values('id','invoice_id','date', 'warehouse_address','warehouse_city',\
			'warehouse_pin','subtotal','cgsttotal','sgsttotal','total','amount_paid').get(id=pk)
		
		line_items=list(invoice_line_item.objects.filter(service_invoice=invoice['id']).order_by('id').values('id','service_name','service_hsn',\
			'service_id','unit','unit_multi', 'unit_id','quantity','quantity_returned','sales_price','discount_amount','line_before_tax','line_total',\
			'is_tax_included', 'cgst_percent','sgst_percent','igst_percent','cgst_value','sgst_value','igst_value',))
		
		invoice['line_items']=line_items

		invoice['tenant_name']=this_tenant.name
		
		jsondata = json.dumps(invoice, cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)


@login_required
def invoice_service_detail_view(request, pk):
	return render(request,'service_sales/invoice_service_detail.html', {'extension': 'base.html', 'pk':pk})

@api_view(['GET', 'POST'],)
def invoice_service_details(request, pk):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		invoice=service_invoice.objects.for_tenant(this_tenant).values('id','invoice_id','date', 'warehouse_address','warehouse_city',\
			'warehouse_pin','subtotal','cgsttotal','sgsttotal','total','amount_paid').get(id=pk)
		line_items=list(invoice_line_item.objects.filter(service_invoice=invoice['id']).order_by('id').values('id','service_name','service_hsn',\
			'service_id','unit', 'quantity','quantity_returned','user_details',))
		
		invoice['line_items']=line_items

		invoice['tenant_name']=this_tenant.name
		
		jsondata = json.dumps(invoice, cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)


@login_required
def invoice_list(request):
	return render(request,'service_sales/sales_list.html', {'extension': 'base.html'})


@api_view(['GET'],)
def all_invoices(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		calltype = request.GET.get('calltype')
		page_no = request.GET.get('page_no')
		end=date_first.date.today()
		start=end-date_first.timedelta(days=15)
		response_data={}
		filter_data={}
		if (calltype == 'all_invoices'):
			# page_no = request.GET.get('page')
			invoices=service_invoice.objects.for_tenant(this_tenant).filter(date__range=(start,end)).values('id','invoice_id', \
				'date','total', 'cgsttotal','sgsttotal').order_by('-date', '-invoice_id')
			
			filter_summary=list(invoices.values('payment_mode_id', 'payment_mode_name').order_by('payment_mode_id', 'payment_mode_name',).\
							annotate(value = Sum('total')))
			
			# page_no=1
			# paginator = Paginator(invoices, 3)
			# receipts_paginated=paginator.page(page_no)
			# for item in receipts_paginated:
			# 	print(item)
		

		elif (calltype == 'apply_filter'):
			start = request.GET.get('start')
			end = request.GET.get('end')
			invoice_no = request.GET.get('invoice_no')
			payment_mode = request.GET.get('payment_mode')
			# productid=request.GET.get('productid')
			# sent_with=request.GET.get('sent_with')
			returntype=request.GET.get('returntype')
			# payment_status=request.GET.get('payment_status')
			if (start and end):
				invoices = retail_invoice.objects.for_tenant(this_tenant).filter(date__range=(start,end)).values('id','invoice_id', \
				'date','total', 'cgsttotal','sgsttotal').order_by('-date', '-invoice_id')
				# invoices=sales_invoice.objects.for_tenant(this_tenant).filter(date__range=[start,end]).all().\
							# select_related('invoiceLineItem_salesInvoice').\
							# values('id','invoice_id','date','customer_name','total', 'amount_paid', 'payable_by').order_by('-date', '-invoice_id')
			
			if invoice_no:
				invoices=invoices.filter(invoice_id__icontains=invoice_no)

			if payment_mode:
				invoices=invoices.filter(payment_mode_id=payment_mode)
			

			# if productid:
			# 	product=Product.objects.for_tenant(this_tenant).get(id=productid)
			# 	invoices=invoices.filter(invoiceLineItem_salesInvoice__product=product).\
			# 			values('id','invoice_id','date','customer_name','total', 'amount_paid', 'payable_by').order_by('-date', '-invoice_id')

			if (returntype == 'download'):
				invoices = invoices.order_by('customer_name', 'customer', '-date', '-invoice_id')
				context = {
					'invoices': invoices,
					'tenant':this_tenant
				}
				pdf = render_to_pdf('sales/customer_pdf.html', context)
				response = HttpResponse(pdf, content_type='application/pdf')
				filename = "Sales Invoice Summary.pdf" 
				content = "attachment; filename='%s'" %(filename)
				response['Content-Disposition'] = content
				return response
		
			#Update code to check this only if page_no is str(1)

			#Send data details as in how much has been sent by what payment mode 
			
			filter_summary=list(invoices.values('payment_mode_id', 'payment_mode_name').order_by('payment_mode_id', 'payment_mode_name',).\
							annotate(value = Sum('total')))
			filter_data['payment details']=filter_summary
			# filter_data['total_pending'] = filter_summary['pending']
			# filter_data['total_value'] = filter_summary['total_sum']
			# print(filter_summary)
		
		if page_no:
			response_data =  paginate_data(page_no, 10, list(invoices))
			response_data.update(filter_data)
		else:
			response_data['object']=list(invoices)
			response_data.update(filter_data)
	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)


@login_required
def user_service_view(request):
	return render(request,'service_sales/user_wise_sales.html', {'extension': 'base.html'})


@api_view(['GET'],)
def user_service_data(request):
	from django.db.models import Count
	
	this_tenant=request.user.tenant
	if request.method == 'GET':
		calltype = request.GET.get('calltype')
		# page_no = request.GET.get('page_no')
		page_no = None
		user_id = request.GET.get('userid')
		end = request.GET.get('end')
		start = request.GET.get('start')
		response_data={}
		filter_data={}
		
		if (calltype == 'all_invoices'):
			# page_no = request.GET.get('page')
			invoices=service_invoice.objects.for_tenant(this_tenant).filter(date__range=(start,end))
			# filter_summary=list(invoices.values('payment_mode_id', 'payment_mode_name').order_by('payment_mode_id', 'payment_mode_name',).\
			# 				annotate(value = Sum('total')))
			# annotate(contrib = KeyTransform(str(user_id), 'user_details')).\

			line_items = invoice_line_item.objects.for_tenant(this_tenant).filter(service_invoice__in = invoices, user_details__has_key = user_id).\
						select_related('service_invoice').\
						values('service_name', 'unit', 'quantity', 'quantity_returned', 'line_before_tax', 'user_details', 'service_invoice__invoice_id')

			
		elif (calltype == 'service_count'):
			print("In service count")
			# page_no = request.GET.get('page')
			invoices=service_invoice.objects.for_tenant(this_tenant).filter(date__range=(start,end))
			
			line_items = invoice_line_item.objects.for_tenant(this_tenant).filter(service_invoice__in = invoices, user_details__has_key = user_id).\
						values('service_name').annotate(total=Count('service_name')).order_by('service_name')

		
		response_data['object']=list(line_items)
			# response_data.update(filter_data)
	
	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)