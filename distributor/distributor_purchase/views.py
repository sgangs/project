import json
# import datetime
from datetime import date, timedelta

from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError, transaction
from django.db.models import Sum, F
from django.shortcuts import render
from django.http import HttpResponse

from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from distributor_master.models import Unit, Product, Vendor, Warehouse
from distributor_account.models import Account, tax_transaction, payment_mode,accounting_period, Journal, journal_entry, account_year,\
									account_inventory, account_year_inventory, journal_inventory, journal_entry_inventory
from distributor_account.journalentry import new_journal, new_journal_entry
from distributor_inventory.models import Inventory, inventory_ledger, warehouse_valuation
from distributor_inventory.inventory_utils import create_new_inventory_ledger

from distributor.global_utils import paginate_data, new_tax_transaction_register
from .purchase_utils import *
from .serializers import *
from .models import *
from .excel_download import *

# @login_required
@api_view(['GET','POST'],)
def get_product(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		q = request.GET.get('term', '')
		calltype=request.GET.get('calltype')
		if (calltype == 'product_id'):
			prod_id=request.GET.get('productid')
			product = Product.objects.for_tenant(this_tenant).get(id=prod_id)
						# select_related('default_unit', 'tax')
			response_data = []
			item_json = {}
			item_json['id'] = product.id
			item_json['label'] = product.name
			item_json['unit_id'] = product.default_unit.id
			item_json['unit'] = product.default_unit.symbol
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
			data = json.dumps(response_data)
		else:
			products = Product.objects.for_tenant(this_tenant).filter(name__icontains  = q )[:8].\
						select_related('default_unit', 'tax')
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

@api_view(['GET'],)
def get_product_data_id(request):
	this_tenant=request.user.tenant
	response_data={}
	if request.method == 'GET':
		try:
			product_id = request.GET.get('product_id')
			product = Product.objects.for_tenant(this_tenant).get(id=product_id)
						# select_related('default_unit', 'tax')
			response_data['product_name'] = product.name
			response_data['product_id'] = product.id
			response_data['unit_id'] = product.default_unit.id
			response_data['unit'] = product.default_unit.symbol
			try:
				response_data['cgst'] = product.cgst.percentage
			except:
				response_data['cgst'] = 0
			try:
				response_data['sgst'] = product.sgst.percentage
			except:
				response_data['sgst'] = 0
			
			# try:
			# 	response_data['igst'] = item.igst.percentage
			# except:
			# 	response_data['igst'] = 0

			# response_data.append(item_json)

		except:
			response_data['error']='Product Does not exist'			
	
	jsondata = json.dumps(response_data,  cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)


@api_view(['GET'],)
def get_product_data_barcode(request):
	this_tenant=request.user.tenant
	response_data={}
	if request.method == 'GET':
		try:
			product_barcode = request.GET.get('product_barcode')
			product = Product.objects.for_tenant(this_tenant).get(barcode=product_barcode)
						# select_related('default_unit', 'tax')
			response_data['product_name'] = product.name
			response_data['product_id'] = product.id
			response_data['unit_id'] = product.default_unit.id
			response_data['unit'] = product.default_unit.symbol
			try:
				response_data['cgst'] = product.cgst.percentage
			except:
				response_data['cgst'] = 0
			try:
				response_data['sgst'] = product.sgst.percentage
			except:
				response_data['sgst'] = 0
			
			# try:
			# 	response_data['igst'] = item.igst.percentage
			# except:
			# 	response_data['igst'] = 0

			# response_data.append(item_json)

		except:
			response_data['error']='Product Does not exist'			
	
	jsondata = json.dumps(response_data,  cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)


@api_view(['GET'],)
def product_inventory_details(request):
	this_tenant=request.user.tenant
	if request.is_ajax():
		product_id = request.GET.get('product_id')
		warehouse_id = request.GET.get('warehouse_id')
		product_quantity=list(Inventory.objects.for_tenant(this_tenant).filter(quantity_available__gt=0,\
					product=product_id, warehouse=warehouse_id).values('purchase_price','tentative_sales_price','mrp').\
					annotate(available=Sum('quantity_available')))
	
	jsondata = json.dumps(product_quantity,  cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

@api_view(['GET'],)
def purchase_receipt_new(request):
	return render(request,'purchase/purchase_receipt.html', {'extension': 'base.html'})

@api_view(['GET'],)
def purchase_receipt_new_noninventory(request):
	return render(request,'purchase/purchase_receipt_noninventy.html', {'extension': 'base.html'})
	
@api_view(['GET','POST'],)
def purchase_receipt_save(request):
	if request.method == 'POST':
		calltype = request.data.get('calltype')
		response_data = {}
		this_tenant=request.user.tenant
		from_purchase_order = False
		#saving the receipt
		if (calltype == 'save' or 'mobilesave'):
			calledfrom = request.data.get('calledfrom')
			if (calledfrom == 'purchaseorder'):
				from_purchase_order = True
			with transaction.atomic():
				try:
					supplier_invoice=request.data.get('supplier_invoice')
					vendor_id = request.data.get('vendor')
					warehouse_id=request.data.get('warehouse')
					date=request.data.get('date')

					is_igst=request.data.get('is_igst')

					if (is_igst == 'true' or is_igst == True):
						is_igst = True
					else:
						is_igst = False
					# is_igst = False
					# grand_discount_type=request.data.get('grand_discount_type')
					# try:
					# 	grand_discount_value=Decimal(request.data.get('grand_discount_value'))
					# except:
					# 	grand_discount_value=0
					subtotal=Decimal(request.data.get('subtotal'))
					cgsttotal=Decimal(request.data.get('cgsttotal'))
					sgsttotal=Decimal(request.data.get('sgsttotal'))
					igsttotal=Decimal(request.data.get('igsttotal'))
					round_value=Decimal(request.data.get('round_value'))
					total=Decimal(request.data.get('total'))
					sum_total = subtotal+cgsttotal+sgsttotal
					
					date=request.data.get('date')
					# if (abs(sum_total - total) <0.90 ):
					# 	total = sum_total
					duedate=request.data.get('duedate')

					if (calltype == 'save'):
						bill_data = json.loads(request.data.get('bill_details'))
					else:
						bill_data = request.data.get('bill_details')
						
					order_id=None

					if (from_purchase_order):
						order_pk = request.data.get('order_pk')
						order = purchase_order.objects.for_tenant(this_tenant).get(id=order_pk)
						vendor = order.vendor
						warehouse = order.warehouse
						order_id = order.id
					else:
						vendor = Vendor.objects.for_tenant(this_tenant).get(id=vendor_id)
						warehouse = Warehouse.objects.for_tenant(this_tenant).get(id=warehouse_id)
					
					vendor.current_balance+= total
					vendor.save

					
					new_receipt=new_purchase_receipt(this_tenant, supplier_invoice, vendor, warehouse, date, duedate,\
							subtotal, cgsttotal, sgsttotal, igsttotal, round_value, total, 0, from_purchase_order, order_id, inventory_type=True)
					
					cgst_paid={}
					sgst_paid={}
					igst_paid={}
					cgst_total=0
					sgst_total=0
					igst_total=0

					vendor_gst=vendor.gst
					vendor_state=vendor.state
					total_purchase_price = 0

				#saving the receipt_line_item and linking them with foreign key to receipt
					for data in bill_data:
						productid=data['product_id']
						if (from_purchase_order):
							order_line_item_id=data['order_line_item_id']
							order_line_item_data = order_line_item.objects.for_tenant(this_tenant).get(id = order_line_item_id)
							unitid=order_line_item_data.unit_id
						else:
							unitid=data['unit_id']
						
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

						try:
							cgst_p=Decimal(data['cgst_p'])
							cgst_v=Decimal(data['cgst_v'])
							sgst_p=Decimal(data['sgst_p'])
							sgst_v=Decimal(data['sgst_v'])
						except:
							cgst_p=0
							cgst_v=0
							sgst_p=0
							sgst_v=0
						try:
							igst_p=Decimal(data['igst_p'])
							igst_v=Decimal(data['igst_v'])
						except:
							igst_p=0
							igst_v=0

						cgst_total+=cgst_v
						sgst_total+=sgst_v
						igst_total+=igst_v

						line_taxable_total=Decimal(data['taxable_total'])
						line_total=Decimal(data['line_total'])
						
						if (from_purchase_order):
							product = order_line_item_data.product
							order_multiplier = order_line_item_data.unit_multi
							order_qty_avialable = (order_line_item_data.quantity - order_line_item_data.quantity_delivered) * order_multiplier
						else:
							product=Product.objects.for_tenant(request.user.tenant).get(id=productid)
						
						unit=Unit.objects.for_tenant(this_tenant).get(id=unitid)
						multiplier=unit.multiplier
						
						original_purchase_price=Decimal(data['purchase'])
						
						try:
							original_free_with_tax=Decimal(data['free_tax'])
						except:
							original_free_with_tax=0

						try:
							original_tentative_sales_price=Decimal(data['sales'])
						except:
							original_tentative_sales_price=0
						try:
							original_mrp=Decimal(data['mrp'])
						except:
							original_mrp=0
						
						purchase_price=Decimal(original_purchase_price/multiplier)
						tentative_sales_price=original_tentative_sales_price/multiplier
						mrp=original_mrp/multiplier

						# original_quantity=Decimal(data['quantity']) + Decimal(0.000)
						original_quantity=Decimal(data['quantity'])
						quantity=original_quantity*multiplier
						if (from_purchase_order):
							if ((quantity) > (order_qty_avialable)):
								raise IntegrityError (('Receipt quantity of product : '+product.name+' more than avialble order quantity.'))
						
						free_with_tax=original_free_with_tax*multiplier
						free_without_tax=0
						total_free=free_without_tax+free_with_tax
						

						if (from_purchase_order):
							order_line_item_data.quantity_delivered+=original_quantity
							if (order_line_item_data.quantity_delivered > order_line_item_data.quantity):
								raise IntegrityError (('Receipt quantity of product : '+product.name+' more than avialble order quantity.'))
							order_line_item_data.save()

						LineItem = receipt_line_item()
						LineItem.purchase_receipt = new_receipt
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
						LineItem.free_with_tax=original_free_with_tax
						# print(LineItem.quantity)
						# print(type(LineItem.quantity))
						if (product.has_batch):
							LineItem.batch=batch
							LineItem.manufacturing_date=manufacturing_date
							LineItem.expiry_date=expiry_date
						if (product.has_instance):
							LineItem.serial_no=serial_no
						
						LineItem.purchase_price=original_purchase_price
						LineItem.tentative_sales_price=original_tentative_sales_price
						LineItem.mrp=original_mrp
						LineItem.discount_type=discount_type
						LineItem.discount_value=discount_value
						LineItem.discount2_type=discount_type_2
						LineItem.discount2_value=discount_value_2
						LineItem.line_tax=line_taxable_total
						LineItem.line_total=line_total
						LineItem.tenant=this_tenant
						LineItem.save()
						# There will be multiple effects in the inventory
						if this_tenant.maintain_inventory:
							inventory=Inventory()
							inventory.product=product
							inventory.warehouse=warehouse
							inventory.purchase_quantity=quantity
							inventory.quantity_available=quantity
							inventory.purchase_date=date
							# if product.has_batch:
							# 	inventory.batch=batch
							# 	inventory.manufacturing_date=manufacturing_date
							# 	inventory.expiry_date=expiry_date
							# if product.has_instance:
							# 	inventory.serial_no=serial_no
							if not discount_value:
								pass
							else:
								if (discount_type == 1):
									purchase_price=(purchase_price)-(discount_value*purchase_price/100)
								elif(discount_type == 2):
									purchase_price=(purchase_price-discount_value/quantity)
							if not discount_value_2:
								pass
							else:
								if (discount_type_2 == 1):
									purchase_price=(purchase_price)-(discount_value_2*purchase_price/100)
								elif(discount_type_2 == 2):
									purchase_price=(purchase_price-discount_value_2/quantity)
							inventory.purchase_price=purchase_price
							inventory.tentative_sales_price=tentative_sales_price
							inventory.mrp=mrp
							inventory.tenant=this_tenant
							inventory.save()
							if (total_free>0):
								inventory=Inventory()
								inventory.product=product
								inventory.warehouse=warehouse
								inventory.purchase_quantity=total_free
								inventory.quantity_available=total_free
								inventory.purchase_date=date
								# if product.has_batch:
								# 	inventory.batch=batch
								# 	inventory.manufacturing_date=manufacturing_date
								# 	inventory.expiry_date=expiry_date
								# if product.has_instance:
								# 	inventory.serial_no=serial_no
								inventory.purchase_price=0
								inventory.tentative_sales_price=tentative_sales_price
								inventory.mrp=mrp
								inventory.tenant=this_tenant
								inventory.save()
								#For free item
								create_new_inventory_ledger(product,warehouse, 1, date, quantity, \
								0, mrp,new_receipt.receipt_id, this_tenant)

							#For not-free items
							create_new_inventory_ledger(product,warehouse, 1, date, quantity, \
								purchase_price, mrp,new_receipt.receipt_id, this_tenant)								
							
							total_purchase_price+=quantity*purchase_price
							# warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).get(warehouse=warehouse)
							# warehouse_valuation_change.valuation+=quantity*purchase_price
							# warehouse_valuation_change.save()

						if (from_purchase_order):
							#Close Order if quantity is zero for every line item
							order_all_line_items=order_line_item.objects.filter(purchase_order = order)
							will_close = True
							for each_row in order_all_line_items:
								qty_avl = each_row.quantity - each_row.quantity_delivered
								if (qty_avl > 0):
									will_close = False
							if (will_close):
								order.is_closed = True
								order.save()

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

					is_vendor_gst = True if vendor_gst else False
					if (is_igst):
						for k,v in igst_paid.items():
							if v[2]>0:
								new_tax_transaction_register("IGST",1, k, v[0],v[1],v[2], new_receipt.id,\
											new_receipt.supplier_invoice, date, this_tenant, is_vendor_gst, vendor_gst, vendor_state)
					else:
						for k,v in cgst_paid.items():
							if v[2]>0:
								new_tax_transaction_register("CGST",1, k, v[0],v[1],v[2], new_receipt.id,\
											new_receipt.supplier_invoice, date, this_tenant, is_vendor_gst, vendor_gst, vendor_state)
						for k,v in sgst_paid.items():
							if v[2]>0:
								new_tax_transaction_register("SGST",1, k, v[0],v[1],v[2], new_receipt.id,\
											new_receipt.supplier_invoice, date, this_tenant, is_vendor_gst, vendor_gst, vendor_state)

					remarks="Purchase Receipt No: "+str(new_receipt.supplier_invoice)
					journal=new_journal(this_tenant, date,"Purchase",remarks, trn_id=new_receipt.id, trn_type=1)
					account= Account.objects.for_tenant(this_tenant).get(name__exact="Purchase")
					new_journal_entry(this_tenant, journal, subtotal, account, 1, date)
					if (cgst_total>0):
						account= Account.objects.for_tenant(this_tenant).get(name__exact="CGST Input")
						new_journal_entry(this_tenant, journal, cgst_total, account, 1, date)
					if (sgst_total>0):
						account= Account.objects.for_tenant(this_tenant).get(name__exact="SGST Input")
						new_journal_entry(this_tenant, journal, sgst_total, account, 1, date)
					if (igst_total>0):
						account= Account.objects.for_tenant(this_tenant).get(name__exact="IGST Input")
						new_journal_entry(this_tenant, journal, igst_total, account, 1, date)
					if (round_value!=0):
						account= Account.objects.for_tenant(this_tenant).get(name__exact="Rounding Adjustment")
						new_journal_entry(this_tenant, journal, round_value, account, 1, date)
						
					account= Account.objects.for_tenant(this_tenant).get(name__exact="Accounts Payable")
					new_journal_entry(this_tenant, journal, total, account, 2, date, vendor.name, vendor.id)						
							
					debit = journal.journalEntry_journal.filter(transaction_type=1).aggregate(Sum('value'))
					credit = journal.journalEntry_journal.filter(transaction_type=2).aggregate(Sum('value'))
					if (debit != credit):
						raise IntegrityError (('Debit and credit value not matching'))
					if this_tenant.maintain_inventory:

						warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).get(warehouse=warehouse)
						warehouse_valuation_change.valuation+=total_purchase_price
						warehouse_valuation_change.save()


						inventory_acct=account_inventory.objects.for_tenant(this_tenant).get(name__exact="Inventory")
						acct_period=accounting_period.objects.for_tenant(this_tenant).get(start__lte=date, end__gte=date)
						inventory_acct_year=account_year_inventory.objects.for_tenant(this_tenant).\
											get(account_inventory=inventory_acct, accounting_period = acct_period)
						inventory_acct_year.current_debit+=subtotal
						inventory_acct_year.save()
						new_journal_inv=journal_inventory()
						new_journal_inv.date=date
						new_journal_inv.transaction_bill_id=new_receipt.id
						new_journal_inv.trn_type=1
						new_journal_inv.tenant=this_tenant
						new_journal_inv.save()
						new_entry_inv=journal_entry_inventory()
						new_entry_inv.transaction_type=1
						new_entry_inv.journal=new_journal_inv
						new_entry_inv.account=inventory_acct
						new_entry_inv.value=subtotal
						new_entry_inv.tenant=this_tenant
						new_entry_inv.save()

					if (calltype == 'save'):
						response_data=new_receipt.id
					else:
						# response_data['pk']=new_invoice.id
						response_data['id']=new_receipt.id
				except:
					transaction.rollback()

		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)


