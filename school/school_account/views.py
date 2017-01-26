import json
import re
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db.models import F, Prefetch, Sum
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.db import IntegrityError, transaction
from .models import accounting_period, Account, ledger_group, Journal, journal_group, journal_entry, payment_mode, account_year
from .forms import PeriodForm, LedgerGroupForm, AccountForm, JournalGroupForm, PaymentForm, AccountYearForm
from school_user.models import Tenant
from .account_support import *

@login_required
#This is the base page.
def base(request, input_type):
	if (input_type == 'Generic'):
		return render (request, 'accounts/generic_base.html')
	elif (input_type == 'Accounts'):
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
	elif (input_type == "Account Year"):
		importform = AccountYearForm
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
	elif (type=="Account"):
		accounts = Account.objects.for_tenant(request.user.tenant).all()
		return render(request, 'accounts/accountlist.html',{'accounts':accounts})
	return render(request, 'accounts/list.html',{'items':items, 'type':type})

@login_required
#For showing the general ledger
def account_detail(request,detail):
	account=Account.objects.for_tenant(request.user.tenant).get(slug__exact=detail)
	# entries=Account.journalEntry_account.all()
	entries=journal_entry.objects.filter(account=account).prefetch_related('journal').all()

	return render(request, 'accounts/accountledger.html',{'account':account, 'entries':entries})

@login_required
#For showing the general ledger
def journal_detail(request,detail):
	journal=Journal.objects.for_tenant(request.user.tenant).get(slug__exact=detail)
	entries=journal_entry.objects.filter(journal=journal).prefetch_related('journal').select_related('account').all()
	print (journal.slug)

	return render(request, 'accounts/journal_entry.html',{'journal':journal,'entries':entries, 'callfrom':'detail'})


@login_required
#This view helps in creating & thereafter saving a purchase invoice
def journalentry(request):
	date=datetime.now()	
	grouplist=journal_group.objects.for_tenant(request.user.tenant).all()
	this_tenant=request.user.tenant
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}

		#getting Account Name
		if (calltype == 'account'):
			accountkey=request.POST.get('account_code')
			response_data['name']=Account.objects.for_tenant(this_tenant).\
									get(key__iexact=accountkey).name
					
		#saving the transaction
		if (calltype == 'save'):
			with transaction.atomic():
				try:
					journal_data = json.loads(request.POST.get('details'))
					journal=Journal()
					journal.tenant=this_tenant
					journal.date=request.POST.get('date')
					journal.remarks=request.POST.get('remarks')
					# journal.journal_type=request.POST.get('journal_type')
					groupid = int(request.POST.get('groupid'))
					journal.group= grouplist.get(id=groupid)
					journal.save()
				#saving the journal entries and linking them with foreign key to journal
					for data in journal_data:
						entry = journal_entry()
						entry.tenant=this_tenant
						entry.journal=journal
						value=data['value']
						accountkey=data['code']
						account=Account.objects.for_tenant(request.user.tenant).get(key__iexact=accountkey)
						#or_value=account.value
						#account.value=or_value+value
						account.save()
						entry.value=value
						entry.account=account
						entry.transaction_type=data['transaction_type']
						# transaction_type= data['transaction_type']
						# if (transaction_type == "Debit"):
						# 	entry.transaction_type = "Debit"
						# elif (transaction_type == "Credit"):
						# 	entry.transaction_type = "Credit"
						entry.save()
					debit = journal.journalEntry_journal.filter(transaction_type="Debit").aggregate(Sum('value'))
					credit = journal.journalEntry_journal.filter(transaction_type="Credit").aggregate(Sum('value'))
					if (debit != credit):
						raise IntegrityError
				except:
					transaction.rollback()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	#return render(request, 'bill/purchaseinvoice.html', {'date':date,'type': type})
	return render(request, 'accounts/journal_entry.html', {'date':date,'type': type, 'groups':grouplist})

#This view is to help create new account
def new_account(request):
	#date=datetime.now()	
	periods=accounting_period.objects.for_tenant(request.user.tenant).all()
	groups=ledger_group.objects.for_tenant(request.user.tenant).all()
	accounts=Account.objects.for_tenant(request.user.tenant).all()
	this_tenant=request.user.tenant
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		#getting Account Name
		if (calltype == 'account'):
			account=request.POST.get('account_name')
			try:
				acct_copy=Account.objects.for_tenant(this_tenant).\
									get(name__iexact=account)
				response_data['error'] = "Account with same name already exist."
			except:
				response_data['valid'] = "Account does not exist."
		elif (calltype == 'key'):
			key=request.POST.get('key')
			try:
				key_copy=Account.objects.for_tenant(this_tenant).\
									get(key__iexact=key)
				response_data['error'] = "Account with same key already exist."
			except:
				response_data['valid'] = "Account does not exist."
		#saving the transaction
		elif (calltype == 'save'):
			with transaction.atomic():
				try:
					ledgerid=request.POST.get('ledgerid')
					name=request.POST.get('name')
					remarks=request.POST.get('remarks')
					key=request.POST.get('key')
					acct_type=request.POST.get('acct_type')
					periodid=request.POST.get('periodid')
					balance_type=request.POST.get('balance_type')
					balance=float(request.POST.get('balance'))
					ledger=ledger_group.objects.get(id=ledgerid)
					period=accounting_period.objects.get(id=periodid)
					account=Account()
					account.ledger_group=ledger
					account.name=name
					account.remarks=remarks
					account.key=key
					account.account_type=acct_type
					account.tenant=this_tenant
					account.save()
					year=account_year()
					year.account=account
					year.accounting_period=period
					if (balance_type=="Debit"):
						year.opening_debit=balance
					elif (balance_type=="Credit"):
						year.opening_credit=balance
					year.tenant=this_tenant
					year.save()
				except:
					transaction.rollback()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	#return render(request, 'bill/purchaseinvoice.html', {'date':date,'type': type})
	return render(request, 'accounts/new_account.html', {'periods':periods, 'groups':groups, 'accounts':accounts})


#This view is for trail balance
def trail_balance(request):
	date=datetime.now()
	period=accounting_period.objects.for_tenant(request.user.tenant).get(current_period=True)
	start=period.start
	end=period.end
	response_data=get_trail_balance(request, start, end)
	jsondata = json.dumps(response_data)
	return render(request, 'accounts/trail_balance.html', {'accounts':jsondata, "start":start, "date":date})

#This view is for profit and loss
def profit_loss(request):
	date=datetime.now()
	period=accounting_period.objects.for_tenant(request.user.tenant).get(current_period=True)
	start=period.start
	end=period.end
	response_data=get_profit_loss(request, start, end)
	jsondata = json.dumps(response_data)
	return render(request, 'accounts/profit_loss.html', {'accounts':jsondata, "start":start, "date":date, "call":"p-l"})

def balance_sheet(request):
	date=datetime.now()
	period=accounting_period.objects.for_tenant(request.user.tenant).get(current_period=True)
	start=period.start
	end=period.end
	response_data=get_balance_sheet(request, start, end)
	jsondata = json.dumps(response_data)
	return render(request, 'accounts/profit_loss.html', {'accounts':jsondata, "start":start, "date":date, "call":'b-s'})

