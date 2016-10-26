from functools import partial, wraps
import json
#from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
#from django.db.models import F
from distribution_inventory.models import Inventory, damagedInventory
from distribution_user.models import Tenant
from .models import Manufacturer, Dimension, Unit, Product, subProduct, Zone, Customer, Vendor, Warehouse
from .forms import ManufacturerForm, UnitForm, ProductForm, subProductForm, ZoneForm, CustomerForm,\
				VendorForm, WarehouseForm, ManufacturerUpdateForm, ProductUpdateForm, \
				CustomerUpdateForm, VendorUpdateForm, WarehouseUpdateForm
from .utils import create_inventory


@login_required
#landing page
def landing(request):
	return render (request, 'master/landing.html')


@login_required
def master_base(request, type):
	if type=='List':
		return render(request, 'master/base/master_base_list.html')
	elif type=='New':
		return render(request, 'master/base/master_base_new.html')



@login_required
def master_list(request, type):

	#for the delete button to work

	if request.method == 'POST':
		itemtype = request.POST.get('type')
		itemkey = request.POST.get('itemkey')
		response_data = {}

		#if (itemtype == 'Manufacturer'):
		#	item = Manufacturer.objects.for_tenant(request.user.tenant).get(key__iexact=itemkey).delete()
		#	response_data['name'] = itemkey
		#	jsondata = json.dumps(response_data)
		#	return HttpResponse(jsondata)
		if (itemtype == 'Unit'):
			item = Unit.objects.for_tenant(request.user.tenant).get(key__iexact=itemkey).delete()
			response_data['name'] = itemkey
			jsondata = json.dumps(response_data)
			return HttpResponse(jsondata)
		elif (itemtype == 'Product'):
			item = Product.objects.for_tenant(request.user.tenant).get(key__iexact=itemkey).delete()
			response_data['name'] = itemkey
			jsondata = json.dumps(response_data)
			return HttpResponse(jsondata)
		elif (itemtype == 'Zone'):
			item = Zone.objects.for_tenant(request.user.tenant).get(key__iexact=itemkey).delete()
			response_data['name'] = itemkey
			jsondata = json.dumps(response_data)
			return HttpResponse(jsondata)
		#elif (itemtype == 'Customer'):
		#	item = Customer.objects.for_tenant(request.user.tenant).get(key__iexact=itemkey).delete()
		#	response_data['name'] = itemkey
		#	jsondata = json.dumps(response_data)
		#	return HttpResponse(jsondata)
		#elif (itemtype == 'Vendor'):
		#	item = Vendor.objects.for_tenant(request.user.tenant).get(key__iexact=itemkey).delete()
		#	response_data['name'] = itemkey
		#	jsondata = json.dumps(response_data)
		#	return HttpResponse(jsondata)
		elif (itemtype == 'Warehouse'):
			item = Warehouse.objects.for_tenant(request.user.tenant).get(key__iexact=itemkey).delete()
			response_data['name'] = itemkey
			jsondata = json.dumps(response_data)
			return HttpResponse(jsondata)
	
	#for the list to be displayed	
	if (type=="Manufacturer"):
		items = Manufacturer.objects.for_tenant(request.user.tenant).all()
	elif (type=="Dimension"):
		items = Dimension.objects.for_tenant(request.user.tenant).all()
	elif (type=="Unit"):
		items = Unit.objects.for_tenant(request.user.tenant).all()
	elif (type=="Product"):
		items = Product.objects.for_tenant(request.user.tenant).all()	
	elif (type=="Zone"):
		items = Zone.objects.for_tenant(request.user.tenant).all()
	elif (type=="Customer"):
		items = Customer.objects.for_tenant(request.user.tenant).all()
	elif (type=="Vendor"):
		items = Vendor.objects.for_tenant(request.user.tenant).all()
	elif (type=="Warehouse"):
		items = Warehouse.objects.for_tenant(request.user.tenant).all()
		return render(request, 'master/list_table.html',{'items':items, 'type':type})

	return render(request, 'master/master_list.html',{'items':items, 'type':type})


@login_required
#For adding new entry for Manufacturer, Unit, Zone, Vendor & Account
def master_new(request, type):
	if (type == "Manufacturer"):
		importform=ManufacturerForm
		name='master:manufacturer_list'
	elif (type == "Unit"):
		importform = UnitForm
		name='master:unit_list'
	elif (type == "Vendor"):
		importform = VendorForm
		name='master:vendor_list'
	elif (type == "Zone"):
		importform = ZoneForm
		name='master:zone_list'	
	#elif (type == "Warehouse"):
	#	importform = WarehouseForm
	#	name='master:zone_list'
	current_tenant=request.user.tenant
	form=importform(tenant=current_tenant)
	#importformset=formset_factory(wraps(importform)(partial(importform, tenant=current_tenant)), extra=3)
	#formset=importformset()
	#helper=ManufacturerFormSetHelper()
	if (request.method == "POST"):
		current_tenant=request.user.tenant
		#form = formset(request.POST, tenant=current_tenant)
		form = importform(request.POST, tenant=current_tenant)
		if form.is_valid():
			item=form.save(commit=False)			
			item.tenant=current_tenant
			item.save()
			return redirect(name)
	#else:
	#	form=importform(tenant=request.user.tenant)	
	#return render(request, 'master/new.html',{'formset': formset, 'helper': helper, 'item': type})
	return render(request, 'master/new.html',{'form': form, 'item': type})

