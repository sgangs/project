import datetime as date_first
from decimal import Decimal
import json


from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError, transaction
from django.db.models import Sum, Count, F
from django.shortcuts import render, redirect
from django.template import Context
from django.http import HttpResponse

from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from distributor_master.models import Unit, Product, Customer, Warehouse
from distributor_inventory.models import Inventory
from distributor_account.models import Account, tax_transaction, payment_mode, accounting_period,\
									account_inventory, account_year_inventory, journal_inventory, journal_entry_inventory
from distributor_account.journalentry import new_journal, new_journal_entry
from distributor_inventory.models import Inventory, inventory_ledger, warehouse_valuation
from distributor.variable_list import small_large_limt

from distributor.global_utils import paginate_data, new_tax_transaction_register, render_to_pdf
from .sales_utils import *
from .models import *
from .serializers import *
from .excel_download import *


@api_view(['GET','POST'],)
def get_product(request):
	this_tenant=request.user.tenant
	if request.method == "GET":
		q = request.GET.get('term', '')
		products = Product.objects.for_tenant(this_tenant).filter(name__icontains  = q )[:10].select_related('default_unit', \
			'cgst','sgst','igst')
		response_data = []
		for item in products:
			item_json = {}
			item_json['id'] = item.id
			item_json['label'] = item.name
			item_json['unit_id'] = item.default_unit.id
			item_json['unit'] = item.default_unit.symbol
			item_json['inventory'] = this_tenant.maintain_inventory
			# item_json['vat_type'] = item.vat_type
			try:
				item_json['cgst'] = item.cgst.percentage
			except:
				item_json['cgst'] = 0
			try:
				item_json['sgst'] = item.sgst.percentage
			except:
				item_json['sgst'] = 0
			try:
				item_json['igst'] = item.igst.percentage
			except:
				item_json['igst'] = 0
			response_data.append(item_json)
		data = json.dumps(response_data, cls=DjangoJSONEncoder)
	else:
		data = 'fail'
	mimetype = 'application/json'
	return HttpResponse(data, mimetype)

