import datetime as date_first
from decimal import Decimal

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError, transaction
from django.db.models import Sum, Count
from django.shortcuts import render
from django.http import HttpResponse
import json

from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from distributor_master.models import Unit, Product, Customer, Warehouse, product_sales_rate
from distributor_inventory.models import Inventory
from distributor_account.models import Account, tax_transaction, account_inventory, account_year_inventory, accounting_period
from distributor_account.journalentry import new_journal, new_journal_entry
from distributor_inventory.models import Inventory, inventory_ledger, warehouse_valuation

from .sales_utils import *
from .models import *


@login_required
def new_sales_invoice(request):
	return render(request,'retail_sales/invoice.html', {'extension': 'base.html'})


@api_view(['GET','POST'],)
def get_product(request):
	this_tenant=request.user.tenant
	if request.is_ajax():
		q = request.GET.get('term', '')
		products = Product.objects.for_tenant(this_tenant).filter(name__icontains  = q )[:10].select_related('default_unit', \
			'cgst', 'sgst')
		response_data = []
		for item in products:
			item_json = {}
			item_json['id'] = item.id
			item_json['label'] = item.name
			item_json['unit_id'] = item.default_unit.id
			item_json['unit'] = item.default_unit.symbol
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
		data = json.dumps(response_data)
	else:
		data = 'fail'
	mimetype = 'application/json'
	return HttpResponse(data, mimetype)

