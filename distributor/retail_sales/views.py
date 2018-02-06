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

from distributor_master.models import Unit, Product, Customer, Warehouse, product_sales_rate
from distributor_inventory.models import Inventory
from distributor_account.models import Account, tax_transaction, account_inventory, account_year_inventory, accounting_period, Journal,journal_entry,\
								journal_inventory, journal_entry_inventory, account_year, payment_mode
from distributor_account.journalentry import new_journal, new_journal_entry
from distributor_inventory.models import Inventory, inventory_ledger, warehouse_valuation
from distributor.variable_list import small_large_limt

from distributor.global_utils import paginate_data, new_tax_transaction_register
from .sales_utils import *
from .models import *

TWOPLACES = Decimal(10) ** -2

@login_required
def new_sales_invoice(request):
	return render(request,'retail_sales/invoice.html', {'extension': 'base.html'})

@api_view(['GET',],)
def get_payment_mode(request):
	payment_modes=list(payment_mode.objects.for_tenant(request.user.tenant).exclude(name__in=["Vendor Debit", "Customer Credit"]).\
				values('id','name', 'default').order_by('-default'))
	jsondata = json.dumps(payment_modes,  cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

@api_view(['GET','POST'],)
def get_product(request):
	this_tenant=request.user.tenant
	if request.method == "GET":
		q = request.GET.get('term', '')
		products = Product.objects.for_tenant(this_tenant).filter(name__istartswith  = q )[:50].select_related('default_unit', \
			'cgst', 'sgst')
		response_data = []
		for item in products:
			item_json = {}
			item_json['id'] = item.id
			item_json['label'] = item.name
			item_json['unit_id'] = item.default_unit.id
			item_json['unit'] = item.default_unit.symbol
			item_json['unit_multiplier'] = item.default_unit.multiplier
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
			response_data.append(item_json)
		data = json.dumps(response_data, cls=DjangoJSONEncoder)
	else:
		data = 'fail'
	mimetype = 'application/json'
	return HttpResponse(data, mimetype)

@api_view(['GET'],)
def get_product_inventory(request):
	this_tenant=request.user.tenant
	response_data={}
	if request.method == "GET":
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

@api_view(['GET'],)
def get_product_barcode(request):
	this_tenant=request.user.tenant
	response_data={}

	if request.method == 'GET':
		try:
			product_barcode = request.GET.get('product_barcode')
			warehouse_id = request.GET.get('warehouse_id')
			
			product_data=Product.objects.for_tenant(this_tenant).get(barcode=product_barcode)
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
	
	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)