@api_view(['GET','POST'],)
def purchase_receipt_noninventory_save(request):
	if request.method == 'POST':
		calltype = request.data.get('calltype')
		response_data = {}
		this_tenant=request.user.tenant
		from_purchase_order = False
		#saving the receipt
		if (calltype == 'save'):
			# calledfrom = request.data.get('calledfrom')
			# if (calledfrom == 'purchaseorder'):
			# 	from_purchase_order = True
			with transaction.atomic():
				try:
					supplier_invoice=request.data.get('supplier_invoice')
					vendor_id = request.data.get('vendor')
					warehouse_id=request.data.get('warehouse')
					date=request.data.get('date')
					
					is_igst = False
					
					subtotal=Decimal(request.data.get('subtotal'))
					cgsttotal=Decimal(request.data.get('cgsttotal'))
					sgsttotal=Decimal(request.data.get('sgsttotal'))
					igsttotal=Decimal(request.data.get('igsttotal'))
					round_value=Decimal(request.data.get('round_value'))
					total=Decimal(request.data.get('total'))
					sum_total = subtotal+cgsttotal+sgsttotal
					
					date=request.data.get('date')
					# if (abs(sum_total - total) <0.90 ):
					# 	total = sum_total
					duedate=request.data.get('duedate')

					bill_data = json.loads(request.data.get('bill_details'))

					# order_id=None

					# if (from_purchase_order):
					# 	order_pk = request.data.get('order_pk')
					# 	order = purchase_order.objects.for_tenant(this_tenant).get(id=order_pk)
					# 	vendor = order.vendor
					# 	warehouse = order.warehouse
					# 	order_id = order.id
					# else:
					vendor = Vendor.objects.for_tenant(this_tenant).get(id=vendor_id)
					warehouse = Warehouse.objects.for_tenant(this_tenant).get(id=warehouse_id)

					vendor.current_balance+= total
					vendor.save()

					new_receipt=new_purchase_receipt(this_tenant, supplier_invoice, vendor, warehouse, date, duedate, subtotal, \
						cgsttotal, sgsttotal, igsttotal, round_value, total, 0, from_purchase_order, order_id=None, inventory_type=False)
					
					cgst_paid={}
					sgst_paid={}
					igst_paid={}
					cgst_total=0
					sgst_total=0
					igst_total=0

					vendor_gst=vendor.gst
					vendor_state=vendor.state
					total_purchase_price = 0

				#saving the receipt_line_item and linking them with foreign key to receipt
					for data in bill_data:
						description=data['description']
						
						cgst_p=Decimal(data['cgst_p'])
						cgst_v=Decimal(data['cgst_v'])
						sgst_p=Decimal(data['sgst_p'])
						sgst_v=Decimal(data['sgst_v'])
						igst_p=Decimal(data['igst_p'])
						igst_v=Decimal(data['igst_v'])

						cgst_total+=cgst_v
						sgst_total+=sgst_v
						igst_total+=igst_v

						line_taxable_total=Decimal(data['taxable_total'])
						line_total=Decimal(data['line_total'])
						
						
						tentative_sales_price=0
						mrp=0
						
						purchase_price = Decimal(data['purchase'])
						
						# original_quantity=Decimal(data['quantity']) + Decimal(0.000)
						
						LineItem = receipt_line_item()
						LineItem.purchase_receipt = new_receipt
						LineItem.product_name= description
						LineItem.date = date
						LineItem.cgst_percent=cgst_p
						LineItem.cgst_value=cgst_v
						LineItem.sgst_percent=sgst_p
						LineItem.sgst_value=sgst_v
						LineItem.igst_percent=igst_p
						LineItem.igst_value=igst_v
						LineItem.purchase_price=purchase_price
						LineItem.tentative_sales_price=tentative_sales_price
						LineItem.mrp=mrp
						LineItem.discount_type=0
						LineItem.discount_value=0
						LineItem.discount2_type=0
						LineItem.discount2_value=0
						LineItem.line_tax=line_taxable_total
						LineItem.line_total=line_total
						LineItem.tenant=this_tenant
						LineItem.save()
						
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

					is_vendor_gst = True if vendor_gst else False
					if (is_igst):
						for k,v in igst_paid.items():
							if v[2]>0:
								new_tax_transaction_register("IGST",1, k, v[0],v[1],v[2], new_receipt.id,\
											new_receipt.supplier_invoice, date, this_tenant, is_vendor_gst, vendor_gst, vendor_state)
					else:
						for k,v in cgst_paid.items():
							if v[2]>0:
								new_tax_transaction_register("CGST",1, k, v[0],v[1],v[2], new_receipt.id,\
											new_receipt.supplier_invoice, date, this_tenant, is_vendor_gst, vendor_gst, vendor_state)
						for k,v in sgst_paid.items():
							if v[2]>0:
								new_tax_transaction_register("SGST",1, k, v[0],v[1],v[2], new_receipt.id,\
											new_receipt.supplier_invoice, date, this_tenant, is_vendor_gst, vendor_gst, vendor_state)

					remarks="Purchase Receipt No: "+str(new_receipt.supplier_invoice)
					journal=new_journal(this_tenant, date,"Purchase",remarks, trn_id=new_receipt.id, trn_type=1)
					account= Account.objects.for_tenant(this_tenant).get(name__exact="Purchase")
					new_journal_entry(this_tenant, journal, subtotal, account, 1, date)
					if (cgst_total>0):
						account= Account.objects.for_tenant(this_tenant).get(name__exact="CGST Input")
						new_journal_entry(this_tenant, journal, cgst_total, account, 1, date)
					if (sgst_total>0):
						account= Account.objects.for_tenant(this_tenant).get(name__exact="SGST Input")
						new_journal_entry(this_tenant, journal, sgst_total, account, 1, date)
					if (igst_total>0):
						account= Account.objects.for_tenant(this_tenant).get(name__exact="IGST Input")
						new_journal_entry(this_tenant, journal, igst_total, account, 1, date)
					if (round_value!=0):
						account= Account.objects.for_tenant(this_tenant).get(name__exact="Rounding Adjustment")
						new_journal_entry(this_tenant, journal, round_value, account, 1, date)
						
					account= Account.objects.for_tenant(this_tenant).get(name__exact="Accounts Payable")
					new_journal_entry(this_tenant, journal, total, account, 2, date, vendor.name, vendor.id)						
							
					debit = journal.journalEntry_journal.filter(transaction_type=1).aggregate(Sum('value'))
					credit = journal.journalEntry_journal.filter(transaction_type=2).aggregate(Sum('value'))
					if (debit != credit):
						raise IntegrityError (('Debit and credit value not matching'))
					response_data=new_receipt.id
				
				except Exception as err:
					response_data  = err.args 
					transaction.rollback()

		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

