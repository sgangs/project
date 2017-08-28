import json
# import datetime
from datetime import date, timedelta

from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.shortcuts import render
from django.http import HttpResponse

from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from distributor_master.models import Unit, Product, Vendor, Warehouse
from distributor_account.models import Account, tax_transaction, payment_mode,accounting_period,\
									account_inventory, account_year_inventory, journal_inventory, journal_entry_inventory
from distributor_account.journalentry import new_journal, new_journal_entry
from distributor_inventory.models import Inventory, inventory_ledger, warehouse_valuation
from distributor_inventory.inventory_utils import create_new_inventory_ledger

from distributor.global_utils import paginate_data
from .purchase_utils import *
from .serializers import *
from .models import *
from .excel_download import *

# @login_required
@api_view(['GET','POST'],)
def get_product(request):
	this_tenant=request.user.tenant
	if request.is_ajax():
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

@login_required
@api_view(['GET'],)
def purchase_receipt_new(request):
	return render(request,'purchase/purchase_receipt.html', {'extension': 'base.html'})
	
@api_view(['GET','POST'],)
def purchase_receipt_save(request):
	if request.method == 'POST':
		calltype = request.data.get('calltype')
		response_data = {}
		this_tenant=request.user.tenant
		#saving the receipt
		if (calltype == 'save'):
			with transaction.atomic():
				try:
					supplier_invoice=request.data.get('supplier_invoice')
					vendor_id = request.data.get('vendor')
					warehouse_id=request.data.get('warehouse')
					date=request.data.get('date')
					
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
					
					# if (abs(sum_total - total) <0.90 ):
					# 	total = sum_total
					duedate=request.data.get('duedate')

					bill_data = json.loads(request.data.get('bill_details'))

					vendor = Vendor.objects.for_tenant(this_tenant).get(id=vendor_id)
					warehouse = Warehouse.objects.for_tenant(this_tenant).get(id=warehouse_id)

					
					new_receipt=new_purchase_receipt(this_tenant, supplier_invoice, vendor, warehouse, date, duedate,\
							subtotal, cgsttotal, sgsttotal, igsttotal, round_value, total, 0)
					
					vat_paid={}
					cgst_paid={}
					sgst_paid={}
					igst_paid={}
					cgst_total=0
					sgst_total=0
					igst_total=0

					vendor_gst=vendor.gst

			#saving the receipt_line_item and linking them with foreign key to receipt
					for data in bill_data:
						productid=data['product_id']
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
						free_with_tax=original_free_with_tax*multiplier
						free_without_tax=0
						total_free=free_without_tax+free_with_tax
						
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
							create_new_inventory_ledger(product,warehouse, 1, date, quantity, \
								purchase_price, mrp,new_receipt.receipt_id, this_tenant)
							if total_free>0:
								create_new_inventory_ledger(product,warehouse, 1, date, quantity, \
								0, mrp,new_receipt.receipt_id, this_tenant)
							
							warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).get(warehouse=warehouse)
							warehouse_valuation_change.valuation+=quantity*purchase_price
							warehouse_valuation_change.save()

						if (cgst_p in sgst_paid):
							cgst_paid[cgst_p]+=cgst_v
						else:
							cgst_paid[cgst_p]=cgst_v
						if (sgst_p in sgst_paid):
							sgst_paid[sgst_p]+=sgst_v
						else:
							sgst_paid[sgst_p]=sgst_v
						if (igst_p in igst_paid):
							igst_paid[igst_p]+=igst_v
						else:
							igst_paid[igst_p]=igst_v

					for k,v in cgst_paid.items():
						if v>0:
							new_tax_transaction=tax_transaction()
							new_tax_transaction.transaction_type=1
							new_tax_transaction.tax_type="CGST"
							new_tax_transaction.tax_percent=k
							new_tax_transaction.tax_value=v
							new_tax_transaction.transaction_bill_id=new_receipt.id
							new_tax_transaction.transaction_bill_no=new_receipt.receipt_id
							new_tax_transaction.date=date
							new_tax_transaction.tenant=this_tenant
							if vendor_gst:
								new_tax_transaction.is_registered = True
							else:
								new_tax_transaction.is_registered = False
							new_tax_transaction.save()

					for k,v in sgst_paid.items():
						if v>0:
							new_tax_transaction=tax_transaction()
							new_tax_transaction.transaction_type=1
							new_tax_transaction.tax_type="SGST"
							new_tax_transaction.tax_percent=k
							new_tax_transaction.tax_value=v
							new_tax_transaction.transaction_bill_id=new_receipt.id
							new_tax_transaction.transaction_bill_no=new_receipt.receipt_id
							new_tax_transaction.date=date
							new_tax_transaction.tenant=this_tenant
							if vendor_gst:
								new_tax_transaction.is_registered = True
							else:
								new_tax_transaction.is_registered = False
							new_tax_transaction.save()

					for k,v in igst_paid.items():
						if v>0:
							new_tax_transaction=tax_transaction()
							new_tax_transaction.transaction_type=1
							new_tax_transaction.tax_type="IGST"
							new_tax_transaction.tax_percent=k
							new_tax_transaction.tax_value=v
							new_tax_transaction.transaction_bill_id=new_invoice.id
							new_tax_transaction.transaction_bill_no=new_invoice.invoice_id
							new_tax_transaction.date=date
							new_tax_transaction.tenant=this_tenant
							if vendor_gst:
								new_tax_transaction.is_registered = True
							else:
								new_tax_transaction.is_registered = False
							new_tax_transaction.save()

					if this_tenant.maintain_inventory:
						#Journal Entry for tenants with inventory
						remarks="Purchase Receipt No: "+str(new_receipt.receipt_id)
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
						new_journal_entry(this_tenant, journal, total, account, 2, date)						
							
						debit = journal.journalEntry_journal.filter(transaction_type=1).aggregate(Sum('value'))
						credit = journal.journalEntry_journal.filter(transaction_type=2).aggregate(Sum('value'))
						if (debit != credit):
							raise IntegrityError

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

					else:
						remarks="Purchase Receipt No: "+str(new_receipt.receipt_id)
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
						
						account= Account.objects.for_tenant(this_tenant).get(name__exact="Accounts Payable")
						new_journal_entry(this_tenant, journal, total, account, 2, date)

						debit = journal.journalEntry_journal.filter(transaction_type=1).aggregate(Sum('value'))
						credit = journal.journalEntry_journal.filter(transaction_type=2).aggregate(Sum('value'))
						if (debit != credit):
							raise IntegrityError

					response_data=new_receipt.id
				except:
					transaction.rollback()

		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)


