import datetime
from functools import wraps
from django.db.models import Sum
from django.shortcuts import redirect, resolve_url
from school_user.models import User, Tenant
from school_account.models import accounting_period, Account, journal_group, journal_entry, ledger_group
from school_fees.models import student_fee_payment, student_fee,monthly_fee_list, yearly_fee_list
 

#This is a custom user passes test function
def user_passes_test_custom(test_func, redirect_namespace):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            return redirect(redirect_namespace)
        return _wrapped_view
    return decorator



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
    			filter(year=year,month__iexact=month).aggregate(Sum('amount'))['amount__sum']
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


def yearly_pl(request):
    account_list=Account.objects.for_tenant(request.user.tenant).filter(account_type__in=('Revenue','Fees',\
                    'Indirect Revenue','Direct Expense', 'Salary','Indirect Expense'))
    response_data=[]
    income=0
    expense=0
    other_income=0
    other_expense=0
    profit=0
    period=accounting_period.objects.for_tenant(request.user.tenant).get(current_period=True)
    start=period.start
    end=period.end
    for item in account_list:
    	total=0
    	if (item.account_type in ('Revenue','Fees','Indirect Revenue')):
            total-=item.current_debit
            total+=item.current_credit
            if(item.account_type in ('Revenue','Fees')):
                income+=total
            else:
                other_income+=total
    	elif (item.account_type in ('Direct Expense', 'Salary','Indirect Expense')):
    		total+=item.current_debit
    		total-=item.current_credit
    		if(item.account_type in ('Direct Expense', 'Salary')):
    			expense+=total
    		else:
    			other_expense+=total

    profit=(income-expense)+other_income-other_expense
    response_data.append({'data_type':'other_income','amount':str(other_income)})
    response_data.append({'data_type':'other_expense','amount':str(other_expense)})
    response_data.append({'data_type':'income','amount':str(income)})
    response_data.append({'data_type':'expense','amount':str(expense)})
    response_data.append({'data_type':'profit','amount':str(profit)})
    return response_data
    