# @login_required
@api_view(['GET'],)
def all_receipts(request):
	this_tenant=request.user.tenant
	page_no = request.GET.get('page_no')
	filter_data={}
	response_data={}
	if request.method == 'GET':
		calltype = request.GET.get('calltype')
		if (calltype == 'all_receipt'):
			receipts=purchase_receipt.objects.for_tenant(this_tenant).all().values('id','receipt_id', 'supplier_invoice', \
				'date','vendor_name','total', 'amount_paid', 'payable_by',).order_by('-date', 'receipt_id')
		elif (calltype == 'unpaid_receipt'):
			receipts=purchase_receipt.objects.for_tenant(this_tenant).filter(final_payment_date__isnull=True).values('id',\
				'receipt_id','supplier_invoice', 'date','vendor_name','total', 'amount_paid', 'payable_by',)\
				.order_by('-date', 'receipt_id')
		elif (calltype == 'apply_filter'):
			vendors=json.loads(request.GET.get('vendors'))
			start=request.GET.get('start')
			end=request.GET.get('end')
			invoice_no=request.GET.get('invoice_no')
			receipts=[]
			sent_with=request.GET.get('sent_with')
			order_no=request.GET.get('order_no')
			if (len(vendors)>0):
				vendors_list=[]
				for item in vendors:
					vendors_list.append(item['vendorid'])
				if (sent_with == 'all_receipts'):
					receipts=purchase_receipt.objects.for_tenant(this_tenant).filter(vendor__in=vendors_list).values('id',\
						'receipt_id', 'supplier_invoice','date','vendor_name','total', 'amount_paid', 'payable_by',).\
						order_by('-date', 'receipt_id')
				if (sent_with == 'unpaid_receipts'):
					receipts=purchase_receipt.objects.for_tenant(this_tenant).\
						filter(final_payment_date__isnull=True, vendor__in=vendors_list).values('id',\
						'receipt_id','supplier_invoice', 'date','vendor_name','total', 'amount_paid', 'payable_by',)\
						.order_by('-date', 'receipt_id')
			else:
				if (sent_with == 'all_receipts'):
					receipts=purchase_receipt.objects.for_tenant(this_tenant).all().values('id',\
						'receipt_id', 'supplier_invoice','date','vendor_name','total', 'amount_paid', 'payable_by',).\
						order_by('-date', 'receipt_id')
				if (sent_with == 'unpaid_receipts'):
					receipts=purchase_receipt.objects.for_tenant(this_tenant).\
						filter(final_payment_date__isnull=True).values('id',\
						'receipt_id','supplier_invoice', 'date','vendor_name','total', 'amount_paid', 'payable_by',)\
						.order_by('-date', 'receipt_id')
			if (start and end):
				receipts=receipts.filter(date__range=[start,end])
			if (order_no):
				order=purchase_order.objects.for_tenant(this_tenant).get(order_id=order_no)
				receipts=receipts.filter(order_id=order.id)
			if invoice_no:
				receipts=receipts.filter(supplier_invoice__icontains=invoice_no)

		elif (calltype== 'vendor_pending'):
			vendorid = request.GET.get('vendorid')
			vendor=Vendor.objects.for_tenant(this_tenant).get(id=vendorid)
			# print(vendor)
			receipts=purchase_receipt.objects.for_tenant(this_tenant).filter(vendor=vendor, final_payment_date__isnull=True).\
				values('id','receipt_id', 'supplier_invoice', 'date','vendor_name','total', 'amount_paid', 'payable_by')
		# response_data = list(receipts)

		# page_no = 1
		response_data={}
		# print(receipts.count())
		if page_no:
			if (page_no == str(1)):
				filter_summary=receipts.aggregate(pending=Sum('total')-Sum('amount_paid'), total_sum=Sum('total'))
				filter_data['total_pending'] = filter_summary['pending']
				filter_data['total_value'] = filter_summary['total_sum']
				
			response_data =  paginate_data(page_no, 10, list(receipts))
			if (page_no == str(1)):
				response_data.update(filter_data)
			 
		else:
			filter_summary=receipts.aggregate(pending=Sum('total')-Sum('amount_paid'), total_sum=Sum('total'))
			filter_data['total_pending'] = filter_summary['pending']
			filter_data['total_value'] = filter_summary['total_sum']
			response_data['object']=list(receipts)
	
	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)


