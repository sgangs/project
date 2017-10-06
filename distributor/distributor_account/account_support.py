from io import BytesIO
import xlsxwriter
import datetime as dt
import calendar
from dateutil.relativedelta import relativedelta


from django.db.models import Sum, F, Case, Value, When, DecimalField
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext

from .models import *

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
def get_profit_loss(request, start, end, period, sent='p-l'):
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
        this_debit=True
        this_credit=True
        total=0
        journal_debit={}
        journal_credit={}
        # journals=journal_entry.objects.for_tenant(request.user.tenant).\
        #     filter(journal__date__range=(start,end), account=item)
        # journal_debit=journals.filter(transaction_type=1).aggregate(Sum('value'))
        # journal_credit=journals.filter(transaction_type=2).aggregate(Sum('value'))
        account_year_data=account_year.objects.for_tenant(request.user.tenant).\
            get(account=item, accounting_period = period)
        journal_debit['value__sum']=account_year_data.current_debit
        journal_credit['value__sum']=account_year_data.current_credit
        # if (journal_debit['value__sum'] == None):
        if (journal_debit['value__sum'] == 0):
            journal_debit['value__sum'] = 0
            this_debit = False
        # if (journal_credit['value__sum'] == None):
        if (journal_credit['value__sum'] == 0):
            journal_credit['value__sum'] = 0
            this_credit = False
        if (item.account_type in ('dirrev','indev')):
            total-=journal_debit['value__sum']
            total+=journal_credit['value__sum']
            if(item.account_type in ('dirrev')):
                income+=total
                if (sent=='p-l'):
                    if (this_debit or this_credit):
                        response_data.append({'data_type':'income','account':item.name,'total':str(total)})
            else:
                other_income+=total
                if (sent == 'p-l'):
                    if (this_debit or this_credit):
                        response_data.append({'data_type':'other_income','account':item.name,'total':str(total)})
        elif (item.account_type in ('direxp', 'taxexp','indexp')):
            total+=journal_debit['value__sum']
            total-=journal_credit['value__sum']
            if(item.account_type in ('direxp')):
                # print(item.name)
                expense+=total
                if (sent == 'p-l'):
                    if (this_debit or this_credit):
                        response_data.append({'data_type':'expense','account':item.name,'total':str(total)})
            # elif(item.account_type in ('indexp')):
            #     other_expense+=total
            #     if (sent == 'p-l'):
            #         response_data.append({'data_type':'other_expense','account':item.name,'total':str(total)})
            else:
                other_expense+=total
                if (sent == 'p-l'):
                    if (this_debit or this_credit):
                        response_data.append({'data_type':'other_expense','account':item.name,'total':str(total)})
            # else:
            #     tax_expense+=total
            #     if (sent == 'p-l'):
            #         response_data.append({'data_type':'tax_expense','account':item.name,'total':str(total)})
        
        inventory_acct=account_inventory.objects.for_tenant(request.user.tenant).get(name__exact="Inventory")
        acct_period=accounting_period.objects.for_tenant(request.user.tenant).get(current_period=True)
        inventory_this_year=account_year_inventory.objects.for_tenant(request.user.tenant).\
                        get(account_inventory=inventory_acct, accounting_period = acct_period)
        opening_stock=inventory_this_year.opening_debit - inventory_this_year.opening_credit
        closing_stock=inventory_this_year.current_debit - inventory_this_year.current_credit
        gross_income=income-expense-opening_stock+closing_stock
        net_income=gross_income+other_income-other_expense
        # income_after_tax=net_income-tax_expense

    if (sent == 'p-l'):
        response_data.append({'data_type':'gross','income':str(gross_income)})
        response_data.append({'data_type':'net','income':str(net_income)})
        response_data.append({'data_type':'opening','income':str(opening_stock)})
        response_data.append({'data_type':'closing','income':str(closing_stock)})
        # response_data.append({'data_type':'net_after_tax','income':str(income_after_tax)})
        return response_data
    return net_income


