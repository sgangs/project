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

from distributor_master.models import Unit, Product, Customer, Warehouse
from distributor_inventory.models import Inventory
from distributor_account.models import Account, tax_transaction
from distributor_account.journalentry import new_journal, new_journal_entry
from distributor_inventory.models import Inventory, inventory_ledger, warehouse_valuation

# from .sales_utils import *
# from .models import *


@login_required
def new_sales_invoice(request):
	return render(request,'retail_sales/invoice.html', {'extension': 'base.html'})