# @login_required
@api_view(['GET'],)
def receipts_metadata(request):
	this_tenant=request.user.tenant
	tod=date.today()
	prev=tod-timedelta(days=30)
	receipts_value=purchase_receipt.objects.for_tenant(this_tenant).filter(date__range=[prev,tod]).aggregate(Sum('total'))
	receipts_paid=purchase_payment.objects.for_tenant(this_tenant).filter(paid_on__range=[prev,tod]).aggregate(Sum('amount_paid'))
	receipts_overdue=purchase_receipt.objects.for_tenant(this_tenant).filter(payable_by__gt=tod).aggregate(Sum('total'))
	response_data = {'receipts_value':receipts_value, 'receipts_paid':receipts_paid, 'receipts_overdue':receipts_overdue}		
		
	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)


@login_required
def receipt_list(request):
	return render(request,'purchase/receipt_list.html', {'extension': 'base.html'})

# @login_required
@api_view(['GET', 'POST'],)
def receipts_details(request, pk):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		receipt=purchase_receipt.objects.for_tenant(this_tenant).values('id','receipt_id','supplier_invoice',\
		'date','vendor_name','vendor_address','vendor_city','vendor_pin','vendor_gst','warehouse_address','warehouse_city',\
		'warehouse_pin','payable_by','subtotal','cgsttotal','sgsttotal','igsttotal','roundoff','total','amount_paid', 'inventory_type').get(id=pk)

		receipt['tenant_name']=this_tenant.name
		receipt['tenant_gst']=this_tenant.gst
		receipt['tenant_address']=this_tenant.address_1+","+this_tenant.address_2
		
		line_items=list(receipt_line_item.objects.filter(purchase_receipt=receipt['id']).values('id','product_name','product_hsn',\
			'unit','unit_multi','quantity','free_with_tax','purchase_price', 'tentative_sales_price','mrp','discount_type',\
			'discount_value','discount2_type','discount2_value','cgst_percent','sgst_percent','igst_percent',\
			'cgst_value','sgst_value','igst_value','line_tax','line_total'))
		receipt['line_items']=line_items
		
		jsondata = json.dumps(receipt, cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)

@login_required
def receipts_detail_view(request, pk):
	return render(request,'purchase/purchase_receipt_detail.html', {'extension': 'base.html', 'pk':pk})


# @login_required
@api_view(['POST'],)
def payment_register(request):
	this_tenant=request.user.tenant
	if request.method == 'POST':
		response_data=[]
		vendorid = request.data.get('vendorid')
		modeid = request.data.get('modeid')
		date = request.data.get('date')
		payment_details = json.loads(request.data.get('payment_details'))
		
		vendor = Vendor.objects.for_tenant(this_tenant).get(id=vendorid)
		mode = payment_mode.objects.for_tenant(this_tenant).get(id=modeid)

		total_payment=0
		invoiceids=""
		cheque_rtgs_all=""
		payment_pk={}
		cheque_rtgs_checker = []
		with transaction.atomic():
			try:
				for item in payment_details:
					purchase_receipt_id=item['receipt_pk']
					amount_paid=Decimal(item['amount'])
					cheque_rtgs_number=item['cheque_rtgs_number']
					receipt=purchase_receipt.objects.for_tenant(this_tenant).get(id=purchase_receipt_id)
					receipt.amount_paid+=amount_paid
					if (round(receipt.total - receipt.amount_paid) == 0):
						receipt.final_payment_date=date
					receipt.save()

					new_purchase_payment = purchase_payment()
					new_purchase_payment.payment_mode=mode
					new_purchase_payment.payment_mode_name=mode.name
					new_purchase_payment.purchase_receipt=receipt
					new_purchase_payment.amount_paid=amount_paid
					new_purchase_payment.cheque_rtgs_number=cheque_rtgs_number
					new_purchase_payment.paid_on=date
					# new_purchase_payment.remarks=remarks
					new_purchase_payment.tenant=this_tenant
					new_purchase_payment.save()

					total_payment+= amount_paid
					invoiceids+= str(receipt.supplier_invoice)+", "
					
					if not cheque_rtgs_number in cheque_rtgs_checker:
						cheque_rtgs_checker.append(cheque_rtgs_number)
						cheque_rtgs_all+= str(cheque_rtgs_number)+", "
					payment_pk[str(receipt.supplier_invoice)]=new_purchase_payment.id

				vendor.current_balance-= total_payment
				vendor.save()

				payment_json=json.dumps(payment_pk, cls=DjangoJSONEncoder)

				if len(cheque_rtgs_all)>0:
					invoiceids+= "Cheque No:  "+cheque_rtgs_all

				journal=new_journal(this_tenant,date,group_name="Purchase",\
					remarks='Payment Against: '+invoiceids, trn_id=new_purchase_payment.id, trn_type=2, other_data=payment_json)
				account= Account.objects.for_tenant(this_tenant).get(name__exact="Accounts Payable")
				new_journal_entry(this_tenant, journal, total_payment, account, 1, date, vendor.name, vendor.id)
				new_journal_entry(this_tenant, journal, total_payment, mode.payment_account, 2, date)
				
			except:
				transaction.rollback()

	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