# @login_required
@api_view(['GET'],)
def get_product_inventory(request):
	this_tenant=request.user.tenant
	if request.method == "GET":
		product_id = request.GET.get('product_id')
		warehouse_id = request.GET.get('warehouse_id')
		product_quantity=list(Inventory.objects.for_tenant(this_tenant).filter(quantity_available__gt=0,\
					product=product_id, warehouse=warehouse_id).values('tentative_sales_price','mrp').\
					annotate(available=Sum('quantity_available')))
	jsondata = json.dumps(product_quantity,  cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

@login_required
def new_sales_invoice(request):
	return render(request,'sales/sales_invoice.html', {'extension': 'base.html'})


# @login_required
@api_view(['POST'],)
def sales_invoice_save(request):
	if request.method == 'POST':
		calltype = request.data.get('calltype')
		response_data = {}
		this_tenant=request.user.tenant
		if (calltype == 'save'):
			try:
				with transaction.atomic():
				
					customer_id = request.data.get('customer')
					warehouse_id=request.data.get('warehouse')
					date=request.data.get('date')

					# Final save will determine whether sales invoice will be finalized or temporary and editable
					is_final=request.data.get('is_final')
					final_save = False
					if (is_final == 'true' or is_final == True):
						final_save = True
					is_igst = False
					
					# grand_discount_type=request.POST.get('grand_discount_type')
					# try:
					# 	grand_discount_value=Decimal(request.POST.get('grand_discount_value'))
					# except:
					grand_discount_value=0
					
					subtotal=Decimal(request.data.get('subtotal'))
					cgsttotal=Decimal(request.data.get('cgsttotal'))
					sgsttotal=Decimal(request.data.get('sgsttotal'))
					igsttotal=Decimal(request.data.get('igsttotal'))
					total=Decimal(request.data.get('total'))
					round_value=Decimal(request.data.get('round_value'))
					# sum_total = subtotal+cgsttotal+sgsttotal
					
					# if (abs(sum_total - total) <0.90 ):
						# total = sum_total
					duedate=request.data.get('duedate')

					
					bill_data = json.loads(request.data.get('bill_details'))

					customer = Customer.objects.for_tenant(this_tenant).get(id=customer_id)
					warehouse = Warehouse.objects.for_tenant(this_tenant).get(id=warehouse_id)
					
					# new_invoice=new_sales_invoice(this_tenant, customer, warehouse, date, duedate,\
					# 		grand_discount_type, grand_discount_value, subtotal, taxtotal, total, 0)
					
					customer_name=customer.name
					try:
						customer_address=customer.address_1+", "+customer.address_2
					except:
						customer_address=''
					customer_state=customer.state
					customer_city=customer.city
					customer_pin=customer.pin
					customer_gst=customer.gst
					
					ware_address=warehouse.address_1+", "+warehouse.address_2
					ware_state=warehouse.state
					ware_city=warehouse.city
					ware_pin=warehouse.pin
					
					new_invoice=sales_invoice()
					new_invoice.tenant=this_tenant

					new_invoice.date = date
					
					new_invoice.customer=customer
					new_invoice.customer_name=customer_name
					new_invoice.customer_address=customer_address
					new_invoice.customer_state=customer_state
					new_invoice.customer_city=customer_city
					new_invoice.customer_pin=customer_pin
					new_invoice.customer_gst=customer_gst
					new_invoice.dl_1=customer.dl_1
					new_invoice.dl_2=customer.dl_2

					new_invoice.warehouse=warehouse
					new_invoice.warehouse_address=ware_address
					new_invoice.warehouse_state=ware_state
					new_invoice.warehouse_city=ware_city
					new_invoice.warehouse_pin=ware_pin

					new_invoice.is_final=final_save


					if (customer.gst):
						new_invoice.gst_type=1
					else:
						if (subtotal<small_large_limt):
							new_invoice.gst_type=3
						else:
							new_invoice.gst_type=2				
					# new_invoice.grand_discount_type=grand_discount_type
					# new_invoice.grand_discount_value=grand_discount_value
					new_invoice.subtotal=subtotal
					new_invoice.cgsttotal=cgsttotal
					new_invoice.sgsttotal=sgsttotal
					new_invoice.igsttotal=igsttotal
					new_invoice.roundoff = round_value
					new_invoice.total = total
					new_invoice.duedate = duedate
					new_invoice.amount_paid = 0
					new_invoice.save()
					
					products_cost=0
					
					vat_paid={}
					cgst_paid={}
					sgst_paid={}
					igst_paid={}

					cgst_total=0
					sgst_total=0
					igst_total=0

					customer_gst=customer.gst

					#Does this tenant maintain inventory?
					maintain_inventory=this_tenant.maintain_inventory
					total_purchase_price=0
					
			#saving the invoice_line_item and linking them with foreign key to receipt
					for data in bill_data:
						productid=data['product_id']
						unitid=data['unit_id']
						price_list={}
						price_list_dict={}
						price_list_list=[]

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
						discount_type=data['disc_type']
						discount_value=Decimal(data['disc'])
						discount_type_2=data['disc_type_2']
						discount_value_2=Decimal(data['disc_2'])
						line_taxable_total=Decimal(data['taxable_total'])
						line_total=Decimal(data['line_total'])

						cgst_p=Decimal(data['cgst_p'])
						cgst_v=Decimal(data['cgst_v'])
						sgst_p=Decimal(data['sgst_p'])
						sgst_v=Decimal(data['sgst_v'])
						igst_p=Decimal(data['igst_p'])
						igst_v=Decimal(data['igst_v'])
						

						cgst_total+=cgst_v
						sgst_total+=sgst_v
						igst_total+=igst_v


						product=Product.objects.for_tenant(this_tenant).select_related('tax').get(id=productid)
								
						unit=Unit.objects.for_tenant(this_tenant).get(id=unitid)
						multiplier=unit.multiplier
						
						original_actual_sales_price=Decimal(data['sales'])
						if not maintain_inventory:
							original_tentative_sales_price = original_actual_sales_price
							original_mrp=0
						else: 	
							original_tentative_sales_price=Decimal(data['tsp'])
							original_mrp=Decimal(data['mrp'])

						actual_sales_price=Decimal(original_actual_sales_price/multiplier)
						tentative_sales_price=original_tentative_sales_price/multiplier
						mrp=original_mrp/multiplier

						original_quantity=int(data['quantity'])
						quantity=original_quantity*multiplier
						if maintain_inventory:
							product_list=Inventory.objects.for_tenant(this_tenant).filter(quantity_available__gt=0,\
									product=productid, warehouse=warehouse, \
									tentative_sales_price=original_tentative_sales_price, mrp=original_mrp).order_by('purchase_date')
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
									inventory_data={'date':item.purchase_date, 'quantity':original_available, \
													'pur_rate':item.purchase_price}
									price_list_list.append(inventory_data)
									price_list[i]={'date':item.purchase_date, 'quantity':original_available,\
													'pur_rate':item.purchase_price}
									total_purchase_price+=original_available*item.purchase_price
									quantity_updated-=original_available
									# item.delete()
									
								else:
									item.quantity_available-=quantity_updated
									products_cost+=item.purchase_price*quantity_updated
									item.save()
									inventory_data={'date':item.purchase_date, 'quantity':quantity_updated,\
													'pur_rate':item.purchase_price}
									price_list_list.append(inventory_data)
									price_list[i]={'date':item.purchase_date, 'quantity':quantity_updated,\
													'pur_rate':item.purchase_price}
									total_purchase_price+=quantity_updated*item.purchase_price
									quantity_updated=0
							
							if (quantity_updated>0):
								raise IntegrityError('Stock/Inventory not available for: '+product.name )
							
							price_list_dict['detail']=price_list_list
							price_list_json = json.dumps(price_list_dict,  cls=DjangoJSONEncoder)

						LineItem = invoice_line_item()
						LineItem.sales_invoice = new_invoice
						LineItem.product= product
						LineItem.product_name= product.name
						LineItem.product_sku=product.sku
						LineItem.product_hsn=product.hsn_code
						LineItem.date = date
						LineItem.cgst_percent=cgst_p
						LineItem.cgst_value=cgst_v
						LineItem.sgst_percent=sgst_p
						LineItem.sgst_value=sgst_v
						LineItem.igst_percent=igst_p
						LineItem.igst_value=igst_v

						LineItem.unit=unit.symbol
						LineItem.unit_multi=unit.multiplier
						LineItem.quantity=original_quantity
						if (product.has_batch):
							LineItem.batch=batch
							LineItem.manufacturing_date=manufacturing_date
							LineItem.expiry_date=expiry_date
						if (product.has_instance):
							LineItem.serial_no=serial_no
						
						LineItem.sales_price=original_actual_sales_price
						LineItem.tentative_sales_price=original_tentative_sales_price
						if maintain_inventory:
							LineItem.other_data=price_list_json
						LineItem.mrp=original_mrp
						LineItem.discount_type=discount_type
						LineItem.discount_value=discount_value
						LineItem.discount2_type=discount_type_2
						LineItem.discount2_value=discount_value_2
						LineItem.line_tax=line_taxable_total
						LineItem.line_total=line_total
						LineItem.tenant=this_tenant
						LineItem.save()

						if maintain_inventory:						
							#Update this. Need to include purchase price here. For each purchase price there will be a ledger entry
							for k,v in price_list.items():
								new_inventory_ledger_sales(product, warehouse, 2, date, v['quantity'],\
										v['pur_rate'], actual_sales_price,  new_invoice.invoice_id, this_tenant)
								
								# new_inventory_ledger=inventory_ledger()
								# new_inventory_ledger.product=product
								# new_inventory_ledger.warehouse=warehouse
								# new_inventory_ledger.transaction_type=2
								# new_inventory_ledger.date=date
								# new_inventory_ledger.quantity=v['quantity']
								# new_inventory_ledger.actual_sales_price=actual_sales_price
								# new_inventory_ledger.purchase_price=v['pur_rate']
								# new_inventory_ledger.transaction_bill_id=new_invoice.invoice_id
								# new_inventory_ledger.tenant=this_tenant
								# new_inventory_ledger.save()
							
							warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).get(warehouse=warehouse)
							warehouse_valuation_change.valuation-=total_purchase_price
							warehouse_valuation_change.save()
						if (is_igst):
							if (igst_p in igst_paid):
								igst_paid[igst_p][0]+=igst_v
								igst_paid[igst_p][1]=total
								igst_paid[igst_p][2]+=line_taxable_total
							else:
								igst_paid[igst_p]=[igst_v, total, line_taxable_total]
						else:
							if (cgst_p in cgst_paid):
								cgst_paid[cgst_p][0]+=cgst_v
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


					#create tax transactions.
					#tax_transaction(cgst_paid, sgst_paid, igst_paid, 2, new_invoice.id, new_invoice.invoice_id, date, this_tenant, customer_gst)
					is_customer_gst = True if customer_gst else False
					if (is_igst):
						for k,v in igst_paid.items():
							try:
								if v[2]>0:
									new_tax_transaction_register("IGST",2, k, v[0],v[1],v[2], new_invoice.id,\
										new_invoice.invoice_id, date, this_tenant, is_customer_gst, customer_gst, customer_state)
							except:
								pass
					else:
						for k,v in cgst_paid.items():
							try:
								if v[2]>0:
									new_tax_transaction_register("CGST",2, k, v[0],v[1],v[2], new_invoice.id, \
										new_invoice.invoice_id, date, this_tenant, is_customer_gst, customer_gst, customer_state)
							except:
								pass

						for k,v in sgst_paid.items():
							try:
								if v[2]>0:
									new_tax_transaction_register("SGST",2, k, v[0],v[1],v[2], new_invoice.id,\
										new_invoice.invoice_id, date, this_tenant, is_customer_gst, customer_gst, customer_state)
							except:
								pass

							# new_tax_transaction=tax_transaction()
							# new_tax_transaction.transaction_type=2
							# new_tax_transaction.tax_type="IGST"
							# new_tax_transaction.tax_percent=k
							# new_tax_transaction.tax_value=v
							# new_tax_transaction.transaction_bill_id=new_invoice.id
							# new_tax_transaction.transaction_bill_no=new_invoice.invoice_id
							# new_tax_transaction.date=date
							# new_tax_transaction.tenant=this_tenant
							# if customer_gst:
							# 	new_tax_transaction.is_registered = True
							# else:
							# 	new_tax_transaction.is_registered = False
							# new_tax_transaction.save()

					if (final_save == True):
						remarks = "Sales Invoice No: "+str(new_invoice.invoice_id)
						journal = new_journal(this_tenant, date,"Sales",remarks,trn_id= new_invoice.id, trn_type=4)
						account = Account.objects.for_tenant(this_tenant).get(name__exact="Sales")
						new_journal_entry(this_tenant, journal, subtotal, account, 2, date)
						
						if (cgst_total>0):
							account = Account.objects.for_tenant(this_tenant).get(name__exact="CGST Output")
							new_journal_entry(this_tenant, journal, cgst_total, account, 2, date)

						if (sgst_total>0):
							account = Account.objects.for_tenant(this_tenant).get(name__exact="SGST Output")
							new_journal_entry(this_tenant, journal, sgst_total, account, 2, date)

						if (igst_total>0):
							account = Account.objects.for_tenant(this_tenant).get(name__exact="IGST Output")
							new_journal_entry(this_tenant, journal, igst_total, account, 2, date)

						if (round_value!=0):
							account = Account.objects.for_tenant(this_tenant).get(name__exact="Rounding Adjustment")
							new_journal_entry(this_tenant, journal, round_value, account, 2, date)
						

						total_round=total+round_value
						account= Account.objects.for_tenant(this_tenant).get(name__exact="Accounts Receivable")
						new_journal_entry(this_tenant, journal, total, account, 1, date)
						
						debit = journal.journalEntry_journal.filter(transaction_type=1).aggregate(Sum('value'))
						credit = journal.journalEntry_journal.filter(transaction_type=2).aggregate(Sum('value'))
						
						if (debit != credit):
							raise IntegrityError('Debit not equal to credit')
							# raise ValueError


						if maintain_inventory:
							#COGS Journal Entry
							# if (total_purchase_price<1):
								# raise IntegrityError
							# journal=new_journal(this_tenant, date,"Sales",remarks,trn_id= new_invoice.id, trn_type=4)
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

							new_journal_inv=journal_inventory()
							new_journal_inv.date=date
							new_journal_inv.transaction_bill_id=new_invoice.id
							new_journal_inv.trn_type=4
							new_journal_inv.tenant=this_tenant
							new_journal_inv.save()
							new_entry_inv=journal_entry_inventory()
							new_entry_inv.transaction_type=2
							new_entry_inv.journal=new_journal_inv
							new_entry_inv.account=inventory_acct
							new_entry_inv.value=total_purchase_price
							new_entry_inv.tenant=this_tenant
							new_entry_inv.save()

							inventory_acct=account_inventory.objects.for_tenant(this_tenant).get(name__exact="Cost of Goods Sold")
							acct_period=accounting_period.objects.for_tenant(this_tenant).get(start__lte=date, end__gte=date)
							inventory_acct_year=account_year_inventory.objects.for_tenant(this_tenant).\
												get(account_inventory=inventory_acct, accounting_period = acct_period)
							inventory_acct_year.current_debit+=total_purchase_price
							inventory_acct_year.save()

							new_entry_inv=journal_entry_inventory()
							new_entry_inv.transaction_type=1
							new_entry_inv.journal=new_journal_inv
							new_entry_inv.account=inventory_acct
							new_entry_inv.value=total_purchase_price
							new_entry_inv.tenant=this_tenant
							new_entry_inv.save()

					response_data['invoice_id']=new_invoice.id

			except Exception as err:
				response_data  = err.args 
				transaction.rollback()

		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)


