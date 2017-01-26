import datetime
from django.db.models import Sum
from school_user.models import User, Tenant
from school_account.models import Account, journal_group, ledger_group
from school_fees.models import student_fee_payment, student_fee,monthly_fee_list, yearly_fee_list
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

#This function is used to create new account
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


#This function is used to show monthly fee collection graph
def fee_paid(request,year):
    now=datetime.date.today()
    month=now.strftime("%b").lower()
    total_paid=student_fee_payment.objects.for_tenant(request.user.tenant).\
    			filter(year=year,month=month).aggregate(Sum('amount'))['amount__sum']
    return total_paid

def month_fee(request, year):
	now=datetime.date.today()
	month=now.strftime("%b").lower()
	students_fee=student_fee.objects.for_tenant(request.user.tenant).filter(year=year)
	yearly_fee_total=0
	monthly_fee_total=0
	for fee in students_fee:
		monthly_fee=fee.monthly_fee
		monthly_fee_total+=monthly_fee_list.objects.filter(monthly_fee=monthly_fee).aggregate(Sum('amount'))['amount__sum']
		yearly_fee=fee.yearly_fee.filter(month=month)
		for item in yearly_fee:
			yearly_fee_total+=yearly_fee_list.objects.filter(yearly_fee=item).aggregate(Sum('amount'))['amount__sum']
	return monthly_fee_total+yearly_fee_total