@api_view(['POST'],)
def sales_invoice_save(request):
	if request.method == 'POST':
		calltype = request.data.get('calltype')
		response_data = {}
		this_tenant=request.user.tenant
		if (calltype == 'save' or calltype == 'mobilesave'):
			# try:
			with transaction.atomic():
				# with transaction.atomic():
				try:
					date = date_first.date.today()
					if (calltype == 'save'):
						bill_data = json.loads(request.data.get('bill_details'))
					else:
						bill_data = request.data.get('bill_details')
					
					customer_phone = request.data.get('customer_phone')
					customer_name = request.data.get('customer_name')
					customer_address = request.data.get('customer_address')
					customer_email = request.data.get('customer_email')
					customer_gender = request.data.get('customer_gender')
					customer_dob = request.data.get('customer_dob')
					
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
						
						try:
							discount_amount=Decimal(data['discount_amount']).quantize(TWOPLACES)
						except:
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

						product=Product.objects.for_tenant(this_tenant).select_related('tax').get(id=productid)
								
						unit=Unit.objects.for_tenant(this_tenant).get(id=unitid)
						multiplier=unit.multiplier
						
						# original_actual_sales_price=Decimal(data['sales'])
						original_actual_sales_price = Decimal(data['sales_after_tax']).quantize(TWOPLACES)
						actual_sales_price=Decimal(original_actual_sales_price/multiplier)
						
						original_quantity=Decimal(data['quantity']).quantize(TWOPLACES)
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
									inventory_data={'date':item.purchase_date, 'quantity':original_available, \
													'pur_rate':item.purchase_price}
									price_list_list.append(inventory_data)
									price_list[i]={'date':item.purchase_date,\
												'quantity':original_available, 'pur_rate':item.purchase_price}
									total_purchase_price+=original_available*item.purchase_price
									quantity_updated-=original_available
									
								else:
									item.quantity_available-=quantity_updated
									products_cost+=item.purchase_price*quantity_updated
									item.save()
									inventory_data={'date':item.purchase_date, 'quantity':quantity_updated,\
													'pur_rate':item.purchase_price}
									price_list_list.append(inventory_data)
									price_list[i]={'date':item.purchase_date,\
												'quantity':quantity_updated, 'pur_rate':item.purchase_price}
									total_purchase_price+=quantity_updated*item.purchase_price
									quantity_updated=0								
							if (quantity_updated>0):
								raise IntegrityError(('Quantity Not Available for: '+product.name))
							price_list_dict['detail']=price_list_list
							price_list_json = json.dumps(price_list_dict,  cls=DjangoJSONEncoder)

						LineItem = invoice_line_item()
						LineItem.retail_invoice = new_invoice
						LineItem.product= product
						LineItem.product_name= product.name
						LineItem.product_sku=product.sku
						LineItem.product_hsn=product.hsn_code
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
						# if (product.has_batch):
						# 	LineItem.batch=batch
						# 	LineItem.manufacturing_date=manufacturing_date
						# 	LineItem.expiry_date=expiry_date
						# if (product.has_instance):
						# 	LineItem.serial_no=serial_no
						
						LineItem.sales_price=original_actual_sales_price
						
						if maintain_inventory:
							LineItem.other_data=price_list_json
						LineItem.discount_amount=discount_amount
						# LineItem.line_before_tax=line_total - cgst_v - sgst_v
						LineItem.line_before_tax=line_taxable_total
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
							
						
						# if (cgst_p in sgst_paid):
						# 	cgst_paid[cgst_p]+=cgst_v
						# else:
						# 	cgst_paid[cgst_p]=cgst_v
						# if (sgst_p in sgst_paid):
						# 	sgst_paid[sgst_p]+=sgst_v
						# else:
						# 	sgst_paid[sgst_p]=sgst_v

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
								new_tax_transaction_register("CGST",5, k, v[0],v[1],v[2], new_invoice.id, \
									new_invoice.invoice_id, date, this_tenant, False, customer_gst=None, customer_state=ware_state)
						except:
							pass

					for k,v in sgst_paid.items():
						try:
							if v[2]>0:
								new_tax_transaction_register("SGST",5, k, v[0],v[1],v[2], new_invoice.id,\
									new_invoice.invoice_id, date, this_tenant, False, customer_gst=None, customer_state=ware_state)
						except:
							pass

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

					if maintain_inventory:
						new_invoice.total_purchase_price = total_purchase_price
						new_invoice.save()
						warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).get(warehouse=warehouse)
						warehouse_valuation_change.valuation-=total_purchase_price
						warehouse_valuation_change.save()
						
						inventory_acct=account_inventory.objects.for_tenant(this_tenant).get(name__exact="Inventory")
						acct_period=accounting_period.objects.for_tenant(this_tenant).get(start__lte=date, end__gte=date)
						inventory_acct_year=account_year_inventory.objects.for_tenant(this_tenant).\
											get(account_inventory=inventory_acct, accounting_period = acct_period)
						inventory_acct_year.current_debit-=total_purchase_price
						inventory_acct_year.save()

						new_journal_inv=journal_inventory()
						new_journal_inv.date=date
						new_journal_inv.transaction_bill_id=new_invoice.id
						new_journal_inv.trn_type=7
						new_journal_inv.tenant=this_tenant
						new_journal_inv.save()
						new_entry_inv=journal_entry_inventory()
						new_entry_inv.transaction_type=1
						new_entry_inv.journal=new_journal_inv
						new_entry_inv.account=inventory_acct
						new_entry_inv.value=-total_purchase_price
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


					response_data['pk']=new_invoice.id
					response_data['id']=new_invoice.invoice_id
			# except Exception as err:
			# 	response_data  = err.args 
			# 	transaction.rollback()
				except Exception as err:
					response_data  = err.args 
					transaction.rollback()

		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)


