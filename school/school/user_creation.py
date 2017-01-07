from datetime import datetime

from school_user.models import User, Tenant
from school_account.models import Account, journal_group, ledger_group
#from distribution_master.models import Dimension, Unit
 

#This function is used to create new journal groups
def create_journal_group(tenant, name):
    group=journal_group()
    group.name=name
    group.tenant=tenant
    group.save()

#This function is used to create new ledger group
def create_ledger_group(tenant, name):
    group=ledger_group()
    group.name=name
    group.tenant=tenant
    group.save()

#This function is used to create new accountChart
#We need to create cash account and lets say some other account.
def create_account(tenant, name, acc_type, remarks, key, ledgername):
	ledger=ledger_group.objects.filter(tenant=tenant).get(name=ledgername)
	account=Account()
	account.ledger_group=ledger
	account.name=name
	account.account_type=acc_type
	account.remarks=remarks
	account.key=key
	account.tenant=tenant
	account.save()

