import django_excel as excel
from datetime import date, datetime
from dateutil.rrule import *
from dateutil.parser import *
from decimal import Decimal

from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
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

from distributor_user.models import Tenant
from distributor_inventory.models import warehouse_valuation
from distributor.variable_list import state_list

from distributor.global_utils import paginate_data
from .serializers import *
from .models import *
from .forms import *
from .customer_support import *

@api_view(['GET'],)
def get_state_list(request):
	state_dict=dict((x, y) for x, y in state_list)
	jsondata = json.dumps(state_dict)
	return HttpResponse(jsondata)


# @login_required
@api_view(['GET','POST'],)
def customer_view(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		calltype = request.GET.get('calltype')
		if (calltype == 'one_customer'):
			customerid = request.GET.get('customerid')
			customer=Customer.objects.for_tenant(this_tenant).get(id=customerid)
			serializer = CustomerSerializers(customer)
		else:
			page_no=1
			customers=Customer.objects.for_tenant(this_tenant).order_by('key').all()
			# customers_paginated=paginate_data(page_no, 2, list(customers))
			# serializer = CustomerSerializers(customers_paginated['object'], many=True)
			serializer = CustomerSerializers(customers, many=True)
			# response_data['object']  = serializer.data
			# response_data['end'] = payments_paginated['end']
			# response_data['start'] = payments_paginated['start']
		return Response(serializer.data)
	elif request.method == 'POST':
		calltype = request.data.get('calltype')
		response_data = {}
		if (calltype == 'newcustomer'):
			name=request.data.get('name')
			key=request.data.get('key')
			address_1=request.data.get('address_1')
			address_2=request.data.get('address_2')
			state=request.data.get('state')
			city=request.data.get('city')
			pin=request.data.get('pin')
			phone_no=request.data.get('phone')
			cst=request.data.get('cst')
			tin=request.data.get('tin')
			gst=request.data.get('gst')
			dl1=request.data.get('dl1')
			dl2=request.data.get('dl2')
			details=request.data.get('details')
			zone_id=request.data.get('zone')
			if (zone_id):
				zone_selected=Zone.objects.for_tenant(this_tenant).get(id=zone_id)
			new_customer=Customer()
			new_customer.name=name
			new_customer.key=key
			new_customer.address_1=address_1
			new_customer.address_2=address_2
			new_customer.state=state
			new_customer.city=city
			new_customer.pin=pin
			new_customer.phone_no=phone_no
			new_customer.cst=cst
			new_customer.tin=tin
			new_customer.gst=gst
			new_customer.dl_2=dl2
			new_customer.dl_1=dl1
			new_customer.details=details
			if (zone_id):
				new_customer.zone=zone_selected
			new_customer.tenant=this_tenant
			new_customer.save()			
		
		elif (calltype == 'updatecustomer'):
			response_data = {}
			pk=request.data.get('pk')
			name=request.data.get('name')
			key=request.data.get('key')
			address_1=request.data.get('address_1')
			address_2=request.data.get('address_2')
			# state=request.data.get('state')
			city=request.data.get('city')
			pin=request.data.get('pin')
			phone_no=request.data.get('phone')
			cst=request.data.get('cst')
			tin=request.data.get('tin')
			gst=request.data.get('gst')
			dl1=request.data.get('dl1')
			dl2=request.data.get('dl2')
			details=request.data.get('details')
			# zone_id=request.data.get('zone')
			# if (zone_id):
				# zone_selected=Zone.objects.for_tenant(this_tenant).get(id=zone_id)
			old_customer=Customer.objects.for_tenant(this_tenant).get(id=pk)
			old_customer.name=name
			old_customer.key=key
			old_customer.address_1=address_1
			old_customer.address_2=address_2
			# old_customer.state=state
			old_customer.city=city
			old_customer.pin=pin
			old_customer.phone_no=phone_no
			old_customer.cst=cst
			old_customer.tin=tin
			old_customer.gst=gst
			old_customer.dl_2=dl2
			old_customer.dl_1=dl1
			old_customer.details=details
			# if (zone_id):
			# 	old_customer.zone=zone_selected
			# # old_customer.tenant=this_tenant
			old_customer.save()			
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

# @login_required
@api_view(['GET','POST'],)
def vendor_view(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		calltype = request.GET.get('calltype')
		if (calltype == 'one_vendor'):
			vendorid = request.GET.get('vendorid')
			vendor=Vendor.objects.for_tenant(this_tenant).get(id=vendorid)
			serializer = VendorSerializers(vendor)
		else:
			vendors=Vendor.objects.for_tenant(this_tenant).order_by('key').all()
			serializer = VendorSerializers(vendors, many=True)
		return Response(serializer.data)
	elif request.method == 'POST':
		calltype = request.data.get('calltype')
		response_data = {}
		if (calltype == 'newvendor'):
			name=request.data.get('name')
			key=request.data.get('key')
			ismanufac=request.data.get('ismanufac')
			address_1=request.data.get('address_1')
			address_2=request.data.get('address_2')
			state=request.data.get('state')
			city=request.data.get('city')
			pin=request.data.get('pin')
			phone_no=request.data.get('phone')
			cst=request.data.get('cst')
			tin=request.data.get('tin')
			gst=request.data.get('gst')
			details=request.data.get('details')
			if (ismanufac == 'true'):
				ismanufac=True
			elif (ismanufac == 'false'):
				ismanufac=False
			with transaction.atomic():
				try:
					new_vendor=Vendor()
					new_vendor.name=name
					new_vendor.key=key
					new_vendor.address_1=address_1
					new_vendor.address_2=address_2
					new_vendor.state=state
					new_vendor.city=city
					new_vendor.pin=pin
					new_vendor.phone_no=phone_no
					new_vendor.cst=cst
					new_vendor.tin=tin
					new_vendor.gst=gst
					new_vendor.details=details
					new_vendor.tenant=this_tenant
					new_vendor.save()
					if ismanufac:	
						new_manufacturer=Manufacturer()
						new_manufacturer.name=name
						new_manufacturer.tenant=this_tenant
						new_manufacturer.save()		
				except:
					transaction.rollback()
		elif (calltype == 'updatevendor'):
			response_data = {}
			pk=request.data.get('pk')
			name=request.data.get('name')
			key=request.data.get('key')
			address_1=request.data.get('address_1')
			address_2=request.data.get('address_2')
			# state=request.data.get('state')
			city=request.data.get('city')
			pin=request.data.get('pin')
			phone_no=request.data.get('phone')
			cst=request.data.get('cst')
			tin=request.data.get('tin')
			gst=request.data.get('gst')
			details=request.data.get('details')
			old_vendor=Vendor.objects.for_tenant(this_tenant).get(id=pk)
			old_vendor.name=name
			old_vendor.key=key
			old_vendor.address_1=address_1
			old_vendor.address_2=address_2
			# old_customer.state=state
			old_vendor.city=city
			old_vendor.pin=pin
			old_vendor.phone_no=phone_no
			old_vendor.cst=cst
			old_vendor.tin=tin
			old_vendor.gst=gst
			old_vendor.details=details
			old_vendor.save()			
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

@api_view(['GET','POST'],)
def get_vendor_autocomplete(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		q = request.GET.get('term', '')
		vendors = Vendor.objects.for_tenant(this_tenant).filter(name__icontains  = q)[:10]
		response_data = []
		for item in vendors:
			item_json = {}
			item_json['id'] = item.id
			item_json['label'] = item.name
			response_data.append(item_json)
		data = json.dumps(response_data)
	else:
		data = 'fail'
	mimetype = 'application/json'
	return HttpResponse(data, mimetype)
	
# @login_required
@api_view(['GET','POST'],)
def zone_view(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		zones=Zone.objects.for_tenant(request.user.tenant).all()
		serializer = ZoneSerializers(zones, many=True)
		# print(JSONRenderer().render(serializer.data))
		return Response(serializer.data)
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		if (calltype == 'newzone'):
			name=request.POST.get('name')
			key=request.POST.get('key')
			details=request.POST.get('details')
			new_zone=Zone()
			new_zone.name=name
			new_zone.key=key
			new_zone.details=details
			new_zone.tenant=this_tenant
			new_zone.save()			
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

# @login_required
@api_view(['GET','POST'],)
def tax_view(request):
	if request.method == 'GET':
		taxes=tax_structure.objects.for_tenant(request.user.tenant).all()
		serializer = TaxSerializers(taxes, many=True)		
		return Response(serializer.data)
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		if (calltype == 'newtax'):
			name=request.POST.data('name')
			percentage=request.data.get('percentage')
			new_tax=tax_structure()
			new_tax.name=name
			new_tax.percentage=percentage
			new_tax.tenant=this_tenant
			new_tax.save()			
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)


# @login_required
@api_view(['GET','POST'],)
def individual_tax_view(request,pk):
	if request.method == 'GET':
		tax=tax_structure.objects.get(id=pk)
		serializer = TaxSerializers(tax, )		
		# return Response(json.dumps(taxes,cls=DjangoJSONEncoder))
		return Response(serializer.data)
	
# @login_required
@api_view(['GET','POST'],)
def dimension_view(request):
	if request.method == 'GET':
		dimensions=Dimension.objects.for_tenant(request.user.tenant).all()
		serializer = DimensionSerializers(dimensions, many=True)		
		# return Response(json.dumps(taxes,cls=DjangoJSONEncoder))
		return Response(serializer.data)
	if request.method == 'POST':
		calltype = request.data.get('calltype')
		response_data = {}
		if (calltype == 'newdimension'):
			name=request.data.get('name')
			details=request.data.get('details')
			new_dim=Dimension()
			new_dim.name=name
			new_dim.details=details
			new_dim.tenant=this_tenant
			new_dim.save()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)			
	
# @login_required
@api_view(['GET','POST'],)
def unit_view(request):
	if request.method == 'GET':
		units=Unit.objects.for_tenant(request.user.tenant).all().order_by('dimension','multiplier')
		serializer = UnitSerializers(units, many=True)		
		# return Response(json.dumps(taxes,cls=DjangoJSONEncoder))
		return Response(serializer.data)
	if request.method == 'POST':
		calltype = request.data.get('calltype')
		response_data = {}
		if (calltype == 'newunit'):
			name=request.data.get('name')
			symbol=request.data.get('symbol')
			multiplier=request.data.get('multiplier')
			dim_id=request.data.get('dimension')
			dim_selected=Dimension.objects.for_tenant(this_tenant).get(id=dim_id)
			new_unit=Unit()
			new_unit.name=name
			new_unit.symbol=symbol
			new_unit.multiplier=multiplier
			new_unit.dimension=dim_selected
			new_unit.tenant=this_tenant
			new_unit.save()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

@api_view(['GET','POST'],)
def unit_base(request):
	if request.method == 'GET':
		units=Unit.objects.for_tenant(request.user.tenant).filter(multiplier=1).order_by('dimension',)
		serializer = UnitSerializers(units, many=True)		
		# return Response(json.dumps(taxes,cls=DjangoJSONEncoder))
		return Response(serializer.data)
		
# @login_required
@api_view(['GET','POST'],)
def attribute_view(request):
	if request.method == 'GET':
		attributes=Attribute.objects.for_tenant(request.user.tenant).all().order_by('name')
		serializer = AttributeSerializers(attributes, many=True)		
		# return Response(json.dumps(taxes,cls=DjangoJSONEncoder))
		return Response(serializer.data)
	if request.method == 'POST':
		calltype = request.data.get('calltype')
		response_data = {}
		if (calltype == 'newattribute'):
			name=request.data.get('name')
			new_attr=Attribute()
			new_attr.name=name
			new_attr.tenant=this_tenant
			new_attr.save()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

# @login_required
@api_view(['GET','POST'],)
def warehouse_view(request):
	if request.method == 'GET':
		warehouses=Warehouse.objects.for_tenant(request.user.tenant).filter(is_active=True).order_by('-default')
		serializer = WarehouseSerializers(warehouses, many=True)
		# return Response(json.dumps(taxes,cls=DjangoJSONEncoder))
		return Response(serializer.data)

# @login_required
@api_view(['GET','POST'],)
def product_view(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		calltype = request.GET.get('calltype')
		if (calltype == 'one_product'):
			productid = request.GET.get('productid')
			product=Product.objects.for_tenant(this_tenant).get(id=productid)
			serializer = ProductDetailSerializers(product)
		
		elif (calltype == 'product_filter'):
			startswith = request.GET.get('startswith')
			hsncode = request.GET.get('hsncode')
			
			products=Product.objects.for_tenant(this_tenant).filter(is_active=True).order_by( 'name','sku',).\
					select_related('default_unit','brand','group').prefetch_related('productSalesRate_product')
			
			if startswith:
				products=products.filter(name__istartswith = startswith)

			if hsncode:
				products=products.filter(hsn_code = hsncode)
			
			serializer = ProductSerializers(products, many=True)
		else:
			products=Product.objects.for_tenant(this_tenant).filter(is_active=True).order_by( 'name','sku',).\
					select_related('default_unit','brand','group').prefetch_related('productSalesRate_product')
			serializer = ProductSerializers(products, many=True)
		return Response(serializer.data)
	elif request.method == 'POST':
		calltype = request.data.get('calltype')
		response_data = {}
		if calltype == 'updateproduct':
			pk=request.data.get('pk')
			name=request.data.get('name')
			sku=request.data.get('sku')
			barcode=request.data.get('barcode')
			cgst=request.data.get('cgst')
			sgst=request.data.get('sgst')
			igst=request.data.get('igst')
			hsn=request.data.get('hsn')
			manufac=request.data.get('manufac')
			taxes=tax_structure.objects.for_tenant(this_tenant).all()
			# state=request.data.get('state')
			if not sku:
				raise IntegrityError
			if not name:
				raise IntegrityError
			
			old_product=Product.objects.for_tenant(this_tenant).get(id=pk)
			old_product.name=name
			old_product.sku=sku
			try:
				old_product.manufacturer = Manufacturer.objects.for_tenant(this_tenant).get(id=manufac)
			except:
				pass
			
			if barcode:
				try:
					is_product=Product.objects.for_tenant(this_tenant).get(barcode=barcode)
				except:
					is_product=''
				if is_product:
					if (is_product.id != old_product.id):
						raise IntegrityError
				old_product.barcode = barcode
			else:
				old_product.barcode = None


			if cgst:
				old_product.cgst=taxes.get(id=cgst)
			if sgst:
				old_product.sgst=taxes.get(id=sgst)
			if igst:
				old_product.igst=taxes.get(id=igst)
			# if hsn:
			old_product.hsn_code=hsn
			old_product.save()

		elif calltype == 'updaterate':
			rate_id = request.data.get('rate_id')
			revised_rate = Decimal(request.data.get('new_rate'))
			is_tax = request.data.get('is_tax')
			prod_id = request.data.get('prod_id')
			if (revised_rate > 0):
				if (is_tax == 'true'):
					is_tax=True
				elif (is_tax == 'false'):
					is_tax=False
				if (rate_id):
					old_rate=product_sales_rate.objects.get(id=rate_id)
					old_rate.tentative_sales_rate=revised_rate
					old_rate.is_tax_included=is_tax
					old_rate.save()
				else:
					new_rate=product_sales_rate()
					new_rate.product=Product.objects.for_tenant(this_tenant).get(id=prod_id)
					new_rate.tentative_sales_rate=revised_rate
					new_rate.is_tax_included=is_tax
					new_rate.tenant=this_tenant
					new_rate.save()

		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
		

#This view will not be needed soon
@api_view(['GET','POST'],)
def product_details(request):
	if request.method == 'GET':
		productid=request.GET.get('productid')
		product=Product.objects.for_tenant(request.user.tenant).filter(is_active=True).get(id=productid)
		serializer = ProductDetailSerializers(product)
		# return Response(json.dumps(taxes,cls=DjangoJSONEncoder))
		return Response(serializer.data)

# @login_required
@api_view(['GET','POST'],)
def manufacturer_view(request):
	if request.method == 'GET':
		manufacturers=Manufacturer.objects.for_tenant(request.user.tenant)
		serializer = ManufacturerSerializers(manufacturers, many=True)
		# return Response(json.dumps(taxes,cls=DjangoJSONEncoder))
		return Response(serializer.data)
	if request.method == 'POST':
		calltype = request.data.get('calltype')
		response_data = {}
		if (calltype == 'newmanufacturer'):
			name=request.data.get('name')
			new_manufacturer=Manufacturer()
			new_manufacturer.name=name
			new_manufacturer.tenant=this_tenant
			new_manufacturer.save()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

# @login_required
@api_view(['GET','POST'],)
def brand_view(request):
	if request.method == 'GET':
		brands=Brand.objects.for_tenant(request.user.tenant)
		serializer = BrandSerializers(brands, many=True)
		# return Response(json.dumps(taxes,cls=DjangoJSONEncoder))
		return Response(serializer.data)
	if request.method == 'POST':
		calltype = request.data.get('calltype')
		response_data = {}
		if (calltype == 'newbrand'):
			name=request.data.get('name')
			manufacturer_id=request.data.get('manufacturer')
			manufacturer=Manufacturer.objects.for_tenant(this_tenant).get(id=manufacturer_id)
			new_brand=Brand()
			new_brand.name=name
			new_brand.manufacturer=manufacturer
			new_brand.tenant=this_tenant
			new_brand.save()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	
#This sets of data of saving to master needs to be converted to api system. 

@login_required
def zone_data(request):
	extension="base.html"
	return render (request, 'master/zone_list.html',{'extension':extension})

@login_required
def customer_data(request):
	extension="base.html"
	this_tenant=request.user.tenant
	zones=Zone.objects.for_tenant(this_tenant).all()
	return render (request, 'master/customer_list.html',{'zone':zones,'states':state_list, 'extension':extension})



@login_required
#View API-ed
def manufacbrand_data(request):
	extension="base.html"
	this_tenant=request.user.tenant
	zones=Zone.objects.for_tenant(this_tenant).all()
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		if (calltype == 'newmanufacturer'):
			name=request.POST.get('name')
			new_manufacturer=Manufacturer()
			new_manufacturer.name=name
			new_manufacturer.tenant=this_tenant
			new_manufacturer.save()
		elif (calltype == 'newbrand'):
			name=request.POST.get('name')
			manufacturer_id=request.POST.get('manufacturer')
			manufacturer=Manufacturer.objects.for_tenant(this_tenant).get(id=manufacturer_id)
			new_brand=Brand()
			new_brand.name=name
			new_brand.manufacturer=manufacturer
			new_brand.tenant=this_tenant
			new_brand.save()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render (request, 'master/manufacturer_brand_list.html',{'extension':extension})


@login_required
def vendor_data(request):
	extension="base.html"
	this_tenant=request.user.tenant
	zones=Zone.objects.for_tenant(this_tenant).all()
	return render (request, 'master/vendor_list.html',{'states':state_list, 'extension':extension})




@login_required
def import_customer(request):
	this_tenant=request.user.tenant
	if request.method == "POST":
		form = UploadFileForm(request.POST, request.FILES)
		def choice_func(row):
			data=customer_validate(row, this_tenant)
			return data		
		if form.is_valid():
			# data = form.cleaned_data
			# batch_data= data['batch']
			# batch_selected=Batch.objects.for_tenant(this_tenant).get(id=batch_data)
			
			# with transaction.atomic():
			# 	try:
			# 		request.FILES['file'].save_to_database(
			# 			model=Customer,
			# 			initializer=choice_func,
			# 			mapdict=['name', 'key', 'address_1','address_2','state', 'city', 'pin', \
			# 			'phone_no','cst','tin','gst','details','tenant'])
			# 		return redirect('master:customer_data')
			# 	except:
			# 		transaction.rollback()
			# 		return HttpResponse("Error")

			data={}
			f = request.FILES['file']
			data['name'] = f.name
			data['size'] = f.size / 1024
			if 'xls' not in f.name and 'xlsx' not in f.name:
				data['error'] = 2
				data['info'] = 'file type must be excel!'
				messages.add_message(request, messages.WARNING, 'File type must be excel.')
				return redirect('master:import_customer')
			elif 0 == f.size:
				data['error'] = 3
				data['info'] = 'file content is empty!'
				messages.add_message(request, messages.WARNING, 'File content is empty.')
				return redirect('master:import_customer')
			# wb = xlrd.open_workbook(inventory)
			else:
				rows = customer_register(f, this_tenant)
				if (rows):
					str1 = ' ,'.join(str(e) for e in rows)
					messages.add_message(request, messages.WARNING, 'There was error in the following rows: '+str1\
							+". Either the compulsory parameters are empty or the customer codes/keys are not unique")
					messages.add_message(request, messages.INFO, 'The rest of the data have been uploaded successfully.')	
				else:
					messages.add_message(request, messages.SUCCESS, 'Data uploaded successfully.')
				return redirect('master:customer_data')
		else:
			return HttpResponseBadRequest()
	else:
		form = UploadFileForm()
	return render(request,'master/upload_customer.html',{'form': form,})


@login_required
def import_product(request):
	this_tenant=request.user.tenant
	if request.method == "POST":
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			# data = form.cleaned_data
			# batch_data= data['batch']
			# batch_selected=Batch.objects.for_tenant(this_tenant).get(id=batch_data)

			data={}
			f = request.FILES['file']
			data['name'] = f.name
			data['size'] = f.size / 1024
			if 'xls' not in f.name and 'xlsx' not in f.name:
				data['error'] = 2
				data['info'] = 'file type must be excel!'
				messages.add_message(request, messages.WARNING, 'File type must be excel.')
				return redirect('master:import_product')
			elif 0 == f.size:
				data['error'] = 3
				data['info'] = 'file content is empty!'
				messages.add_message(request, messages.WARNING, 'File content is empty.')
				return redirect('master:import_product')
			# wb = xlrd.open_workbook(inventory)
			else:
				rows = product_register(f, this_tenant)
				if (rows):
					str1 = ' ,'.join(str(e) for e in rows)
					messages.add_message(request, messages.WARNING, 'There was error in the following rows: .'+str1\
							+". Either the compulsory parameters are empty or the SKU/Barcodes are not unique.")
					messages.add_message(request, messages.INFO, 'The rest of the data have been uploaded successfully.')	
				else:
					messages.add_message(request, messages.SUCCESS, 'Data uploaded successfully.')
				return redirect('master:product_data')
			
		else:
			return HttpResponseBadRequest()
	else:
		form = UploadFileForm()
	return render(request,'master/upload_product.html',{'form': form,})



@login_required
#View API-ed
def tax_data(request):
	extension="base.html"
	this_tenant=request.user.tenant
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		if (calltype == 'newtax'):
			name=request.POST.get('name')
			percentage=request.POST.get('percentage')
			new_tax=tax_structure()
			new_tax.name=name
			new_tax.percentage=percentage
			new_tax.tenant=this_tenant
			new_tax.save()			
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render (request, 'master/tax_list.html',{'extension':extension})


@login_required
#Already API-ed
def dimension_unit_data(request):
	extension="base.html"
	this_tenant=request.user.tenant
	dimensions=Dimension.objects.for_tenant(this_tenant).all()
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		if (calltype == 'newdimension'):
			name=request.POST.get('name')
			details=request.POST.get('details')
			new_dim=Dimension()
			new_dim.name=name
			new_dim.details=details
			new_dim.tenant=this_tenant
			new_dim.save()			
		elif (calltype == 'newunit'):
			name=request.POST.get('name')
			symbol=request.POST.get('symbol')
			multiplier=request.POST.get('multiplier')
			dim_id=request.POST.get('dimension')
			dim_selected=Dimension.objects.for_tenant(this_tenant).get(id=dim_id)
			new_unit=Unit()
			new_unit.name=name
			new_unit.symbol=symbol
			new_unit.multiplier=multiplier
			new_unit.dimension=dim_selected
			new_unit.tenant=this_tenant
			new_unit.save()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render (request, 'master/dimension_unit_list.html',{'extension':extension, 'dimensions':dimensions})


@login_required
def product_data(request):
	extension="base.html"
	this_tenant=request.user.tenant
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		if (calltype == 'newproduct'):
			name=request.POST.get('name')
			sku=request.POST.get('sku')
			hsn=request.POST.get('hsn')
			barcode=request.POST.get('barcode')
			if barcode:
				try:
					is_product=Product.objects.for_tenant(this_tenant).get(barcode=barcode)
				except:
					is_product=''
				if is_product:
					raise IntegrityError
			# vat_type=request.POST.get('vat_type')
			# tax=request.POST.get('tax')
			cgst=request.POST.get('cgst')
			sgst=request.POST.get('sgst')
			igst=request.POST.get('igst')
			reorder_point=request.POST.get('reorder')
			if not reorder_point:
				reorder_point=0
			unit_id=request.POST.get('unit')
			brand_id=request.POST.get('brand')
			manufacturer_id=request.POST.get('manufacturer')
			group_id=request.POST.get('group')
			has_batch=request.POST.get('has_batch')
			has_instance=request.POST.get('has_instance')
			has_attribute=request.POST.get('has_attribute')
			if (has_batch == 'true'):
				has_batch=True
			elif(has_batch == 'false'):
				has_batch=False
			if (has_instance == 'true'):
				has_instance=True
			elif(has_instance == 'false'):
				has_instance=False
			if (has_attribute == 'true'):
				has_attribute=True
			elif(has_attribute == 'false'):
				has_attribute=False
			remarks=request.POST.get('remarks')
			# tax_selected=tax_structure.objects.for_tenant(this_tenant).get(id=tax)
			tax_all=tax_structure.objects.for_tenant(this_tenant).all()
			unit_selected=Unit.objects.for_tenant(this_tenant).get(id=unit_id)
			if (brand_id):
				brand_selected=Brand.objects.for_tenant(this_tenant).get(id=brand_id)
			if (group_id):
				group_selected=Group.objects.for_tenant(this_tenant).get(id=group_id)
			if (has_attribute):
				attributes = json.loads(request.POST.get('attributes'))
			with transaction.atomic():
				try:
					new_product=Product()
					new_product.name=name
					new_product.sku=sku
					new_product.hsn_code=hsn
					new_product.barcode=barcode
					# new_product.vat_type=vat_type
					# new_product.tax=tax_selected
					if (cgst):
						cgst_selected=tax_all.get(id=cgst)
						new_product.cgst=cgst_selected
					if (sgst):
						sgst_selected=tax_all.get(id=sgst)
						new_product.sgst=sgst_selected
					if (igst):
						igst_selected=tax_all.get(id=igst)
						new_product.igst=igst_selected			
					new_product.reorder_point=reorder_point
					new_product.default_unit=unit_selected
					if (brand_id):
						new_product.brand=brand_selected
					if (group_id):
						new_product.group=group_selected
					new_product.has_batch=has_batch
					new_product.has_attribute=has_attribute
					new_product.has_instance=has_instance
					new_product.tenant=this_tenant
					new_product.remarks=remarks
					new_product.save()
					
					# if (has_attribute):
					# 	for data in attributes:
					# 		attr_id=int(data['attribute_id'])
					# 		value=data['value']
					# 		attr_selected=Attribute.objects.for_tenant(this_tenant).get(id=attr_id)
					# 		product_attr=product_attribute()
					# 		product_attr.product=new_product
					# 		product_attr.attribute=attr_selected
					# 		product_attr.value=value
					# 		product_attr.tenant=this_tenant
				except:
					transaction.rollback()
					messages.add_message(request, messages.WARNING, "There were some errors. Note Barcode & SKU must be unique."+
										" Name, SKU and default unit cannot be blank.")
					return redirect('master:product_data')
		#Attribute API-ed
		elif (calltype == 'newattribute'):
			name=request.POST.get('name')
			new_attr=Attribute()
			new_attr.name=name
			new_attr.tenant=this_tenant
			new_attr.save()
		
		elif (calltype == 'newrate'):
			productid=request.POST.get('productid')
			is_tax=request.POST.get('is_tax')
			if (is_tax == 'true'):
				is_tax=True
			elif (is_tax == 'false'):
				is_tax=False
			rate=Decimal(request.POST.get('rate'))
			if (rate > 0):
				new_rate=product_sales_rate()
				new_rate.product=Product.objects.for_tenant(this_tenant).get(id=productid)
				new_rate.tentative_sales_rate=rate
				new_rate.is_tax_included=is_tax
				new_rate.tenant=this_tenant
				new_rate.save()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	return render (request, 'master/product_list.html',{'extension':extension})


@login_required
#This is a event list view - Change period to academic year period
def warehouse_data(request):
	extension="base.html"
	this_tenant=request.user.tenant
	# dimensions=Dimension.objects.for_tenant(this_tenant).all()
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		if (calltype == 'newwarehouse'):
			name=request.POST.get('name')
			address_1=request.POST.get('address_1')
			address_2=request.POST.get('address_2')
			state=request.POST.get('state')
			city=request.POST.get('city')
			pin=request.POST.get('pin')
			remarks=request.POST.get('remarks')
			# default=request.POST.get('default')
			retail=request.POST.get('retail')
			if (retail == 'true'):
				retail = True
			elif (retail == 'false'):
				retail = False
			with transaction.atomic():
				try:
					new_warehouse=Warehouse()
					new_warehouse.name=name
					new_warehouse.address_1=address_1
					new_warehouse.address_2=address_2
					new_warehouse.state=state
					new_warehouse.city=city
					new_warehouse.pin=pin
					new_warehouse.remarks=remarks
					new_warehouse.is_retail_channel=retail
					new_warehouse.tenant=this_tenant
					new_warehouse.save()
					new_valuation=warehouse_valuation()
					new_valuation.warehouse=new_warehouse
					new_valuation.valuation=0
					new_valuation.tenant=this_tenant
					new_valuation.save()
				except:
					pass
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render (request, 'master/warehouse_list.html',{'extension':extension,'states':state_list })


@login_required
def product_group(request):
	extension="base.html"
	# this_tenant=request.user.tenant
	return render (request, 'master/product_group_list.html',{'extension':extension,'states':state_list })

@api_view(['GET','POST'],)
def product_group_data(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		calltype = request.GET.get('calltype')
		# if (calltype == 'one_service'):
		# 	serviceid = request.GET.get('serviceid')
		# 	service=Service.objects.for_tenant(this_tenant).get(id=serviceid)
		# 	serializer = ServiceDetailSerializers(service)
		# else:
		product_groups=list(Group.objects.for_tenant(this_tenant).order_by( 'name',).values('id','name'))
		
		jsondata = json.dumps(product_groups, cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)
	
	elif request.method == 'POST':
		calltype = request.data.get('calltype')
		response_data = {}

		if (calltype == 'newgroup'):
			response_data = {}
			name=request.POST.get('name')
			
			new_group=Group()
			new_group.name=name
			new_group.tenant=this_tenant
			new_group.save()
			
			jsondata = json.dumps(response_data)
			return HttpResponse(jsondata)

		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)


@login_required
def customer_import_format(request):
	# if 'excel' in request.POST:
	response = HttpResponse(content_type='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename=Customer_Import.xlsx'
	xlsx_data = customer_format()
	response.write(xlsx_data)
	return response

@login_required
def product_import_format(request):
	# if 'excel' in request.POST:
	response = HttpResponse(content_type='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename=Product_Import.xlsx'
	xlsx_data = product_format()
	response.write(xlsx_data)
	return response

@login_required
def service_view(request):
	extension="base.html"
	return render (request, 'master/service_list.html',{'extension':extension})


# @login_required
@api_view(['GET','POST'],)
def service_data(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		calltype = request.GET.get('calltype')
		if (calltype == 'one_service'):
			serviceid = request.GET.get('serviceid')
			service=Service.objects.for_tenant(this_tenant).get(id=serviceid)
			serializer = ServiceDetailSerializers(service)
		else:
			services=Service.objects.for_tenant(this_tenant).filter(is_active=True).order_by( 'name','sku',).\
					select_related('default_unit', 'group').prefetch_related('serviceSalesRate_service')
			serializer = ServiceSerializers(services, many=True)
		return Response(serializer.data)
	elif request.method == 'POST':
		calltype = request.data.get('calltype')
		response_data = {}

		if (calltype == 'newservice'):
			response_data = {}
			name=request.POST.get('name')
			sku=request.POST.get('sku')
			hsn=request.POST.get('hsn')
			# barcode=request.POST.get('barcode')
			# if barcode:
			# 	try:
			# 		is_product=Product.objects.for_tenant(this_tenant).get(barcode=barcode)
			# 	except:
			# 		is_product=''
			# 	if is_product:
			# 		raise IntegrityError
			# vat_type=request.POST.get('vat_type')
			# tax=request.POST.get('tax')
			cgst=request.POST.get('cgst')
			sgst=request.POST.get('sgst')
			igst=request.POST.get('igst')
			unit_id=request.POST.get('unit')
			
			# brand_id=request.POST.get('brand')
			# manufacturer_id=request.POST.get('manufacturer')
			group_id=request.POST.get('group')
			# has_batch=request.POST.get('has_batch')
			# has_instance=request.POST.get('has_instance')
			# has_attribute=request.POST.get('has_attribute')
			# if (has_batch == 'true'):
			# 	has_batch=True
			# elif(has_batch == 'false'):
			# 	has_batch=False
			# if (has_instance == 'true'):
			# 	has_instance=True
			# elif(has_instance == 'false'):
			# 	has_instance=False
			# if (has_attribute == 'true'):
			# 	has_attribute=True
			# elif(has_attribute == 'false'):
			# 	has_attribute=False
			# remarks=request.POST.get('remarks')
			# tax_selected=tax_structure.objects.for_tenant(this_tenant).get(id=tax)
			
			tax_all=tax_structure.objects.for_tenant(this_tenant).all()
			unit_selected=Unit.objects.for_tenant(this_tenant).get(id=unit_id)
			# if (brand_id):
			# 	brand_selected=Brand.objects.for_tenant(this_tenant).get(id=brand_id)
			if (group_id):
				group_selected=service_group.objects.for_tenant(this_tenant).get(id=group_id)
			# if (has_attribute):
			# 	attributes = json.loads(request.POST.get('attributes'))
			with transaction.atomic():
				try:
					new_service=Service()
					new_service.name=name
					new_service.sku=sku
					new_service.hsn_code=hsn
					# new_service.barcode=barcode
					
					if (cgst):
						cgst_selected=tax_all.get(id=cgst)
						new_service.cgst=cgst_selected
					if (sgst):
						sgst_selected=tax_all.get(id=sgst)
						new_service.sgst=sgst_selected
					if (igst):
						igst_selected=tax_all.get(id=igst)
						new_service.igst=igst_selected			
					
					new_service.default_unit=unit_selected
					
					# if (brand_id):
					# 	new_product.brand=brand_selected
					if (group_id):
						new_service.group=group_selected
					# new_product.has_batch=has_batch
					# new_product.has_attribute=has_attribute
					# new_product.has_instance=has_instance
					
					new_service.tenant=this_tenant
					# new_service.remarks=remarks
					new_service.save()
					
					# if (has_attribute):
					# 	for data in attributes:
					# 		attr_id=int(data['attribute_id'])
					# 		value=data['value']
					# 		attr_selected=Attribute.objects.for_tenant(this_tenant).get(id=attr_id)
					# 		product_attr=product_attribute()
					# 		product_attr.product=new_product
					# 		product_attr.attribute=attr_selected
					# 		product_attr.value=value
					# 		product_attr.tenant=this_tenant
				except:
					transaction.rollback()
					# messages.add_message(request, messages.WARNING, "There were some errors. Note Barcode & SKU must be unique."+
					# 					" Name, SKU and default unit cannot be blank.")
					response_data["error"] = "There were some errors. Note Barcode & SKU must be unique. Name, SKU and default unit cannot be blank." 
			
			jsondata = json.dumps(response_data)
			return HttpResponse(jsondata)

		elif calltype == 'updateservice':
			pk=request.data.get('pk')
			name=request.data.get('name')
			sku=request.data.get('sku')
			# barcode=request.data.get('barcode')
			cgst=request.data.get('cgst')
			sgst=request.data.get('sgst')
			igst=request.data.get('igst')
			hsn=request.data.get('hsn')
			group = request.data.get('group')
			taxes=tax_structure.objects.for_tenant(this_tenant).all()
			
			if not sku:
				raise IntegrityError
			if not name:
				raise IntegrityError
			
			old_service=Service.objects.for_tenant(this_tenant).get(id=pk)
			old_service.name=name
			old_service.sku=sku
			
			# if barcode:
			# 	try:
			# 		is_product=Product.objects.for_tenant(this_tenant).get(barcode=barcode)
			# 	except:
			# 		is_product=''
				# if is_product:
				# 	if (is_product.id != old_product.id):
				# 		raise IntegrityError
				# old_product.barcode = barcode
			# else:
			# 	old_product.barcode = None


			if cgst:
				old_service.cgst=taxes.get(id=cgst)
			if sgst:
				old_service.sgst=taxes.get(id=sgst)
			if igst:
				old_service.igst=taxes.get(id=igst)
			if group:
				old_service.group=service_group.objects.for_tenant(this_tenant).get(id=group)
			# if hsn:
			old_service.hsn_code=hsn
			old_service.save()

		elif calltype == 'updaterate':
			rate_id = request.data.get('rate_id')
			revised_rate = Decimal(request.data.get('new_rate'))
			is_tax = request.data.get('is_tax')
			serviceid = request.data.get('serviceid')
			if (revised_rate > 0):
				if (is_tax == 'true'):
					is_tax=True
				elif (is_tax == 'false'):
					is_tax=False
				if (rate_id):
					old_rate = service_sales_rate.objects.get(id=rate_id)
					old_rate.tentative_sales_rate = revised_rate
					old_rate.is_tax_included = is_tax
					old_rate.save()
				else:
					new_rate = service_sales_rate()
					new_rate.service = Service.objects.for_tenant(this_tenant).get(id=serviceid)
					new_rate.tentative_sales_rate = revised_rate
					new_rate.is_tax_included = is_tax
					new_rate.tenant = this_tenant
					new_rate.save()

		elif (calltype == 'newrate'):
			serviceid=request.POST.get('serviceid')
			is_tax=request.POST.get('is_tax')
			if (is_tax == 'true'):
				is_tax=True
			elif (is_tax == 'false'):
				is_tax=False
			rate=Decimal(request.POST.get('rate'))
			if (rate > 0):
				new_rate=service_sales_rate()
				new_rate.service=Service.objects.for_tenant(this_tenant).get(id=serviceid)
				new_rate.tentative_sales_rate=rate
				new_rate.is_tax_included=is_tax
				new_rate.tenant=this_tenant
				new_rate.save()

		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

@login_required
def service_group_view(request):
	extension="base.html"
	# this_tenant=request.user.tenant
	return render (request, 'master/service_group_list.html',{'extension':extension})

@api_view(['GET','POST'],)
def service_group_data(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		calltype = request.GET.get('calltype')
		# if (calltype == 'one_service'):
		# 	serviceid = request.GET.get('serviceid')
		# 	service=Service.objects.for_tenant(this_tenant).get(id=serviceid)
		# 	serializer = ServiceDetailSerializers(service)
		# else:
		service_groups=list(service_group.objects.for_tenant(this_tenant).order_by( 'name',).values('id','name'))
		
		jsondata = json.dumps(service_groups, cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)
	
	elif request.method == 'POST':
		calltype = request.data.get('calltype')
		response_data = {}

		if (calltype == 'newgroup'):
			response_data = {}
			name=request.POST.get('name')
			
			new_group=service_group()
			new_group.name=name
			new_group.tenant=this_tenant
			new_group.save()
			
			jsondata = json.dumps(response_data)
			return HttpResponse(jsondata)

		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