#This is used bth in app & website. Change to POST before prodcution.
@api_view(['GET'],)
def sales_invoice_delete(request):
		if request.method == 'GET':
			calltype = request.GET.get('calltype')
			response_data = {}
			this_tenant=request.user.tenant
			if (calltype == 'delete'):
				# response_data = delete_inventory(request)
				with transaction.atomic():
					try:
						invoice_pk=request.GET.get('invoice_id')
						old_invoice=retail_invoice.objects.for_tenant(this_tenant).get(id=invoice_pk)
		
						all_line_items=invoice_line_item.objects.for_tenant(this_tenant).filter(retail_invoice=old_invoice)
						
						#Does this tenant maintain inventory?
						maintain_inventory=this_tenant.maintain_inventory
						total_purchase_price=0
						#saving the invoice_line_item and linking them with foreign key to receipt

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
									total_purchase_price+=Decimal(each_item['quantity'])*Decimal(each_item['pur_rate'])
									inventory=Inventory()
									inventory.product=productid
									inventory.warehouse=old_invoice.warehouse
									inventory.purchase_quantity=Decimal(each_item['quantity'])
									inventory.quantity_available=Decimal(each_item['quantity'])
									inventory.purchase_date=each_item['date']
									inventory.purchase_price=Decimal(each_item['pur_rate'])
									inventory.tentative_sales_price=tentative_sales_price
									inventory.mrp=mrp
									inventory.tenant=this_tenant
									inventory.save()

							#Update Warehouse Valuation
							warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).get(warehouse=old_invoice.warehouse)
							warehouse_valuation_change.valuation+=total_purchase_price
							warehouse_valuation_change.save()
								
							# delete inventory_ledger() - only if you maintain inventory
							inventory_ledger.objects.for_tenant(this_tenant).filter(date=old_invoice.date,transaction_type=9,\
									transaction_bill_id=old_invoice.invoice_id).delete()
						
						# delete tax_transaction
						tax_transaction.objects.for_tenant(this_tenant).filter(date=old_invoice.date,transaction_type=5,\
									transaction_bill_id=old_invoice.id).delete()
						#delete old line items
						all_line_items.delete()

						#delete all journal entries
						old_journal=Journal.objects.for_tenant(this_tenant).get(trn_type=7, transaction_bill_id=old_invoice.id)
						# Update the current balance of all journal related accounts
						journal_line_items=journal_entry.objects.for_tenant(this_tenant).filter(journal=old_journal)
						acct_period = accounting_period.objects.for_tenant(this_tenant).get(start__lte=old_journal.date, end__gte=old_journal.date)
						
						for item in journal_line_items:
							trn_type = item.transaction_type
							account = item.account
							account_journal_year=account_year.objects.get(account=account, accounting_period = acct_period)
							if (trn_type == 1):
								account_journal_year.current_debit=account_journal_year.current_debit-item.value
							elif (trn_type == 2):
								account_journal_year.current_credit=account_journal_year.current_credit-item.value
							account_journal_year.save()
						old_journal.delete()
						
						#delete all inventory journal entries
						old_journal_inv=journal_inventory.objects.for_tenant(this_tenant).filter(trn_type=7, transaction_bill_id=old_invoice.id)
						# Update the current balance of all inventory journal related accounts
						journal_inv_line_items = journal_entry_inventory.objects.for_tenant(this_tenant).filter(journal__in=old_journal_inv)
						for item in journal_inv_line_items:
							inventory_acct = item.account
							account_journal_year=account_year_inventory.objects.get(account_inventory=inventory_acct, accounting_period = acct_period)
							if (trn_type == 1):
								account_journal_year.current_debit=account_journal_year.current_debit-item.value
							elif (trn_type == 2):
								account_journal_year.current_credit=account_journal_year.current_credit-item.value
							account_journal_year.save()
						
						old_journal_inv.delete()
						# raise IntegrityError

						old_invoice.delete()

						response_data['success'] = True
					except:
						transaction.rollback()

			jsondata = json.dumps(response_data)
			return HttpResponse(jsondata)


@api_view(['GET'],)
def sales_invoice_edit_view(request):
	return render(request,'retail_sales/edit_invoice.html', {'extension': 'base.html'})