# @login_required
@api_view(['GET', 'POST'],)
def sales_total_values(request):
	end=date_first.date.today()
	start=end-date_first.timedelta(days=30)
	sales_daily=sales_day_wise(start, end, request.user.tenant)
	jsondata = json.dumps(sales_daily,  cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

@login_required
def invoice_list(request):
	return render(request,'sales/sales_list.html', {'extension': 'base.html'})

@api_view(['GET'],)
def all_invoices(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		calltype = request.GET.get('calltype')
		page_no = request.GET.get('page_no')
		response_data={}
		filter_data={}
		if (calltype == 'all_invoices'):
			invoices=sales_invoice.objects.for_tenant(this_tenant).all().values('id','invoice_id', \
				'date','customer_name','total', 'amount_paid', 'payable_by').order_by('-date', '-invoice_id')[:300]
		
		elif (calltype == 'unpaid_invoices'):
			invoices=sales_invoice.objects.for_tenant(this_tenant).all().filter(final_payment_date__isnull=True)\
			.values('id','invoice_id','date','customer_name','total', 'amount_paid', 'payable_by').order_by('-date', '-invoice_id')[:300]
		
		elif (calltype== 'customer_pending'):
			customerid = request.GET.get('customerid')
			invoices=sales_invoice.objects.for_tenant(this_tenant).filter(customer=customerid, is_final=True, final_payment_date__isnull=True,).\
				values('id','invoice_id','date','customer_name','total', 'amount_paid', 'payable_by')[:300]

		elif (calltype == 'apply_filter'):
			customers=json.loads(request.GET.get('customers'))
			start=request.GET.get('start')
			end=request.GET.get('end')
			invoice_no=request.GET.get('invoice_no')
			invoice_status=request.GET.get('invoice_status')
			productid=request.GET.get('productid')
			sent_with=request.GET.get('sent_with')
			returntype=request.GET.get('returntype')
			payment_status=request.GET.get('payment_status')
			if (start and end):
				if (payment_status == 'unpaid'):
					invoices=sales_invoice.objects.for_tenant(this_tenant).filter(date__range=[start,end], final_payment_date__isnull=True).all().\
							select_related('invoiceLineItem_salesInvoice').\
							values('id','invoice_id','date','customer_name','total', 'amount_paid', 'payable_by').order_by('-date', '-invoice_id')

				elif (payment_status == 'paid'):
					invoices=sales_invoice.objects.for_tenant(this_tenant).filter(date__range=[start,end], final_payment_date__isnull=False).all().\
							select_related('invoiceLineItem_salesInvoice').\
							values('id','invoice_id','date','customer_name','total', 'amount_paid', 'payable_by').order_by('-date', '-invoice_id')

				else:
					invoices=sales_invoice.objects.for_tenant(this_tenant).filter(date__range=[start,end]).all().\
							select_related('invoiceLineItem_salesInvoice').\
							values('id','invoice_id','date','customer_name','total', 'amount_paid', 'payable_by').order_by('-date', '-invoice_id')
			if (len(customers)>0):
				customers_list=[]
				for item in customers:
					customers_list.append(item['customerid'])
				if (sent_with == 'unpaid_invoices'):
					invoices=invoices.filter(final_payment_date__isnull=True, customer__in=customers_list).all()
				# if (sent_with == 'all_invoices'):
				# 	invoices=invoices.filter(customer__in=customers_list).all()
				else:
					invoices=invoices.filter(customer__in=customers_list).all()
			else:
				if (sent_with == 'all_invoices'):
					pass
				if (sent_with == 'unpaid_receipts'):
					invoices=invoices.filter(final_payment_date__isnull=True).\
						all()
			if invoice_no:
				invoices=invoices.filter(invoice_id__icontains=invoice_no)
			if invoice_status:
				if (invoice_status == 'open'):
					invoices=invoices.filter(is_final=False)
				elif (invoice_status == 'final'):
					invoices=invoices.filter(is_final=True)
			if productid:
				product=Product.objects.for_tenant(this_tenant).get(id=productid)
				invoices=invoices.filter(invoiceLineItem_salesInvoice__product=product).\
						values('id','invoice_id','date','customer_name','total', 'amount_paid', 'payable_by').order_by('-date', '-invoice_id')

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
			filter_summary=invoices.aggregate(pending=Sum('total')-Sum('amount_paid'), total_sum=Sum('total'))
			filter_data['total_pending'] = filter_summary['pending']
			filter_data['total_value'] = filter_summary['total_sum']
		
		if page_no:
			response_data =  paginate_data(page_no, 10, list(invoices))
			response_data.update(filter_data)
		else:
			response_data['object']=list(invoices)
			response_data.update(filter_data)
	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

@api_view(['GET'],)
def invoice_purchase_wise_details(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		calltype = request.GET.get('calltype')
		page_no = request.GET.get('page_no')
		response_data=[]
		# if (calltype == 'all_invoices'):
		# invoices=sales_invoice.objects.for_tenant(this_tenant).all().values('id','invoice_id', \
		# 	'date','customer_name','total', 'amount_paid', 'payable_by').order_by('-date', '-invoice_id')[:300]
		invoices=sales_invoice.objects.for_tenant(this_tenant).all()
		line_items=invoice_line_item.objects.for_tenant(this_tenant).filter(sales_invoice__in=invoices)
		total_overall=0
		for item in line_items:
			total_pur=0
			product_items=json.loads(item.other_data)['detail']
			for i in product_items:
				total_pur += Decimal(i['pur_rate'])*Decimal(i['quantity'])
			response_data.append({'invoice_no':item.sales_invoice.invoice_id,'product':item.product_name,'quantity':item.quantity,\
					'sales': item.line_tax, 'purchase': total_pur, 'is_final':item.sales_invoice.is_final})
			total_overall+=total_pur
		response_data.append({'total_overall': total_overall})
		
		
	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)


# @login_required
@api_view(['GET'],)
def invoices_metadata(request):
	this_tenant=request.user.tenant
	tod=date_first.date.today()
	prev=tod-date_first.timedelta(days=30)
	invoice_value=sales_invoice.objects.for_tenant(this_tenant).filter(date__range=[prev,tod]).aggregate(Sum('total'))
	invoice_paid=sales_payment.objects.for_tenant(this_tenant).filter(paid_on__range=[prev,tod]).aggregate(Sum('amount_received'))
	invoice_overdue=sales_invoice.objects.for_tenant(this_tenant).filter(payable_by__gt=tod).aggregate(Sum('total'))
	response_data = {'invoice_value':invoice_value, 'invoice_paid':invoice_paid, 'invoice_overdue':invoice_overdue}		
		
	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

# @login_required
@api_view(['GET', 'POST'],)
def invoice_details(request, pk):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		invoice=sales_invoice.objects.for_tenant(this_tenant).values('id','invoice_id','date',\
		'customer_name','customer_address','customer_city','customer_pin','customer_gst','warehouse_address','warehouse_city',\
		'warehouse_pin','payable_by','grand_discount_type','grand_discount','subtotal','cgsttotal','sgsttotal','igsttotal','roundoff',\
		'total','amount_paid', 'dl_1', 'dl_2').get(id=pk)
		
		line_items=list(invoice_line_item.objects.filter(sales_invoice=invoice['id']).values('id','product_name','product_id',\
			'product_hsn','unit','unit_multi','quantity','quantity_returned','sales_price',\
			'tentative_sales_price','mrp','discount_type','discount_value','discount2_type','discount2_value', 'line_tax',\
			'line_total', 'cgst_percent','sgst_percent','igst_percent','cgst_value','sgst_value','igst_value',))
		invoice['line_items']=line_items
		invoice['tenant_gst']=this_tenant.gst
		invoice['tenant_name']=this_tenant.name
		invoice['tenant_dl1']=this_tenant.dl_1
		invoice['tenant_dl2']=this_tenant.dl_2
		
		jsondata = json.dumps(invoice, cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)

@api_view(['GET', 'POST'],)
def edit_invoice_details(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		invoice_id = request.GET.get('invoice_id')
		invoice=sales_invoice.objects.for_tenant(this_tenant).filter(is_final=False).values('id','invoice_id','date',\
		'customer_name','customer_address','customer_city','customer_pin','customer_gst','warehouse_address','warehouse_address','warehouse_city',\
		'warehouse_pin','warehouse','payable_by','grand_discount_type','grand_discount','subtotal','cgsttotal','sgsttotal','igsttotal',\
		'total','amount_paid').get(invoice_id=invoice_id)
		
		line_items=invoice_line_item.objects.filter(sales_invoice=invoice['id']).all()
		response_data=[]
		for item in line_items:
			try:
				qty_avl=Inventory.objects.for_tenant(this_tenant).filter(quantity_available__gt=0,\
						product=item.product_id, warehouse=invoice['warehouse'], tentative_sales_price=item.tentative_sales_price, mrp=item.mrp).\
						values('tentative_sales_price','mrp').annotate(avl=Sum('quantity_available'))[0]['avl']
			except:
				qty_avl=0
			response_data.append({'id':item.id,'product_name':item.product_name,'product_id': item.product_id,'unit':item.unit,\
				'unit_multi':item.unit_multi,'quantity':item.quantity,'quantity_returned':item.quantity_returned,'sales_price': item.sales_price,\
				'tentative_sales_price': item.tentative_sales_price,'mrp':item.mrp,'discount_type': item.discount_type, \
				'discount_value':item.discount_value,'discount2_type':item.discount2_type,'discount2_value':item.discount2_value, \
				'line_tax':item.line_tax,'line_total':item.line_total, 'cgst_percent': item.cgst_percent, 'sgst_percent': item.sgst_percent,\
				'igst_percent':item.igst_percent, 'cgst_value':item.cgst_value,'sgst_value':item.sgst_value,\
				'igst_value':item.igst_value, 'qty_avl':qty_avl+item.quantity-item.quantity_returned})


		invoice['line_items']=response_data
		invoice['tenant_gst']=this_tenant.gst
		invoice['tenant_name']=this_tenant.name
		invoice['maintain_inventory']=this_tenant.maintain_inventory
		
		jsondata = json.dumps(invoice, cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)


@login_required
def invoice_detail_view(request, pk):
	return render(request,'sales/sales_invoice_detail.html', {'extension': 'base.html', 'pk':pk})

@api_view(['POST'],)
def payment_register(request):
	this_tenant=request.user.tenant
	if request.method == 'POST':
		response_data=[]
		total_amount_collected= 0
		customerid = request.data.get('customerid')
		modeid = request.data.get('modeid')
		date = request.data.get('date')
		payment_details = json.loads(request.data.get('payment_details'))
		mode = payment_mode.objects.for_tenant(this_tenant).get(id=modeid)
		invoiceids=""
		cheque_rtgs_all=""
		payment_pk={}
		cheque_rtgs_checker = []
		total_amount_received=0
		with transaction.atomic():
			try:
				for item in payment_details:
					invoice_id=item['invoice_pk']
					amount_received=Decimal(item['amount'])
					total_amount_received+=amount_received
					cheque_rtgs_number=item['cheque_rtgs_number']
			
					invoice=sales_invoice.objects.for_tenant(this_tenant).get(id=invoice_id)
					invoice.amount_paid+=amount_received
					if (round(invoice.total - invoice.amount_paid) == 0):
						invoice.final_payment_date=date
					elif (round(invoice.total - invoice.amount_paid) < 0):
						raise IntegrityError
					invoice.save()

					new_sales_payment = sales_payment()
					new_sales_payment.payment_mode=mode
					new_sales_payment.payment_mode_name=mode.name
					new_sales_payment.sales_invoice=invoice
					new_sales_payment.amount_received=amount_received
					new_sales_payment.cheque_rtgs_number=cheque_rtgs_number
					new_sales_payment.paid_on=date
					# new_purchase_payment.remarks=remarks
					new_sales_payment.tenant=this_tenant
					new_sales_payment.save()
					total_amount_collected+= amount_received
					invoiceids+= str(invoice.invoice_id)+", "
					if not cheque_rtgs_number in cheque_rtgs_checker:
						cheque_rtgs_checker.append(cheque_rtgs_number)
						cheque_rtgs_all+= cheque_rtgs_number+", "
					payment_pk[str(invoice.invoice_id)]=new_sales_payment.id
				
				payment_json=json.dumps(payment_pk, cls=DjangoJSONEncoder)
				if len(cheque_rtgs_all)>0:
					invoiceids+= "Cheque No:  "+cheque_rtgs_all
				# raise IntegrityError
				journal=new_journal(this_tenant,date,group_name="Sales", remarks="Collection Against: "+invoiceids\
					,trn_id=new_sales_payment.id, trn_type=5, other_data=payment_json)
				account= Account.objects.for_tenant(this_tenant).get(name__exact="Accounts Receivable")
				new_journal_entry(this_tenant, journal, total_amount_collected, account, 2, date)
				new_journal_entry(this_tenant, journal, total_amount_collected, mode.payment_account, 1, date)

			except:
				transaction.rollback()

	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

@login_required
def sales_edit_view(request):
	return render(request,'sales/sales_edit.html', {'extension': 'base.html'})

@api_view(['POST'],)
def sales_invoice_edit(request):
	if request.method == 'POST':
		calltype = request.data.get('calltype')
		response_data = {}
		this_tenant=request.user.tenant
		if (calltype == 'save'):
			with transaction.atomic():
				try:
					final_save = False
					is_igst = False
					invoice_id = request.data.get('invoiceid')
					# date=request.data.get('date')

					subtotal=Decimal(request.data.get('subtotal'))
					cgsttotal=Decimal(request.data.get('cgsttotal'))
					sgsttotal=Decimal(request.data.get('sgsttotal'))
					igsttotal=Decimal(request.data.get('igsttotal'))
					round_value=Decimal(request.data.get('round_value'))
					total=Decimal(request.data.get('total'))
					
					bill_data = json.loads(request.data.get('bill_details'))

					old_invoice = sales_invoice.objects.for_tenant(this_tenant).get(id=invoice_id)
					date = old_invoice.date
					

					old_invoice.is_final=final_save
					old_invoice.subtotal=subtotal
					old_invoice.cgsttotal=cgsttotal
					old_invoice.sgsttotal=sgsttotal
					old_invoice.igsttotal=igsttotal
					old_invoice.roundoff=round_value
					old_invoice.total = total
					if (subtotal<small_large_limt):
						old_invoice.gst_type=3
					else:
						old_invoice.gst_type=2
					old_invoice.save()
					
					cgst_paid={}
					sgst_paid={}
					igst_paid={}

					cgst_total=0
					sgst_total=0
					igst_total=0

					customer_gst=old_invoice.customer.gst
					customer_state=old_invoice.customer.state

					#Does this tenant maintain inventory?
					maintain_inventory=this_tenant.maintain_inventory
					total_purchase_price=0
					this_warehouse=old_invoice.warehouse
					warehouse=old_invoice.warehouse

					#First delete all the old entries
					all_line_items=invoice_line_item.objects.for_tenant(this_tenant).filter(sales_invoice=old_invoice)
					
					#Undo change in inventory
					old_total_purchase_price=0
					if maintain_inventory:
						for item in all_line_items:
							productid=item.product
							multiplier=item.unit_multi
							# print(multiplier)
							try:
								original_tentative_sales_price=item.tentative_sales_price
								tentative_sales_price=original_tentative_sales_price/multiplier
							except:
								tentative_sales_price=0
							try:
								original_mrp=item.mrp
								mrp=original_mrp/multiplier
							except:
								mrp=0
							product_items=json.loads(item.other_data)['detail']
							for each_item in product_items:
								old_total_purchase_price+=Decimal(each_item['quantity'])*Decimal(each_item['pur_rate'])
								inventory=Inventory()
								inventory.product=productid
								inventory.warehouse=this_warehouse
								inventory.purchase_quantity=Decimal(each_item['quantity'])
								inventory.quantity_available=Decimal(each_item['quantity'])
								inventory.purchase_date=each_item['date']
								inventory.purchase_price=Decimal(each_item['pur_rate'])
								inventory.tentative_sales_price=tentative_sales_price
								inventory.mrp=mrp
								inventory.tenant=this_tenant
								inventory.save()

						#Update Warehouse Valuation
						warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).get(warehouse=warehouse)
						warehouse_valuation_change.valuation+=old_total_purchase_price
						warehouse_valuation_change.save()
							
						# delete inventory_ledger() - only if you maintain inventory
						inventory_ledger.objects.for_tenant(this_tenant).filter(date=date,transaction_type=2,\
								transaction_bill_id=old_invoice.invoice_id).delete()
					
					# delete tax_transaction
					tax_transaction.objects.for_tenant(this_tenant).filter(date=date,transaction_type=2,transaction_bill_id=old_invoice.id).\
								delete()
					#delete old line items
					all_line_items.delete()

					products_cost = 0						
					
			#saving the line_item and linking them with foreign key to receipt
					for data in bill_data:
						productid=data['product_id']
						unit_symbol=data['unit_symbol']
						multiplier=Decimal(data['unit_multi'])
						price_list={}
						price_list_dict={}
						price_list_list=[]

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

						discount_type=data['disc_type']
						discount_value=Decimal(data['disc'])
						discount_type_2=data['disc_type_2']
						discount_value_2=Decimal(data['disc_2'])
						line_taxable_total=Decimal(data['taxable_total'])
						line_total=Decimal(data['line_total'])

						cgst_p=Decimal(data['cgst_p'])
						cgst_v=Decimal(data['cgst_v'])
						sgst_p=Decimal(data['sgst_p'])
						sgst_v=Decimal(data['sgst_v'])
						igst_p=Decimal(data['igst_p'])
						igst_v=Decimal(data['igst_v'])
						

						cgst_total+=cgst_v
						sgst_total+=sgst_v
						igst_total+=igst_v


						product=Product.objects.for_tenant(this_tenant).select_related('tax').get(id=productid)
								
						# unit=Unit.objects.for_tenant(this_tenant).get(id=unitid)
						
						
						original_actual_sales_price=Decimal(data['sales'])
						if not maintain_inventory:
							original_tentative_sales_price = original_actual_sales_price
							original_mrp=0
						else: 	
							original_tentative_sales_price=Decimal(data['tsp'])
							original_mrp=Decimal(data['mrp'])

						actual_sales_price=Decimal(original_actual_sales_price/multiplier)
						tentative_sales_price=original_tentative_sales_price/multiplier
						mrp=original_mrp/multiplier

						original_quantity=int(data['quantity'])
						quantity=original_quantity*multiplier
						if maintain_inventory:
							product_list=Inventory.objects.for_tenant(this_tenant).filter(quantity_available__gt=0,\
									product=productid, warehouse=warehouse, \
									tentative_sales_price=original_tentative_sales_price, mrp=original_mrp).order_by('purchase_date')
							
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
									inventory_data={'date':item.purchase_date, 'quantity':original_available, \
													'pur_rate':item.purchase_price}
									price_list_list.append(inventory_data)
									price_list[i]={'date':item.purchase_date, 'quantity':original_available,\
													'pur_rate':item.purchase_price}
									total_purchase_price+=original_available*item.purchase_price
									quantity_updated-=original_available
									# item.delete()
									
								else:
									item.quantity_available-=quantity_updated
									products_cost+=item.purchase_price*quantity_updated
									item.save()
									inventory_data={'date':item.purchase_date, 'quantity':quantity_updated,\
													'pur_rate':item.purchase_price}
									price_list_list.append(inventory_data)
									price_list[i]={'date':item.purchase_date, 'quantity':quantity_updated,\
													'pur_rate':item.purchase_price}
									total_purchase_price+=quantity_updated*item.purchase_price
									quantity_updated=0								
							if (quantity_updated>0):
								raise IntegrityError
							price_list_dict['detail']=price_list_list
							price_list_json = json.dumps(price_list_dict,  cls=DjangoJSONEncoder)

						LineItem = invoice_line_item()
						LineItem.sales_invoice = old_invoice
						LineItem.product= product
						LineItem.product_name= product.name
						LineItem.product_sku=product.sku
						LineItem.product_hsn=product.hsn_code
						LineItem.date = date
						LineItem.cgst_percent=cgst_p
						LineItem.cgst_value=cgst_v
						LineItem.sgst_percent=sgst_p
						LineItem.sgst_value=sgst_v
						LineItem.igst_percent=igst_p
						LineItem.igst_value=igst_v

						LineItem.unit=unit_symbol
						LineItem.unit_multi=multiplier
						LineItem.quantity=original_quantity
						if (product.has_batch):
							LineItem.batch=batch
							LineItem.manufacturing_date=manufacturing_date
							LineItem.expiry_date=expiry_date
						if (product.has_instance):
							LineItem.serial_no=serial_no
						
						LineItem.sales_price=original_actual_sales_price
						LineItem.tentative_sales_price=original_tentative_sales_price
						if maintain_inventory:
							LineItem.other_data=price_list_json
						LineItem.mrp=original_mrp
						LineItem.discount_type=discount_type
						LineItem.discount_value=discount_value
						LineItem.discount2_type=discount_type_2
						LineItem.discount2_value=discount_value_2
						LineItem.line_tax=line_taxable_total
						LineItem.line_total=line_total
						LineItem.tenant=this_tenant
						LineItem.save()

						if maintain_inventory:						
							for k,v in price_list.items():
								new_inventory_ledger_sales(product, warehouse, 2, date, v['quantity'],\
										v['pur_rate'], actual_sales_price,  old_invoice.invoice_id, this_tenant)
							
							warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).get(warehouse=warehouse)
							warehouse_valuation_change.valuation-=total_purchase_price
							warehouse_valuation_change.save()

						if (is_igst):
							if (igst_p in igst_paid):
								igst_paid[igst_p][0]+=igst_v
								igst_paid[igst_p][1]=total
								igst_paid[igst_p][2]+=line_taxable_total
							else:
								igst_paid[igst_p]=[igst_v, total, line_taxable_total]
						else:
							if (cgst_p in cgst_paid):
								cgst_paid[cgst_p][0]+=cgst_v
								cgst_paid[cgst_p][1]=total
								cgst_paid[cgst_p][2]+=line_taxable_total
							else:
								cgst_paid[cgst_p]=[cgst_v, total, line_taxable_total]

							if (sgst_p in sgst_paid):
								sgst_paid[sgst_p][0]+=sgst_v
								sgst_paid[sgst_p][1]=total
								cgst_paid[cgst_p][2]+=line_taxable_total
							else:
								sgst_paid[sgst_p]=[sgst_v, total, line_taxable_total]
						

					is_customer_gst = True if customer_gst else False
					if (is_igst):
						for k,v in igst_paid.items():
							if v[2]>0:
								new_tax_transaction_register("IGST",2, k, v[0],v[1], v[2], old_invoice.id,\
									old_invoice.invoice_id, date, this_tenant, is_customer_gst, customer_gst, customer_state)
					else:
						for k,v in cgst_paid.items():
							if v[2]>0:
								new_tax_transaction_register("CGST",2, k, v[0],v[1], v[2], old_invoice.id,\
									old_invoice.invoice_id, date, this_tenant, is_customer_gst, customer_gst, customer_state)

						for k,v in sgst_paid.items():
							if v[2]>0:
								new_tax_transaction_register("SGST",2, k, v[0],v[1], v[2], old_invoice.id,\
									old_invoice.invoice_id, date, this_tenant, is_customer_gst, customer_gst, customer_state)

					#One more journal entry for COGS needs to be done
					if (final_save):
						remarks="Sales Invoice No: "+str(old_invoice.invoice_id)
						journal=new_journal(this_tenant, date,"Sales",remarks,trn_id= old_invoice.id, trn_type=4)
						account= Account.objects.for_tenant(this_tenant).get(name__exact="Sales")
						new_journal_entry(this_tenant, journal, subtotal, account, 2, date)
						
						if (cgst_total>0):
							account= Account.objects.for_tenant(this_tenant).get(name__exact="CGST Output")
							new_journal_entry(this_tenant, journal, cgst_total, account, 2, date)

						if (sgst_total>0):
							account= Account.objects.for_tenant(this_tenant).get(name__exact="SGST Output")
							new_journal_entry(this_tenant, journal, sgst_total, account, 2, date)

						if (igst_total>0):
							account= Account.objects.for_tenant(this_tenant).get(name__exact="IGST Output")
							new_journal_entry(this_tenant, journal, igst_total, account, 2, date)

						if (round_value!=0):
							account= Account.objects.for_tenant(this_tenant).get(name__exact="Rounding Adjustment")
							new_journal_entry(this_tenant, journal, round_value, account, 2, date)
							
						account= Account.objects.for_tenant(this_tenant).get(name__exact="Accounts Receivable")
						new_journal_entry(this_tenant, journal, total, account, 1, date)
						
						debit = journal.journalEntry_journal.filter(transaction_type=1).aggregate(Sum('value'))
						credit = journal.journalEntry_journal.filter(transaction_type=2).aggregate(Sum('value'))

						if (debit != credit):
							raise IntegrityError

						if maintain_inventory:
							inventory_acct=account_inventory.objects.for_tenant(this_tenant).get(name__exact="Inventory")
							acct_period=accounting_period.objects.for_tenant(this_tenant).get(start__lte=date, end__gte=date)
							inventory_acct_year=account_year_inventory.objects.for_tenant(this_tenant).\
												get(account_inventory=inventory_acct, accounting_period = acct_period)
							inventory_acct_year.current_debit-=total_purchase_price
							inventory_acct_year.save()

							new_journal_inv=journal_inventory()
							new_journal_inv.date=date
							new_journal_inv.transaction_bill_id=old_invoice.id
							new_journal_inv.trn_type=4
							new_journal_inv.tenant=this_tenant
							new_journal_inv.save()
							new_entry_inv=journal_entry_inventory()
							new_entry_inv.transaction_type=2
							new_entry_inv.journal=new_journal_inv
							new_entry_inv.account=inventory_acct
							new_entry_inv.value=total_purchase_price
							new_entry_inv.tenant=this_tenant
							new_entry_inv.save()

							inventory_acct=account_inventory.objects.for_tenant(this_tenant).get(name__exact="Cost of Goods Sold")
							acct_period=accounting_period.objects.for_tenant(this_tenant).get(start__lte=date, end__gte=date)
							inventory_acct_year=account_year_inventory.objects.for_tenant(this_tenant).\
												get(account_inventory=inventory_acct, accounting_period = acct_period)
							inventory_acct_year.current_debit+=total_purchase_price
							inventory_acct_year.save()

							# new_journal_inv=journal_inventory()
							# new_journal_inv.date=date
							# new_journal_inv.transaction_bill_id=old_invoice.id
							# new_journal_inv.trn_type=4
							# new_journal_inv.tenant=this_tenant
							# new_journal_inv.save()
							new_entry_inv=journal_entry_inventory()
							new_entry_inv.transaction_type=1
							new_entry_inv.journal=new_journal_inv
							new_entry_inv.account=inventory_acct
							new_entry_inv.value=total_purchase_price
							new_entry_inv.tenant=this_tenant
							new_entry_inv.save()

					response_data=old_invoice.id
				except:
					transaction.rollback()

		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

# @login_required
@api_view(['GET'],)
def collection_list(request):
	if request.method == 'GET':
		this_tenant = request.user.tenant
		page_no=request.GET.get('page_no')
		calltype=request.GET.get('calltype')
		response_data={}
		if (calltype == 'apply_filter'):
			customers=json.loads(request.GET.get('customers'))
			start=request.GET.get('start')
			end=request.GET.get('end')
			invoice_no=request.GET.get('invoice_no')
			# productid=request.GET.get('productid')
			cheque_rtgs=request.GET.get('cheque_rtgs')
			# invoices=sales_invoice.objects.for_tenant(this_tenant).filter(date__range=[start,end]).all().\
			# 			select_related('invoiceLineItem_salesInvoice').\
			# 			values('id','invoice_id','date','customer_name','total', 'amount_paid', 'payable_by').order_by('-date', '-invoice_id')

			payments = sales_payment.objects.for_tenant(this_tenant).filter(paid_on__range=[start,end]).\
						order_by('-paid_on', 'cheque_rtgs_number','-sales_invoice')
			if (len(customers)>0):
				customers_list=[]
				for item in customers:
					customers_list.append(item['customerid'])
					invoices=sales_invoice.objects.for_tenant(this_tenant).filter(date__range=[start,end],customer__in=customers_list)
				payments=payments.filter(sales_invoice__in=invoices).all()
				
			if invoice_no:
				invoices=sales_invoice.objects.for_tenant(this_tenant).filter(invoice_id__icontains=invoice_no)
				payments=payments.filter(sales_invoice__in=invoices)

			if cheque_rtgs:
				payments=payments.filter(cheque_rtgs_number=cheque_rtgs)
				print(payments)
			
			# if productid:
			# 	product=Product.objects.for_tenant(this_tenant).get(id=productid)
			# 	invoices=invoices.filter(invoiceLineItem_salesInvoice__product=product).\
			# 			values('id','invoice_id','date','customer_name','total', 'amount_paid', 'payable_by').order_by('-date', '-invoice_id')
		
		else:
			response_data={}
			payments=sales_payment.objects.for_tenant(this_tenant).order_by('-paid_on', 'cheque_rtgs_number','-sales_invoice')
		
		if (page_no):
			payments_paginated=paginate_data(page_no, 10, list(payments))
			serializer = CollectionSerializers(payments_paginated['object'], many=True)
			response_data['object']  = serializer.data
			response_data['end'] = payments_paginated['end']
			response_data['start'] = payments_paginated['start']
		else:
			response_data['object'] = payments
		jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)

