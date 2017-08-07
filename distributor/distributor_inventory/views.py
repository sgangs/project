from io import BytesIO
import django_excel as excel
from decimal import Decimal
import xlrd
import datetime as dt

from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum
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
from reportlab.graphics.barcode import code128
from reportlab.lib.units import mm


from distributor_master.models import Unit, Product, Warehouse
from distributor_user.models import Tenant
from distributor_account.models import Account, tax_transaction, payment_mode, accounting_period,\
									account_inventory, account_year_inventory, journal_inventory, journal_entry_inventory
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
def inventory_data(request):
	extension="base.html"
	this_tenant=request.user.tenant
	calltype = request.GET.get('calltype')
	if (calltype == 'stockwise'):
		current_inventory=list(Inventory.objects.for_tenant(this_tenant).filter(quantity_available__gt=0).\
					select_related('product', 'warehouse').values('product__name','product__sku','purchase_date','expiry_date',\
					'purchase_price','warehouse__address_1','warehouse__address_2', 'warehouse__city').\
					annotate(available=Sum('quantity_available')).order_by('product__sku','product__name','purchase_date',))
	if (calltype == 'current'):
		current_inventory=list(Inventory.objects.for_tenant(this_tenant).filter(quantity_available__gt=0).\
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
		inventories=initial_inventory.objects.for_tenant(this_tenant).all()
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
			all_data = json.loads(request.POST.get('all_details'))
			total=0
			if (from_warehouseid == to_warehouseid):
				raise IntegrityError
			# unitid=request.POST.get('unit')
			# unit=Unit.objects.for_tenant(this_tenant).get(id=unitid)
			# multiplier=unit.multiplier
			# quantity=Decimal(request.POST.get('quantity'))*multiplier
			# batch=request.POST.get('batch')
			# manufacturing_date=request.POST.get('manufacturing_date')
			# expiry_date=request.POST.get('expiry_date')
			# serial_no=request.POST.get('serial_no')
			from_warehouse=Warehouse.objects.for_tenant(this_tenant).get(id=from_warehouseid)
			to_warehouse=Warehouse.objects.for_tenant(this_tenant).get(id=to_warehouseid)
			with transaction.atomic():
				try:
					new_inventory_transfer=inventory_transfer()
					new_inventory_transfer.from_warehouse=from_warehouse
					new_inventory_transfer.to_warehouse=to_warehouse
					new_inventory_transfer.initiated_on=date
					new_inventory_transfer.total_value=total
					new_inventory_transfer.in_transit=record_transit
					new_inventory_transfer.tenant=this_tenant
					new_inventory_transfer.save()

					for data in all_data:
						inventory_id=data['quantity']
						product=Product.objects.for_tenant(this_tenant).get(id=product_id)
						unit=Unit.objects.for_tenant(this_tenant).get(id=unit_id)
						multiplier=unit.multiplier
						actual_qty=Decimal(original_qty)*multiplier
						inventory_item=Inventory.objects.for_tenant(this_tenant).get(id=inventory_id)
						if (actual_qty>inventory_item.quantity_available):
							raise IntegrityError
						inventory_item.quantity_available-=actual_qty
						inventory_item.save()

						new_item=inventory_transfer_items()
						new_item.inventory_id=inventory_item.id
						new_item.transfer=new_inventory_transfer
						new_item.product=product
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
			if 'xls' not in f.name and 'xlsx' not in f.name:
				data['error'] = 2
				data['info'] = 'file type must be excel!'
				
			elif 0 == f.size:
				data['error'] = 3
				data['info'] = 'file content is empty!'
			# wb = xlrd.open_workbook(inventory)
			else:
				rows = opening_inventory_upload_save(f, this_tenant)
				if (rows):
					str1 = ' ,'.join(str(e) for e in rows)
					messages.add_message(request, messages.WARNING, 'There was error in the following rows: .'+str1)
					messages.add_message(request, messages.INFO, 'The rest of the data have been uploaded successfully.')	
				else:
					messages.add_message(request, messages.SUCCESS, 'Data uploaded successfully.')
				return redirect('inventory:opening_inventory')
		else:
			return HttpResponseBadRequest()
	else:
		form = UploadFileForm()
	return render(request,'master/upload_product.html',{'form': form,})




@login_required
def write_pdf_view(request, pk_detail):
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'attachment;; filename="barcode.pdf"'	
	this_tenant=request.user.tenant
	try:
		barcode=Product.objects.for_tenant(this_tenant).get(id=pk_detail).barcode
		buffer = BytesIO()
		p = canvas.Canvas(buffer)
		
		# Start writing the PDF here
		# p.drawString(100, 100, 'Hello world.')
		if barcode:
			barcode = code128.Code128(barcode,barHeight=15*mm,barWidth = 0.25*mm, humanReadable=True)
			y=5
			for i in range(12):
				x=5
				for j in range(4):
					barcode.drawOn(p,x*mm,y*mm)
					x=x+52.5
				y=y+24.75
				
			

			# End writing
			p.showPage()
			p.save()

			pdf = buffer.getvalue()
			buffer.close()
			response.write(pdf)

			return response
		else:
			messages.add_message(request, messages.WARNING, "Barcode for the product doesn't exist")
			return redirect('master:product_data')

	except:
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