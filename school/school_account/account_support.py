from django.db.models import Sum
from django.shortcuts import get_object_or_404


from .models import Account, accounting_period, journal_entry
# from school_student.models import Student
# from school_eduadmin.models import class_section, classstudent, Exam, Syllabus
# from school_genadmin.models import class_group, Subject 


#This function is used to provide trail balance details
def get_trail_balance(request, start, end):
    account_list=Account.objects.for_tenant(request.user.tenant)
    response_data=[]
    debit=0
    credit=0
    for item in account_list:
        journals=journal_entry.objects.for_tenant(request.user.tenant).\
            filter(journal__date__range=(start,end), account=item)
        journal_debit=journals.filter(transaction_type="Debit").aggregate(Sum('value'))
        journal_credit=journals.filter(transaction_type="Credit").aggregate(Sum('value'))
        if (journal_debit['value__sum'] == None):
            journal_debit['value__sum'] = 0
        if (journal_credit['value__sum'] == None):
            journal_credit['value__sum'] = 0
        debit+=journal_debit['value__sum']
        credit+=journal_credit['value__sum']
        response_data.append({'data_type':'journal','account':item.name,'account_type':item.account_type,\
                                'debit':str(journal_debit['value__sum']),'credit':str(journal_credit['value__sum'])})
    response_data.append({'data_type':'value','debit':str(debit),'credit':str(credit)})
    return response_data


#This function is used to provide profit loss details
def get_profit_loss(request, start, end, sent='p-l'):
    account_list=Account.objects.for_tenant(request.user.tenant).filter(account_type__in=('Revenue','Fees',\
                    'Indirect Revenue','Direct Expense', 'Salary','Indirect Expense'))
    response_data=[]
    income=0
    expense=0
    other_income=0
    other_expense=0
    profit=0
    for item in account_list:
        total=0
        journals=journal_entry.objects.for_tenant(request.user.tenant).\
            filter(journal__date__range=(start,end), account=item)
        journal_debit=journals.filter(transaction_type="Debit").aggregate(Sum('value'))
        journal_credit=journals.filter(transaction_type="Credit").aggregate(Sum('value'))
        if (journal_debit['value__sum'] == None):
            journal_debit['value__sum'] = 0
        if (journal_credit['value__sum'] == None):
            journal_credit['value__sum'] = 0
        if (item.account_type in ('Revenue','Fees','Indirect Revenue')):
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
        elif (item.account_type in ('Direct Expense', 'Salary','Indirect Expense')):
            total+=journal_debit['value__sum']
            total-=journal_credit['value__sum']
            if(item.account_type in ('Direct Expense', 'Salary')):
                expense+=total
                if (sent == 'p-l'):
                    response_data.append({'data_type':'expense','account':item.name,'total':str(total)})
            else:
                other_expense+=total
                if (sent == 'p-l'):
                    response_data.append({'data_type':'other_expense','account':item.name,'total':str(total)})
        
        gross_income=income-expense
        net_income=gross_income+other_income-other_expense

    if (sent == 'p-l'):
        response_data.append({'data_type':'gross','income':str(gross_income)})
        response_data.append({'data_type':'net','income':str(net_income)})
        return response_data
    return net_income


#This function is used to provide profit loss details
def get_balance_sheet(request, start, end):
    account_list=Account.objects.for_tenant(request.user.tenant).filter(account_type__in=('Current Assets','Long Term Assets',\
                    'Depreciation','Current Liabilities', 'Long Term Liabilities'))
    response_data=[]
    asset=0
    long_asset=0
    total_asset=0
    liability=0
    long_liability=0
    total_liability=0
    depreciation=0
    profit=0
    for item in account_list:
        total=0
        journals=journal_entry.objects.for_tenant(request.user.tenant).\
            filter(journal__date__range=(start,end), account=item)
        journal_debit=journals.filter(transaction_type="Debit").aggregate(Sum('value'))
        journal_credit=journals.filter(transaction_type="Credit").aggregate(Sum('value'))
        if (journal_debit['value__sum'] == None):
            journal_debit['value__sum'] = 0
        if (journal_credit['value__sum'] == None):
            journal_credit['value__sum'] = 0
        if (item.account_type in ('Current Assets','Long Term Assets','Depreciation')):
            total+=journal_debit['value__sum']
            total-=journal_credit['value__sum']
            if(item.account_type in ('Current Assets')):
                asset+=total
                response_data.append({'data_type':'assets','account':item.name,'total':str(total)})
            elif (item.account_type in ('Long Term Assets')):
                long_asset+=total
                response_data.append({'data_type':'long_assets','account':item.name,'total':str(total)})
            else:
                depreciation+=total
                response_data.append({'data_type':'depreciation','account':item.name,'total':str(total)})
        elif (item.account_type in ('Current Liabilities', 'Long Term Liabilities')):
            total-=journal_debit['value__sum']
            total+=journal_credit['value__sum']
            if(item.account_type in ('Current Liabilities',)):
                liability+=total
                response_data.append({'data_type':'liability','account':item.name,'total':str(total)})
            else:
                long_liability+=total
                response_data.append({'data_type':'long_liability','account':item.name,'total':str(total)})

    total_asset=asset+long_asset-depreciation
    profit=get_profit_loss(request,start,end,sent="balance-sheet")
    total_liability=liability+long_liability+profit
    response_data.append({'data_type':'total_asset','total':str(total_asset)})
    response_data.append({'data_type':'profit','total':str(profit)})
    response_data.append({'data_type':'total_liability','total':str(total_liability)})
    return response_data
            

