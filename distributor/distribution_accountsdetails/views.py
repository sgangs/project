from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import F, Sum
from decimal import *
import json
from datetime import datetime

from distribution_accounts.models import accountChart, Journal, journalEntry
from distribution_user.models import Tenant

@login_required
#This view helps in creating & thereafter saving a purchase invoice
def journalentry(request):
	date=datetime.now()	
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		
		#getting Account Name
		if (calltype == 'account'):
			accountkey=request.POST.get('account_code')
			response_data['name']=accountChart.objects.for_tenant(request.user.tenant).\
									get(key__iexact=accountkey).name
					
		#saving the trNAction
		if (calltype == 'save'):
			with transaction.atomic():
				try:
					journal_data = json.loads(request.POST.get('journal_details'))
					journal=Journal()
					#vendorkey = request.POST.get('vendor')
					journal.tenant=request.user.tenant
					journal.journal_type=request.POST.get('journal_type')
					group = request.POST.get('group')
					if (group != ""):
						journal.group=group					
					else:
						journal.group=""
					journal.save()
				#saving the journal entries and linking them with foreign key to journal
					for data in journal_data:
						entry = journalEntry()
						entry.tenant=request.user.tenant
						entry.journal=journal
						entry.value=data['value']
						accountkey=data['account_code']
						entry.account=accountChart.objects.for_tenant(request.user.tenant).get(key__iexact=accountkey)
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
	return render(request, 'accounts/journalentry.html', {'date':date,'type': type})