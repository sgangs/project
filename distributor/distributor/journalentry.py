from datetime import datetime

from distribution_purchase.models import purchaseInvoice, purchaseLineItem, purchasePayment
from distribution_accounts.models import accountChart, Journal, journalEntry, paymentMode, journalGroup
from distribution_user.models import Tenant

#def new_journal(tenant, date, group,journal_type = None, key=None):
def new_journal(tenant, date, group,journal_type = None):
	journal=Journal()
	journal.tenant=tenant
	journal.date=date
	journal.journal_type=journal_type
	journal.group=journalGroup.objects.for_tenant(tenant).get(name=group)
	#if (key != None):
	#	journal.key=key
	journal.save()
	return journal

def journal_entry(tenant, journal, value, account, trn_type):
	entry=journalEntry()
	entry.tenant=tenant
	entry.journal=journal
	entry.value=value
	entry.account= account
	entry.transaction_type = trn_type
	entry.save()	

