from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
#from django.db import IntegrityError, transaction
#from django.db.models import F

import json
#from datetime import datetime
from distribution_user.models import Tenant
from .models import Manufacturer, Unit, Product, Zone, Customer, Vendor
#, accountingPeriod, accountChart
from .forms import ManufacturerForm, UnitForm, ProductForm, subProductForm, ZoneForm, CustomerForm,\
				VendorForm
#, AccountForm


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

		if (itemtype == 'Manufacturer'):
			item = Manufacturer.objects.for_tenant(request.user.tenant).get(key__iexact=itemkey).delete()
			response_data['name'] = itemkey
			jsondata = json.dumps(response_data)
			return HttpResponse(jsondata)

		elif (itemtype == 'Unit'):
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

		elif (itemtype == 'Customer'):
			item = Customer.objects.for_tenant(request.user.tenant).get(key__iexact=itemkey).delete()
			response_data['name'] = itemkey
			jsondata = json.dumps(response_data)
			return HttpResponse(jsondata)

		elif (itemtype == 'Vendor'):
			item = Vendor.objects.for_tenant(request.user.tenant).get(key__iexact=itemkey).delete()
			response_data['name'] = itemkey
			jsondata = json.dumps(response_data)
			return HttpResponse(jsondata)

	
	#for the list to be displayed	
	if (type=="Manufacturer"):
		items = Manufacturer.objects.for_tenant(request.user.tenant).all()
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
	#elif (type=="Account"):
	#	items = Account.objects.for_tenant(request.user.tenant).all()

	return render(request, 'master/list.html',{'items':items, 'type':type})


@login_required
#For adding new entry for Manufacturer, Unit, Zone, Vendor & Account
def master_new(request, type):
	if (type == "Manufacturer"):
		importform=ManufacturerForm
		name='master:manufacturer_list'
	elif (type == "Unit"):
		importform = UnitForm
		name='master:unit_list'
	elif (type == "Zone"):
		importform = ZoneForm
		name='master:zone_list'
	elif (type == "Vendor"):
		importform = VendorForm
		name='master:vendor_list'
	#elif (type == "Account"):
	#	importform = AccountForm
	#	name='master:account_list'
	if (request.method == "POST"):
		form = importform(request.POST)
		if form.is_valid():
			item=form.save(commit=False)
			current_tenant=request.user.tenant
			item.tenant=current_tenant
			item.save()
			return redirect(name)
	else:
		form=importform()
	
	return render(request, 'master/new.html',{'form': form, 'item': type})


@login_required
#Add new product
def new_product(request, type):
	#importform = ProductForm(request)
	name='master:product_list'
	if (request.method == "POST"):
		form = ProductForm(request.POST, tenant=request.user.tenant)
		if form.is_valid():
			item=form.save(commit=False)
			current_tenant=request.user.tenant
			item.tenant=current_tenant
			item.save()
			return redirect(name)
			#return HttpResponse(manufacturer.name)
	else:
		form=ProductForm(tenant=request.user.tenant)
	
	return render(request, 'master/new.html',{'form': form, 'item': type})


@login_required
#Add new subproduct
def new_subproduct(request, type):
	name='master:product_list'
	if (request.method == "POST"):
		form = subProductForm(request.POST, tenant=request.user.tenant)
		if form.is_valid():
			item=form.save(commit=False)
			#current_tenant=request.user.tenant
			#item.tenant=current_tenant
			item.save()
			return redirect(name)
	else:
		form=subProductForm(tenant=request.user.tenant)
	
	return render(request, 'master/new.html',{'form': form, 'item': type})

@login_required
#Add new customer
def new_customer(request, type):
	name='master:customer_list'
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