@api_view(['POST'],)
def sales_invoice_edit(request):
		if request.method == 'POST':
			calltype = request.data.get('calltype')
			response_data = {}
			this_tenant=request.user.tenant
			if (calltype == 'edit' or calltype == 'mobileedit'):
				# response_data = delete_inventory(request)
				with transaction.atomic():
					try:
						invoice_pk=request.data.get('invoice_pk')
						old_invoice=retail_invoice.objects.for_tenant(this_tenant).get(id=invoice_pk)

						all_line_items=invoice_line_item.objects.for_tenant(this_tenant).filter(retail_invoice=old_invoice)
						
						#Does this tenant maintain inventory?
						maintain_inventory=this_tenant.maintain_inventory
						total_purchase_price=0
						#saving the invoice_line_item and linking them with foreign key to receipt

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
									total_purchase_price+=Decimal(each_item['quantity'])*Decimal(each_item['pur_rate'])
									inventory=Inventory()
									inventory.product=productid
									inventory.warehouse=old_invoice.warehouse
									inventory.purchase_quantity=Decimal(each_item['quantity'])
									inventory.quantity_available=Decimal(each_item['quantity'])
									inventory.purchase_date=each_item['date']
									inventory.purchase_price=Decimal(each_item['pur_rate'])
									inventory.tentative_sales_price=tentative_sales_price
									inventory.mrp=mrp
									inventory.tenant=this_tenant
									inventory.save()

							#Update Warehouse Valuation
							warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).get(warehouse=old_invoice.warehouse)
							warehouse_valuation_change.valuation+=total_purchase_price
							warehouse_valuation_change.save()
								
							# delete inventory_ledger() - only if you maintain inventory
							inventory_ledger.objects.for_tenant(this_tenant).filter(date=old_invoice.date,transaction_type=9,\
									transaction_bill_id=old_invoice.invoice_id).delete()
						
						# delete tax_transaction
						tax_transaction.objects.for_tenant(this_tenant).filter(date=old_invoice.date,transaction_type=5,\
									transaction_bill_id=old_invoice.id).delete()
						#delete old line items
						all_line_items.delete()

						#delete all journal entries
						old_journal=Journal.objects.for_tenant(this_tenant).get(trn_type=7, transaction_bill_id=old_invoice.id)
						# Update the current balance of all journal related accounts
						journal_line_items=journal_entry.objects.for_tenant(this_tenant).filter(journal=old_journal)
						acct_period = accounting_period.objects.for_tenant(this_tenant).get(start__lte=old_journal.date, end__gte=old_journal.date)
						
						for item in journal_line_items:
							trn_type = item.transaction_type
							account = item.account
							account_journal_year=account_year.objects.get(account=account, accounting_period = acct_period)
							if (trn_type == 1):
								account_journal_year.current_debit=account_journal_year.current_debit-item.value
							elif (trn_type == 2):
								account_journal_year.current_credit=account_journal_year.current_credit-item.value
							account_journal_year.save()
						old_journal.delete()
						
						#delete all inventory journal entries
						old_journal_inv=journal_inventory.objects.for_tenant(this_tenant).filter(trn_type=7, transaction_bill_id=old_invoice.id)
						# Update the current balance of all inventory journal related accounts
						journal_inv_line_items = journal_entry_inventory.objects.for_tenant(this_tenant).filter(journal__in=old_journal_inv)
						for item in journal_inv_line_items:
							inventory_acct = item.account
							account_journal_year=account_year_inventory.objects.get(account_inventory=inventory_acct, accounting_period = acct_period)
							if (trn_type == 1):
								account_journal_year.current_debit=account_journal_year.current_debit-item.value
							elif (trn_type == 2):
								account_journal_year.current_credit=account_journal_year.current_credit-item.value
							account_journal_year.save()
						
						old_journal_inv.delete()
						# raise IntegrityError

						# old_invoice.delete()

						#Edit Invoice with new data

						if (calltype == 'edit'):
							bill_data = json.loads(request.data.get('bill_details'))
						else:
							bill_data = request.data.get('bill_details')
						
						# if (paymentmode_id):
						# 	payment_mode_selected=payment_mode.objects.for_tenant(this_tenant).get(id=paymentmode_id)
						# else:
						# 	payment_mode_selected=payment_mode.objects.for_tenant(this_tenant).get(default=True)
						
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
						
						old_invoice.subtotal=subtotal
						old_invoice.cgsttotal=cgsttotal
						old_invoice.sgsttotal=sgsttotal
						# new_invoice.taxtotal=taxtotal
						
						#This will provide the details, whether this is B2CL or B2CS
						# if (subtotal<small_large_limt):
						# 	new_invoice.gst_type=3
						# else:
						# 	new_invoice.gst_type=2
						

						old_invoice.roundoff = roundoff
						old_invoice.total = total
						old_invoice.amount_paid = total
						old_invoice.save()
						
						products_cost=0
						
						vat_paid={}
						cgst_paid={}
						sgst_paid={}
						
						cgst_total=0
						sgst_total=0
						
						#Does this tenant maintain inventory?
						maintain_inventory=this_tenant.maintain_inventory
						total_purchase_price=0
						date = old_invoice.date

						warehouse = old_invoice.warehouse
						ware_address=warehouse.address_1+", "+warehouse.address_2
						ware_state=warehouse.state
						ware_city=warehouse.city
						ware_pin=warehouse.pin

						paymentmode_id = old_invoice.payment_mode_id

						payment_mode_selected=payment_mode.objects.for_tenant(this_tenant).get(id=paymentmode_id)
						#saving the invoice_line_item and linking them with foreign key to receipt
						for data in bill_data:
							productid=data['product_id']
							unit_name=data['unit_name']
							unit_id=data['unit_id']
							multiplier=Decimal(data['unit_multi']).quantize(TWOPLACES)
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

							product=Product.objects.for_tenant(this_tenant).select_related('tax').get(id=productid)
									
							
							# original_actual_sales_price=Decimal(data['sales'])
							original_actual_sales_price = Decimal(data['sales_before_tax']).quantize(TWOPLACES)
							actual_sales_price=Decimal(original_actual_sales_price/multiplier)
							
							original_quantity=Decimal(data['quantity']).quantize(TWOPLACES)
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
										inventory_data={'date':item.purchase_date, 'quantity':original_available, \
														'pur_rate':item.purchase_price}
										price_list_list.append(inventory_data)
										price_list[i]={'date':item.purchase_date,\
													'quantity':original_available, 'pur_rate':item.purchase_price}
										total_purchase_price+=original_available*item.purchase_price
										quantity_updated-=original_available
										
									else:
										item.quantity_available-=quantity_updated
										products_cost+=item.purchase_price*quantity_updated
										item.save()
										inventory_data={'date':item.purchase_date, 'quantity':quantity_updated,\
														'pur_rate':item.purchase_price}
										price_list_list.append(inventory_data)
										price_list[i]={'date':item.purchase_date,\
													'quantity':quantity_updated, 'pur_rate':item.purchase_price}
										total_purchase_price+=quantity_updated*item.purchase_price
										quantity_updated=0								
								if (quantity_updated>0):
									raise IntegrityError(('Quantity Not Available for: '+product.name))
								price_list_dict['detail']=price_list_list
								price_list_json = json.dumps(price_list_dict,  cls=DjangoJSONEncoder)

							LineItem = invoice_line_item()
							LineItem.retail_invoice = old_invoice
							LineItem.product= product
							LineItem.product_name= product.name
							LineItem.product_sku=product.sku
							LineItem.product_hsn=product.hsn_code
							LineItem.date = date
							LineItem.cgst_percent=cgst_p
							LineItem.cgst_value=cgst_v
							LineItem.sgst_percent=sgst_p
							LineItem.sgst_value=sgst_v
							LineItem.is_tax_included=is_tax
							
							LineItem.unit=unit_name
							LineItem.unit_id=unit_id
							LineItem.unit_multi=multiplier
							LineItem.quantity=original_quantity
							
							# if (product.has_batch):
							# 	LineItem.batch=batch
							# 	LineItem.manufacturing_date=manufacturing_date
							# 	LineItem.expiry_date=expiry_date
							# if (product.has_instance):
							# 	LineItem.serial_no=serial_no
							
							LineItem.sales_price=original_actual_sales_price
							
							if maintain_inventory:
								LineItem.other_data=price_list_json
							LineItem.discount_amount=discount_amount
							# LineItem.line_before_tax=line_total - cgst_v - sgst_v
							LineItem.line_before_tax=line_taxable_total
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
									new_inventory_ledger.transaction_bill_id=old_invoice.invoice_id
									new_inventory_ledger.tenant=this_tenant
									new_inventory_ledger.save()

							# if (cgst_p in sgst_paid):
							# 	cgst_paid[cgst_p]+=cgst_v
							# else:
							# 	cgst_paid[cgst_p]=cgst_v
							# if (sgst_p in sgst_paid):
							# 	sgst_paid[sgst_p]+=sgst_v
							# else:
							# 	sgst_paid[sgst_p]=sgst_v

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
									new_tax_transaction_register("CGST",5, k, v[0],v[1],v[2], old_invoice.id, \
										old_invoice.invoice_id, date, this_tenant, False, customer_gst=None, customer_state=ware_state)
							except:
								pass

						for k,v in sgst_paid.items():
							try:
								if v[2]>0:
									new_tax_transaction_register("SGST",5, k, v[0],v[1],v[2], old_invoice.id,\
										old_invoice.invoice_id, date, this_tenant, False, customer_gst=None, customer_state=ware_state)
							except:
								pass

						#One more journal entry for COGS needs to be done
						remarks="Retail Invoice No: "+str(old_invoice.invoice_id)
						journal=new_journal(this_tenant, date,"Sales",remarks, trn_id=old_invoice.id, trn_type=7)
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

						if maintain_inventory:

							warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).get(warehouse=warehouse)
							warehouse_valuation_change.valuation-=total_purchase_price
							warehouse_valuation_change.save()

							old_invoice.total_purchase_price = total_purchase_price
							old_invoice.save()
							
							inventory_acct=account_inventory.objects.for_tenant(this_tenant).get(name__exact="Inventory")
							acct_period=accounting_period.objects.for_tenant(this_tenant).get(start__lte=date, end__gte=date)
							inventory_acct_year=account_year_inventory.objects.for_tenant(this_tenant).\
												get(account_inventory=inventory_acct, accounting_period = acct_period)
							inventory_acct_year.current_debit-=total_purchase_price
							inventory_acct_year.save()

							new_journal_inv=journal_inventory()
							new_journal_inv.date=date
							new_journal_inv.transaction_bill_id=old_invoice.id
							new_journal_inv.trn_type=7
							new_journal_inv.tenant=this_tenant
							new_journal_inv.save()
							new_entry_inv=journal_entry_inventory()
							new_entry_inv.transaction_type=1
							new_entry_inv.journal=new_journal_inv
							new_entry_inv.account=inventory_acct
							new_entry_inv.value=-total_purchase_price
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


						response_data['pk']=old_invoice.id
						response_data['id']=old_invoice.invoice_id

						response_data['success'] = True
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
		
		line_items=list(invoice_line_item.objects.filter(retail_invoice=invoice['id']).order_by('id').values('id','product_name','product_hsn',\
			'product_id','unit','unit_multi', 'unit_id','quantity','quantity_returned','sales_price','discount_amount','line_before_tax','line_total',\
			'is_tax_included', 'cgst_percent','sgst_percent','igst_percent','cgst_value','sgst_value','igst_value',))
		invoice['line_items']=line_items

		invoice['tenant_name']=this_tenant.name
		
		jsondata = json.dumps(invoice, cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)