@login_required
def collection_list_view(request):
	return render(request,'sales/collection_list.html', {'extension': 'base.html'})

@login_required
def sales_return_view(request):
	return render(request,'sales/sales_return.html', {'extension': 'base.html'})

@api_view(['GET'],)
def get_return_data(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		calltype = request.GET.get('calltype')
		if (calltype == 'Sales Return'):
			invoice_id = request.GET.get('invoice_id')
			response_data=sales_invoice.objects.for_tenant(this_tenant).get(invoice_id=invoice_id).id
		return redirect('sales:invoice_details', pk=response_data)

	# jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	# return HttpResponse(jsondata)


@api_view(['GET'],)
def get_customer_pending(request):
	this_tenant=request.user.tenant
	response_data={}
	if request.method == 'GET':
		customerid = request.GET.get('customerid')
		customer=Customer.objects.for_tenant(this_tenant).get(id=customerid)
		invoices=sales_invoice.objects.for_tenant(this_tenant).filter(customer=customer, final_payment_date__isnull=True).all()
		value_pending=invoices.aggregate(pending=Sum('total')-Sum('amount_paid'))['pending']
		invoice_count=invoices.count()
		
		response_data['value_pending'] = value_pending
		response_data['invoice_count'] = invoice_count
		
		jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)