@api_view(['GET'],)
def get_product_inventory(request):
	this_tenant=request.user.tenant
	response_data={}
	if request.is_ajax():
		product_id = request.GET.get('product_id')
		warehouse_id = request.GET.get('warehouse_id')
		product_quantity=Inventory.objects.for_tenant(this_tenant).filter(quantity_available__gt=0,product=product_id,\
				warehouse=warehouse_id).aggregate(Sum('quantity_available'))['quantity_available__sum']
		product_rate=list(product_sales_rate.objects.for_tenant(this_tenant).filter(product=product_id).\
					values('tentative_sales_rate', 'is_tax_included'))

		response_data['quantity']=product_quantity
		response_data['rate']=product_rate
	
	jsondata = json.dumps(response_data,  cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

@api_view(['GET'],)
def get_product_barcode(request):
	this_tenant=request.user.tenant
	response_data={}
	if request.method == 'GET':
		try:
			product_barcode = request.GET.get('product_barcode')
			warehouse_id = request.GET.get('warehouse_id')

			product_data=Product.objects.for_tenant(this_tenant).get(barcode  = product_barcode)
			product_quantity=Inventory.objects.for_tenant(this_tenant).filter(quantity_available__gt=0,product=product_data,\
					warehouse=warehouse_id).aggregate(Sum('quantity_available'))['quantity_available__sum']
			product_rate=list(product_sales_rate.objects.for_tenant(this_tenant).filter(product=product_data).\
						values('tentative_sales_rate', 'is_tax_included'))
			

			response_data['quantity']=product_quantity
			response_data['rate']=product_rate
			response_data['product_id']=product_data.id
			response_data['product_name']=product_data.name
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
		if (calltype == 'save'):
			with transaction.atomic():
				try:
					date = date_first.date.today()
					bill_data = json.loads(request.data.get('bill_details'))
					print(request.data)
					# new_invoice=new_sales_invoice(this_tenant, request, 0)
					
					customer_phone = request.data.get('customer_phone')
					customer_name = request.data.get('customer_name')
					customer_address = request.data.get('customer_address')
					customer_email = request.data.get('customer_email')
					customer_gender = request.data.get('customer_gender')
					customer_dob = request.data.get('customer_dob')
					
					warehouse_id=request.data.get('warehouse')
					
					subtotal=Decimal(request.data.get('subtotal'))
					cgsttotal=Decimal(request.data.get('cgsttotal'))
					sgsttotal=Decimal(request.data.get('sgsttotal'))
					
					total=Decimal(request.data.get('total'))
					warehouse = Warehouse.objects.for_tenant(this_tenant).get(id=warehouse_id)


					ware_address=warehouse.address_1+", "+warehouse.address_2
					ware_state=warehouse.state
					ware_city=warehouse.city
					ware_pin=warehouse.pin
					
					new_invoice=retail_invoice()
					new_invoice.tenant=this_tenant

					new_invoice.date = date
					
					new_invoice.customer_name=customer_name
					new_invoice.customer_phone_no=customer_phone
					new_invoice.customer_address=customer_address
					new_invoice.customer_email=customer_email
					new_invoice.customer_gender=customer_gender
					new_invoice.customer_dob=customer_dob
					
					new_invoice.warehouse=warehouse
					new_invoice.warehouse_address=ware_address
					new_invoice.warehouse_state=ware_state
					new_invoice.warehouse_city=ware_city
					new_invoice.warehouse_pin=ware_pin
					
					new_invoice.subtotal=subtotal
					new_invoice.cgsttotal=cgsttotal
					new_invoice.sgsttotal=sgsttotal
					# new_invoice.taxtotal=taxtotal
					new_invoice.total = total
					new_invoice.amount_paid = total
					new_invoice.save()
					
					products_cost=0
					
					vat_paid={}
					cgst_paid={}
					sgst_paid={}
					
					cgst_total=0
					sgst_total=0
					
					#Does this tenant maintain inventory?
					maintain_inventory=this_tenant.maintain_inventory
					total_purchase_price=0
					#saving the invoice_line_item and linking them with foreign key to receipt
					for data in bill_data:
						productid=data['product_id']
						unitid=data['unit_id']
						price_list={}

						try:
							batch=data['batch']
							manufacturing_date=data['manufacturing_date']
							expiry_date=data['expiry_date']
						except:
							batch=''
							manufacturing_date=''
							expiry_date=''
						try:
							serial_no=data['serial_no']
						except:
							serial_no=''

						discount_amount=data['discount_amount']
						# line_taxable_total=Decimal(data['taxable_total'])
						line_total=Decimal(data['line_total'])

						cgst_p=Decimal(data['cgst_p'])
						cgst_v=Decimal(data['cgst_v'])
						sgst_p=Decimal(data['sgst_p'])
						sgst_v=Decimal(data['sgst_v'])

						cgst_total+=cgst_v
						sgst_total+=sgst_v

						product=Product.objects.for_tenant(this_tenant).select_related('tax').get(id=productid)
								
						unit=Unit.objects.for_tenant(this_tenant).get(id=unitid)
						multiplier=unit.multiplier
						
						original_actual_sales_price=Decimal(data['sales'])
						actual_sales_price=Decimal(original_actual_sales_price/multiplier)
						
						original_quantity=int(data['quantity'])
						quantity=original_quantity*multiplier
						if maintain_inventory:
							product_list=Inventory.objects.for_tenant(this_tenant).filter(quantity_available__gt=0,\
									product=productid, warehouse=warehouse,).order_by('purchase_date')
							quantity_updated=quantity
							i=0
							for item in product_list:
								i+=1
								if (quantity_updated<1):
									break
								original_available=item.quantity_available
								if (quantity_updated>=original_available):
									item.quantity_available=0
									products_cost+=item.purchase_price*original_available
									item.save()
									price_list[i]={'date':item.purchase_date,\
												'quantity':original_available, 'pur_rate':item.purchase_price}
									total_purchase_price+=original_available*item.purchase_price
									quantity_updated-=original_available
									
								else:
									item.quantity_available-=quantity_updated
									products_cost+=item.purchase_price*quantity_updated
									item.save()
									price_list[i]={'date':item.purchase_date,\
												'quantity':quantity_updated, 'pur_rate':item.purchase_price}
									total_purchase_price+=quantity_updated*item.purchase_price
									quantity_updated=0								
							if (quantity_updated>0):
								raise IntegrityError
							price_list_json = json.dumps(price_list,  cls=DjangoJSONEncoder)

						LineItem = invoice_line_item()
						LineItem.retail_invoice = new_invoice
						LineItem.product= product
						LineItem.product_name= product.name
						LineItem.product_sku=product.sku
						LineItem.date = date
						LineItem.cgst_percent=cgst_p
						LineItem.cgst_value=cgst_v
						LineItem.sgst_percent=sgst_p
						LineItem.sgst_value=sgst_v
						
						LineItem.unit=unit.symbol
						LineItem.unit_id=unitid
						LineItem.unit_multi=unit.multiplier
						LineItem.quantity=original_quantity
						if (product.has_batch):
							LineItem.batch=batch
							LineItem.manufacturing_date=manufacturing_date
							LineItem.expiry_date=expiry_date
						if (product.has_instance):
							LineItem.serial_no=serial_no
						
						LineItem.sales_price=original_actual_sales_price
						
						if maintain_inventory:
							LineItem.other_data=price_list_json
						LineItem.discount_amount=discount_amount
						LineItem.line_before_tax=line_total - cgst_v - sgst_v
						LineItem.line_total=line_total
						LineItem.tenant=this_tenant
						LineItem.save()

						if maintain_inventory:						
							#Update this. Need to include purchase price here. For each purchase price there will be a ledger entry
							for k,v in price_list.items():
								new_inventory_ledger=inventory_ledger()
								new_inventory_ledger.product=product
								new_inventory_ledger.warehouse=warehouse
								new_inventory_ledger.transaction_type=9
								new_inventory_ledger.date=date
								new_inventory_ledger.quantity=v['quantity']
								new_inventory_ledger.actual_sales_price=actual_sales_price
								new_inventory_ledger.purchase_price=v['pur_rate']
								new_inventory_ledger.transaction_bill_id=new_invoice.invoice_id
								new_inventory_ledger.tenant=this_tenant
								new_inventory_ledger.save()
							
							warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).get(warehouse=warehouse)
							warehouse_valuation_change.valuation-=total_purchase_price
							warehouse_valuation_change.save()

						if (cgst_p in sgst_paid):
							cgst_paid[cgst_p]+=cgst_v
						else:
							cgst_paid[cgst_p]=cgst_v
						if (sgst_p in sgst_paid):
							sgst_paid[sgst_p]+=sgst_v
						else:
							sgst_paid[sgst_p]=sgst_v
						

					for k,v in cgst_paid.items():
						if v>0:
							new_tax_transaction=tax_transaction()
							new_tax_transaction.transaction_type=5
							new_tax_transaction.tax_type="CGST"
							new_tax_transaction.tax_percent=k
							new_tax_transaction.tax_value=v
							new_tax_transaction.transaction_bill_id=new_invoice.id
							new_tax_transaction.transaction_bill_no=new_invoice.invoice_id
							new_tax_transaction.date=date
							new_tax_transaction.tenant=this_tenant
							new_tax_transaction.save()

					for k,v in sgst_paid.items():
						if v>0:
							new_tax_transaction=tax_transaction()
							new_tax_transaction.transaction_type=5
							new_tax_transaction.tax_type="SGST"
							new_tax_transaction.tax_percent=k
							new_tax_transaction.tax_value=v
							new_tax_transaction.transaction_bill_id=new_invoice.id
							new_tax_transaction.transaction_bill_no=new_invoice.invoice_id
							new_tax_transaction.date=date
							new_tax_transaction.tenant=this_tenant
							new_tax_transaction.save()

					#One more journal entry for COGS needs to be done
					remarks="Retail Invoice No: "+str(new_invoice.invoice_id)
					journal=new_journal(this_tenant, date,"Sales",remarks, trn_id=new_invoice.id, trn_type=7)
					account= Account.objects.for_tenant(this_tenant).get(name__exact="Sales")
					new_journal_entry(this_tenant, journal, subtotal, account, 2, date)
					
					if (cgst_total>0):
						account= Account.objects.for_tenant(this_tenant).get(name__exact="CGST Output")
						new_journal_entry(this_tenant, journal, cgst_total, account, 2, date)

					if (sgst_total>0):
						account= Account.objects.for_tenant(this_tenant).get(name__exact="SGST Output")
						new_journal_entry(this_tenant, journal, sgst_total, account, 2, date)

					account= Account.objects.for_tenant(this_tenant).get(name__exact="Cash")
					new_journal_entry(this_tenant, journal, total, account, 1, date)
					
					debit = journal.journalEntry_journal.filter(transaction_type=1).aggregate(Sum('value'))
					credit = journal.journalEntry_journal.filter(transaction_type=2).aggregate(Sum('value'))

					if (debit != credit):
						if ((debit['value__sum'] - credit['value__sum'])>0.98):
							raise IntegrityError

					if maintain_inventory:
						#COGS Journal Entry
						# if (total_purchase_price<1):
						# 	raise IntegrityError
						# journal=new_journal(this_tenant, date,"Sales",remarks, trn_id=new_invoice.id, trn_type=7)
						# account= Account.objects.for_tenant(this_tenant).get(name__exact="Cost of Goods Sold")
						# new_journal_entry(this_tenant, journal, total_purchase_price, account, 1, date)
						# account= Account.objects.for_tenant(this_tenant).get(name__exact="Inventory")
						# new_journal_entry(this_tenant, journal, total_purchase_price, account, 2, date)
						# debit = journal.journalEntry_journal.filter(transaction_type=1).aggregate(Sum('value'))
						# credit = journal.journalEntry_journal.filter(transaction_type=2).aggregate(Sum('value'))
						# if (debit != credit):
						# 	raise IntegrityError

						inventory_acct=account_inventory.objects.for_tenant(this_tenant).get(name__exact="Inventory")
						acct_period=accounting_period.objects.for_tenant(this_tenant).get(start__lte=date, end__gte=date)
						inventory_acct_year=account_year_inventory.objects.for_tenant(this_tenant).\
											get(account_inventory=inventory_acct, accounting_period = acct_period)
						inventory_acct_year.current_debit-=total_purchase_price
						inventory_acct_year.save()

						inventory_acct=account_inventory.objects.for_tenant(this_tenant).get(name__exact="Cost of Goods Sold")
						acct_period=accounting_period.objects.for_tenant(this_tenant).get(start__lte=date, end__gte=date)
						inventory_acct_year=account_year_inventory.objects.for_tenant(this_tenant).\
											get(account_inventory=inventory_acct, accounting_period = acct_period)
						inventory_acct_year.current_debit+=total_purchase_price
						inventory_acct_year.save()


					response_data=new_invoice.id
				except:
					transaction.rollback()

		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)


