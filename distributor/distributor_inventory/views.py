from io import BytesIO
import calendar
import django_excel as excel
from datetime import timedelta, date
from decimal import Decimal
import xlrd

from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum, F, Case, When
from django.http import HttpResponse
from django.utils import timezone
from django.utils.timezone import localtime
import json
#from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.graphics.barcode import code128
from reportlab.platypus import Image, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


from distributor_master.models import Unit, Product, Warehouse
from distributor_user.models import Tenant
from distributor_account.models import Account, tax_transaction, payment_mode, accounting_period,\
									account_inventory, account_year_inventory, journal_inventory, journal_entry_inventory
from distributor.global_utils import paginate_data, render_to_pdf, daterange_list
from .forms import *
from .models import *
from .serializers import *
from .inventory_utils import *
from .inventory_control import *


@login_required
@user_passes_test_custom(tenant_has_inventory, redirect_namespace='inventory:not_maintained_inventory')
def inventory_template(request):
	extension="base.html"
	return render (request, 'inventory/inventory_list.html',{'extension':extension})

@login_required
def not_maintained_inventory(request):
	return render (request, 'error/not_maintained_inventory.html')


# @login_required
@api_view(['GET', 'POST', ])
# @user_passes_test_custom(tenant_has_inventory, redirect_namespace='inventory:not_maintained_inventory')
def inventory_data(request):
	extension="base.html"
	this_tenant=request.user.tenant
	calltype = request.GET.get('calltype')
	
	if (calltype == 'stockwise'):
		current_inventory=list(Inventory.objects.for_tenant(this_tenant).filter(quantity_available__gt=0).\
					select_related('product', 'warehouse').values('product__name','product__sku','purchase_date','expiry_date',\
					'purchase_price','warehouse__address_1','warehouse__address_2', 'warehouse__city').\
					annotate(available=Sum('quantity_available')).order_by('product__sku','product__name','purchase_date',))
	
	elif (calltype == 'current'):
		current_inventory=list(Inventory.objects.for_tenant(this_tenant).filter(quantity_available__gt=0).\
					select_related('product', 'warehouse').values('product__name','product__sku','expiry_date',\
					'purchase_price','warehouse__address_1','warehouse__address_2', 'warehouse__city').\
					annotate(available=Sum('quantity_available')).order_by('product__sku','product__name'))
	
	elif (calltype == 'manufacturer group'):
		current_inventory = list(Inventory.objects.for_tenant(this_tenant).filter(quantity_available__gt=0).\
						select_related('product__manufacturer',).values('product__manufacturer__name', 'product__manufacturer__id').\
						annotate(total_value=Sum(F('quantity_available')*F('purchase_price'))))
	
	elif(calltype == 'download_current'):
		current_inventory=list(Inventory.objects.for_tenant(this_tenant).filter(quantity_available__gt=0).\
					select_related('product', 'warehouse').values('product__name','expiry_date',\
					'purchase_price','warehouse__address_1','warehouse__address_2', 'warehouse__city').\
					annotate(available=Sum('quantity_available')).order_by('product__name'))
		context = {
			'inventories': current_inventory,
			'tenant':this_tenant
		}
		pdf = render_to_pdf('inventory/current_inventory_pdf.html', context)
		response = HttpResponse(pdf, content_type='application/pdf')
		filename = "Current Inventory.pdf" 
		content = "attachment; filename='%s'" %(filename)
		response['Content-Disposition'] = content
		return response

	elif (calltype == 'manufacturer products'):
		manufacturer_id = request.GET.get('manufac_id')
		if not manufacturer_id or manufacturer_id == 'null':
			products=Product.objects.for_tenant(this_tenant).filter(manufacturer__isnull=True)
		else:
			manufacturer = Manufacturer.objects.for_tenant(this_tenant).get(id=manufacturer_id)
			products=Product.objects.for_tenant(this_tenant).filter(manufacturer = manufacturer)
		current_inventory=list(Inventory.objects.for_tenant(this_tenant).filter(quantity_available__gt=0, product__in = products).\
					select_related('product', 'warehouse').values('product__name','product__sku','expiry_date',\
					'purchase_price','warehouse__address_1','warehouse__address_2', 'warehouse__city').\
					annotate(available=Sum('quantity_available')).order_by('product__sku','product__name'))

	jsondata = json.dumps(current_inventory, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)


