import json
import re
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import F, Prefetch, Sum
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.db import IntegrityError, transaction


from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from .serializers import *

from distributor_master.models import Product
from distributor.variable_list import account_type_general
from distributor_user.models import Tenant
from .models import *
from .journalentry import *
from .account_support import *
# from .excel_download import *

# @login_required
@api_view(['GET','POST'],)
def payment_mode_view(request):
	if request.method == 'GET':
		payment_modes=payment_mode.objects.for_tenant(request.user.tenant).order_by('default')
		serializer = PaymentModeSerializers(payment_modes, many=True)
		# return Response(json.dumps(taxes,cls=DjangoJSONEncoder))
		return Response(serializer.data)

@api_view(['GET','POST'],)
def ledger_group_view(request):
	if request.method == 'GET':
		ledger_groups=ledger_group.objects.for_tenant(request.user.tenant)
		serializer = LedgerGroupSerializers(ledger_groups, many=True)
		return Response(serializer.data)

@api_view(['GET','POST'],)
def journal_group_view(request):
	if request.method == 'GET':
		journal_groups=journal_group.objects.for_tenant(request.user.tenant)
		serializer = JournalGroupSerializers(journal_groups, many=True)
		return Response(serializer.data)

@login_required
def new_journal_entry(request):
	extension="base.html"
	return render (request, 'account/journal_entry.html',{'extension':extension})

@login_required
def new_tax_report(request):
	extension="base.html"
	return render (request, 'account/tax_report.html',{'extension':extension})