@api_view(['GET',],)
def invoice_details_with_no(request):
	this_tenant=request.user.tenant
	invoice_no=request.GET.get('invoice_no')
	if request.method == 'GET':
		invoice=retail_invoice.objects.for_tenant(this_tenant).values('id','invoice_id','date','customer_name',\
			'warehouse_address','warehouse_city', 'warehouse_pin','subtotal','cgsttotal','sgsttotal','roundoff',	\
		'total','amount_paid').get(invoice_id=invoice_no)
		
		line_items=list(invoice_line_item.objects.filter(retail_invoice=invoice['id']).order_by('id').values('id','product_name','product_hsn',\
			'product', 'product_id','unit','unit_multi', 'unit_id','quantity','quantity_returned','sales_price','discount_amount','line_before_tax',\
			'line_total', 'is_tax_included', 'cgst_percent','sgst_percent','igst_percent','cgst_value','sgst_value','igst_value',))
		
		invoice['line_items']=line_items
		invoice['tenant_name']=this_tenant.name
		
		jsondata = json.dumps(invoice, cls=DjangoJSONEncoder)
		# print(jsondata)
		return HttpResponse(jsondata)

@login_required
def invoice_detail_view(request, pk):
	return render(request,'retail_sales/retail_invoice_detail.html', {'extension': 'base.html', 'pk':pk})