@login_required
@user_passes_test_custom(tenant_has_inventory, redirect_namespace='inventory:not_maintained_inventory')
def opening_inventory(request):
	extension="base.html"
	return render (request, 'inventory/opening_inventory.html',{'extension':extension})

@api_view(['GET', 'POST', ])
def opening_inventory_data(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		inventories=initial_inventory.objects.for_tenant(this_tenant).all().order_by('product')
		serializer = initialInventorySerializers(inventories, many=True)
		return Response(serializer.data)
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		if (calltype == 'newinventory'):
			productid=int(request.POST.get('productid'))
			warehouseid=int(request.POST.get('warehouse'))
			unitid=request.POST.get('unit')
			unit=Unit.objects.for_tenant(this_tenant).get(id=unitid)
			multiplier=unit.multiplier
			quantity=Decimal(request.POST.get('quantity'))*multiplier
			# batch=request.POST.get('batch')
			# manufacturing_date=request.POST.get('manufacturing_date')
			# expiry_date=request.POST.get('expiry_date')
			# serial_no=request.POST.get('serial_no')
			purchase_price=Decimal(request.POST.get('purchase'))
			tentative_sales_price=request.POST.get('tsp')
			mrp=request.POST.get('mrp')
			date=request.POST.get('date')

			if not date:
				date=this_tenant.registered_on
			product=Product.objects.for_tenant(this_tenant).get(id=productid)
			warehouse=Warehouse.objects.for_tenant(this_tenant).get(id=warehouseid)
			total_inventory_value=quantity*purchase_price
			with transaction.atomic():
				try:
					new_initial_inventory=initial_inventory()
					new_initial_inventory.product=product
					new_initial_inventory.warehouse=warehouse
					new_initial_inventory.quantity=quantity
					# new_initial_inventory.batch=batch
					# new_initial_inventory.manufacturing_date=manufacturing_date
					# new_initial_inventory.expiry_date=expiry_date
					# new_initial_inventory.serial_no=serial_no
					new_initial_inventory.purchase_price=purchase_price
					new_initial_inventory.tentative_sales_price=tentative_sales_price
					new_initial_inventory.mrp=mrp
					new_initial_inventory.tenant=this_tenant
					new_initial_inventory.save()

					new_inventory=Inventory()
					new_inventory.product=product
					new_inventory.warehouse=warehouse
					new_inventory.purchase_date=date
					new_inventory.purchase_quantity=quantity
					new_inventory.quantity_available=quantity
					# new_inventory.batch=batch
					# new_inventory.manufacturing_date=manufacturing_date
					# new_inventory.expiry_date=expiry_date
					# new_inventory.serial_no=serial_no
					new_inventory.purchase_price=purchase_price
					new_inventory.tentative_sales_price=tentative_sales_price
					new_inventory.mrp=mrp
					new_inventory.tenant=this_tenant
					new_inventory.save()

					warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).get(warehouse=warehouse)
					warehouse_valuation_change.valuation+=total_inventory_value
					warehouse_valuation_change.save()

					# inventory_account=Account.objects.for_tenant(this_tenant).get(name='Inventory')
					# current_period=accounting_period.objects.for_tenant(this_tenant).get(current_period=True)
					# inventory_account_data=account_year.objects.for_tenant(this_tenant).get(account=inventory_account, \
					# 						accounting_period=current_period)
					# inventory_account_data.first_debit=total_inventory_value
					# inventory_account_data.current_debit+=total_inventory_value
					# inventory_account_data.save()

					inventory_acct=account_inventory.objects.for_tenant(this_tenant).get(name__exact="Inventory")
					current_period=accounting_period.objects.for_tenant(this_tenant).get(current_period=True)
					inventory_acct_year=account_year_inventory.objects.for_tenant(this_tenant).\
												get(account_inventory=inventory_acct, accounting_period = current_period)
					try:
						inventory_acct_year.first_debit+=total_inventory_value
					except:
						inventory_acct_year.first_debit=total_inventory_value
					try:
						inventory_acct_year.opening_debit+=total_inventory_value
					except:
						inventory_acct_year.opening_debit=total_inventory_value
					try:
						inventory_acct_year.current_debit+=total_inventory_value
					except:
						inventory_acct_year.current_debit=total_inventory_value
					inventory_acct_year.save()


				except:
					transaction.rollback()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)


