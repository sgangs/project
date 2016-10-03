from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
#from django.db import IntegrityError, transaction
#from django.db.models import F

import json
import re
#from datetime import datetime
from distribution_user.models import Tenant
from .models import accountingPeriod, accountChart, Journal, journalEntry, paymentMode
from .forms import PeriodForm, ChartForm, PaymentForm

@login_required
#This is the accounts base list
def accounts_base(request):
		return render(request, 'accounts/accounts_base.html')


@login_required
def master_list(request, type):
	#for the delete button to work
	if request.method == 'POST':
		itemtype = request.POST.get('type')
		itemkey = request.POST.get('itemkey')
		response_data = {}
		if (itemtype == 'Period'):
			item = Period.objects.for_tenant(request.user.tenant).get(key__iexact=itemkey).delete()
			response_data['name'] = itemkey
			jsondata = json.dumps(response_data)
			return HttpResponse(jsondata)
		elif (itemtype == 'Chart'):
			item = accountChart.objects.for_tenant(request.user.tenant).get(key__iexact=itemkey).delete()
			response_data['name'] = itemkey
			jsondata = json.dumps(response_data)
			return HttpResponse(jsondata)	
	#for the list to be displayed	
	if (type=="Period"):
		items = accountingPeriod.objects.for_tenant(request.user.tenant).all()
	elif (type=="Payment Mode"):
		items = paymentMode.objects.for_tenant(request.user.tenant).all()
		return render(request, 'master/list_table.html',{'items':items, 'type':type})
	elif (type=="Chart"):
		accounts = accountChart.objects.for_tenant(request.user.tenant).all()
		return render(request, 'accounts/accountlist.html',{'accounts':accounts})
	return render(request, 'master/list.html',{'items':items, 'type':type})

@login_required
#For adding new entry for Aoccunting Period or Chart of Account
def master_new(request, type):
	if (type == "Period"):
		importform=PeriodForm
		name='accounts:period_list'
	elif (type == "Chart"):
		importform = ChartForm
		name='accounts:chart_list'
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
#Add new payment moce
def new_payment_mode(request, type):
	name='accounts:paymentmode_list'
	form=PaymentForm(tenant=request.user.tenant)
	if (request.method == "POST"):
		form = PaymentForm(request.POST, tenant=request.user.tenant)
		if form.is_valid():
			item=form.save(commit=False)
			current_tenant=request.user.tenant
			item.tenant=current_tenant
			default=item.default
			account=item.payment_account
			item.save()
			return redirect(name)
	return render(request, 'master/new.html',{'form': form, 'item': type})
	

@login_required
#For adding new entry for Manufacturer, Unit, Zone, Vendor & Account
def journal_list(request):
	journals=Journal.objects.filter(tenant=request.user.tenant).prefetch_related('journalEntry_journal')	
	return render(request, 'accounts/journal.html',{'journals':journals})

@login_required
#For showing the general ledger
def account_detail(request,detail):
	key_raw=detail.split("-",1)[1]
	accountkey=re.sub("-"," ",key_raw)
	#jrentry refers to jouirnal entry
	#account_with_jrentry=accountChart.objects.for_tenant(request.user.tenant).\
			#get(key__exact=accountkey).prefetch_related('journalEntry_accountChart')
	#account=account_with_jrentry.prefetch_related('journalEntry_journal')
	account=accountChart.objects.for_tenant(request.user.tenant).get(key__exact=accountkey)
	entries=account.journalEntry_accountChart.all()

	return render(request, 'accounts/accountledger.html',{'account':account, 'entries':entries})