@login_required
def open_invoices(request):
	extension = 'base.html'
	return render(request,'sales/open_invoice_list.html', {'extension': extension})


@api_view(['GET'],)
def open_invoice_list(request):
	this_tenant=request.user.tenant
	response_data={}
	page_no=request.GET.get('page_no')
	invoices=list(sales_invoice.objects.for_tenant(this_tenant).filter(is_final=False).values('id','invoice_id','date',\
		'customer_name','customer_address','customer_city','customer_pin','customer_gst','warehouse_address','warehouse_address','warehouse_city',\
		'warehouse_pin','warehouse','payable_by','grand_discount_type','grand_discount','subtotal','cgsttotal','sgsttotal','igsttotal',\
		'total','amount_paid').all().order_by('-date', '-invoice_id'))
	if page_no:
		response_data=paginate_data(page_no, 10, invoices)
	else:
		response_data['object'] = invoices
	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

@api_view(['GET','POST'],)
def finalize_open_invoices(request):
	this_tenant=request.user.tenant
	invoices_pk=json.loads(request.POST.get('invoices_list'))
	# print(invoices_pk)
	calltype=request.POST.get('calltype')
	response_data = {}
	with transaction.atomic():
		try:
			if (calltype=="Finalize"):
				for pk in invoices_pk:
					new_invoice=sales_invoice.objects.get(id=pk['invoice_id'])
					new_invoice.is_final=True
					new_invoice.save()
					date=new_invoice.date
					total_purchase_price = 0
					remarks="Sales Invoice No: "+str(new_invoice.invoice_id)
					line_items=invoice_line_item.objects.filter(sales_invoice=new_invoice)
					for item in line_items:
						product_items=json.loads(item.other_data)['detail']
						for i in product_items:
							total_purchase_price += Decimal(i['pur_rate'])*Decimal(i['quantity'])
					
					journal=new_journal(this_tenant, date,"Sales",remarks,trn_id= new_invoice.id, trn_type=4)
					account= Account.objects.for_tenant(this_tenant).get(name__exact="Sales")
					new_journal_entry(this_tenant, journal, new_invoice.subtotal, account, 2, date)
						
					if (new_invoice.cgsttotal>0):
						account= Account.objects.for_tenant(this_tenant).get(name__exact="CGST Output")
						new_journal_entry(this_tenant, journal, new_invoice.cgsttotal, account, 2, date)

					if (new_invoice.sgsttotal>0):
						account= Account.objects.for_tenant(this_tenant).get(name__exact="SGST Output")
						new_journal_entry(this_tenant, journal, new_invoice.sgsttotal, account, 2, date)

					if (new_invoice.igsttotal>0):
						account= Account.objects.for_tenant(this_tenant).get(name__exact="IGST Output")
						new_journal_entry(this_tenant, journal, new_invoice.igsttotal, account, 2, date)

					#Change here

					if (new_invoice.roundoff!=0):
						account= Account.objects.for_tenant(this_tenant).get(name__exact="Rounding Adjustment")
						new_journal_entry(this_tenant, journal, new_invoice.roundoff, account, 2, date)
										
					account= Account.objects.for_tenant(this_tenant).get(name__exact="Accounts Receivable")
					new_journal_entry(this_tenant, journal, new_invoice.total, account, 1, date)
									
					debit = journal.journalEntry_journal.filter(transaction_type=1).aggregate(Sum('value'))
					credit = journal.journalEntry_journal.filter(transaction_type=2).aggregate(Sum('value'))

					if (debit != credit):
						raise IntegrityError

					if this_tenant.maintain_inventory:
						inventory_acct=account_inventory.objects.for_tenant(this_tenant).get(name__exact="Inventory")
						acct_period=accounting_period.objects.for_tenant(this_tenant).get(start__lte=date, end__gte=date)
						inventory_acct_year=account_year_inventory.objects.for_tenant(this_tenant).\
								get(account_inventory=inventory_acct, accounting_period = acct_period)
						inventory_acct_year.current_debit-=total_purchase_price
						inventory_acct_year.save()

						new_journal_inv=journal_inventory()
						new_journal_inv.date=date
						new_journal_inv.transaction_bill_id=new_invoice.id
						new_journal_inv.trn_type=4
						new_journal_inv.tenant=this_tenant
						new_journal_inv.save()
						new_entry_inv=journal_entry_inventory()
						new_entry_inv.transaction_type=2
						new_entry_inv.journal=new_journal_inv
						new_entry_inv.account=inventory_acct
						new_entry_inv.value=total_purchase_price
						new_entry_inv.tenant=this_tenant
						new_entry_inv.save()
							
						inventory_acct=account_inventory.objects.for_tenant(this_tenant).get(name__exact="Cost of Goods Sold")
						acct_period=accounting_period.objects.for_tenant(this_tenant).get(start__lte=date, end__gte=date)
						inventory_acct_year=account_year_inventory.objects.for_tenant(this_tenant).\
								get(account_inventory=inventory_acct, accounting_period = acct_period)
						inventory_acct_year.current_debit+=total_purchase_price
						inventory_acct_year.save()
							
						# new_journal_inv=journal_inventory()
						# new_journal_inv.date=date
						# new_journal_inv.transaction_bill_id=new_invoice.id
						# new_journal_inv.trn_type=4
						# new_journal_inv.tenant=this_tenant
						# new_journal_inv.save()
						new_entry_inv=journal_entry_inventory()
						new_entry_inv.transaction_type=1
						new_entry_inv.journal=new_journal_inv
						new_entry_inv.account=inventory_acct
						new_entry_inv.value=total_purchase_price
						new_entry_inv.tenant=this_tenant
						new_entry_inv.save()

			elif(calltype == "Delete"):
				total_purchase_price=0
				maintain_inventory=this_tenant.maintain_inventory
				for pk in invoices_pk:
					new_invoice=sales_invoice.objects.get(id=pk['invoice_id'])
					line_items=invoice_line_item.objects.filter(sales_invoice=new_invoice)
					warehouse=new_invoice.warehouse
					date=new_invoice.date
					if (maintain_inventory):
						for item in line_items:
							productid=item.product
							multiplier=item.unit_multi
							try:
								original_tentative_sales_price=item.tentative_sales_price
								tentative_sales_price=original_tentative_sales_price/multiplier
							except:
								tentative_sales_price=0
							try:
								original_mrp=item.mrp
								mrp=original_mrp/multiplier
							except:
								mrp=0
							product_items=json.loads(item.other_data)['detail']
							for each_item in product_items:
								total_purchase_price+=Decimal(each_item['quantity'])*Decimal(each_item['pur_rate'])
								inventory=Inventory()
								inventory.product=productid
								inventory.warehouse=warehouse
								inventory.purchase_quantity=Decimal(each_item['quantity'])
								inventory.quantity_available=Decimal(each_item['quantity'])
								inventory.purchase_date=each_item['date']
								inventory.purchase_price=Decimal(each_item['pur_rate'])
								inventory.tentative_sales_price=tentative_sales_price
								inventory.mrp=mrp
								inventory.tenant=this_tenant
								inventory.save()
							
						# delete inventory_ledger()
						inventory_ledger.objects.for_tenant(this_tenant).filter(date=date,transaction_type=2,\
							transaction_bill_id=new_invoice.invoice_id).delete()
					# delete tax_transaction
					tax_transaction.objects.for_tenant(this_tenant).filter(date=date,transaction_type=2,transaction_bill_id=new_invoice.id).\
								delete()
					#delete invoice and line item
					new_invoice.delete()

				if (maintain_inventory):
					warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).get(warehouse=warehouse)
					warehouse_valuation_change.valuation+=total_purchase_price
					warehouse_valuation_change.save()

			elif(calltype == "Cancel"):
				total_purchase_price=0
				maintain_inventory=this_tenant.maintain_inventory
				for pk in invoices_pk:
					new_invoice=sales_invoice.objects.get(id=pk['invoice_id'])
					line_items=invoice_line_item.objects.filter(sales_invoice=new_invoice)
					warehouse=new_invoice.warehouse
					date=new_invoice.date
					if (maintain_inventory):
						for item in line_items:
							productid=item.product
							multiplier=item.unit_multi
							try:
								original_tentative_sales_price=item.tentative_sales_price
								tentative_sales_price=original_tentative_sales_price/multiplier
							except:
								tentative_sales_price=0
							try:
								original_mrp=item.mrp
								mrp=original_mrp/multiplier
							except:
								mrp=0
							product_items=json.loads(item.other_data)['detail']
							for each_item in product_items:
								total_purchase_price+=Decimal(each_item['quantity'])*Decimal(each_item['pur_rate'])
								inventory=Inventory()
								inventory.product=productid
								inventory.warehouse=warehouse
								inventory.purchase_quantity=Decimal(each_item['quantity'])
								inventory.quantity_available=Decimal(each_item['quantity'])
								inventory.purchase_date=each_item['date']
								inventory.purchase_price=Decimal(each_item['pur_rate'])
								inventory.tentative_sales_price=tentative_sales_price
								inventory.mrp=mrp
								inventory.tenant=this_tenant
								inventory.save()
							
						# delete inventory_ledger()
						inventory_ledger.objects.for_tenant(this_tenant).filter(date=date,transaction_type=2,\
							transaction_bill_id=new_invoice.invoice_id).delete()
					# delete tax_transaction
					tax_transaction.objects.for_tenant(this_tenant).filter(date=date,transaction_type=2,transaction_bill_id=new_invoice.id).\
								delete()
					#delete line item
					line_items.delete()
					#update invoices
					new_invoice.subtotal=0
					new_invoice.cgsttotal = 0
					new_invoice.sgsttotal = 0
					new_invoice.roundoff=0
					new_invoice.total = 0
					new_invoice.final_payment_date=date_first.date.today()
					new_invoice.is_final = True
					new_invoice.save()

				if (maintain_inventory):
					warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).get(warehouse=warehouse)
					warehouse_valuation_change.valuation+=total_purchase_price
					warehouse_valuation_change.save()
		except:
			transaction.rollback()	


	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