@login_required
#separate function for warehouse saving, as for every new warehouse, one needs a new inventory
def new_warehouse(request, type):
	name='master:product_list'
	form=WarehouseForm(tenant=request.user.tenant)
	if (request.method == "POST"):
		form = WarehouseForm(request.POST, tenant=request.user.tenant)
		if form.is_valid():
			subproducts=subProduct.objects.for_tenant(request.user.tenant).all()
			item=form.save(commit=False)
			current_tenant=request.user.tenant
			item.tenant=current_tenant
			with transaction.atomic():
				try:
					item.save()	
					for subproduct in subproducts:
						create_inventory(current_tenant,"new", subproduct, item)
						create_inventory(current_tenant,"returnable", subproduct, item)
						create_inventory(current_tenant,"damaged", subproduct, item)
						# daminventory=damagedInventory()
						# daminventory.item=subproduct
						# daminventory.warehouse=item
						# daminventory.save()
						# inventory=Inventory()
						# inventory.item=subproduct
						# inventory.warehouse=item
						# inventory.save()
					return redirect(name)
				except:
					transaction.rollback()
	return render(request, 'master/new.html',{'form': form, 'item': type})


@login_required
#Add new product
def new_product(request, type):
	if (type=="Product"):
		name='master:product_list'
		form=ProductForm(tenant=request.user.tenant)
	if (request.method == "POST"):
		form = ProductForm(request.POST, tenant=request.user.tenant)
		if form.is_valid():
			item=form.save(commit=False)
			current_tenant=request.user.tenant
			item.tenant=current_tenant
			item.save()
			return redirect(name)
	return render(request, 'master/new.html',{'form': form, 'item': type})


@login_required
#Add new subproduct. Urgently need to add atomic block
def new_subproduct(request, type):
	name='master:product_list'
	form=subProductForm(tenant=request.user.tenant)
	if (request.method == "POST"):
		form = subProductForm(request.POST, tenant=request.user.tenant)
		if form.is_valid():
			item=form.save(commit=False)
			current_tenant=request.user.tenant
			item.tenant=current_tenant
			#new_user.set_password(userform.cleaned_data['password'])
			unit=item.unit
			multiplier=unit.multiplier
			item.cost_price=round(item.cost_price/multiplier,2)
			item.discount2=round(item.cost_price/multiplier,2)
			item.mrp=round(item.mrp/multiplier,2)
			item.selling_price=round(item.selling_price/multiplier,2)
			with transaction.atomic():
				try:
					item.save()
					warehouses=Warehouse.objects.for_tenant(request.user.tenant).all()
					for warehouse in warehouses:
						create_inventory(current_tenant,"new", item, warehouse)
						create_inventory(current_tenant,"returnable", item, warehouse)
						create_inventory(current_tenant,"damaged", item, warehouse)
						# daminventory=damagedInventory()
						# daminventory.item=item
						# daminventory.warehouse=warehouse
						# daminventory.save()
						# inventory=Inventory()
						# inventory.item=item
						# inventory.warehouse=warehouse
						# inventory.save()
				except:
					transaction.rollback()

			return redirect(name)
	return render(request, 'master/new.html',{'form': form, 'item': type})

@login_required
#Add new customer
def new_customer(request, type):
	name='master:customer_list'
	form=CustomerForm(tenant=request.user.tenant)
	if (request.method == "POST"):
		form = CustomerForm(request.POST, tenant=request.user.tenant)
		if form.is_valid():
			item=form.save(commit=False)
			current_tenant=request.user.tenant
			item.tenant=current_tenant
			item.save()
			return redirect(name)
			#return HttpResponse(manufacturer.name)
	else:
		form=CustomerForm(tenant=request.user.tenant)
	
	return render(request, 'master/new.html',{'form': form, 'item': type})

@login_required
def master_detail(request, detail):
	#search for the clicked item details one after other from manufacturer through customer
	master_type=detail.split("-",2)[0]
	if (master_type=="man"):
		item=get_object_or_404(Manufacturer.objects.for_tenant(request.user.tenant), slug=detail)
		importform=ManufacturerUpdateForm
		name='master:manufacturer_list'
	#elif(master_type=="uni"):
	#	item=get_object_or_404(Unit.objects.for_tenant(request.user.tenant), slug=detail)
	#	importform=UnitForm
	#	name='master:unit_list'
	elif(master_type=="pro"):
		item=get_object_or_404(Product.objects.for_tenant(request.user.tenant), slug=detail)
		importform=ProductUpdateForm
		name='master:product_list'
	#elif(master_type=="zon"):
	#	item=get_object_or_404(Zone.objects.for_tenant(request.user.tenant), slug=detail)
	#	importform=ZoneForm
	#	name='master:zone_list'
	elif(master_type=="cus"):
		item=get_object_or_404(Customer.objects.for_tenant(request.user.tenant), slug=detail)
		importform=CustomerUpdateForm
		name='master:customer_list'
	elif(master_type=="ven"):
		item=get_object_or_404(Vendor.objects.for_tenant(request.user.tenant), slug=detail)
		importform=VendorUpdateForm
		name='master:vendor_list'
	#Once found check for the form and display
	if (request.method == "POST"):
		form = importform(request.POST, instance=item, tenant=request.user.tenant)
		if form.is_valid():
			form.save()
			return redirect(name)
	elif (master_type=="man" or master_type=="zone"):
		form=importform(instance=item)
	else:
		form=importform(instance=item,tenant=request.user.tenant)

	return render(request, 'master/new.html',{'form': form, 'item': item, 'editable': True})