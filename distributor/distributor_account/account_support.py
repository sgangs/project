from io import BytesIO
import xlsxwriter

from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext

from .models import Account, account_year, accounting_period, journal_entry

def create_new_accounts_year(new_period, this_tenant):
    acoounts_list=Account.objects.for_tenant(this_tenant).all()
    for item in acoounts_list:
        year=account_year()
        year.account=item
        year.accounting_period=new_period
        year.opening_debit=0
        year.opening_credit=0
        year.tenant=this_tenant
        year.save()

#This function is used to provide trail balance details
def get_trial_balance(request, start, end):
    this_tenant=request.user.tenant
    account_list=Account.objects.for_tenant(request.user.tenant).all()
    response_data=[]
    debit=0
    credit=0
    for item in account_list:
        this_debit=True
        this_credit=True
        item_debit=0
        item_credit=0
        journals=journal_entry.objects.for_tenant(this_tenant).\
            filter(journal__date__range=(start,end), account=item)
        journal_debit=journals.filter(transaction_type=1).aggregate(Sum('value'))
        journal_credit=journals.filter(transaction_type=2).aggregate(Sum('value'))
        if (journal_debit['value__sum'] == None):
            journal_debit['value__sum'] = 0
            this_debit=False
        if (journal_credit['value__sum'] == None):
            journal_credit['value__sum'] = 0
            this_credit=False
        if (this_debit or this_credit):
            if (item.account_type in ('ca','nca','rec','direxp','taxexp','indexp')):
                debit+=journal_debit['value__sum']-journal_credit['value__sum']
                item_debit=journal_debit['value__sum']-journal_credit['value__sum']
                item_credit=""
            elif (item.account_type in ('cl','pay', 'ncl','dirrev','indrev')):
                credit+=journal_credit['value__sum']-journal_debit['value__sum']
                item_credit=journal_credit['value__sum']-journal_debit['value__sum']
                item_debit=""
            elif(item.account_type in ('equ')):
                if (journal_credit['value__sum']>journal_debit['value__sum']):
                    item_credit=journal_credit['value__sum']-journal_debit['value__sum']
                    item_debit=""
                else:
                    item_debit=journal_debit['value__sum']-journal_credit['value__sum']
                    item_credit=""
            response_data.append({'data_type':'journal','account':item.name,'account_type':item.account_type,\
                                'debit':str(item_debit),'credit':str(item_credit)})
    response_data.append({'data_type':'value','debit':str(debit),'credit':str(credit)})
    return response_data


#This function is used to provide profit loss details
def get_profit_loss(request, start, end, sent='p-l'):
    account_list=Account.objects.for_tenant(request.user.tenant).filter(account_type__in=('dirrev','indrev',\
        'direxp', 'taxexp','indexp'))
    response_data=[]
    income=0
    expense=0
    other_income=0
    other_expense=0
    tax_expense=0
    profit=0
    for item in account_list:
        total=0
        journals=journal_entry.objects.for_tenant(request.user.tenant).\
            filter(journal__date__range=(start,end), account=item)
        journal_debit=journals.filter(transaction_type=1).aggregate(Sum('value'))
        journal_credit=journals.filter(transaction_type=2).aggregate(Sum('value'))
        if (journal_debit['value__sum'] == None):
            journal_debit['value__sum'] = 0
        if (journal_credit['value__sum'] == None):
            journal_credit['value__sum'] = 0
        if (item.account_type in ('dirrev','indev')):
            total-=journal_debit['value__sum']
            total+=journal_credit['value__sum']
            if(item.account_type in ('Revenue','Fees')):
                income+=total
                if (sent=='p-l'):
                    response_data.append({'data_type':'income','account':item.name,'total':str(total)})
            else:
                other_income+=total
                if (sent == 'p-l'):
                    response_data.append({'data_type':'other_income','account':item.name,'total':str(total)})
        elif (item.account_type in ('direxp', 'taxexp','indexp')):
            total+=journal_debit['value__sum']
            total-=journal_credit['value__sum']
            if(item.account_type in ('direxp')):
                expense+=total
                if (sent == 'p-l'):
                    response_data.append({'data_type':'expense','account':item.name,'total':str(total)})
            elif(item.account_type in ('indexp')):
                other_expense+=total
                if (sent == 'p-l'):
                    response_data.append({'data_type':'other_expense','account':item.name,'total':str(total)})
            else:
                tax_expense+=total
                if (sent == 'p-l'):
                    response_data.append({'data_type':'tax_expense','account':item.name,'total':str(total)})
        
        gross_income=income-expense
        net_income=gross_income+other_income-other_expense
        income_after_tax=net_income-tax_expense

    if (sent == 'p-l'):
        response_data.append({'data_type':'gross','income':str(gross_income)})
        response_data.append({'data_type':'net','income':str(net_income)})
        response_data.append({'data_type':'net_after_tax','income':str(income_after_tax)})
        return response_data
    return income_after_tax


#This function is used to provide profit loss details
def get_balance_sheet(request, start, end):
    account_list=Account.objects.for_tenant(request.user.tenant).filter(account_type__in=('ca','rec','nca'\
                    'cl','pay', 'ncl', 'equ'))
    response_data=[]
    asset=0
    long_asset=0
    total_asset=0
    liability=0
    long_liability=0
    total_liability=0
    drawings=0
    profit=0
    for item in account_list:
        total=0
        journals=journal_entry.objects.for_tenant(request.user.tenant).\
            filter(journal__date__range=(start,end), account=item)
        journal_debit=journals.filter(transaction_type=1).aggregate(Sum('value'))
        journal_credit=journals.filter(transaction_type=2).aggregate(Sum('value'))
        if (journal_debit['value__sum'] == None):
            journal_debit['value__sum'] = 0
        if (journal_credit['value__sum'] == None):
            journal_credit['value__sum'] = 0
        if (item.account_type in ('ca','rec','ncsa')):
            total+=journal_debit['value__sum']
            total-=journal_credit['value__sum']
            if(item.account_type in ('ca','rec')):
                asset+=total
                response_data.append({'data_type':'assets','account':item.name,'total':str(total)})
            elif (item.account_type in ('nca')):
                long_asset+=total
                response_data.append({'data_type':'long_assets','account':item.name,'total':str(total)})
        elif (item.account_type in ('cl', 'ncl', 'pay')):
            total-=journal_debit['value__sum']
            total+=journal_credit['value__sum']
            if(item.account_type in ('cl','pay')):
                liability+=total
                response_data.append({'data_type':'liability','account':item.name,'total':str(total)})
            else:
                long_liability+=total
                response_data.append({'data_type':'long_liability','account':item.name,'total':str(total)})
        elif(item.account_type in ('equ')):
            total-=journal_debit['value__sum']
            total+=journal_credit['value__sum']
            drawings+=total
            response_data.append({'data_type':'liability','account':item.name,'total':str(total)})
            
    total_asset=asset+long_asset
    profit=get_profit_loss(request,start,end,sent="balance-sheet")
    total_liability=liability+long_liability+profit+drawings
    response_data.append({'data_type':'total_asset','total':str(total_asset)})
    response_data.append({'data_type':'profit','total':str(profit)})
    response_data.append({'data_type':'total_liability','total':str(total_liability)})
    return response_data
            