#Check before allowing it
@api_view(['POST'],)
def sales_return_save(request):
	if request.method == 'POST':
		calltype = request.data.get('calltype')
		response_data = {}
		this_tenant=request.user.tenant
		if (calltype == 'save'):
			with transaction.atomic():
				try:
					is_igst = False

					invoice_id = request.data.get('invoiceid')
					date=request.data.get('date')
					
					subtotal=Decimal(request.data.get('subtotal'))
					cgsttotal=Decimal(request.data.get('cgsttotal'))
					sgsttotal=Decimal(request.data.get('sgsttotal'))
					igsttotal=Decimal(request.data.get('igsttotal'))
					total=Decimal(request.data.get('total'))
					sum_total = subtotal+cgsttotal+sgsttotal
					if (abs(sum_total - total) <0.90 ):
						total = sum_total
					
					bill_data = json.loads(request.data.get('bill_details'))

					invoice = sales_invoice.objects.for_tenant(this_tenant).get(id=invoice_id)

					customer_gst = invoice.customer.gst
					customer_state = invoice.customer.state
					
					new_invoice=sales_return()
					new_invoice.tenant=this_tenant
					new_invoice.invoice=invoice

					new_invoice.date = date
					
					new_invoice.customer=invoice.customer
					new_invoice.customer_name=invoice.customer_name
					new_invoice.customer_address=invoice.customer_address
					new_invoice.customer_state=customer_state
					new_invoice.customer_city=invoice.customer_city
					new_invoice.customer_pin=invoice.customer_pin
					new_invoice.customer_gst=customer_gst

					new_invoice.warehouse=invoice.warehouse
					new_invoice.warehouse_address=invoice.warehouse_address
					new_invoice.warehouse_state=invoice.warehouse_state
					new_invoice.warehouse_city=invoice.warehouse_city
					new_invoice.warehouse_pin=invoice.warehouse_pin
					
					new_invoice.subtotal=subtotal
					new_invoice.cgsttotal=cgsttotal
					new_invoice.sgsttotal=sgsttotal
					new_invoice.igsttotal=igsttotal
					new_invoice.total = total
			# 		new_invoice.amount_paid = 0
					new_invoice.save()
					
			# 		products_cost=0
					
			# 		vat_paid={}
					cgst_paid={}
					sgst_paid={}
					igst_paid={}

					cgst_total=0
					sgst_total=0
					igst_total=0

					customer_gst=invoice.customer.gst

					#Does this tenant maintain inventory?
					maintain_inventory=this_tenant.maintain_inventory
					total_purchase_price=0
					
			# #saving the line_item and linking them with foreign key to receipt
					for data in bill_data:
						productid=data['product_id']
						line_item_id=data['line_item_id']
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

						line_taxable_total=Decimal(data['taxable_total'])
						line_total=Decimal(data['line_total'])

						cgst_p=Decimal(data['cgst_p'])
						cgst_v=Decimal(data['cgst_v'])
						sgst_p=Decimal(data['sgst_p'])
						sgst_v=Decimal(data['sgst_v'])
						igst_p=Decimal(data['igst_p'])
						igst_v=Decimal(data['igst_v'])

						cgst_total+=cgst_v
						sgst_total+=sgst_v
						igst_total+=igst_v

						line_item = invoice_line_item.objects.for_tenant(this_tenant).get(id=line_item_id)

						product=Product.objects.for_tenant(this_tenant).select_related('tax').get(id=productid)
								
						unit=line_item.unit
						multiplier=line_item.unit_multi
						
						original_actual_sales_price=Decimal(data['return_price'])
						if not maintain_inventory:
							original_tentative_sales_price = original_actual_sales_price
							original_mrp=0
						else: 	
							original_tentative_sales_price=line_item.tentative_sales_price
							original_mrp=line_item.mrp

						actual_sales_price=Decimal(original_actual_sales_price/multiplier)
						tentative_sales_price=original_tentative_sales_price/multiplier
						mrp=original_mrp/multiplier

						original_quantity=int(data['quantity'])
						quantity=original_quantity*multiplier

						already_returned=line_item.quantity_returned

						if this_tenant.maintain_inventory:
							product_items=json.loads(line_item.other_data)['detail']
							quantity_left=quantity
							total_quantity=0
							total_left=quantity_left+already_returned
							for product_item in product_items:
								if (total_left>0):
									new_total_left=total_left
									this_quantity=Decimal(product_item['quantity'])
									total_quantity+=Decimal(product_item['quantity'])
									total_left-=Decimal(product_item['quantity'])
									if (this_quantity>already_returned):
										total_useful=this_quantity-already_returned
									else:
										already_returned-=this_quantity
										continue

									if (quantity_left>total_useful):
										quantity_left=quantity_left-total_useful
									else:
										total_useful=quantity_left
									
									inventory=Inventory()
									inventory.product=product
									inventory.warehouse=invoice.warehouse
									inventory.purchase_quantity=total_useful
									inventory.quantity_available+=total_useful
									inventory.purchase_date=product_item['date']
									inventory.purchase_price=Decimal(product_item['pur_rate'])
									inventory.tentative_sales_price=line_item.tentative_sales_price
									inventory.mrp=line_item.mrp
									inventory.tenant=this_tenant
									inventory.save()

									total_purchase_price+=Decimal(product_item['pur_rate'])*total_useful
									
									new_inventory_ledger=inventory_ledger()
									new_inventory_ledger.product=product
									new_inventory_ledger.warehouse=invoice.warehouse
									new_inventory_ledger.transaction_type=3
									new_inventory_ledger.date=date
									new_inventory_ledger.quantity=total_useful
									new_inventory_ledger.actual_sales_price=actual_sales_price
									new_inventory_ledger.purchase_price=Decimal(product_item['pur_rate'])
									new_inventory_ledger.transaction_bill_id=new_invoice.return_id
									new_inventory_ledger.tenant=this_tenant
									new_inventory_ledger.save()

						line_item.quantity_returned+=original_quantity
						line_item.save()

						LineItem = return_line_item()
						LineItem.sales_return = new_invoice
						LineItem.product= product
						LineItem.product_name= product.name
						LineItem.product_sku=product.sku
						LineItem.product_hsn=product.hsn_code
						LineItem.date = date
						LineItem.cgst_percent=cgst_p
						LineItem.cgst_value=cgst_v
						LineItem.sgst_percent=sgst_p
						LineItem.sgst_value=sgst_v
						LineItem.igst_percent=igst_p
						LineItem.igst_value=igst_v

						LineItem.unit=unit
						LineItem.unit_multi=multiplier
						LineItem.quantity=original_quantity
						
			# 			if (product.has_batch):
			# 				LineItem.batch=batch
			# 				LineItem.manufacturing_date=manufacturing_date
			# 				LineItem.expiry_date=expiry_date
			# 			if (product.has_instance):
			# 				LineItem.serial_no=serial_no
						
						LineItem.return_price=original_actual_sales_price
						LineItem.tentative_sales_price=original_tentative_sales_price
			# 			if maintain_inventory:
			# 				LineItem.other_data=price_list_json
						LineItem.mrp=original_mrp
						LineItem.line_tax=line_taxable_total
						LineItem.line_total=line_total
						LineItem.tenant=this_tenant
						LineItem.save()

						if maintain_inventory:						
							warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).\
									get(warehouse=invoice.warehouse)
							warehouse_valuation_change.valuation+=total_purchase_price
							warehouse_valuation_change.save()

						if (is_igst):
							if (igst_p in igst_paid):
								igst_paid[igst_p][0]+=igst_v
								igst_paid[igst_p][1]=total
								igst_paid[igst_p][2]+=line_taxable_total
							else:
								igst_paid[igst_p]=[igst_v, total, line_taxable_total]
						else:
							if (cgst_p in cgst_paid):
								cgst_paid[cgst_p][0]+=cgst_v
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

					is_customer_gst = True if customer_gst else False

					if (is_igst):
						for k,v in igst_paid.items():
							if v[2]>0:
								new_tax_transaction_register("IGST",3, k, v[0], v[1], v[2],new_invoice.id,\
									new_invoice.return_id, date, this_tenant, is_customer_gst, customer_gst, customer_state)
					else:
						for k,v in cgst_paid.items():
							if v[2]>0:
								new_tax_transaction_register("CGST",3, k, v[0], v[1], v[2], new_invoice.id, \
									new_invoice.return_id, date, this_tenant, is_customer_gst, customer_gst, customer_state)
								

						for k,v in sgst_paid.items():
							if v[2]>0:
								new_tax_transaction_register("SGST",3, k, v[0], v[1], v[2],new_invoice.id,\
									new_invoice.return_id, date, this_tenant, is_customer_gst, customer_gst, customer_state)

					#One more journal entry for COGS needs to be done
					remarks="Sales Return No: "+str(new_invoice.return_id)
					journal=new_journal(this_tenant, date,"Sales",remarks,trn_id= new_invoice.id, trn_type=4)
					account= Account.objects.for_tenant(this_tenant).get(name__exact="Sales")
					new_journal_entry(this_tenant, journal, subtotal, account, 1, date)
					
					if (cgst_total>0):
						account= Account.objects.for_tenant(this_tenant).get(name__exact="CGST Output")
						new_journal_entry(this_tenant, journal, cgst_total, account, 1, date)

					if (sgst_total>0):
						account= Account.objects.for_tenant(this_tenant).get(name__exact="SGST Output")
						new_journal_entry(this_tenant, journal, sgst_total, account, 1, date)

					if (igst_total>0):
						account= Account.objects.for_tenant(this_tenant).get(name__exact="IGST Output")
						new_journal_entry(this_tenant, journal, igst_total, account, 1, date)
						
					account= Account.objects.for_tenant(this_tenant).get(name__exact="Accounts Receivable")
					new_journal_entry(this_tenant, journal, total, account, 2, date)
					
					debit = journal.journalEntry_journal.filter(transaction_type=1).aggregate(Sum('value'))
					credit = journal.journalEntry_journal.filter(transaction_type=2).aggregate(Sum('value'))

					try:
						customer_credit_account=customer_credit.objects.for_tenant(this_tenant).get(customer=invoice.customer)
						customer_credit_account.credit_amount+=total
						customer_credit_account.save()
					except:
						new_account=customer_credit()
						new_account.customer=invoice.customer
						new_account.credit_amount=total
						new_account.tenant=this_tenant
						new_account.save()

					if (debit != credit):
						raise IntegrityError

					if maintain_inventory:						
						inventory_acct=account_inventory.objects.for_tenant(this_tenant).get(name__exact="Inventory")
						acct_period=accounting_period.objects.for_tenant(this_tenant).get(start__lte=date, end__gte=date)
						inventory_acct_year=account_year_inventory.objects.for_tenant(this_tenant).\
											get(account_inventory=inventory_acct, accounting_period = acct_period)
						inventory_acct_year.current_debit+=total_purchase_price
						inventory_acct_year.save()

						new_journal_inv=journal_inventory()
						new_journal_inv.date=date
						new_journal_inv.transaction_bill_id=new_invoice.id
						new_journal_inv.trn_type=6
						new_journal_inv.tenant=this_tenant
						new_journal_inv.save()
						new_entry_inv=journal_entry_inventory()
						new_entry_inv.transaction_type=1
						new_entry_inv.journal=new_journal_inv
						new_entry_inv.account=inventory_acct
						new_entry_inv.value=total_purchase_price
						new_entry_inv.tenant=this_tenant
						new_entry_inv.save()

						inventory_acct=account_inventory.objects.for_tenant(this_tenant).get(name__exact="Cost of Goods Sold")
						acct_period=accounting_period.objects.for_tenant(this_tenant).get(start__lte=date, end__gte=date)
						inventory_acct_year=account_year_inventory.objects.for_tenant(this_tenant).\
											get(account_inventory=inventory_acct, accounting_period = acct_period)
						inventory_acct_year.current_debit-=total_purchase_price
						inventory_acct_year.save()

						# new_journal_inv=journal_inventory()
						# new_journal_inv.date=date
						# new_journal_inv.transaction_bill_id=new_invoice.id
						# new_journal_inv.trn_type=6
						# new_journal_inv.tenant=this_tenant
						# new_journal_inv.save()
						new_entry_inv=journal_entry_inventory()
						new_entry_inv.transaction_type=2
						new_entry_inv.journal=new_journal_inv
						new_entry_inv.account=inventory_acct
						new_entry_inv.value=total_purchase_price
						new_entry_inv.tenant=this_tenant
						new_entry_inv.save()

					response_data=new_invoice.id
				except:
					transaction.rollback()

		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)



