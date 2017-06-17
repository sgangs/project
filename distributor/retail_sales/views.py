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
from distributor_account.models import Account, tax_transaction
from distributor_account.journalentry import new_journal, new_journal_entry
from distributor_inventory.models import Inventory, inventory_ledger, warehouse_valuation

# from .sales_utils import *
# from .models import *


@login_required
def new_sales_invoice(request):
	return render(request,'retail_sales/invoice.html', {'extension': 'base.html'})


@api_view(['GET','POST'],)
def get_product(request):
	this_tenant=request.user.tenant
	if request.is_ajax():
		print(request.GET)
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