@api_view(['GET','POST'],)
def get_product(request):
	this_tenant=request.user.tenant
	if request.is_ajax():
		q = request.GET.get('term', '')
		products = Product.objects.for_tenant(this_tenant).filter(name__icontains  = q )[:10].select_related('default_unit', 'tax')
		response_data = []
		for item in products:
			item_json = {}
			item_json['id'] = item.id
			item_json['label'] = item.name
			response_data.append(item_json)
		data = json.dumps(response_data)
	else:
		data = 'fail'
	mimetype = 'application/json'
	return HttpResponse(data, mimetype)

@api_view(['GET'],)
def get_product_inventory(request):
	this_tenant=request.user.tenant
	if request.is_ajax():
		product_id = request.GET.get('product_id')
		warehouse_id = request.GET.get('warehouse_id')
		product_quantity=list(Inventory.objects.for_tenant(this_tenant).filter(quantity_available__gt=0,\
					product=product_id, warehouse=warehouse_id).values('id','purchase_price','tentative_sales_price','mrp',\
					'purchase_date','quantity_available'))
	jsondata = json.dumps(product_quantity,  cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

@login_required
@user_passes_test_custom(tenant_has_inventory, redirect_namespace='inventory:not_maintained_inventory')
def inventory_transfer_template(request):
	extension="base.html"
	return render (request, 'inventory/inventory_transfer.html',{'extension':extension})

@login_required
@user_passes_test_custom(tenant_has_inventory, redirect_namespace='inventory:not_maintained_inventory')
def inventory_wastage_template(request):
	extension="base.html"
	return render (request, 'inventory/inventory_wastage.html',{'extension':extension})


@login_required
@user_passes_test_custom(tenant_has_inventory, redirect_namespace='inventory:not_maintained_inventory')
def transfer_detail_view(request, pk):
	return render(request,'inventory/internal_challan_detail.html', {'extension': 'base.html', 'pk':pk})


@api_view(['GET'],)
@user_passes_test_custom(tenant_has_inventory, redirect_namespace='inventory:not_maintained_inventory')
def transfer_details(request, pk):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		transfer=inventory_transfer.objects.for_tenant(this_tenant).values('id','transfer_id','initiated_on',\
		'from_warehouse','from_warehouse_address','to_warehouse', 'to_warehouse_address',).get(id=pk)
		
		line_items=list(inventory_transfer_items.objects.filter(transfer=transfer['id']).values('id','product__name','product__id',\
			'product__hsn','quantity',))
		
		transfer['line_items']=line_items
		# invoice['tenant_gst']=this_tenant.gst
		# invoice['tenant_name']=this_tenant.name
		# invoice['tenant_dl1']=this_tenant.dl_1
		# invoice['tenant_dl2']=this_tenant.dl_2
		
		jsondata = json.dumps(transfer, cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)


@api_view(['GET', 'POST'],)
def inventory_transfer_data(request):
	this_tenant=request.user.tenant
	response_data=[]
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		if (calltype == 'newtransfer'):
			from_warehouseid=int(request.POST.get('from_warehouseid'))
			to_warehouseid=int(request.POST.get('to_warehouseid'))
			date=request.POST.get('date')
			record_transit=request.POST.get('record_transit')
			if (record_transit == 'true'):
				record_transit=True
			elif (record_transit == 'false'):
				record_transit=False
			else:
				record_transit=False

			all_data = json.loads(request.POST.get('all_details'))
			total=0
			if (from_warehouseid == to_warehouseid):
				raise IntegrityError
			
			from_warehouse=Warehouse.objects.for_tenant(this_tenant).get(id=from_warehouseid)
			to_warehouse=Warehouse.objects.for_tenant(this_tenant).get(id=to_warehouseid)
			with transaction.atomic():
				try:
					new_inventory_transfer=inventory_transfer()
					new_inventory_transfer.from_warehouse=from_warehouse
					new_inventory_transfer.from_warehouse_address=from_warehouse.address_1+", "+from_warehouse.address_2  
					new_inventory_transfer.from_warehouse_state=from_warehouse.state
					new_inventory_transfer.from_warehouse_city=from_warehouse.city
					new_inventory_transfer.from_warehouse_pin=from_warehouse.pin

					new_inventory_transfer.to_warehouse=to_warehouse
					new_inventory_transfer.to_warehouse_address=to_warehouse.address_1+", "+to_warehouse.address_2  
					new_inventory_transfer.to_warehouse_state=to_warehouse.state
					new_inventory_transfer.to_warehouse_city=to_warehouse.city
					new_inventory_transfer.to_warehouse_pin=to_warehouse.pin

					new_inventory_transfer.initiated_on=date
					new_inventory_transfer.total_value=total
					new_inventory_transfer.in_transit=record_transit
					new_inventory_transfer.tenant=this_tenant
					new_inventory_transfer.save()

					for data in all_data:
						original_qty=data['quantity']
						product_id=data['product_id']
						unit_id=data['unit_id']
						inventory_id=data['inventory_id']
						product=Product.objects.for_tenant(this_tenant).get(id=product_id)
						unit=Unit.objects.for_tenant(this_tenant).get(id=unit_id)
						multiplier=unit.multiplier
						actual_qty=Decimal(original_qty)*multiplier
						inventory_item=Inventory.objects.for_tenant(this_tenant).get(id=inventory_id)
						if (actual_qty>inventory_item.quantity_available):
							raise IntegrityError
						elif (actual_qty == inventory_item.quantity_available):
							inventory_item.delete()
						else:	
							inventory_item.quantity_available-=actual_qty
							inventory_item.save()

						new_item=inventory_transfer_items()
						new_item.inventory_id=inventory_id
						new_item.transfer=new_inventory_transfer
						new_item.product=product
						new_item.product_name=product.name
						new_item.product_hsn=product.hsn_code
						new_item.quantity=original_qty
						new_item.unit=unit
						# new_inventory.batch=batch
						# new_inventory.manufacturing_date=manufacturing_date
						# new_inventory.expiry_date=expiry_date
						# new_inventory.serial_no=serial_no
						new_item.purchase_date=inventory_item.purchase_date
						new_item.purchase_price=inventory_item.purchase_price
						new_item.tentative_sales_price=inventory_item.tentative_sales_price
						new_item.mrp=inventory_item.mrp
						new_item.tenant=this_tenant
						new_item.save()

						new_inventory=Inventory()
						new_inventory.product=product
						new_inventory.warehouse=to_warehouse
						new_inventory.purchase_date=inventory_item.purchase_date
						new_inventory.purchase_quantity=actual_qty
						new_inventory.quantity_available=actual_qty
						# new_inventory.batch=batch
						# new_inventory.manufacturing_date=manufacturing_date
						# new_inventory.expiry_date=expiry_date
						# new_inventory.serial_no=serial_no
						new_inventory.purchase_price=inventory_item.purchase_price
						new_inventory.tentative_sales_price=inventory_item.tentative_sales_price
						new_inventory.mrp=inventory_item.mrp
						new_inventory.tenant=this_tenant
						new_inventory.save()

						total+=inventory_item.purchase_price*actual_qty
						new_inventory_transfer.total_value=total
						new_inventory_transfer.save()
					
					warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).get(warehouse=from_warehouse)
					warehouse_valuation_change.valuation-=total
					warehouse_valuation_change.save()
					
					if not record_transit:
						warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).get(warehouse=to_warehouse)
						warehouse_valuation_change.valuation+=total
						warehouse_valuation_change.save()


				except:
					transaction.rollback()


	jsondata = json.dumps(response_data)
	return HttpResponse(jsondata)