#This function is used to provide profit loss details
def get_balance_sheet(request, start, end, period):
    account_list=Account.objects.for_tenant(request.user.tenant).filter(account_type__in=('ca','rec','nca',\
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
        this_debit=True
        this_credit=True
        journals=journal_entry.objects.for_tenant(request.user.tenant).\
            filter(journal__date__range=(start,end), account=item)
        journal_debit=journals.filter(transaction_type=1).aggregate(Sum('value'))
        journal_credit=journals.filter(transaction_type=2).aggregate(Sum('value'))
        if (journal_debit['value__sum'] == None):
            journal_debit['value__sum'] = 0
            this_debit = False
        if (journal_credit['value__sum'] == None):
            journal_credit['value__sum'] = 0
            this_credit = False
        if (item.account_type in ('ca','rec','ncsa')):
            total+=journal_debit['value__sum']
            total-=journal_credit['value__sum']
            if(item.account_type in ('ca','rec')):
                asset+=total
                if (this_debit or this_credit):
                    response_data.append({'data_type':'assets','account':item.name,'total':str(total)})
            elif (item.account_type in ('nca')):
                long_asset+=total
                if (this_debit or this_credit):
                    response_data.append({'data_type':'long_assets','account':item.name,'total':str(total)})
        elif (item.account_type in ('cl', 'ncl', 'pay')):
            total-=journal_debit['value__sum']
            total+=journal_credit['value__sum']
            if(item.account_type in ('cl','pay')):
                liability+=total
                if (this_debit or this_credit):
                    response_data.append({'data_type':'liability','account':item.name,'total':str(total)})
            else:
                long_liability+=total
                if (this_debit or this_credit):
                    response_data.append({'data_type':'long_liability','account':item.name,'total':str(total)})
        
        elif(item.account_type in ('equ')):
            total-=journal_debit['value__sum']
            total+=journal_credit['value__sum']
            drawings+=total
            if (this_debit or this_credit):
                response_data.append({'data_type':'equity','account':item.name,'total':str(total)})
    
    inventory_acc=account_inventory.objects.for_tenant(request.user.tenant).get(name="Inventory")
    inventory_closing=account_year_inventory.objects.for_tenant(request.user.tenant).get(account_inventory=inventory_acc, accounting_period=period)
    response_data.append({'data_type':'assets','account':"Closing Inventory",\
                    'total':str(inventory_closing.current_debit-inventory_closing.current_credit)})
            
    total_asset=asset+long_asset+(inventory_closing.current_debit-inventory_closing.current_credit)
    profit=get_profit_loss(request,start,end, period, sent="balance-sheet")
    total_liability=liability+long_liability+profit
    if (drawings != 0):
        response_data.append({'data_type':'total_equity','total':str(drawings)})
    response_data.append({'data_type':'total_asset','total':str(total_asset)})
    response_data.append({'data_type':'profit','total':str(profit)})
    response_data.append({'data_type':'total_liability','total':str(total_liability)})

    # print(response_data)
    return response_data
            

def get_income_expense(this_tenant, no_months):
    today=dt.date.today()
    response_data=[]
    last_date_max=today-relativedelta(months=no_months+4)
    
    #Steps: Get Accounts. Get Journals in date range. Filter journal entries of those journal in date range contianing those accounts
    #Sum the total debit & total credit to get actual data 
    all_journals=Journal.objects.for_tenant(this_tenant).filter(date__range=(last_date_max,today)).all()
    all_cogs_journals=journal_inventory.objects.for_tenant(this_tenant).filter(date__range=(last_date_max,today)).all()

    income_accounts=Account.objects.for_tenant(this_tenant).filter(account_type__in=['dirrev', 'indrev']).all()
    expense_accounts=Account.objects.for_tenant(this_tenant).filter(account_type__in=['direxp', 'indexp']).\
                    exclude(name__in=['Purchase', 'Purchase Return']).all()
    cogs_accounts=account_inventory.objects.for_tenant(this_tenant).get(name='Cost of Goods Sold')
    
    
    # print(current_income_entries['credit'])
    # print(current_expense_entries)
    # print(response_data)

    for i in range(no_months):
        last_month=today-relativedelta(months=i)
        last_month_start=last_month.replace(day=1)
        last_month_end=last_month.replace(day = calendar.monthrange(last_month.year, last_month.month)[1])

        current_journals=all_journals.filter(date__range=(last_month_start,last_month_end)).all()
        current_cogs_journals=all_cogs_journals.filter(date__range=(last_month_start,last_month_end)).all()

        current_income_entries=journal_entry.objects.filter(journal__in=current_journals,account__in=income_accounts).\
                    aggregate(debit=Sum(Case(When(transaction_type=1, then='value'),output_field=DecimalField())),\
                        credit=Sum(Case(When(transaction_type=2, then='value'),output_field=DecimalField())))
        current_expense_entries=journal_entry.objects.filter(journal__in=current_journals,account__in=expense_accounts).\
                    aggregate(debit=Sum(Case(When(transaction_type=1, then='value'),output_field=DecimalField())),\
                        credit=Sum(Case(When(transaction_type=2, then='value'),output_field=DecimalField())))

        current_COGS_entries=journal_entry_inventory.objects.filter(journal__in=current_cogs_journals,account=cogs_accounts).\
                    aggregate(debit=Sum(Case(When(transaction_type=1, then='value'),output_field=DecimalField())),\
                        credit=Sum(Case(When(transaction_type=2, then='value'),output_field=DecimalField())))
        if (current_income_entries['credit'] == None):
            current_income_entries['credit'] = 0
        if (current_income_entries['debit'] == None):
            current_income_entries['debit'] = 0
        
        if (current_expense_entries['debit'] == None):
            current_expense_entries['debit'] = 0
        if (current_expense_entries['credit'] == None):
            current_expense_entries['credit'] = 0
        
        if (current_COGS_entries['debit'] == None):
            current_COGS_entries['debit'] = 0
        if (current_COGS_entries['credit'] == None):
            current_COGS_entries['credit'] = 0

        current_month=last_month_start.month
        response_data.append({'month': calendar.month_name[current_month], 'income':current_income_entries['credit']-current_income_entries['debit'],\
                            'expense':(current_expense_entries['debit']+current_COGS_entries['debit'])-\
                            (current_expense_entries['credit']+current_COGS_entries['credit'])})

    return response_data