@api_view(['GET', 'POST'],)
def excel_invoice(request, pk):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		invoice=sales_invoice.objects.for_tenant(this_tenant).get(id=pk)
		
		line_items=list(invoice_line_item.objects.filter(sales_invoice=invoice).values('product_name','product_hsn',\
			'unit','quantity','sales_price','mrp','discount_type',\
			'discount_value','discount2_type','discount2_value','line_tax', 'line_total', 'cgst_percent','sgst_percent',\
			'igst_percent','cgst_value','sgst_value','igst_value',))
		
		x='Sales_Invoice '+str(invoice.invoice_id)+'.xlsx'
		response = HttpResponse(content_type='application/vnd.ms-excel')
		response['Content-Disposition'] = 'attachment; filename='+x
		xlsx_data = sales_invoice_excel(line_items, invoice, this_tenant)
		response.write(xlsx_data)
		return response

@login_required
def return_list_view(request):
	extension = 'base.html'
	return render(request,'sales/return_list.html', {'extension': extension})


@api_view(['GET'],)
def all_return(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		calltype = request.GET.get('calltype')
		if (calltype == 'all_returns'):
			invoices=sales_return.objects.for_tenant(this_tenant).all().select_related('invoice').values('invoice__invoice_id','invoice__date',\
			'return_id','date','customer_name','total',).order_by('-date', '-invoice_id')[:300]
		response_data = list(invoices)		
		
	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

@login_required
def sales_report(request):
	return render(request,'sales/view_salesreport_crossfilter.html', {'extension': 'base.html'})

@login_required
def sales_report_data(request):
	this_tenant=request.user.tenant
	tod=date_first.date.today()
	prev=tod-date_first.timedelta(days=30)
	invoices=sales_invoice.objects.for_tenant(this_tenant).filter(date__range=[prev,tod])
	line_items=invoice_line_item.objects.filter(sales_invoice__in=invoices).all().prefetch_related("sales_invoice")
	response_data=[]
	for item in line_items:
		response_data.append({'product_name': item.product_name,'quantity': item.quantity*item.unit_multi,\
        	'cgst_percent':item.cgst_percent,'line_total':item.line_total, 'invoice_no':item.sales_invoice.invoice_id,\
        	'customer_name':item.sales_invoice.customer_name})

	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)