@login_required
def invoice_list(request):
	return render(request,'retail_sales/sales_list.html', {'extension': 'base.html'})

#This has to be updated to provide details as needed by the app
@api_view(['GET'],)
def all_invoice_app(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		calltype = request.GET.get('calltype')
		page_no = request.GET.get('page_no')
		end=date_first.date.today()
		start=end-date_first.timedelta(days=3)
		response_data={}
		invoices=retail_invoice.objects.for_tenant(this_tenant).filter(date__range=(start,end)).values('id','invoice_id', \
				'date','total', 'cgsttotal','sgsttotal').order_by('-date', '-invoice_id')
		
			# page_no=1
			# paginator = Paginator(invoices, 3)
			# receipts_paginated=paginator.page(page_no)
			# for item in receipts_paginated:
			# 	print(item)
	response_data = list(invoices)

	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

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
			invoices=retail_invoice.objects.for_tenant(this_tenant).filter(date__range=(start,end)).values('id','invoice_id', \
				'date','total', 'cgsttotal','sgsttotal').order_by('-date', '-invoice_id')
			
			if (page_no == 1 or page_no == str(1)):
				filter_summary = list(invoices.values('payment_mode_id', 'payment_mode_name').order_by('payment_mode_id', 'payment_mode_name',).\
							annotate(value = Sum('total')))
			
			
		elif (calltype == 'apply_filter'):
			start = request.GET.get('start')
			end = request.GET.get('end')
			invoice_no = request.GET.get('invoice_no')
			payment_mode = request.GET.get('payment_mode')
			# groups = json.loads(request.GET.get('groups'))
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

			# if (len(groups)>0):
			# 	groups_list=[]
			# 	for item in groups:
			# 		groups_list.append(item['groupid'])

			# 	products = Product.objects.filter(group__in = groups_list)
			# 	invoices=invoices.filter(invoiceLineItem_salesInvoice__product__in=products)

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
			if (page_no == 1 or page_no == str(1)):
				filter_summary = list(invoices.values('payment_mode_id', 'payment_mode_name').order_by('payment_mode_id', 'payment_mode_name',).\
							annotate(value = Sum('total')))
				filter_data['payment details']=filter_summary
			# filter_data['total_pending'] = filter_summary['pending']
			# filter_data['total_value'] = filter_summary['total_sum']
		
		if page_no:
			response_data =  paginate_data(page_no, 20, list(invoices))
			response_data.update(filter_data)
		else:
			response_data['object']=list(invoices)
			response_data.update(filter_data)
	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)


@login_required
def sales_return_view(request):
	extension='base.html'
	return render(request,'retail_sales/sales_return.html', {'extension': extension})