# @login_required
@api_view(['GET','POST'],)
def all_receipts(request):
	this_tenant=request.user.tenant
	page_no = request.GET.get('page_no')
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
			if invoice_no:
				receipts=receipts.filter(supplier_invoice__icontains=invoice_no)

		elif (calltype== 'vendor_pending'):
			vendorid = request.GET.get('vendorid')
			vendor=Vendor.objects.for_tenant(this_tenant).get(id=vendorid)
			# print(vendor)
			receipts=purchase_receipt.objects.for_tenant(this_tenant).filter(vendor=vendor, final_payment_date__isnull=True).\
				values('id','receipt_id', 'supplier_invoice', \
				'date','vendor_name','total', 'amount_paid', 'payable_by')
		# response_data = list(receipts)

		# page_no = 1
		response_data={}
		# print(receipts.count())
		if page_no:
			response_data =  paginate_data(page_no, 10, list(receipts))
		else:
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
		'warehouse_pin','payable_by','subtotal','cgsttotal','sgsttotal','igsttotal','roundoff','total','amount_paid').get(id=pk)

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
		mode = payment_mode.objects.for_tenant(this_tenant).get(id=modeid)
		for item in payment_details:
			purchase_receipt_id=item['receipt_pk']
			amount_paid=Decimal(item['amount'])
			# cheque_rtgs_number=item['cheque_rtgs_number']
			with transaction.atomic():
				try:
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
					# new_purchase_payment.cheque_rtgs_number=cheque_rtgs_number
					new_purchase_payment.paid_on=date
					# new_purchase_payment.remarks=remarks
					new_purchase_payment.tenant=this_tenant
					new_purchase_payment.save()

					journal=new_journal(this_tenant,date,group_name="Purchase",\
						remarks='Payment Against: '+str(receipt.receipt_id), trn_id=new_purchase_payment.id, trn_type=2)
					account= Account.objects.for_tenant(this_tenant).get(name__exact="Accounts Payable")
					new_journal_entry(this_tenant, journal, amount_paid, account, 1, date)
					new_journal_entry(this_tenant, journal, amount_paid, mode.payment_account, 2, date)
				
				except:
					transaction.rollback()

	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