# @login_required
@api_view(['GET'],)
def payment_list(request):
	this_tenant = request.user.tenant
	response_data = {}
	if request.method == 'GET':
		calltype = request.GET.get('calltype')
		if (calltype == 'apply_filter'):
			vendors = json.loads(request.GET.get('vendors'))
			start = request.GET.get('start')
			end = request.GET.get('end')
			receipt_no = request.GET.get('receipt_no')
			cheque_rtgs = request.GET.get('cheque_rtgs')
			page_no = request.GET.get('page_no')
			# modeid = request.GET.get('modeid')
			if (receipt_no):
				receipt = purchase_receipt.objects.for_tenant(this_tenant).get(supplier_invoice = receipt_no)
				payments = purchase_payment.objects.for_tenant(this_tenant).filter(purchase_receipt=receipt,)\
					.order_by('-paid_on', 'cheque_rtgs_number','-purchase_receipt')
			else:
				if (len(vendors)>0):
					vendors_list=[]
					for item in vendors:
						vendors_list.append(item['vendorid'])
					payments = purchase_payment.objects.for_tenant(this_tenant).select_related('purchase_receipt').filter(paid_on__range=[start,end],\
						purchase_receipt__vendor__in=vendors_list).order_by('-paid_on', 'cheque_rtgs_number','-purchase_receipt')
				else:
					payments = purchase_payment.objects.for_tenant(this_tenant).filter(paid_on__range=[start,end],)\
						.order_by('-paid_on', 'cheque_rtgs_number','-purchase_receipt')
				
				if cheque_rtgs:
					payments=payments.filter(cheque_rtgs_number=cheque_rtgs).order_by('-paid_on', 'cheque_rtgs_number','-purchase_receipt')
				# serializer = PaymentSerializers(payments, many=True)
		else:
			page_no = request.GET.get('page_no')
			start = request.GET.get('start')
			end = request.GET.get('end')

			payments = purchase_payment.objects.for_tenant(this_tenant).filter(paid_on__range=[start,end],)\
					.order_by('-paid_on', 'cheque_rtgs_number','-purchase_receipt')
			# serializer = PaymentSerializers(payments, many=True)		

		if (page_no):
			payments_paginated=paginate_data(page_no, 10, list(payments))
			serializer = PaymentSerializers(payments_paginated['object'], many=True)
			response_data['object']  = serializer.data
			response_data['end'] = payments_paginated['end']
			response_data['start'] = payments_paginated['start']
		else:
			serializer = PaymentSerializers(payments, many=True)
			response_data['object'] = serializer.data
		
		jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)

@login_required
def payment_list_view(request):
	return render(request,'purchase/payment_list.html', {'extension': 'base.html'})

@login_required
def debit_note_return_view(request):
	return render(request,'purchase/debit_note_return.html', {'extension': 'base.html'})

@api_view(['POST'],)
def delete_purchase(request):
	this_tenant = request.user.tenant
	response_data = {}
	#Write unit test to check round off issue.
	#delete only if amount paid  = 0
	#search & delete available inventory. If not avialable raise error.
	if request.method == 'POST':
		calltype = request.data.get('calltype')
		if (calltype == 'delete'):
			try:
				with transaction.atomic():
					receipt_pk = request.data.get('receipt_pk')
					old_receipt = purchase_receipt.objects.for_tenant(this_tenant).get(id=receipt_pk)
					order_id = old_receipt.order_id
					if (order_id):
						raise IntegrityError(('Purchase receipt from Purchase Order cannot be deleted'))
					maintain_inventory = this_tenant.maintain_inventory
					warehouse = old_receipt.warehouse
					amount_paid = old_receipt.amount_paid
					purchase_date = old_receipt.date
					total_purchase_price = 0
					inventory_type=old_receipt.inventory_type
					vendor = old_receipt.vendor
					vendor.current_balance-= old_receipt.total
					vendor.save()
					if (amount_paid == 0):
						all_line_items=receipt_line_item.objects.for_tenant(this_tenant).filter(purchase_receipt=old_receipt)
						if (inventory_type):
							if maintain_inventory:
								for each_item in all_line_items:
									productid=each_item.product
									multiplier=each_item.unit_multi
									
									original_purchase_price=each_item.purchase_price
									purchase_price=round(original_purchase_price/multiplier,2)
									
									original_quantity=each_item.quantity
									quantity=round(original_quantity*multiplier,2)
									
									discount_type = each_item.discount_type
									discount_value = each_item.discount_value
									discount_type_2 = each_item.discount2_type
									discount_value_2 = each_item.discount2_value
									total_free = each_item.free_with_tax

									try:
										original_tentative_sales_price=each_item.tentative_sales_price
										tentative_sales_price=round(original_tentative_sales_price/multiplier,2)
									except:
										tentative_sales_price=0
									
									
									if discount_value:									
										if (discount_type == 1):
											purchase_price=(purchase_price)-(discount_value*purchase_price/100)
										elif(discount_type == 2):
											purchase_price=(purchase_price-discount_value/quantity)
									
									if discount_value_2:
										if (discount_type_2 == 1):
											purchase_price=(purchase_price)-(discount_value_2*purchase_price/100)
										elif(discount_type_2 == 2):
											purchase_price=(purchase_price-discount_value_2/quantity)

									purchase_price = round(purchase_price,2)
									purchase_price_min=purchase_price-Decimal(0.01)
									purchase_price_max=purchase_price+Decimal(0.01)
									# purchase_price = round(purchase_price,2)
									

									try:
										original_mrp=each_item.mrp
										mrp=round(original_mrp/multiplier,2)
									except:
										mrp=0
									
									# total_purchase_price+=quantity*purchase_price
									
									product_list=Inventory.objects.for_tenant(this_tenant).filter(purchase_date = purchase_date, \
													quantity_available__gt=0, product=productid, warehouse=warehouse, \
													purchase_price__range=[purchase_price_min,purchase_price_max],\
													tentative_sales_price=tentative_sales_price, mrp=mrp).order_by('purchase_date')
									quantity_updated=quantity
									for item in product_list:
										if (quantity_updated==0):
											break
										original_available=item.quantity_available
										if (quantity_updated>=original_available):
											item.quantity_available=0
											# products_cost+=item.purchase_price*original_available
											total_purchase_price+=original_available*item.purchase_price
											
											quantity_updated-=original_available
											item.delete()
													
										else:
											item.quantity_available-=quantity_updated
											total_purchase_price+=quantity_updated*item.purchase_price
											# products_cost+=item.purchase_price*quantity_updated
											item.save()
											quantity_updated=0								
									if (quantity_updated>0):
										raise IntegrityError (('Quantity of item: '+productid+' not available.'))
									
									if (total_free >0):
										product_list=Inventory.objects.for_tenant(this_tenant).filter(purchase_date = purchase_date, \
													quantity_available__gt=0,product=productid, warehouse=warehouse, purchase_price=0,\
													tentative_sales_price=tentative_sales_price, mrp=mrp).order_by('purchase_date')
										quantity_updated=total_free
										for item in product_list:
											if (quantity_updated==0):
												break
											original_available=item.quantity_available
											if (quantity_updated>=original_available):
												item.quantity_available=0
												# products_cost+=item.purchase_price*original_available
												
												quantity_updated-=original_available
												item.delete()
														
											else:
												item.quantity_available-=quantity_updated
												# products_cost+=item.purchase_price*quantity_updated
												item.save()
												quantity_updated=0								
										if (quantity_updated>0):
											raise IntegrityError (('Quantity of item: '+productid+' not available.'))


								#Update Warehouse Valuation
								warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).get(warehouse=warehouse)
								warehouse_valuation_change.valuation-=total_purchase_price
								warehouse_valuation_change.save()
								
						#delete tax transactions
						tax_transaction.objects.for_tenant(this_tenant).filter(date=old_receipt.date,transaction_type=1,\
									transaction_bill_id=old_receipt.id).delete()
						#delete journal
						old_journal=Journal.objects.for_tenant(this_tenant).get(trn_type=1, transaction_bill_id=old_receipt.id)
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

						if (inventory_type):
							if maintain_inventory:
								#Only if maintain inventory
								#delete inventory_ledger()
								inventory_ledger.objects.for_tenant(this_tenant).filter(date=old_receipt.date,transaction_type=1,\
											transaction_bill_id=old_receipt.receipt_id).delete()

								#delete all inventory journal entries
								old_journal_inv=journal_inventory.objects.for_tenant(this_tenant).filter(trn_type=1, transaction_bill_id=old_receipt.id)
								# # Update the current balance of all inventory journal related accounts
								journal_inv_line_items = journal_entry_inventory.objects.for_tenant(this_tenant).filter(journal__in=old_journal_inv)
								for item in journal_inv_line_items:
									inventory_acct = item.account
									inventory_acct_year=account_year_inventory.objects.get(account_inventory=inventory_acct,\
											accounting_period = acct_period)
									if (trn_type == 1):
										inventory_acct_year.current_debit=inventory_acct_year.current_debit-item.value
									elif (trn_type == 2):
										inventory_acct_year.current_credit=inventory_acct_year.current_credit-item.value
									inventory_acct_year.save()
								
								old_journal_inv.delete()
								# # raise IntegrityError

						#delete purchase receipt
						all_line_items.delete()
						old_receipt.delete()
					else:
						#display error that amount is already paid against this invoice & it cant be edited
						pass
			except Exception as err:
				response_data  = err.args 
				transaction.rollback()
		
		jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)


