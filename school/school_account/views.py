import json
import re
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db.models import F, Prefetch, Sum
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.db import IntegrityError, transaction
from .models import *
from .forms import PeriodForm, LedgerGroupForm, AccountForm, JournalGroupForm, PaymentForm, AccountYearForm
from school_user.models import Tenant
from .account_support import *
from .excel_download import *




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
#Download Accounts List in Excel
def account_export(request):
	# if 'excel' in request.POST:
	response = HttpResponse(content_type='application/vnd.ms-excel')
	name=request.user.tenant.name
	response['Content-Disposition'] = 'attachment; filename=Accounts List-'+name+'.xlsx'
	data_type="Account List"
	accounts = Account.objects.for_tenant(request.user.tenant).all()
	xlsx_data = account_excel(accounts, data_type)
	response.write(xlsx_data)
	return response

@login_required
#For showing the general ledger
def account_detail(request,detail):
	account=Account.objects.for_tenant(request.user.tenant).get(slug__exact=detail)
	# entries=Account.journalEntry_account.all()
	entries=journal_entry.objects.filter(account=account).select_related('journal').all()
	return render(request, 'accounts/accountledger.html',{'account':account, 'entries':entries})

@login_required
#For showing the general ledger
def journal_detail(request,detail):
	journal=Journal.objects.for_tenant(request.user.tenant).get(slug__exact=detail)
	entries=journal_entry.objects.filter(journal=journal).prefetch_related('journal').select_related('account').all()	
	return render(request, 'accounts/journal_entry.html',{'journal':journal,'entries':entries, 'callfrom':'detail'})

@login_required
#This view helps in creating & thereafter saving a purchase invoice
def journalentry(request):
	date=datetime.now()	
	this_tenant=request.user.tenant
	grouplist=journal_group.objects.for_tenant(this_tenant).all()
	accounts=Account.objects.for_tenant(this_tenant).values('name','key','current_debit','current_credit')

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
						trn_type=data['transaction_type']
						account=Account.objects.for_tenant(this_tenant).get(key__iexact=accountkey)
						if (trn_type == "Debit"):
							account.current_debit=account.current_debit+value
						elif (trn_type == "Credit"):
							account.current_credit=account.current_credit+value
						else:
							transaction.rollback()
							raise IntegrityError
						account.save()
						entry.value=value
						# entry.this_debit=account.current_debit
						# entry.this_credit=account.current_credit
						entry.account=account
						entry.transaction_type=trn_type
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
	return render(request, 'accounts/new_journal_entry.html', {'date':date,'type': type, 'groups':grouplist, 'accounts':accounts,})

@login_required
#This view is to help create new account
def new_account(request):
	#date=datetime.now()
	account_type_dict=dict((y, x) for x, y in account_type_general)
	this_tenant=request.user.tenant
	periods=accounting_period.objects.for_tenant(this_tenant).filter(finalized=False).values('id','start','end')
	groups=ledger_group.objects.for_tenant(this_tenant).all()
	accounts=Account.objects.for_tenant(this_tenant).values('name','current_debit','current_credit')
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
					sub_acct_type=request.POST.get('sub_acct_type')
					if (acct_type not in account_type_dict):
						raise IntegrityError
					periodid=request.POST.get('periodid')
					balance_type=request.POST.get('balance_type')
					balance=float(request.POST.get('balance'))
					ledger=ledger_group.objects.for_tenant(this_tenant).get(id=ledgerid)
					period=accounting_period.objects.for_tenant(this_tenant).get(id=periodid)
					account=Account()
					account.ledger_group=ledger
					account.sub_account_type=sub_acct_type
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


@login_required
#This view is for trail balance
def trail_balance(request):
	date=datetime.now()
	period=accounting_period.objects.for_tenant(request.user.tenant).get(current_period=True)
	start=period.start
	end=period.end
	try:
		response_data=get_trail_balance(request, start, end)
	except:
		response_data=[]
	jsondata = json.dumps(response_data)
	return render(request, 'accounts/trail_balance.html', {'accounts':jsondata, "start":start, "date":date})