@login_required
@user_passes_test_custom(tenant_has_inventory, redirect_namespace='inventory:not_maintained_inventory')
def transfer_list(request):
	return render(request,'inventory/transfer_list.html', {'extension': 'base.html'})


@api_view(['GET'],)
@user_passes_test_custom(tenant_has_inventory, redirect_namespace='inventory:not_maintained_inventory')
def transfer_list_data(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		calltype = request.GET.get('calltype')
		page_no = request.GET.get('page_no')
		response_data={}
		filter_data={}
		if (calltype == 'all_transfer'):
			transfers=inventory_transfer.objects.for_tenant(this_tenant).all().values('id','transfer_id', \
				'initiated_on','from_warehouse', 'from_warehouse_address', 'to_warehouse', 'to_warehouse_address', 'total_value').\
				order_by('-initiated_on', '-transfer_id')[:300]
		
		elif (calltype == 'apply_filter'):
			customers=json.loads(request.GET.get('customers'))
			start=request.GET.get('start')
			end=request.GET.get('end')
			invoice_no=request.GET.get('invoice_no')
			productid=request.GET.get('productid')
			sent_with=request.GET.get('sent_with')
			if (start and end):
				invoices=sales_invoice.objects.for_tenant(this_tenant).filter(date__range=[start,end]).all().\
							select_related('invoiceLineItem_salesInvoice').\
							values('id','invoice_id','date','customer_name','total', 'amount_paid', 'payable_by').order_by('-date', '-invoice_id')
			if (len(customers)>0):
				customers_list=[]
				for item in customers:
					customers_list.append(item['customerid'])
				if (sent_with == 'all_invoices'):
					invoices=invoices.filter(customer__in=customers_list).\
						all()
				if (sent_with == 'unpaid_invoices'):
					invoices=invoices.filter(final_payment_date__isnull=True, customer__in=customers_list).\
						all()
			else:
				if (sent_with == 'all_invoices'):
					pass
				if (sent_with == 'unpaid_receipts'):
					invoices=invoices.filter(final_payment_date__isnull=True).\
						all()
			if invoice_no:
				invoices=invoices.filter(invoice_id__icontains=invoice_no)
			if productid:
				product=Product.objects.for_tenant(this_tenant).get(id=productid)
				invoices=invoices.filter(invoiceLineItem_salesInvoice__product=product).\
						values('id','invoice_id','date','customer_name','total', 'amount_paid', 'payable_by').order_by('-date', '-invoice_id')
		
			filter_summary=invoices.aggregate(pending=Sum('total')-Sum('amount_paid'), total_sum=Sum('total'))
			filter_data['total_pending'] = filter_summary['pending']
			filter_data['total_value'] = filter_summary['total_sum']
		
		if page_no:
			response_data =  paginate_data(page_no, 10, list(transfers))
			response_data.update(filter_data)
		else:
			response_data['object']=list(transfers)
			response_data.update(filter_data)
	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)