@api_view(['GET'],)
def get_tax_report(request):
	this_tenant=request.user.tenant
	calltype=request.GET.get('calltype')
	response_data={}
	if (calltype == 'all_list'):
		response_data=list(tax_transaction.objects.for_tenant(request.user.tenant).values('transaction_type','tax_type',\
			'tax_percent', 'tax_value','transaction_bill_no','date','is_registered')\
			.order_by('transaction_type','date','tax_type','tax_percent'))
	elif (calltype == 'short_summary'):
		#This data can also be taken from chart of accounts
		response_data['cgst_input']=tax_transaction.objects.for_tenant(this_tenant).\
					filter(transaction_type=1,tax_type='CGST', is_registered=True).aggregate(Sum('tax_value'))['tax_value__sum']
		response_data['sgst_input']=tax_transaction.objects.for_tenant(this_tenant).\
					filter(transaction_type=1,tax_type='SGST', is_registered=True).aggregate(Sum('tax_value'))['tax_value__sum']
		response_data['igst_input']=tax_transaction.objects.for_tenant(this_tenant).\
					filter(transaction_type=1,tax_type='IGST', is_registered=True).aggregate(Sum('tax_value'))['tax_value__sum']
		
		response_data['cgst_output']=tax_transaction.objects.for_tenant(this_tenant).filter(transaction_type__in=[2,5],tax_type='CGST').\
					aggregate(Sum('tax_value'))['tax_value__sum']
		response_data['sgst_output']=tax_transaction.objects.for_tenant(this_tenant).filter(transaction_type__in=[2,5],tax_type='SGST').\
					aggregate(Sum('tax_value'))['tax_value__sum']
		response_data['igst_output']=tax_transaction.objects.for_tenant(this_tenant).filter(transaction_type=2,tax_type='IGST').\
					aggregate(Sum('tax_value'))['tax_value__sum']
		
		if not response_data['cgst_input']:
			response_data['cgst_input']=0
		if not response_data['sgst_input']:
			response_data['sgst_input']=0
		if not response_data['igst_input']:
			response_data['igst_input']=0

		if not response_data['cgst_output']:
			response_data['cgst_output']=0
		if not response_data['sgst_output']:
			response_data['sgst_output']=0
		if not response_data['igst_output']:
			response_data['igst_output']=0
		
		# jsondata = json.dumps(response_data,  cls=DjangoJSONEncoder)
		# return HttpResponse(jsondata)
	elif (calltype == 'apply_filter'):
		tax_percent=int(request.GET.get('tax_percent'))
		tax_type=request.GET.get('tax_type')
		response_data=tax_transaction.objects.for_tenant(request.user.tenant).all()
		if (tax_percent):
			response_data=response_data.filter(tax_percent=tax_percent).all()
		if (tax_type):
			response_data=response_data.filter(tax_type=tax_type).all()
		response_data=list(response_data.values('transaction_type','tax_type','tax_percent',\
			'tax_value','transaction_bill_no','date',).order_by('transaction_type','date','tax_type','tax_percent'))

	jsondata = json.dumps(response_data,cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

@login_required
def new_gst_purchase(request):
	extension="base.html"
	return render (request, 'gst_report/gst_purchase.html',{'extension':extension})

@api_view(['GET'],)
def get_gst_purchase(request):
	this_tenant=request.user.tenant
	calltype=request.GET.get('calltype')
	response_data={}
	if (calltype == 'all_list'):
		response_data=list(tax_transaction.objects.for_tenant(request.user.tenant).filter(transaction_type=1).\
			values('transaction_type','tax_type','tax_percent', 'tax_value','transaction_bill_no','date',)\
			.order_by('transaction_type','date','tax_type','tax_percent'))
		
	# elif (calltype == 'apply_filter'):
	# 	tax_percent=int(request.GET.get('tax_percent'))
	# 	tax_type=request.GET.get('tax_type')
	# 	response_data=tax_transaction.objects.for_tenant(request.user.tenant).all()
	# 	if (tax_percent):
	# 		response_data=response_data.filter(tax_percent=tax_percent).all()
	# 	if (tax_type):
	# 		response_data=response_data.filter(tax_type=tax_type).all()
	# 	response_data=list(response_data.values('transaction_type','tax_type','tax_percent',\
	# 		'tax_value','transaction_bill_no','date',).order_by('transaction_type','date','tax_type','tax_percent'))

	jsondata = json.dumps(response_data,cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)


#Restricted Access
@login_required
def account_info_view(request):
	extension="base.html"
	return render (request, 'account/important_figures.html',{'extension':extension})

@login_required
def get_account_type(request):
	if request.method == 'GET':
		jsondata = json.dumps(account_type_general,cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)


@api_view(['GET', 'POST'],)
def account_details_view(request):
	this_tenant=request.user.tenant
	current_year=accounting_period.objects.for_tenant(this_tenant).get(current_period=True)
	response_data = []
	type_dict={p:q for (p,q) in account_type_general}
	if request.method == 'GET':
		# accounts=Account.objects.for_tenant(this_tenant).exclude(key__in=["igstin","igstout","igstpay", \
		# 	 "sgstin","sgstout", "sgstpay", "cgstin","cgstout", "cgstpay"])
		accounts=Account.objects.for_tenant(this_tenant).exclude(key__in=["vatin","vatout","vatpay", "pur_return", "sales_return"])
		for item in accounts:
			this_account_year=account_year.objects.get(account=item, accounting_period=current_year)
			response_data.append({'id':item.id,'name':item.name,'key':item.key, 'type':type_dict[item.account_type], \
				'debit':this_account_year.current_debit, 'credit':this_account_year.current_credit})
		jsondata = json.dumps(response_data,cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)
	if request.method == 'POST':
		name=request.POST.get('name')
		key=request.POST.get('key')
		ledgerid=request.POST.get('ledger')
		account_type=request.POST.get('account_type')
		remarks=request.POST.get('remarks')
		try:
			opendebit=Decimal(request.POST.get('opendebit'))
		except:
			opendebit=0.00
		try:
			opencredit=Decimal(request.POST.get('opencredit'))
		except:
			opencredit=0.00
		try:
			debit=Decimal(request.POST.get('debit'))
		except:
			debit=0.00
		try:
			credit=Decimal(request.POST.get('credit'))
		except:
			credit=0.00
		try:
			ledger=ledger_group.objects.for_tenant(this_tenant).get(id=ledgerid)
		except:
			ledger = None
		with transaction.atomic():
			try:
				new_account=Account()
				new_account.name=name
				new_account.ledger_group=ledger
				new_account.remarks=remarks
				new_account.account_type=account_type
				new_account.key=key
				new_account.tenant=this_tenant
				new_account.save()
				new_account_year=account_year()
				new_account_year.account=new_account
				new_account_year.opening_debit=opendebit
				new_account_year.opening_credit=opencredit
				new_account_year.current_credit=credit
				new_account_year.current_debit=debit
				new_account_year.accounting_period=current_year
				new_account_year.tenant=this_tenant
				new_account_year.save()
			except:
				transaction.rollback()
		jsondata = json.dumps(response_data,cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)
		

@login_required
def payment_mode_data(request):
	extension="base.html"
	this_tenant=request.user.tenant
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		if (calltype == 'newmode'):
			name=request.POST.get('name')
			accountid=request.POST.get('accountid')
			default=request.POST.get('default')
			if (default == 'true'):
				default = True
			elif (default == 'false'):
				default = False
			account=Account.objects.for_tenant(this_tenant).get(id=accountid)
			new_mode=payment_mode()
			new_mode.name=name
			new_mode.payment_account=account
			new_mode.details=details
			new_mode.tenant=this_tenant
			new_mode.save()			
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render (request, 'account/payment_mode.html',{'extension':extension})

@login_required
def account_data(request):
	extension="base.html"
	this_tenant=request.user.tenant
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		if (calltype == 'newaccount'):
			name=request.POST.get('name')
			ledger_groupid=request.POST.get('ledger_group')
			remarks=request.POST.get('remarks')
			account_type=request.POST.get('account_type')
			key=request.POST.get('key')

			current_debit=request.POST.get('current_debit')
			current_credit=request.POST.get('current_credit')
			opening_debit=request.POST.get('opening_debit')
			opening_credit=request.POST.get('opening_credit')

			ledger=ledger_group.objects.for_tenant(this_tenant).get(id=ledger_groupid)
			current_year=accounting_period.objects.for_tenant(this_tenant).get(current_period=True)

			with transaction.atomic():
				try:
					new_account=Account()
					new_account.name=name
					new_account.ledger_group=ledger
					new_account.remarks=remarks
					new_account.account_type=account_type
					new_account.key=key
					new_account.tenant=this_tenant
					new_account.save()

					new_account_year=account_year()
					new_account_year.account=new_account
					new_account_year.opening_debit=opening_debit
					new_account_year.opening_credit=opening_credit
					new_account_year.current_credit=current_credit
					new_account_year.current_debit=current_debit
					new_account_year.accounting_period=current_year
					new_account_year.tenant=this_tenant
					new_account_year.save()
				except:
					transaction.rollback()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render (request, 'account/account.html',{'extension':extension})



@api_view(['GET', 'POST'],)
def journal_entry_data(request):
	this_tenant=request.user.tenant
	response_data=[]
	if request.method == 'POST':
		group_name = request.data.get('groupname')
		date = request.data.get('date')
		remarks = request.data.get('remarks')
		entries = json.loads(request.data.get('entries'))
		with transaction.atomic():
			try:
				journal=new_journal(this_tenant,date,group_name,remarks, trn_id=None, trn_type=9, other_data=None)
				for item in entries:
					trn_type=item['trn_type']
					accountid=item['accountid']
					account=Account.objects.for_tenant(this_tenant).get(id=accountid)
					value=item['value']
					# new_journal_entry(this_tenant, journal, value, account, trn_type)

					entry=journal_entry()
					entry.tenant=this_tenant
					entry.journal=journal
					entry.value=value
					entry.account= account
					entry.transaction_type = trn_type
					entry.save()	

					acct_period=accounting_period.objects.for_tenant(this_tenant).get(start__lte=date, end__gte=date)
					account_journal_year=account_year.objects.get(account=account, accounting_period = acct_period)
					if (trn_type == 1):
						account_journal_year.current_debit=account_journal_year.current_debit+value
					elif (trn_type == 2):
						account_journal_year.current_credit=account_journal_year.current_credit+value

				debit = journal.journalEntry_journal.filter(transaction_type=1).aggregate(Sum('value'))
				credit = journal.journalEntry_journal.filter(transaction_type=2).aggregate(Sum('value'))
				
				if (debit != credit):
					raise IntegrityError
			
			except:
				transaction.rollback()
	jsondata = json.dumps(response_data,cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

@login_required
def account_opening_view(request):
	extension="base.html"
	return render (request, 'account/opening_value.html',{'extension':extension})

@api_view(['GET', 'POST'],)
def account_opening_data(request):
	this_tenant=request.user.tenant
	response_data=[]
	if request.method == 'GET':
		accounts=Account.objects.for_tenant(this_tenant).all()
		current_period=accounting_period.objects.for_tenant(this_tenant).get(current_period=True)
		for item in accounts:
			item_detail=account_year.objects.for_tenant(this_tenant).get(account=item,accounting_period=current_period)	
			response_data.append({'accountid':item.id,'detailid':item_detail.id, \
                'name':item.name,'opening_debit':item_detail.opening_debit,'opening_credit':item_detail.opening_credit, \
                'first_debit':item_detail.first_debit, 'first_credit':item_detail.first_credit})
	jsondata = json.dumps(response_data,cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

@login_required
def account_period_view(request):
	extension="base.html"
	return render (request, 'account/account_year.html',{'extension':extension})

@api_view(['GET', 'POST'],)
def account_period_data(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		calltype = request.GET.get('calltype')
		# if (calltype == 'one_period'):
		# 	vendorid = request.GET.get('vendorid')
		# 	vendor=Vendor.objects.for_tenant(this_tenant).get(id=vendorid)
		# 	serializer = AccountingPeriodSerializers(vendor)
		# else:
		periods=accounting_period.objects.for_tenant(this_tenant).all()
		serializer = AccountingPeriodSerializers(periods, many=True)
		return Response(serializer.data)


@api_view(['GET'],)
#This is one option
def tax_short_summary(request):
	this_tenant=request.user.tenant
	response_data = {}
	if request.method == 'GET':
		# calltype = request.GET.get('calltype')
		account=Account.objects.for_tenant(this_tenant).get(name='CGST Input')
		response_data['cgst_input']=journal_entry.objects.for_tenant(this_tenant).filter(transaction_type=1,account=account).\
					aggregate(Sum('value'))['value__sum']
		
		account=Account.objects.for_tenant(this_tenant).get(name='SGST Input')
		response_data['sgst_input']=journal_entry.objects.for_tenant(this_tenant).filter(transaction_type=1,account=account).\
					aggregate(Sum('value'))['value__sum']

		account=Account.objects.for_tenant(this_tenant).get(name='GST Input')
		response_data['igst_input']=journal_entry.objects.for_tenant(this_tenant).filter(transaction_type=1,account=account).\
					aggregate(Sum('value'))['value__sum']

		
		if not response_data['cgst_input']:
			response_data['cgst_input']=0
		if not response_data['sgst_input']:
			response_data['sgst_input']=0
		if not response_data['igst_input']:
			response_data['igst_input']=0
		
		jsondata = json.dumps(response_data,  cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)
		

@login_required
def trial_balance_view(request):
	extension="base.html"
	date=datetime.now()
	period=accounting_period.objects.for_tenant(request.user.tenant).get(current_period=True)
	start=period.start
	end=period.end
	try:
		response_data=get_trial_balance(request, start, end)
	except:
		response_data=[]
	jsondata = json.dumps(response_data)
	return render(request, 'account/trial_balance.html', {'accounts':jsondata, "start":start, "date":date, 'extension':extension})
	# return render(request, 'account/trial_balance.html')


@api_view(['GET', 'POST'],)
def trial_balance_data(request):
	period=accounting_period.objects.for_tenant(request.user.tenant).get(current_period=True)
	start=period.start
	end=period.end
	tenant=request.user.tenant
	account_list=Account.objects.for_tenant(tenant).all()
	response_data=[]
	try:
		response_data=get_trial_balance(request, start, end)
	except:
		response_data=[]
	jsondata = json.dumps(response_data)
	return HttpResponse(jsondata)


# @api_view(['GET', 'POST'],)
@login_required
def account_journal_entries(request, pk_detail):
	extension="base.html"
	account=Account.objects.for_tenant(request.user.tenant).get(id=pk_detail)
	entries=journal_entry.objects.filter(account=account).select_related('journal').all()
	return render(request, 'account/accountwisejournal.html',{'account':account, 'entries':entries, 'extension':extension})


# @api_view(['GET', 'POST'],)
@login_required
#For showing the general ledger
def journal_detail(request,pk_detail):
	extension="base.html"
	journal=Journal.objects.for_tenant(request.user.tenant).get(id=pk_detail)
	entries=journal_entry.objects.filter(journal=journal).order_by('transaction_type').prefetch_related('journal').\
			select_related('account').all()
	return render(request, 'account/journal_view.html',{'journal':journal,'entries':entries,'extension':extension})



@login_required
def gst_payment(request):
	extension="base.html"
	return render(request, 'gst_report/gst_payment.html',{'extension':extension})


@login_required
#This view is for profit and loss
def profit_loss_view(request):
	extension="base.html"
	period=accounting_period.objects.for_tenant(request.user.tenant).get(current_period=True)
	start=period.start
	end=period.end
	# try:
	response_data=get_profit_loss(request, start, end, period)
	# except:
		# response_data=[]
	jsondata = json.dumps(response_data)
	return render(request, 'account/profit_loss.html', {'accounts':jsondata, "start":start, "date":end, "call":"p-l", \
					'extension':extension})


@login_required
#Show Balance Sheet
def balance_sheet(request):
	extension="base.html"
	date=datetime.now()
	period=accounting_period.objects.for_tenant(request.user.tenant).get(current_period=True)
	start=period.start
	end=period.end
	# try:
	response_data=get_balance_sheet(request, start, end, period)
	# except:
		# response_data=[]
	jsondata = json.dumps(response_data)
	return render(request, 'account/profit_loss.html', {'accounts':jsondata, "start":start, "date":date, "call":'b-s', 'extension':extension})