@login_required
def customer_wise_sales(request):
	return render(request,'sales/customer_wise_sales.html', {'extension': 'base.html'})


@login_required
def customer_wise_sales_data(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		customerid = request.GET.get('customerid')
		start=request.GET.get('start')
		end=request.GET.get('end')
		# page_no=1
		# end=date_first.date.today()
		# start=end-date_first.timedelta(days=120)
		invoices=sales_invoice.objects.for_tenant(this_tenant).filter(date__range=[start,end], customer=customerid)

		all_items=invoice_line_item.objects.for_tenant(this_tenant).filter(sales_invoice__in = invoices).select_related('product').\
							values('product', 'product_name').annotate(taxable_value=Sum('line_tax'), total_amount=Sum('line_total'), \
								quantities=Sum(F('quantity') * F('unit_multi'))).order_by('product')
		
	response_data={}
	# if page_no:
		# response_data =  paginate_data(page_no, 10, list(all_items))
	# else:
	response_data['object']=list(all_items)
		
	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)


	
@login_required
def hsn_report(request):
	extension="base.html"
	return render (request, 'sales/hsn_report.html',{'extension':extension})

@api_view(['GET'],)
def get_hsn_report(request):
	this_tenant=request.user.tenant
	calltype=request.GET.get('calltype')
	response_data={}
	if (calltype == 'apply_filter'):
		start=request.GET.get('start')
		end=request.GET.get('end')
		invoices=sales_invoice.objects.for_tenant(this_tenant).filter(date__range=[start,end]).all()
		all_items=invoice_line_item.objects.for_tenant(this_tenant).filter(sales_invoice__in = invoices).values('product_hsn').\
					annotate(taxable_value=Sum('line_tax'), total_amount=Sum('line_total'),cgst_amount=Sum('cgst_value'), \
					igst_amount=Sum('igst_value'), quantities=Sum(F('quantity') * F('unit_multi')) - Sum(F('quantity_returned') * F('unit_multi'))).\
					order_by('product_hsn')
	
	response_data['object']=list(all_items)

	jsondata = json.dumps(response_data,cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)


@login_required
def customer_wise_summary(request):
	extension="base.html"
	return render (request, 'sales/customer_wise_summary.html',{'extension':extension})

@api_view(['GET'],)
def get_customer_wise_summary(request):
	this_tenant=request.user.tenant
	response_data={}
	if request.method == 'GET':
		start=request.GET.get('start')
		end=request.GET.get('end')

		invoices=sales_invoice.objects.for_tenant(this_tenant).filter(date__range=[start,end]).values('customer', 'customer_name').\
				annotate(total_sales=Sum('total'), total_paid=Sum('amount_paid') )
	
	response_data['object']=list(invoices)

	jsondata = json.dumps(response_data,cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

@api_view(['GET'],)
def group_sales_report_select(request):
	extension="base.html"
	return render (request, 'sales/sales_report_select.html',{'extension':extension})

@api_view(['GET'],)
def get_group_sales_report_select(request):
	from django.db.models.functions import TruncMonth
	this_tenant = request.user.tenant
	response_data={}
	calltype = request.GET.get('calltype')
	start=request.GET.get('start')
	end=request.GET.get('end')

	if (calltype == 'monthwise'):
		invoices=sales_invoice.objects.for_tenant(this_tenant).filter(date__range=[start,end])\
			.annotate(month=TruncMonth('date')).values('month').annotate(total_sales=Sum('total'), total_paid=Sum('amount_paid'))
	
	elif (calltype == 'zonewise'):
		invoices=sales_invoice.objects.for_tenant(this_tenant).filter(date__range=[start,end])\
			.values('customer__zone__name').annotate(total_sales=Sum('total'), total_paid=Sum('amount_paid'))
	
	elif (calltype == 'datewise'):
		invoices=sales_invoice.objects.for_tenant(this_tenant).filter(date__range=[start,end])\
			.values('date').annotate(total_sales=Sum('total'), total_paid=Sum('amount_paid'))

	elif (calltype == 'customerwise'):
		invoices=sales_invoice.objects.for_tenant(this_tenant).filter(date__range=[start,end])\
			.values('customer', 'customer_name').annotate(total_sales=Sum('total'), total_paid=Sum('amount_paid'))

	response_data['object']=list(invoices)

	jsondata = json.dumps(response_data,cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)