@login_required
@user_passes_test_custom(tenant_has_inventory, redirect_namespace='inventory:not_maintained_inventory')
def import_opening_inventory(request):
	this_tenant=request.user.tenant
	if request.method == "POST":
		form = UploadFileForm(request.POST, request.FILES)
		def choice_func(row):
			data=oepning_inventory_validate(row, this_tenant, calculate_total=True)
			return data		
		if form.is_valid():
			# inventory=request.FILES['Inventory_Import']
			data={}
			f = request.FILES['file']
			data['name'] = f.name
			data['size'] = f.size / 1024
			form_data = form.cleaned_data
			identify_type = form_data['Identify_your_product_with']
			if 'xls' not in f.name and 'xlsx' not in f.name:
				data['error'] = 2
				data['info'] = 'file type must be excel!'
				
			elif 0 == f.size:
				data['error'] = 3
				data['info'] = 'file content is empty!'
			# wb = xlrd.open_workbook(inventory)
			else:
				rows = opening_inventory_upload_save(f, this_tenant, identify_type)
				if (rows):
					str1 = ' ,'.join(str(e) for e in rows)
					messages.add_message(request, messages.WARNING, 'There was error in the following rows: .'+str1)
					messages.add_message(request, messages.INFO, 'The rest of the data have been uploaded successfully.')	
				else:
					messages.add_message(request, messages.SUCCESS, 'Data uploaded successfully.')
				return redirect('inventory:opening_inventory')
		else:
			messages.add_message(request, messages.WARNING, 'There was error ')
			return render(request,'inventory/upload_opening_inventory.html',{'form': form,})
	else:
		form = UploadFileForm()
	return render(request,'inventory/upload_opening_inventory.html',{'form': form,})

