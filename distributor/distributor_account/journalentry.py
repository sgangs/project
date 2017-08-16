from datetime import datetime

from .models import Account, Journal, journal_entry, journal_group, accounting_period, account_year
from distributor_user.models import Tenant

#def new_journal(tenant, date, group,journal_type = None, key=None):
def new_journal(tenant, date, group_name, remarks='', trn_id=None, trn_type=None, other_data=None):
	journal_group_selected=journal_group.objects.for_tenant(tenant).get(name = group_name)
	journal=Journal()
	journal.tenant=tenant
	journal.date=date
	journal.group=journal_group_selected
	journal.remarks=remarks
	journal.transaction_bill_id=trn_id
	journal.trn_type=trn_type
	journal.other_data=other_data
	journal.save()
	return journal

def new_journal_entry(tenant, journal, value, account, trn_type, date):
	entry=journal_entry()
	entry.tenant=tenant
	entry.journal=journal
	entry.value=value
	entry.account= account
	entry.transaction_type = trn_type
	entry.save()

	acct_period=accounting_period.objects.for_tenant(tenant).get(start__lte=date, end__gte=date)
	account_journal_year=account_year.objects.get(account=account, accounting_period = acct_period)
	if (trn_type == 1):
		account_journal_year.current_debit=account_journal_year.current_debit+value
	elif (trn_type == 2):
		account_journal_year.current_credit=account_journal_year.current_credit+value
	account_journal_year.save()