# @login_required
@api_view(['GET'],)
def payment_list(request):
	if request.method == 'GET':
		payments=purchase_payment.objects.for_tenant(request.user.tenant).all()
		serializer = PaymentSerializers(payments, many=True)		
		return Response(serializer.data)

@login_required
def payment_list_view(request):
	return render(request,'purchase/payment_list.html', {'extension': 'base.html'})

@login_required
def debit_note_return_view(request):
	return render(request,'purchase/debit_note_return.html', {'extension': 'base.html'})


@login_required
@api_view(['GET','POST'],)
def debit_note_save(request):
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		this_tenant=request.user.tenant
		if (calltype == 'save'):
			with transaction.atomic():
				try:
					customer_id = request.data.get('customer')
					warehouse_id=request.data.get('warehouse')
					credit_note_no=request.data.get('credit_note_no')
					date=request.data.get('date')
					subtotal=Decimal(request.data.get('subtotal'))
					taxtotal=Decimal(request.data.get('taxtotal'))
					total=Decimal(request.data.get('total'))
					bill_data = json.loads(request.data.get('bill_details'))

					customer = Customer.objects.for_tenant(this_tenant).get(id=customer_id)
					warehouse = Warehouse.objects.for_tenant(this_tenant).get(id=warehouse_id)

					customer_name=customer.name
					customer_address=customer.address_1+", "+customer.address_2
					customer_state=customer.state
					customer_city=customer.city
					customer_pin=customer.pin
					
					ware_address=warehouse.address_1+", "+warehouse.address_2
					ware_state=warehouse.state
					ware_city=warehouse.city
					ware_pin=warehouse.pin
					
					new_debit_note=debit_note()
					new_debit_note.tenant=this_tenant

					new_debit_note.date = date
					
					new_debit_note.customer=customer
					new_debit_note.customer_name=customer_name
					new_debit_note.customer_address=customer_address
					new_debit_note.customer_state=customer_state
					new_debit_note.customer_city=customer_city
					new_debit_note.customer_pin=customer_pin

					new_debit_note.warehouse=warehouse
					new_debit_note.warehouse_address=ware_address
					new_debit_note.warehouse_state=ware_state
					new_debit_note.warehouse_city=ware_city
					new_debit_note.warehouse_pin=ware_pin
					
					new_debit_note.subtotal=subtotal
					new_debit_note.taxtotal=taxtotal
					new_debit_note.total = total
					new_invoice.save()
					
					remarks="Debit Note No: "+str(new_debit_note.note_id)
					journal=new_journal(this_tenant, date,"Purchase",remarks, trn_id=new_debit_note.id, trn_type=3)
					# debit_note_account = request.data.get('debit_note_account')
					account= Account.objects.for_tenant(this_tenant).get(name__exact="Inventory")
					new_journal_entry(this_tenant, journal, taxtotal, account, 2, date)
					# This has to change.
					account= Account.objects.for_tenant(this_tenant).get(name__exact="Accounts Payable")
					new_journal_entry(this_tenant, journal, total, account, 1, date)
					
					debit = journal.journalEntry_journal.filter(transaction_type=1).aggregate(Sum('value'))
					credit = journal.journalEntry_journal.filter(transaction_type=2).aggregate(Sum('value'))
					if (debit != credit):
						raise IntegrityError

					products_cost=0

					for data in bill_data:
						productid=data['product_id']
						unitid=data['unit_id']
						is_tax=data['is_tax']

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
						if is_tax:
							LineItem.vat_type=product.vat_type
							LineItem.tax_percent=product.tax.percentage

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
						for k,v in price_list.items():
							new_inventory_ledger=inventory_ledger()
							new_inventory_ledger.product=product
							new_inventory_ledger.warehouse=warehouse
							new_inventory_ledger.transaction_type=5
							new_inventory_ledger.date=date
							new_inventory_ledger.quantity=v['quantity']
							new_inventory_ledger.purchase_price=v['pur_rate']
							new_inventory_ledger.transaction_bill_id=new_debit_note.note_id
							new_inventory_ledger.tenant=this_tenant
							new_inventory_ledger.save()
						
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
		