@api_view(['GET',])
def inventory_import_format(request):
	# if 'excel' in request.POST:
	response = HttpResponse(content_type='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename=Inventory_Import.xlsx'
	xlsx_data = inventory_format()
	response.write(xlsx_data)
	return response


@login_required
def write_pdf_view(request, pk_detail):
	try:
		this_tenant=request.user.tenant
		product = Product.objects.for_tenant(this_tenant).get(id=pk_detail) 
		barcode = product.barcode
		name = product.name
		
		if (len(name) > 30):
			name_text = name[:25]+"..."
		else:
			name_text = name

		response = HttpResponse(content_type='application/pdf')
		response['Content-Disposition'] = 'attachment;; filename="Barcode"'+name_text+'"48.pdf"'	
		

		buffer = BytesIO()
		# size = potrait(A4)
		
		lWidth, lHeight = A4
		p = canvas.Canvas(buffer)

		p.setPageSize((lWidth, lHeight))

		styles = getSampleStyleSheet()

		# name_text = Paragraph(name, style=styles["Normal"])
		
		# Start writing the PDF here
		# p.drawString(100, 100, 'Hello world.')
		if barcode:
			barcode = code128.Code128(barcode,barHeight=15*mm,barWidth = 0.25*mm, humanReadable=True)
			# y=5
			# for i in range(12):
			# 	x=5
			# 	for j in range(4):
			# 		barcode.drawOn(p,x*mm,y*mm)
			# 		x=x+52.5
			# 	y=y+24.75
			
			y=15
			for i in range(12):
				x=4
				for j in range(4):
					barcode.drawOn(p,x*mm,y*mm)
					# name_text.drawOn(p,x*mm,(y+14)*mm)
					p.setFont("Helvetica", 6)
					p.drawString((x+7)*mm,(y-5)*mm,name_text)
					x=x+53
				y=y+24

			# End writing
			# p.showPage()
			p.save()

			pdf = buffer.getvalue()
			buffer.close()
			response.write(pdf)

			return response
		else:
			messages.add_message(request, messages.WARNING, "Barcode for the product doesn't exist")
			return redirect('master:product_data')

	except Exception as err:
		messages.add_message(request, messages.WARNING, "Barcode for the product doesn't exist")
		return redirect('master:product_data')


@api_view(['GET', 'POST', ])
def product_valuation_movement_data(request):
	extension="base.html"
	this_tenant=request.user.tenant
	calltype = request.GET.get('calltype')
	warehouse=request.GET.get('warehouse')
	# start=request.GET.get('start')
	# end=request.GET.get('end')
	date=request.GET.get('date')
	if (calltype == 'productid'):
		productid=request.GET.get('product')
		product=Product.objects.for_tenant(this_tenant).get(id=productid)
	elif (calltype == 'productid'):
		productbarcode=request.GET.get('product')
		product=Product.objects.for_tenant(this_tenant).get(id=productbarcode)
	response_data=list(inventory_ledger.objects.filter(product=product, warehouse=warehouse, date__gte=date).order_by('-date','-id').\
					values('quantity','purchase_price', 'transaction_type','date', 'actual_sales_price'))
	current_avl=Inventory.objects.filter(product=product, warehouse=warehouse, quantity_available__gt=0)
	current_val=0
	current_qty=0
	for item in current_avl:
		# current_val+=item['purchase_price']*item['quantity_available']
		current_val+=item.purchase_price*item.quantity_available
		current_qty+=item.quantity_available
	open_val=current_val
	open_qty=current_qty
	if (len(response_data) == 0):
		response_data=[{'transaction_type' : 0, 'current_qty':current_qty,'current_val':round(current_val,2) }]
	else:
		for item in response_data:
			if item['transaction_type'] in [1,3,4,8,10]:
				item['current_qty']=open_qty
				item['current_val']=round(open_val,2)
				open_qty-=item['quantity']
				open_val-=(item['purchase_price']*item['quantity'])
			else:
				item['current_qty']=open_qty
				item['current_val']=round(open_val,2)
				open_qty+=item['quantity']
				open_val+=(item['purchase_price']*item['quantity'])
	

	# if (calltype == 'stockwise'):
	# 	current_inventory=list(Inventory.objects.for_tenant(this_tenant).filter(quantity_available__gt=0).\
	# 				select_related('product', 'warehouse').values('product__name','product__sku','purchase_date','expiry_date',\
	# 				'purchase_price','warehouse__address_1','warehouse__address_2', 'warehouse__city').\
	# 				annotate(available=Sum('quantity_available')).order_by('purchase_date'))
	# if (calltype == 'current'):
	# 	current_inventory=list(Inventory.objects.for_tenant(this_tenant).filter(quantity_available__gt=0).\
	# 				select_related('product', 'warehouse').values('product__name','product__sku','expiry_date',\
	# 				'purchase_price','warehouse__address_1','warehouse__address_2', 'warehouse__city').\
	# 				annotate(available=Sum('quantity_available')).order_by('product__sku'))
	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)
		

