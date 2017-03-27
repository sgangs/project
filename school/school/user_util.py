import datetime
from functools import wraps
from django.db.models import Sum
from django.shortcuts import redirect, resolve_url
from school_user.models import User, Tenant
from school_hr.models import leave_type
from school_account.models import accounting_period, Account, journal_group, journal_entry, ledger_group, account_year
from school_fees.models import student_fee_payment, student_fee,generic_fee_list, generic_fee
 

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

def create_account_year(tenant, key, period):
    account=account_year()
    account_selected=Account.objects.for_tenant(tenant).get(key=key)
    account.account=account_selected
    account.opening_debit=0
    account.opening_credit=0
    account.current_debit=0
    account.current_credit=0
    account.accounting_period=period
    account.tenant=tenant
    account.save()

#This function is used to create new leave type
def create_leave_type(name, key, current_leave_type, tenant):
    leave=leave_type()
    leave.name=name
    leave.key=key
    leave.leave_type=current_leave_type
    leave.tenant=tenant
    leave.save()

#This function is used to show monthly fee collection graph
def fee_paid(request,year):
    now=datetime.date.today()
    month=now.strftime("%b")
    total_paid=student_fee_payment.objects.for_tenant(request.user.tenant).\
    			filter(year=year,month__iexact=month).aggregate(Sum('amount'))['amount__sum']
    return total_paid

def month_fee(request, year):
    now=datetime.date.today()
    month=now.strftime("%b")
    feelist=student_fee.objects.for_tenant(request.user.tenant).filter(year=year)
    fee_total=0
    for fee in feelist:
        generic_fee=fee.generic_fee.filter(month__contains=[month]).all() 
        for item in generic_fee:
            fee_total+=item.total
    return fee_total
	
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
    