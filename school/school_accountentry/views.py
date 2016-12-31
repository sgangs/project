from datetime import datetime
from decimal import *
import json
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import F, Sum
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render

from school_account.models import Account, Journal, journal_entry, journal_group
from school_user.models import Tenant

@login_required
#This view helps in creating & thereafter saving a purchase invoice
def journalentry(request):
	date=datetime.now()	
	grouplist=journal_group.objects.for_tenant(request.user.tenant).all()
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}

		#getting Account Name
		if (calltype == 'account'):
			accountkey=request.POST.get('account_code')
			response_data['name']=Account.objects.for_tenant(request.user.tenant).\
									get(key__iexact=accountkey).name
					
		#saving the transaction
		if (calltype == 'save'):
			with transaction.atomic():
				try:
					journal_data = json.loads(request.POST.get('journal_details'))
					journal=Journal()
					journal.tenant=request.user.tenant
					journal.journal_type=request.POST.get('journal_type')
					group = request.POST.get('group')
					journal.group= grouplist.get(name__iexact=group)
					journal.save()
				#saving the journal entries and linking them with foreign key to journal
					for data in journal_data:
						entry = journal_entry()
						entry.tenant=request.user.tenant
						entry.journal=journal
						entry.value=data['value']
						accountkey=data['account_code']
						entry.account=Account.objects.for_tenant(request.user.tenant).get(key__iexact=accountkey)
						transaction_type= data['transaction_type']
						if (transaction_type == "Debit"):
							entry.transaction_type = "Debit"
						elif (transaction_type == "Credit"):
							entry.transaction_type = "Credit"
						entry.save()
					debit = journal.journalEntry_journal.filter(transaction_type="Debit").aggregate(Sum('value'))
					credit = journal.journalEntry_journal.filter(transaction_type="Credit").aggregate(Sum('value'))
					if (debit != credit):
						raise IntegrityError
				except:
					transaction.rollback()
				#this part is just for checking
				#response_data['name'] = accountkey
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	#return render(request, 'bill/purchaseinvoice.html', {'date':date,'type': type})
	return render(request, 'accounts/journalentry.html', {'date':date,'type': type, 'groups':grouplist})