@login_required
@user_passes_test_custom(tenant_has_inventory, redirect_namespace='inventory:not_maintained_inventory')
def product_valuation_movement_template(request):
	extension="base.html"
	return render (request, 'inventory/product_movement.html',{'extension':extension})


@api_view(['GET','POST'],)
@user_passes_test_custom(tenant_has_inventory, redirect_namespace='inventory:not_maintained_inventory')
def get_product(request):
	this_tenant=request.user.tenant
	if request.method=='GET':
		q = request.GET.get('term', '')
		calltype=request.GET.get('calltype')
		products = Product.objects.for_tenant(this_tenant).filter(name__icontains  = q )[:10]
		response_data = []
		for item in products:
			item_json = {}
			item_json['id'] = item.id
			item_json['label'] = item.name
			response_data.append(item_json)
		data = json.dumps(response_data)
	else:
		data = 'fail'
	mimetype = 'application/json'
	return HttpResponse(data, mimetype)


@user_passes_test_custom(tenant_has_inventory, redirect_namespace='inventory:not_maintained_inventory')
def delete_inventory_view(request):
	extension="base.html"
	return render (request, 'inventory/inventory_delete.html',{'extension':extension})


@api_view(['GET'],)
@user_passes_test_custom(tenant_has_inventory, redirect_namespace='inventory:not_maintained_inventory')
def productwise_opening_inventory(request):
	this_tenant = request.user.tenant
	product_id = request.GET.get('product_id')
	inventory_list = list(initial_inventory.objects.for_tenant(this_tenant).filter(product = product_id).select_related('warehouse').\
					values('id','warehouse__address_1','warehouse__address_2', 'quantity', 'purchase_price', 'tentative_sales_price', 'mrp'))

	jsondata = json.dumps(inventory_list, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)



@api_view(['POST'],)
def delete_opening_inventory(request):
	this_tenant = request.user.tenant
	if request.method=='POST':
		response_data = {}
		inventory_id_list = json.loads(request.data.get('inventory_id_list'))
		# revised_qty = request.data.get('revised_qty')
		# Put this insode atomic transaction
		proceed = True
		total_purchase_price = 0
		with transaction.atomic():
			try:
				for each_item in inventory_id_list:
					# Get revised_qty, inventory_id
					revised_qty = each_item['revised_qty']
					inventory_id = each_item['inventory_id']
					initial_inventory_selected=initial_inventory.objects.for_tenant(this_tenant).get(id = inventory_id)
					if not revised_qty:
						proceed = False
					else:
						if (revised_qty < 0):
							raise IntegrityError
						quantity_reduced = initial_inventory_selected.quantity - revised_qty 
						product=initial_inventory_selected.product
						purchase_price = initial_inventory_selected.purchase_price
						warehouse = initial_inventory_selected.warehouse
						tsp = initial_inventory_selected.tentative_sales_price
						mrp = initial_inventory_selected.mrp
						available_inventory = Inventory.objects.for_tenant(this_tenant).filter(product = product, \
												quantity_available__gt=0, warehouse = warehouse, \
												purchase_price = purchase_price, tentative_sales_price = tsp, mrp = mrp).order_by('purchase_date')
						quantity_reduced_loop = quantity_reduced
						for item in available_inventory:
							if item.quantity_available > quantity_reduced_loop:
								item.quantity_available = item.quantity_available - quantity_reduced_loop
								total_purchase_price+=purchase_price*quantity_reduced_loop
								quantity_reduced_loop = 0
							else:
								total_purchase_price+=purchase_price*item.quantity_available
								quantity_reduced_loop-=item.quantity_available
								item.quantity_available = 0
							item.save()
						if quantity_reduced_loop > 0:
							raise IntegrityError
						initial_inventory_selected.quantity=revised_qty
						initial_inventory_selected.save()

				warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).get(warehouse=warehouse)
				warehouse_valuation_change.valuation-=total_purchase_price
				warehouse_valuation_change.save()

				inventory_acct=account_inventory.objects.for_tenant(this_tenant).get(name__exact="Inventory")
				opening_period=accounting_period.objects.for_tenant(this_tenant).get(is_first_year=True)
				inventory_acct_year=account_year_inventory.objects.for_tenant(this_tenant).\
						get(account_inventory=inventory_acct, accounting_period = opening_period)
				inventory_acct_year.first_debit-=total_purchase_price
				inventory_acct_year.opening_debit-=total_purchase_price
				inventory_acct_year.current_debit-=total_purchase_price
				inventory_acct_year.save()

				response_data['result'] = True
				jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
			except:
				transaction.rollback()
		return HttpResponse(jsondata)