@login_required
#Export Account List
def trail_balance_export(request):
	# if 'excel' in request.POST:
	response = HttpResponse(content_type='application/vnd.ms-excel')
	name=request.user.tenant.name
	response['Content-Disposition'] = 'attachment; filename=Trail Balance-'+name+'.xlsx'
	period=accounting_period.objects.for_tenant(request.user.tenant).get(current_period=True)
	start=period.start
	end=period.end
	data_type="Trail Balance Summary"
	data=get_trail_balance(request, start, end)
	xlsx_data = trail_balance_excel(data, data_type)
	response.write(xlsx_data)
	return response


@login_required
#This view is for profit and loss
def profit_loss(request):
	date=datetime.now()
	period=accounting_period.objects.for_tenant(request.user.tenant).get(current_period=True)
	start=period.start
	end=period.end
	try:
		response_data=get_profit_loss(request, start, end)
	except:
		response_data=[]
	jsondata = json.dumps(response_data)
	return render(request, 'accounts/profit_loss.html', {'accounts':jsondata, "start":start, "date":date, "call":"p-l"})

@login_required
#Export Account List
def profit_loss_export(request):
	# if 'excel' in request.POST:
	response = HttpResponse(content_type='application/vnd.ms-excel')
	name=request.user.tenant.name
	response['Content-Disposition'] = 'attachment; filename=Income Expenditure-'+name+'.xlsx'
	period=accounting_period.objects.for_tenant(request.user.tenant).get(current_period=True)
	start=period.start
	end=period.end
	data_type="Income Expenditure Summary"
	data=get_profit_loss(request, start, end)
	xlsx_data = profit_loss_excel(data, data_type)
	response.write(xlsx_data)
	return response


@login_required
#Show Balance Sheet
def balance_sheet(request):
	date=datetime.now()
	period=accounting_period.objects.for_tenant(request.user.tenant).get(current_period=True)
	start=period.start
	end=period.end
	try:
		response_data=get_balance_sheet(request, start, end)
	except:
		response_data=[]
	jsondata = json.dumps(response_data)
	return render(request, 'accounts/profit_loss.html', {'accounts':jsondata, "start":start, "date":date, "call":'b-s'})



@login_required
#Show Balance Sheet
def cash_history(request):
	this_tenant=request.user.tenant
	response_data=[]
	date=datetime.now()
	period=accounting_period.objects.for_tenant(request.user.tenant).get(current_period=True)
	start=period.start
	end=period.end
	cash_account=Account.objects.for_tenant(this_tenant).get(key='cash')
	entries=journal_entry.objects.for_tenant(request.user.tenant).\
		filter(journal__date__range=(start,end), account=cash_account).order_by('journal__date').select_related('journal')
	try:
		opening=account_year.objects.for_tenant(this_tenant).get(account=cash_account, accounting_period=period)
		opening_credit=opening.opening_credit
		opening_debit=opening.opening_debit
	except:
		opening_credit=0
		opening_debit=0
	balance=opening_debit-opening_credit
	for entry in entries:
		if (entry.transaction_type == "Debit"):
			balance=balance+entry.value
			response_data.append({'slug':entry.journal.slug,'date':entry.journal.date,'trn_id':entry.journal.key,\
            	'trn_type':entry.transaction_type,'value':entry.value,'balance':balance,})
		elif (entry.transaction_type == "Credit"):
			balance=balance-entry.value
			response_data.append({'slug':entry.journal.slug,'date':entry.journal.date,'trn_id':entry.journal.key,\
            	'trn_type':entry.transaction_type,'value':entry.value,'balance':balance,})
		print(balance)
	# try:
	# 	response_data=get_balance_sheet(request, start, end)
	# except:
	# 	response_data=[]
	# jsondata = json.dumps(response_data)
	return render(request, 'accounts/cash_accountledger.html', {'entries':response_data})