@api_view(['GET','POST'],)
def debit_note_save(request):
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		this_tenant=request.user.tenant
		if (calltype == 'save'):
			with transaction.atomic():
				try:
					vendor_id = request.data.get('vendor')
					warehouse_id=request.data.get('warehouse')
					credit_note_no=request.data.get('credit_note_no')
					date=request.data.get('date')
					subtotal=Decimal(request.data.get('subtotal'))
					taxtotal=Decimal(request.data.get('taxtotal'))
					total=Decimal(request.data.get('total'))
					bill_data = json.loads(request.data.get('bill_details'))

					vendor = Vendor.objects.for_tenant(this_tenant).get(id=vendor_id)
					warehouse = Warehouse.objects.for_tenant(this_tenant).get(id=warehouse_id)

					vendor_name=vendor.name
					vendor_address=vendor.address_1+", "+vendor.address_2
					vendor_state=vendor.state
					vendor_city=vendor.city
					vendor_pin=vendor.pin
					
					ware_address=warehouse.address_1+", "+warehouse.address_2
					ware_state=warehouse.state
					ware_city=warehouse.city
					ware_pin=warehouse.pin
					
					new_debit_note=debit_note()
					new_debit_note.tenant=this_tenant

					new_debit_note.date = date
					
					new_debit_note.vendor=customer
					new_debit_note.vendor_name=vendor_name
					new_debit_note.vendor_address=vendor_address
					new_debit_note.vendor_state=vendor_state
					new_debit_note.vendor_city=vendor_city
					new_debit_note.vendor_pin=vendor_pin

					new_debit_note.warehouse=warehouse
					new_debit_note.warehouse_address=ware_address
					new_debit_note.warehouse_state=ware_state
					new_debit_note.warehouse_city=ware_city
					new_debit_note.warehouse_pin=ware_pin
					
					new_debit_note.subtotal=subtotal
					new_debit_note.taxtotal=taxtotal
					new_debit_note.total = total
					new_invoice.save()
					
					# remarks="Debit Note No: "+str(new_debit_note.note_id)
					# journal=new_journal(this_tenant, date,"Purchase",remarks, trn_id=new_debit_note.id, trn_type=3)
					# # debit_note_account = request.data.get('debit_note_account')
					# account= Account.objects.for_tenant(this_tenant).get(name__exact="Inventory")
					# new_journal_entry(this_tenant, journal, taxtotal, account, 2, date)
					# # This has to change.
					# account= Account.objects.for_tenant(this_tenant).get(name__exact="Accounts Payable")
					# new_journal_entry(this_tenant, journal, total, account, 1, date)
					
					# debit = journal.journalEntry_journal.filter(transaction_type=1).aggregate(Sum('value'))
					# credit = journal.journalEntry_journal.filter(transaction_type=2).aggregate(Sum('value'))
					# if (debit != credit):
					# 	raise IntegrityError (('Debit and credit value not matching.'))

					products_cost=0

					for data in bill_data:
						productid=data['product_id']
						unitid=data['unit_id']

						if is_tax =='true':
							is_tax=True
						elif is_tax == 'false':
							is_tax=False
						
						line_taxable_total=Decimal(data['taxable_total'])
						line_total=Decimal(data['line_total'])
						product=Product.objects.for_tenant(this_tenant).select_related('tax').get(id=productid)
								
						unit=Unit.objects.for_tenant(this_tenant).get(id=unitid)
						multiplier=unit.multiplier
						
						original_pr=Decimal(data['pr'])
						original_tsp=Decimal(data['tsp'])
						original_mrp=Decimal(data['mrp'])
						pr=original_pr/multiplier
						tsp=original_tsp/multiplier
						mrp=original_mrp/multiplier

						original_quantity=int(data['quantity'])
						
						quantity=original_quantity*multiplier
						
						product_list=Inventory.objects.for_tenant(this_tenant).filter(quantity_available__gt=0,\
								product=productid, warehouse=warehouse, purchase_price = original_pr,\
								tentative_sales_price=original_tsp, mrp=original_mrp).order_by('purchase_date')
						quantity_updated=quantity
						total_purchase_price=0
						
						#If maintain inventory, add product back to database. Update the related journal. Also update the warehouse valuation.
						#Modify the price list json to match purchase format.

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
								price_list[str(i)]={'date':item.purchase_date, \
											'quantity':original_available, 'pur_rate':item.purchase_price}
								total_purchase_price+=original_available*item.purchase_price
								quantity_updated-=original_available
								
							else:
								item.quantity_available-=quantity_updated
								products_cost+=item.purchase_price*quantity_updated
								item.save()
								price_list[str(i)]={'date':item.purchase_date, \
											'quantity':quantity_updated, 'pur_rate':item.purchase_price}
								total_purchase_price+=quantity_updated*item.purchase_price
								quantity_updated=0								
						
						if (quantity_updated>0):
							raise IntegrityError
						price_list_json = json.dumps(price_list,  cls=DjangoJSONEncoder)

						LineItem = debit_note_line_item()
						LineItem.debit_note = new_debit_note
						LineItem.product= product
						LineItem.product_name= product.name
						LineItem.product_sku=product.sku
						
						LineItem.cgst_percent=cgst_p
						LineItem.cgst_value=cgst_v
						LineItem.sgst_percent=sgst_p
						LineItem.sgst_value=sgst_v
						LineItem.igst_percent=igst_p
						LineItem.igst_value=igst_v

						LineItem.unit=unit.symbol
						LineItem.unit_multi=unit.multiplier
						LineItem.quantity=original_quantity
						
						LineItem.purchase_price=original_pr
						LineItem.tentative_sales_price=original_tsp
						LineItem.mrp=original_mrp
						LineItem.line_tax=line_taxable_total
						LineItem.line_total=line_total
						LineItem.tenant=this_tenant
						LineItem.save()
						

						#Update this. Need to include purchase price here. For each purchase price there will be a ledger entry
						#Adjust payment against the receipt. 
						#Add journal entry for debit note, linking it to debit note and linking it to purchase payment.

						#If maintain inventory
						for k,v in price_list.items():
							# new_inventory_ledger=inventory_ledger()
							# new_inventory_ledger.product=product
							# new_inventory_ledger.warehouse=warehouse
							# new_inventory_ledger.transaction_type=5
							# new_inventory_ledger.date=date
							# new_inventory_ledger.quantity=v['quantity']
							# new_inventory_ledger.purchase_price=v['pur_rate']
							# new_inventory_ledger.transaction_bill_id=new_debit_note.note_id
							# new_inventory_ledger.tenant=this_tenant
							# new_inventory_ledger.save()

							create_new_inventory_ledger(product,warehouse, 1, date, quantity, \
								purchase_price, mrp,new_receipt.receipt_id, this_tenant)
						
						warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).get(warehouse=warehouse)
						warehouse_valuation_change.valuation-=total_purchase_price
						warehouse_valuation_change.save()
						
						if is_tax:
							new_tax_transaction=tax_transaction()
							new_tax_transaction.transaction_type=5
							new_tax_transaction.tax_type="VAT"
							new_tax_transaction.product=product
							new_tax_transaction.product_name=product.name
							new_tax_transaction.tax_percent=product.tax.percentage
							new_tax_transaction.tax_value=line_total-line_taxable_total
							new_tax_transaction.transaction_bill_id=new_debit_note.id
							new_tax_transaction.transaction_bill_no=new_debit_note.note_id
							new_tax_transaction.date=date
							new_tax_transaction.tenant=this_tenant
							new_tax_transaction.save()

				except:
					transaction.rollback()

		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)