@api_view(['GET'],)
def get_return_data(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		calltype = request.GET.get('calltype')
		if (calltype == 'Sales Return'):
			invoice_id = request.GET.get('invoice_id')
			response_data=retail_invoice.objects.for_tenant(this_tenant).get(invoice_id=invoice_id).id
		return redirect('retailsales:invoice_details', pk=response_data)

@api_view(['POST'],)
def sales_return_save(request):
	if request.method == 'POST':
		calltype = request.data.get('calltype')
		response_data = {}
		this_tenant=request.user.tenant
		if (calltype == 'save'):
			with transaction.atomic():
				try:
					invoice_id = request.data.get('invoiceid')
					date=request.data.get('date')
					
					subtotal=Decimal(request.data.get('subtotal'))
					cgsttotal=Decimal(request.data.get('cgsttotal'))
					sgsttotal=Decimal(request.data.get('sgsttotal'))
					total=Decimal(request.data.get('total'))
					sum_total = subtotal+cgsttotal+sgsttotal
					if (abs(sum_total - total) <0.90 ):
						total = sum_total
					
					bill_data = json.loads(request.data.get('bill_details'))

					invoice = retail_invoice.objects.for_tenant(this_tenant).get(id=invoice_id)
					
					new_invoice=sales_return()
					new_invoice.tenant=this_tenant
					new_invoice.invoice=invoice

					new_invoice.date = date
					
					# new_invoice.customer=invoice.customer
					# new_invoice.customer_name=invoice.customer_name
					# new_invoice.customer_address=invoice.customer_address
					# new_invoice.customer_state=invoice.customer_state
					# new_invoice.customer_city=invoice.customer_city
					# new_invoice.customer_pin=invoice.customer_pin
					# new_invoice.customer_gst=invoice.customer.gst

					new_invoice.warehouse=invoice.warehouse
					new_invoice.warehouse_address=invoice.warehouse_address
					new_invoice.warehouse_state=invoice.warehouse_state
					new_invoice.warehouse_city=invoice.warehouse_city
					new_invoice.warehouse_pin=invoice.warehouse_pin
					
					new_invoice.subtotal=subtotal
					new_invoice.cgsttotal=cgsttotal
					new_invoice.sgsttotal=sgsttotal
					new_invoice.total = total
			# 		new_invoice.amount_paid = 0
					new_invoice.save()
					
			# 		products_cost=0
					
			# 		vat_paid={}
					cgst_paid={}
					sgst_paid={}
					
					cgst_total=0
					sgst_total=0
					
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
						
						cgst_total+=cgst_v
						sgst_total+=sgst_v
						
						line_item = invoice_line_item.objects.for_tenant(this_tenant).get(id=line_item_id)

						product=Product.objects.for_tenant(this_tenant).select_related('tax').get(id=productid)
								
						unit=line_item.unit
						multiplier=line_item.unit_multi
						
						original_actual_sales_price=Decimal(data['return_price'])
						
						actual_sales_price=Decimal(original_actual_sales_price/multiplier)
						# tentative_sales_price=original_tentative_sales_price/multiplier
						# mrp=original_mrp/multiplier

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
									inventory.quantity_available=total_useful
									inventory.purchase_date=product_item['date']
									inventory.purchase_price=Decimal(product_item['pur_rate'])
									# inventory.tentative_sales_price=line_item.tentative_sales_price
									# inventory.mrp=line_item.mrp
									inventory.tenant=this_tenant
									inventory.save()

									total_purchase_price+=Decimal(product_item['pur_rate'])*total_useful
									
									new_inventory_ledger=inventory_ledger()
									new_inventory_ledger.product=product
									new_inventory_ledger.warehouse=invoice.warehouse
									new_inventory_ledger.transaction_type=10 #Change trn type 
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
						
						LineItem.unit=unit_name
						LineItem.unit_multi=multiplier
						LineItem.quantity=original_quantity
						
			# 			if (product.has_batch):
			# 				LineItem.batch=batch
			# 				LineItem.manufacturing_date=manufacturing_date
			# 				LineItem.expiry_date=expiry_date
			# 			if (product.has_instance):
			# 				LineItem.serial_no=serial_no
						
						LineItem.return_price=original_actual_sales_price
						# LineItem.tentative_sales_price=original_tentative_sales_price
			# 			if maintain_inventory:
			# 				LineItem.other_data=price_list_json
						# LineItem.mrp=original_mrp
						LineItem.line_before_tax=line_taxable_total
						LineItem.line_total=line_total
						LineItem.tenant=this_tenant
						LineItem.save()

						if maintain_inventory:						
							warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).get(warehouse=invoice.warehouse)
							warehouse_valuation_change.valuation+=total_purchase_price
							warehouse_valuation_change.save()

						if (cgst_p in cgst_paid):
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
							new_tax_transaction.transaction_type=6 #Check trn type
							new_tax_transaction.tax_type="CGST"
							new_tax_transaction.tax_percent=k
							new_tax_transaction.tax_value=v
							new_tax_transaction.transaction_bill_id=new_invoice.id
							new_tax_transaction.transaction_bill_no=new_invoice.return_id
							new_tax_transaction.date=date
							new_tax_transaction.tenant=this_tenant
							new_tax_transaction.is_registered = False
							new_tax_transaction.save()

					for k,v in sgst_paid.items():
						if v>0:
							new_tax_transaction=tax_transaction()
							new_tax_transaction.transaction_type=6 #Check trn type
							new_tax_transaction.tax_type="SGST"
							new_tax_transaction.tax_percent=k
							new_tax_transaction.tax_value=v
							new_tax_transaction.transaction_bill_id=new_invoice.id
							new_tax_transaction.transaction_bill_no=new_invoice.return_id
							new_tax_transaction.date=date
							new_tax_transaction.tenant=this_tenant
							new_tax_transaction.is_registered = False
							new_tax_transaction.save()

					remarks="Retail Sales Return No: "+str(new_invoice.return_id)
					journal=new_journal(this_tenant, date,"Sales",remarks,trn_id= new_invoice.id, trn_type=8)
					account= Account.objects.for_tenant(this_tenant).get(name__exact="Sales")
					new_journal_entry(this_tenant, journal, subtotal, account, 1, date)
					
					if (cgst_total>0):
						account= Account.objects.for_tenant(this_tenant).get(name__exact="CGST Output")
						new_journal_entry(this_tenant, journal, cgst_total, account, 1, date)

					if (sgst_total>0):
						account= Account.objects.for_tenant(this_tenant).get(name__exact="SGST Output")
						new_journal_entry(this_tenant, journal, sgst_total, account, 1, date)

					account= Account.objects.for_tenant(this_tenant).get(name__exact="Cash")
					new_journal_entry(this_tenant, journal, total, account, 2, date)

					#Right now it can take in cash. But it must be able to opt for payment mode.
					# account= Account.objects.for_tenant(this_tenant).get(name__exact="Cash")
					# new_journal_entry(this_tenant, journal, total, account, 2, date)
					
					debit = journal.journalEntry_journal.filter(transaction_type=1).aggregate(Sum('value'))
					credit = journal.journalEntry_journal.filter(transaction_type=2).aggregate(Sum('value'))


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
						new_journal_inv.trn_type=8
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
						# new_journal_inv.transactionansaction_bill_id=new_invoice.id
						# new_journal_inv.trn_type=8
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


