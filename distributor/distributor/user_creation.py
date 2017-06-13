from datetime import datetime
from django.db import IntegrityError, transaction

from distributor.variable_list import account_type_general
from distributor_user.models import User, Tenant
from distributor_account.models import Account, journal_group , ledger_group, account_year
from distributor_master.models import Dimension, Unit
 

type_dict={q:p for (p,q) in account_type_general}


#This function is used to create new ledger group
def create_ledger_group(tenant, name):
    group=ledger_group()
    group.name=name
    group.tenant=tenant
    group.save()
    return group


#This function is used to create new journal groups
def create_journal_group(tenant, name):
    group=journal_group()
    group.name=name
    group.tenant=tenant
    group.save()

#This function is used to create new accountChart
def create_accountChart(tenant, name, acc_type, remarks, key, period, ledgername, is_first_year = False):
	ledger=ledger_group.objects.filter(tenant=tenant).get(name=ledgername)
	with transaction.atomic():
		try:
			account=Account()
			account.name=name
			account.key=key
			account.ledger_group=ledger
			account.account_type=type_dict[acc_type]
			account.remarks=remarks
			account.tenant=tenant
			account.save()
			create_account_year(tenant, account, period, is_first_year)
			return account
		except:
			transaction.rollback()

def create_account_year(tenant, account_selected, period, is_first_year = False):
    account=account_year()
    account.account=account_selected
    account.opening_debit=0
    account.opening_credit=0
    account.current_debit=0
    account.current_credit=0
    account.accounting_period=period
    account.is_first_year=True
    account.tenant=tenant
    account.save()

def create_dimension(tenant, name, details, ):
	dimension=Dimension()
	dimension.name=name
	dimension.details=details
	dimension.tenant=tenant
	dimension.save()
	return dimension

def create_unit(tenant, dimension, name, symbol, multiplier):
	new_unit=Unit()
	new_unit.dimension=dimension
	new_unit.name=name
	new_unit.symbol=symbol
	new_unit.multiplier=multiplier
	new_unit.tenant=tenant
	new_unit.save()
