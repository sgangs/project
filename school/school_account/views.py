import json
import re
#from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db.models import F, Prefetch, Sum
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
#from django.db import IntegrityError, transaction

from .models import accounting_period, Account, ledger_group, Journal, journal_group, journal_entry, payment_mode
from .forms import PeriodForm, LedgerGroupForm, AccountForm, JournalGroupForm, PaymentForm
from school_user.models import Tenant

@login_required
#This is the base page.
def base(request):
	return render (request, 'accounts/accounts_base.html')

@login_required
#For adding new entry for Aoccunting Period or Chart of Account
def account_new(request, input_type):
	if (input_type == "Period"):
		importform=PeriodForm
		name='accounts:period_list'
	elif (input_type == "Ledger Group"):
		importform = LedgerGroupForm
		name='accounts:ledger_group_list'
	elif (input_type == "Account"):
		importform = AccountForm
		name='accounts:account_list'
	elif (input_type == "Journal Group"):
		importform = JournalGroupForm
		name='accounts:journalgroup_list'
	form=importform(tenant=request.user.tenant)
	if (request.method == "POST"):
		form = importform(request.POST, tenant=request.user.tenant)
		if form.is_valid():
			item=form.save(commit=False)
			current_tenant=request.user.tenant
			item.tenant=current_tenant
			item.save()
			return redirect(name)
	return render(request, 'genadmin/new.html',{'form': form, 'item': input_type})

@login_required
#Add new payment mode
def payment_mode_new(request, input_type):
	name='accounts:paymentmode_list'
	form=PaymentForm(tenant=request.user.tenant)
	if (request.method == "POST"):
		form = PaymentForm(request.POST, tenant=request.user.tenant)
		if form.is_valid():
			item=form.save(commit=False)
			current_tenant=request.user.tenant
			item.tenant=current_tenant
			default=item.default
			if (default == "Yes"):
				try:
					old_default=paymentMode.objects.for_tenant(request.user.tenant).get(default="Yes")
					old_default.default="No"
					old_default.save()
				except:
					pass
			account=item.payment_account
			item.save()
			return redirect(name)
	return render(request, 'genadmin/new.html',{'form': form, 'item': type})


@login_required
def account_list(request, type):
	#for the delete button to work
	# if request.method == 'POST':
	# 	itemtype = request.POST.get('type')
	# 	itemkey = request.POST.get('itemkey')
	# 	response_data = {}
	# 	if (itemtype == 'Period'):
	# 		item = Period.objects.for_tenant(request.user.tenant).get(key__iexact=itemkey).delete()
	# 		response_data['name'] = itemkey
	# 		jsondata = json.dumps(response_data)
	# 		return HttpResponse(jsondata)
	# 	elif (itemtype == 'Chart'):
	# 		item = accountChart.objects.for_tenant(request.user.tenant).get(key__iexact=itemkey).delete()
	# 		response_data['name'] = itemkey
	# 		jsondata = json.dumps(response_data)
	# 		return HttpResponse(jsondata)	
	#for the list to be displayed	
	if (type=="Ledger Group"):
		items = ledger_group.objects.for_tenant(request.user.tenant).all()
	if (type=="Period"):
		items = accounting_period.objects.for_tenant(request.user.tenant).all()
	elif (type=="Payment Mode"):
		items = payment_mode.objects.for_tenant(request.user.tenant).all()
		return render(request, 'accounts/list_table.html',{'items':items, 'type':type})
	elif (type=="Journal Group"):
		items = journal_group.objects.for_tenant(request.user.tenant).all()
	elif (type=="Chart"):
		accounts = Account.objects.for_tenant(request.user.tenant).all()
		return render(request, 'accounts/accountlist.html',{'accounts':accounts})
	return render(request, 'accounts/list.html',{'items':items, 'type':type})