@api_view(['GET', 'POST'],)
def excel_receipt(request, pk):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		receipt=purchase_receipt.objects.for_tenant(this_tenant).get(id=pk)

		line_items=list(receipt_line_item.objects.filter(purchase_receipt=receipt).values('id','product_name','product_hsn',\
			'unit','quantity','purchase_price', 'tentative_sales_price','mrp','discount_type',\
			'discount_value','discount2_type','discount2_value','cgst_percent','sgst_percent','igst_percent',\
			'cgst_value','sgst_value','igst_value','line_tax','line_total'))
		
		x='Purchase_Invoice '+str(receipt.supplier_invoice)+'.xlsx'
		response = HttpResponse(content_type='application/vnd.ms-excel')
		response['Content-Disposition'] = 'attachment; filename='+x
		xlsx_data = purchase_invoice_excel(line_items, receipt, this_tenant)
		response.write(xlsx_data)
		return response
		
@login_required
def purchase_crossfilter(request):
	return render(request,'purchase/vendor_payment_crossfilter.html', {'extension': 'base.html'})


@api_view(['GET', 'POST'],)
def receipts_crossfilter(request):
	this_tenant=request.user.tenant
	calltype = request.GET.get('calltype')
	if calltype == 'purchase crossfilter':
		start = request.GET.get('start')
		end = request.GET.get('end')

		receipt=purchase_receipt.objects.for_tenant(this_tenant).filter(date__range=[start,end])

		line_items=list(receipt_line_item.objects.filter(purchase_receipt__in=receipt).values('id','product_name','product_sku',\
			'line_total', 'purchase_receipt__vendor_name', 'purchase_receipt__warehouse_address',\
			'purchase_receipt__supplier_invoice', 'purchase_receipt__date'))

		jsondata = json.dumps(line_items, cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)


@login_required
def hsn_report(request):
	extension="base.html"
	return render (request, 'account/tax_report.html',{'extension':extension})

@api_view(['GET'],)
def get_hsn_report(request):
	this_tenant=request.user.tenant
	calltype=request.GET.get('calltype')
	calltype = 'all_list'
	response_data={}
	if (calltype == 'all_list'):
		all_items=receipt_line_item.objects.for_tenant(this_tenant).values('product_hsn').\
							annotate(taxable_value=Sum('line_tax'), total_amount=Sum('line_total'), \
							quantities=Sum(F('quantity') * F('unit_multi')) - Sum(F('quantity_returned') * F('unit_multi'))).order_by('product_hsn')
	
	# elif (calltype == 'apply_filter'):
	# 	start=request.GET.get('start')
	# 	end=request.GET.get('end')
	# 	# tax_percent=int(request.GET.get('tax_percent'))
	# 	# tax_type=request.GET.get('tax_type')
	# 	all_items=tax_transaction.objects.for_tenant(request.user.tenant).filter(date__range=[start,end]).all()
	# 	# if (tax_percent):
	# 		# response_data=response_data.filter(tax_percent=tax_percent, date__range=[start,end]).all()
	# 	# if (tax_type):
	# 		# response_data=response_data.filter(tax_type=tax_type, date__range=[start,end]).all()
	# 	all_items=list(response_data.values('transaction_type','tax_type',\
	# 		'tax_percent', 'tax_value','transaction_bill_no','date','is_registered').order_by('transaction_type','date','tax_type','tax_percent'))

	response_data={}
	# if page_no:
		# response_data =  paginate_data(page_no, 10, list(all_items))
	# else:
	response_data['object']=list(all_items)

	jsondata = json.dumps(response_data,cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)
		

@login_required
@api_view(['GET'],)
def purchase_order_new(request):
	return render(request,'purchase/purchase_order.html', {'extension': 'base.html'})


@api_view(['GET','POST'],)
def purchase_order_save(request):
	# Change the models where data is getting saved
	if request.method == 'POST':
		calltype = request.data.get('calltype')
		response_data = {}
		this_tenant=request.user.tenant
		#saving the receipt
		if (calltype == 'save'):
			try:
				with transaction.atomic():
					supplier_order=request.data.get('supplier_order')
					vendor_id = request.data.get('vendor')
					warehouse_id=request.data.get('warehouse')
					date=request.data.get('date')
					
					is_igst = False
					
					subtotal=Decimal(request.data.get('subtotal'))
					cgsttotal=Decimal(request.data.get('cgsttotal'))
					sgsttotal=Decimal(request.data.get('sgsttotal'))
					igsttotal=Decimal(request.data.get('igsttotal'))
					round_value=Decimal(request.data.get('round_value'))
					total=Decimal(request.data.get('total'))
					sum_total = subtotal+cgsttotal+sgsttotal
					
					deliverydate=request.data.get('deliverydate')

					bill_data = json.loads(request.data.get('bill_details'))

					vendor = Vendor.objects.for_tenant(this_tenant).get(id=vendor_id)
					warehouse = Warehouse.objects.for_tenant(this_tenant).get(id=warehouse_id)

					
					new_order=new_purchase_order(this_tenant, supplier_order, vendor, warehouse, date, deliverydate,\
							subtotal, cgsttotal, sgsttotal, igsttotal, round_value, total)
					
					cgst_paid={}
					sgst_paid={}
					igst_paid={}
					cgst_total=0
					sgst_total=0
					igst_total=0

					vendor_gst=vendor.gst
					vendor_state=vendor.state

			#saving the receipt_line_item and linking them with foreign key to receipt
					for data in bill_data:
						productid=data['product_id']
						unitid=data['unit_id']

						discount_type=data['disc_type']
						discount_value=Decimal(data['disc'])
						discount_type_2=data['disc_type_2']
						discount_value_2=Decimal(data['disc_2'])

						cgst_p=Decimal(data['cgst_p'])
						cgst_v=Decimal(data['cgst_v'])
						sgst_p=Decimal(data['sgst_p'])
						sgst_v=Decimal(data['sgst_v'])
						igst_p=Decimal(data['igst_p'])
						igst_v=Decimal(data['igst_v'])

						cgst_total+=cgst_v
						sgst_total+=sgst_v
						igst_total+=igst_v

						line_taxable_total=Decimal(data['taxable_total'])
						line_total=Decimal(data['line_total'])
						product=Product.objects.for_tenant(request.user.tenant).get(id=productid)
						unit=Unit.objects.for_tenant(this_tenant).get(id=unitid)
						multiplier=unit.multiplier
						
						original_purchase_price=Decimal(data['purchase'])
						
						original_free_with_tax=Decimal(data['free_tax'])

						purchase_price=Decimal(original_purchase_price/multiplier)
						
						# original_quantity=Decimal(data['quantity']) + Decimal(0.000)
						original_quantity=Decimal(data['quantity'])
						
						quantity=original_quantity*multiplier
						
						if (quantity == 0):
							raise IntegrityError (('Quantity of item: '+product.name+' cannot be zero.'))

						free_with_tax=original_free_with_tax*multiplier
						free_without_tax=0
						total_free=free_without_tax+free_with_tax
						
						LineItem = order_line_item()
						LineItem.purchase_order = new_order
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
						LineItem.free_with_tax=original_free_with_tax
						LineItem.purchase_price=original_purchase_price
						LineItem.discount_type=discount_type
						LineItem.discount_value=discount_value
						LineItem.discount2_type=discount_type_2
						LineItem.discount2_value=discount_value_2
						LineItem.line_tax=line_taxable_total
						LineItem.line_total=line_total
						LineItem.tenant=this_tenant
						LineItem.save()

					response_data['order_id']=new_order.id
			
			except Exception as err:
				response_data  = err.args 
				transaction.rollback()

		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)


@login_required
def order_list_view(request):
	return render(request,'purchase/order_list.html', {'extension': 'base.html'})


@api_view(['GET','POST'],)
def all_orders(request):
	this_tenant=request.user.tenant
	page_no = request.GET.get('page_no')
	calltype = request.GET.get('calltype')
	if request.method == 'GET':
		if (calltype == 'all_receipt'):
			orders=purchase_order.objects.for_tenant(this_tenant).all().values('id','order_id', 'supplier_order', \
				'date','vendor_name','total', 'delivery_by','is_closed').order_by('-date', 'order_id')
		elif (calltype == 'apply_filter'):
			vendors=json.loads(request.GET.get('vendors'))
			start=request.GET.get('start')
			order_type=request.GET.get('order_type')
			if (order_type == 'all'):
				is_closed= [True, False]
			elif (order_type == 'open'):
				is_closed= [False]
			elif (order_type == 'closed'):
				is_closed= [True]
			end=request.GET.get('end')
			order_id=request.GET.get('order_id')
			filter_type=request.GET.get('filter_type')
			orders=[]
			if (len(vendors)>0):
				vendors_list=[]
				for item in vendors:
					vendors_list.append(item['vendorid'])
				orders=purchase_order.objects.for_tenant(this_tenant).filter(vendor__in=vendors_list, is_closed__in = is_closed).\
					values('id','order_id', 'supplier_order', 'date','vendor_name','total', 'delivery_by','is_closed').order_by('-date', 'order_id')
			else:
				orders=purchase_order.objects.for_tenant(this_tenant).filter(is_closed__in = is_closed).\
					values('id','order_id', 'supplier_order', 'date','vendor_name','total', 'delivery_by','is_closed').order_by('-date', 'order_id')
			
			if (start and end):
				orders=orders.filter(date__range=[start,end])
			if order_id:
				orders=orders.filter(order_id__icontains=order_id)

		
		response_data={}
		
		if page_no:
			response_data =  paginate_data(page_no, 10, list(orders))
		else:
			response_data['object']=list(orders)
		
	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