@api_view(['GET'],)
def eod_sales_data(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		try:
			calltype = request.GET.get('calltype')
		except:
			calltype = 'data'
		
		if (calltype == 'eod_download_csv'):
			response = HttpResponse(content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename="eodReport.csv"'

			writer = csv.writer(response)
			date=request.GET.get('date')
			warehouse=request.GET.get('warehouse_id')
			date=request.GET.get('date')
			invoice=retail_invoice.objects.for_tenant(this_tenant).filter(date=date, warehouse = warehouse)
			line_items=list(invoice_line_item.objects.filter(retail_invoice__in=invoice).select_related('product').order_by('product__name',).\
						values('product__name',).annotate(sold_quantity=Sum('quantity')).annotate(value_sold=Sum('line_before_tax')))

			writer.writerow(['Product Name', 'Quantity Sold', 'Value(Excluding Tax) Sold'])

			for item in line_items:
				writer.writerow([item['product__name'], item['sold_quantity'], item['value_sold']])

			return response

		else:	
			date=request.GET.get('date')
			warehouse=request.GET.get('warehouse')
			# date=date_first.date.today()
			invoice=retail_invoice.objects.for_tenant(this_tenant).filter(date=date, warehouse = warehouse)
			returns=sales_return.objects.for_tenant(this_tenant).filter(date=date, warehouse = warehouse)
			line_items=list(invoice_line_item.objects.filter(retail_invoice__in=invoice).select_related('product').order_by('product__name',).\
						values('product__name',).annotate(sold_quantity=Sum('quantity')).annotate(value_sold=Sum('line_before_tax')))
			return_line_items=list(return_line_item.objects.filter(sales_return__in=returns).select_related('product').order_by('product__name',).\
						values('product__name',).annotate(returned_quantity=Sum('quantity')).annotate(value_returned=Sum('line_before_tax')))
			line_items.extend(return_line_items)
			jsondata = json.dumps(line_items, cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)

@login_required
def eod_sales_report(request):
	extension = 'base.html'
	return render(request,'retail_sales/eod_sales.html', {'extension': extension})


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
		invoices=retail_invoice.objects.for_tenant(this_tenant).all()
		line_items=invoice_line_item.objects.for_tenant(this_tenant).filter(retail_invoice__in=invoices)
		total_overall=0
		for item in line_items:
			total_pur=0
			product_items=json.loads(item.other_data)['detail']
			for i in product_items:
				total_pur += Decimal(i['pur_rate'])*Decimal(i['quantity'])
			response_data.append({'invoice_no':item.retail_invoice.invoice_id,'product':item.product_name,'quantity':item.quantity,\
					'sales': item.line_before_tax, 'purchase': total_pur,})
			total_overall+=total_pur
		response_data.append({'total_overall': total_overall})
		
		
	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)


@api_view(['GET',],)
def sales_summary_graph(request):
	this_tenant=request.user.tenant
	try:
		days = int(request.GET.get('days'))
	except:
		days=5
	end=date_first.date.today()
	start=end-date_first.timedelta(days=days)
	sales_daily=retail_sales_day_wise(start, end, this_tenant)
	jsondata = json.dumps(sales_daily, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

@api_view(['GET'],)
def billsummary_profit(request):
	extension="base.html"
	return render (request, 'sales/billsummary_profit.html',{'extension':extension})

@api_view(['GET'],)
def billsummary_profit_data(request):
	this_tenant=request.user.tenant
	response_data={}
	if request.method == 'GET':
		start = request.GET.get('start')
		end = request.GET.get('end')
		calltype = request.GET.get('calltype')
		filtertype = request.GET.get('filtertype')

		if (calltype == 'product_wise'):
			productid = request.GET.get('productid')
			products = Product.objects.filter(id = productid)

		elif (calltype == 'manufacturer_wise'):
			manufacturerid = request.GET.get('manufacturerid')
			manufacs = Manufacturer.objects.get(id = manufacturerid)
			products = Product.objects.filter(manufaturer = manufacs)

		if (filtertype == 'filter'):
			pass
		else:
			invoices=list(sales_invoice.objects.for_tenant(this_tenant).filter(date__range=[start,end]).\
					values('id','invoice_id', 'subtotal', 'date','customer', 'customer_name', 'total'))
			
			for invoice in invoices:
				total_purchase = 0
				lines = invoice_line_item.objects.filter(sales_invoice=invoice['id'])
				for line in lines:
					items = json.loads(line.other_data)['detail']
					for i in items:
						total_purchase+=Decimal(i['pur_rate'])*Decimal(i['quantity'])
				invoice['purchase']=total_purchase
	
	response_data['object'] = invoices

	jsondata = json.dumps(response_data,cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