@api_view(['GET', 'POST', ])
def inventory_man_wise(request):
	this_tenant=request.user.tenant
	
	current_inventory = list(Inventory.objects.for_tenant(this_tenant).filter(quantity_available__gt=0).\
						values('product__manufacturer__name').\
						annotate(tol_value=Sum(F('quantity_available')*F('purchase_price'))))

	jsondata = json.dumps(current_inventory, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)


@api_view(['GET'])
@user_passes_test_custom(tenant_has_inventory, redirect_namespace='inventory:not_maintained_inventory')
def product_movement_consolidated_view(request):
	extension="base.html"
	return render (request, 'inventory/product_movement_consolidated.html',{'extension':extension})


@api_view(['GET'],)
@user_passes_test_custom(tenant_has_inventory, redirect_namespace='inventory:not_maintained_inventory')
def product_movement_consolidated_data(request):
	this_tenant = request.user.tenant
	start = request.GET.get('start')
	end = request.GET.get('end')
	warehouse = request.GET.get('warehouse')
	inventory_details = list(inventory_ledger.objects.for_tenant(this_tenant).filter(warehouse = warehouse, date__range=[start, end]).\
					select_related('product').values('product','product__name').order_by('product__name').annotate(\
						purchase_total=Sum(Case(When(transaction_type = 1, then = "quantity"))),\
						sales_total=Sum(Case(When(transaction_type__in = [2,9], then = "quantity")))))

	jsondata = json.dumps(inventory_details, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)


@api_view(['GET'],)
@user_passes_test_custom(tenant_has_inventory, redirect_namespace='inventory:not_maintained_inventory')
def product_monthly_movement_chart(request):
	extension="base.html"
	return render (request, 'inventory/product_monthly_movement_chart.html',{'extension':extension})

@api_view(['GET'],)
@user_passes_test_custom(tenant_has_inventory, redirect_namespace='inventory:not_maintained_inventory')
def product_monthly_movement_product(request):
	this_tenant = request.user.tenant
	manufacturer = request.GET.get('manufacturer')
	response_data={}
	products = list(Product.objects.for_tenant(this_tenant).filter(manufacturer = manufacturer).values('id', 'name'))
	response_data = products
	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)


@api_view(['GET'],)
@user_passes_test_custom(tenant_has_inventory, redirect_namespace='inventory:not_maintained_inventory')
def product_movement_data(request):
	this_tenant = request.user.tenant
	response_data = {}
	month = int(request.GET.get('month'))
	year = int(request.GET.get('year'))
	manufacturer = request.GET.get('manufacturer')
	warehouse = request.GET.get('warehouse')
	last_day = calendar.monthrange(year,month)[1]
	# warehouse = request.GET.get('warehouse')
	start = date(year, month, 1)
	end = date(year, month, last_day)
	products = Product.objects.for_tenant(this_tenant).filter(manufacturer = manufacturer).values('id')
	data = list(inventory_ledger.objects.for_tenant(this_tenant).filter(date__range=[start, end], product__in = products, warehouse = warehouse).\
					select_related('product').values('product','product__name', 'date').order_by('product__name').annotate(\
						sales_total=Sum(Case(When(transaction_type__in = [2,9], then = "quantity")))))
	newdata = {}	
	for entry in data:
	    prod_id = str(entry['product'])
	    entry_date = str(entry['date'])
	    newdata[prod_id+"_"+entry_date] = entry
	
	# for product in products:
	# 	for date in daterange_list(start, end):
	# 		key = str(product['id'])+"_"+str(date)
	# 		if key in newdata:
	# 			response_data[key] = newdata[key]
	# 				# print(newdata[key])
	# 		else:
	# 			response_data[key] = {'sales_total': Decimal('0'), 'product__name': product['name'], 'date': date, 'product': product['id']}

	response_data = newdata
	jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)