@login_required
def order_detail_view(request, pk):
	return render(request,'purchase/purchase_order_detail.html', {'extension': 'base.html', 'pk':pk})


@api_view(['GET'],)
def order_details(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		order_pk=request.GET.get('order_pk')
		receipt=purchase_order.objects.for_tenant(this_tenant).values('id','order_id','supplier_order',\
		'date','vendor_name','vendor_address','vendor_city','vendor_pin','vendor_gst','warehouse_address','warehouse_city',\
		'warehouse_pin','delivery_by','subtotal','cgsttotal','sgsttotal','igsttotal','roundoff','total', 'is_closed').get(id=order_pk)

		receipt['tenant_name']=this_tenant.name
		receipt['tenant_gst']=this_tenant.gst
		receipt['tenant_address']=this_tenant.address_1+","+this_tenant.address_2
		
		line_items=list(order_line_item.objects.filter(purchase_order=receipt['id']).values('id','product_id', 'product_name','product_hsn',\
			'unit','unit_multi','quantity', 'quantity_delivered','free_with_tax','purchase_price','discount_type',\
			'discount_value','discount2_type','discount2_value','cgst_percent','sgst_percent','igst_percent',\
			'cgst_value','sgst_value','igst_value','line_tax','line_total'))
		receipt['line_items']=line_items
		
		jsondata = json.dumps(receipt, cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)


@login_required
def receipt_order(request, pk):
	return render(request,'purchase/purchase_receipt_order.html', {'extension': 'base.html', 'pk':pk})


@api_view(['POST'],)
def order_delete(request):
	this_tenant=request.user.tenant
	response_data = 'Data format does not match.'
	if request.method == 'POST':
		calltype = request.data.get('calltype')
		if (calltype == 'delete'):
			order_pk = request.data.get('order_pk')
			order=purchase_order.objects.for_tenant(this_tenant).get(id=order_pk)
			if (order.is_closed):
				response_data = "Order is already closed. This cannot be deleted."
			else:
				if purchase_receipt.objects.for_tenant(this_tenant).filter(order_id=order_pk).exists():
					response_data = "Purchase already made from this order. It cannot be deleted."
				else:
					# order.delete()
					response_data = "Success"				
		
		jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)


@api_view(['GET'],)
def vendor_ledger(request):
	extension="base.html"
	return render (request, 'purchase/vendor_ledger.html',{'extension':extension})


@api_view(['GET'],)
def vendor_ledger_data(request):
	this_tenant=request.user.tenant
	response_data = {}
	start=request.GET.get('start')
	end=request.GET.get('end')
	vendorid=int(request.GET.get('vendorid'))
	journal = Journal.objects.for_tenant(request.user.tenant).filter(date__range=[start,end], trn_type__in = [1,2,3],)
	entries=list(journal_entry.objects.for_tenant(request.user.tenant).filter(related_data__id=vendorid, journal__in = journal)\
			.prefetch_related('journal').\
			values('related_data', 'transaction_type', 'journal__id', 'journal__date','transaction_type','journal__remarks', 'value',).\
			all().order_by('journal__date'))	
	response_data['object'] = entries
	jsondata = json.dumps(response_data,cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

@api_view(['GET', 'POST'],)
def vendor_opening_balance(request):
	this_tenant=request.user.tenant
	response_data = {}
	if request.method == 'POST':
		calltype = request.data.get('calltype')
		if (calltype == 'update_opening_balance'):
			try:
				with transaction.atomic():
				# try:
					vendorid = request.data.get('vendorid')
					opening_balance = Decimal(request.data.get('opening_balance'))
						
					vendor = Vendor.objects.for_tenant(this_tenant).get(id=vendorid)
					if (vendor.opening_balance ==0 or vendor.opening_balance is None or vendor.opening_balance==''):
						vendor.opening_balance = opening_balance
						vendor.current_balance+=opening_balance
						vendor.save()
					else:
						raise IntegrityError (('Opening Balance is already registered against this vendor. This cannot be changed.'))
					# update accounts payable opening
					account= Account.objects.for_tenant(this_tenant).get(name__exact="Accounts Payable")
					acct_period=accounting_period.objects.for_tenant(this_tenant).get(is_first_year=True)
					account_journal_year = account_year.objects.get(account=account, accounting_period = acct_period)
					account_journal_year.opening_credit+=opening_balance
					account_journal_year.current_credit+=opening_balance
					account_journal_year.save()
			
			except Exception as err:
				response_data  = err.args 
				transaction.rollback()

		elif (calltype == 'opening_balance_payment'):
			payment_pk={}
			try:
				with transaction.atomic():
				# try:
					vendorid = request.data.get('vendorid')
					amount_paid = Decimal(request.data.get('amount_paid'))
					modeid = request.data.get('modeid')
					date = request.data.get('date')
					cheque_rtgs_number=request.data.get('cheque_rtgs_number')
						
					vendor = Vendor.objects.for_tenant(this_tenant).get(id=vendorid)
					vendor_name = vendor.name
					opening_balance = vendor.opening_balance

					mode = payment_mode.objects.for_tenant(this_tenant).get(id=modeid)

					if (amount_paid > opening_balance):
						raise IntegrityError (('Amount paid cannot be more than opening balance.'))

					if (amount_paid <=0):
						raise IntegrityError (('Amount paid must be a positive number.'))						
					
					
					new_payment = other_payment()
					new_payment.payment_mode_id = modeid
					new_payment.payment_mode_name = mode.name
					new_payment.vendorid = vendorid
					new_payment.paid_on = date
					new_payment.payment_reason_details = "Opening Payment Clearance"
					new_payment.payment_reason_type = 1
					new_payment.amount_paid = amount_paid
					new_payment.cheque_rtgs_number = cheque_rtgs_number
					new_payment.tenant = this_tenant
					new_payment.save()

					payment_pk["Opening_"+str(vendorid)]=new_payment.id

					vendor.current_balance-= amount_paid
					vendor.save()

					payment_json=json.dumps(payment_pk, cls=DjangoJSONEncoder)
					remarks_payment = "Opening Payment Clearance against Vendor: "+vendor_name
					if (cheque_rtgs_number):
						remarks_payment+= ",Cheque No:  "+cheque_rtgs_number

					journal=new_journal(this_tenant,date,group_name="General",\
						remarks=remarks_payment, trn_id=new_payment.id, trn_type=12, other_data=payment_json)
					account= Account.objects.for_tenant(this_tenant).get(name__exact="Accounts Payable")
					new_journal_entry(this_tenant, journal, amount_paid, account, 1, date, vendor.name, vendor.id)
					new_journal_entry(this_tenant, journal, amount_paid, mode.payment_account, 2, date)
			
			except Exception as err:
				response_data  = err.args 
				transaction.rollback()
		
		jsondata = json.dumps(response_data,cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)
	else:
		calltype = request.GET.get('calltype')
		if (calltype == 'vendor_opening_details'):
			vendorid = request.GET.get('vendorid')
			vendor = Vendor.objects.for_tenant(this_tenant).get(id=vendorid)
			opening_balance = vendor.opening_balance
			total_payment = other_payment.objects.for_tenant(this_tenant).filter(vendorid = vendorid, payment_reason_type = 1).\
				aggregate(Sum('amount_paid'))

			response_data['opening_balance'] = opening_balance
			response_data['opening_balance_paid'] = total_payment['amount_paid__sum']

		jsondata = json.dumps(response_data,cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)
			# print(total_payment)


@api_view(['GET'],)
def debit_note_new_noninventory(request):
	return render(request,'purchase/debit_note_voucher.html', {'extension': 'base.html'})