@api_view(['GET', 'POST'],)
def invoice_details(request, pk):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		invoice=retail_invoice.objects.for_tenant(this_tenant).values('id','invoice_id','date','customer_name',\
			'warehouse_address','warehouse_city', 'warehouse_pin','subtotal','cgsttotal','sgsttotal',\
		'total','amount_paid').get(id=pk)
		
		line_items=list(invoice_line_item.objects.filter(retail_invoice=invoice['id']).values('product_name',\
			'unit','unit_multi','quantity','sales_price','discount_amount','line_before_tax','line_total',\
			'cgst_percent','sgst_percent','igst_percent','cgst_value','sgst_value','igst_value',))
		invoice['line_items']=line_items

		invoice['tenant_name']=this_tenant.name
		
		jsondata = json.dumps(invoice, cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)

@login_required
def invoice_detail_view(request, pk):
	return render(request,'retail_sales/retail_invoice_detail.html', {'extension': 'base.html', 'pk':pk})

@login_required
def invoice_list(request):
	return render(request,'retail_sales/sales_list.html', {'extension': 'base.html'})

@api_view(['GET'],)
def all_invoices(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		calltype = request.GET.get('calltype')
		end=date_first.date.today()
		start=end-date_first.timedelta(days=15)
		if (calltype == 'all_invoices'):
			# page_no = request.GET.get('page')
			invoices=retail_invoice.objects.for_tenant(this_tenant).filter(date__range=(start,end)).values('id','invoice_id', \
				'date','total', 'cgsttotal','sgsttotal').order_by('-date', '-invoice_id')
			# page_no=1
			# paginator = Paginator(invoices, 3)
			# receipts_paginated=paginator.page(page_no)
			# for item in receipts_paginated:
			# 	print(item)
		elif (calltype== 'customer_pending'):
			customerid = request.GET.get('customerid')
			invoices=sales_invoice.objects.for_tenant(this_tenant).filter(customer=customerid).\
				values('id','invoice_id','date','customer_name','total', 'amount_paid', 'payable_by')
		response_data = list(invoices)		
		
	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)