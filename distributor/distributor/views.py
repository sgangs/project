import datetime as date_first
import json
from datetime import datetime
#from django.conf import settings
from django.http import HttpResponse
from django.db import IntegrityError, transaction
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login, password_reset
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, redirect
from django.utils.timezone import localtime, now
from django.views.generic import TemplateView

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from distributor_user.forms import UserRegistrationForm,CustomerRegistrationForm
from distributor_user.models import User, Tenant
from .forms import LoginForm
from distributor_account.models import accounting_period, payment_mode
from distributor_inventory.models import warehouse_valuation
from distributor_master.models import Warehouse
from distributor_sales.sales_utils import sales_day_wise, sales_raised_value, sales_collected_value
from .user_creation import *

#landing page
class HomeView(TemplateView):
    template_name = "index.html"


#Redirect authenticated users to landing page
# def Registration(request):
    # return render(request,'registration_success.html')
    
#Redirect authenticated users to landing page
def custom_login(request):
    if request.user.is_authenticated():
        # token, created = Token.objects.get_or_create(user=request.user)
        return redirect(landing)
    else:
        return login(request)
    
#registration page
def RegisterView(request):
    if request.method == 'POST':
        customerform = CustomerRegistrationForm(request.POST)
        userform = UserRegistrationForm(request.POST)
        if userform.is_valid() and customerform.is_valid():
            #Create new tenant
            new_tenant=customerform.save(commit=False)
            #Create new user
            new_user=userform.save(commit=False)
            #Validate Password
            new_user.set_password(userform.cleaned_data['password'])
            with transaction.atomic():
                try:
                    new_tenant.paid=False
                    new_tenant.trial=True
                    now_time=localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
                    new_tenant.trial_from=now_time
                    new_tenant.trial_to=now_time+date_first.timedelta(days=120)
                    new_tenant.save()
                    new_user.tenant=new_tenant
                    new_user.save()
                    #Do this after user's first login maybe.
                    warehouse=Warehouse()
                    warehouse.name="Default"
                    warehouse.address_1=new_tenant.address_1
                    warehouse.address_2=new_tenant.address_2
                    warehouse.state=new_tenant.state
                    warehouse.city=new_tenant.city
                    warehouse.pin=new_tenant.pin
                    warehouse.default=True
                    warehouse.tenant=new_tenant
                    warehouse.save()
                    valuation=warehouse_valuation()
                    valuation.warehouse=warehouse
                    valuation.tenant=new_tenant
                    valuation.save()
                    today=datetime.now()
                    if (today.month >4):
                        start_date=datetime(year=today.year, month=4, day=1)
                        end_date=datetime(year=today.year+1, month=3, day=31)
                    else:
                        start_date=datetime(year=today.year-1, month=4, day=1)
                        end_date=datetime(year=today.year, month=3, day=31)
                    period=accounting_period()
                    period.start=start_date
                    period.end=end_date
                    period.current_period=True
                    period.is_first_year=True
                    period.tenant=new_tenant
                    period.save()
                    new_ledger=create_ledger_group(new_tenant, "General")
                    
                    create_journal_group(new_tenant,"General")                            
                    create_journal_group(new_tenant,"Sales")
                    create_journal_group(new_tenant,"Purchase")
                    
                    
                    create_accountChart(new_tenant,"IGST Payments",\
                        "Tax Expense", "IGST Payment Account", "igstpay", period, new_ledger, is_first_year=True)
                    create_accountChart(new_tenant,"IGST Input",\
                        "Current Assets", "IGST Input Account", "igstin", period, new_ledger, is_first_year=True)
                    create_accountChart(new_tenant,"IGST Output",\
                        "Current Liabilities", "IGST Output Account", "igstout", period, new_ledger, is_first_year=True)
                    
                    create_accountChart(new_tenant,"SGST Payments",\
                        "Tax Expense", "SGST Payment Account", "sgstpay", period, new_ledger, is_first_year=True)
                    create_accountChart(new_tenant,"SGST Input",\
                        "Current Assets", "SGST Input Account", "sgstin", period, new_ledger, is_first_year=True)
                    create_accountChart(new_tenant,"SGST Output",\
                        "Current Liabilities", "SGST Output Account", "sgstout", period, new_ledger, is_first_year=True)
                    
                    create_accountChart(new_tenant,"CGST Payments",\
                        "Tax Expense", "CGST Payment Account", "cgstpay", period, new_ledger, is_first_year=True)
                    create_accountChart(new_tenant,"CGST Input",\
                        "Current Assets", "CGST Input Account", "cgstin", period, new_ledger, is_first_year=True)
                    create_accountChart(new_tenant,"CGST Output",\
                        "Current Liabilities", "CGST Output Account", "cgstout", period, new_ledger, is_first_year=True)
                    
                    create_accountChart(new_tenant,"VAT Payments",\
                        "Tax Expense", "VAT Payment Account", "vatpay", period, new_ledger, is_first_year=True)
                    create_accountChart(new_tenant,"VAT Input",\
                        "Current Assets", "VAT Input Account", "vatin", period, new_ledger, is_first_year=True)
                    create_accountChart(new_tenant,"VAT Output",\
                        "Current Liabilities", "VAT Output Account", "vatout", period, new_ledger, is_first_year=True)
                    
                    #This account will consider COGS return - as we store purchase value only in COGS
                    #this contra is something like purchase contra
                    create_accountChart(new_tenant,"Cost of Goods Sold Contra", "Direct Expense",\
                        "Parent COGS Contra Accounts", "cogs contra", period, new_ledger, is_first_year=True, is_contra=True)
                        #This is used to consider sales return - check if it should be expense or revenue
                    create_accountChart(new_tenant,"Sales Contra", "Direct Revenue",\
                        "Contra Sales Account", "sales contra", period, new_ledger, is_first_year=True, is_contra=True)
                        
                    create_accountChart(new_tenant,"Inventory Waste Expense", "Direct Expense",\
                        "Parent Inventory Wastage", "inventory waste", period, new_ledger, is_first_year=True, is_contra=True)
                    

                    #Purchase account only if user choses not to maintain inventory

                    # create_accountChart(new_tenant,"Purchase","Direct Expense", "Purchase Account", "purchase", period, \
                    #     new_ledger, is_first_year=True)
                    
                    cash_account=create_accountChart(new_tenant,"Cash","Current Assets", \
                        "Cash in hand account", "cash", period, new_ledger, is_first_year=True)

                    bank_account=create_accountChart(new_tenant,"Bank","Current Assets", \
                        "Bank account", "bank", period, new_ledger, is_first_year=True)

                    vendor_debit=create_accountChart(new_tenant, "Vendor Debit","Current Liabilities",\
                        "Debit Note Vendor Debit", "vd", period, new_ledger, is_first_year=True, is_contra=True)

                    customer_credit=create_accountChart(new_tenant, "Customer Credit","Current Assets",\
                        "Credit Note Customer Credit", "cc", period, new_ledger, is_first_year=True, is_contra=True)
                    
                    create_accountChart(new_tenant, "Inventory","Current Assets",\
                        "Parent Inventory Account", "inventory", period, new_ledger, is_first_year=True)
                    create_accountChart(new_tenant,"Cost of Goods Sold",\
                        "Direct Expense", "Parent COGS Accounts", "cogs", period, new_ledger, is_first_year=True)
                    
                    create_accountChart(new_tenant,"Accounts Payable",\
                        "Current Liabilities", "Parent Accounts Payable Accounts", "payable", period, new_ledger, is_first_year=True)
                    create_accountChart(new_tenant,"Accounts Receivable",\
                        "Current Assets", "Parent Accounts Receivable Accounts", "receivable",\
                        period, new_ledger, is_first_year=True)
                    create_accountChart(new_tenant,"Sales","Direct Revenue", "Parent Sales Accounts", "sales",\
                        period, new_ledger, is_first_year=True)
                    
                    dimension=create_dimension(new_tenant, "Number", "For numbers")
                    create_unit(new_tenant, dimension, "Number", "No", 1)
                    
                    dimension=create_dimension(new_tenant, "Length", "For measuring length")
                    create_unit(new_tenant, dimension, "Metre", "Mtr", 1)
                    
                    dimension=create_dimension(new_tenant, "Weight", "For measuring weight")
                    create_unit(new_tenant, dimension, "Gram", "gm", 1)
                    
                    payment= payment_mode()
                    payment.name="Cash"
                    payment.default=True
                    payment.tenant=new_tenant
                    payment.payment_account=cash_account
                    payment.save()

                    payment= payment_mode()
                    payment.name="NEFT/RTGS"
                    payment.default=False
                    payment.tenant=new_tenant
                    payment.payment_account=bank_account
                    payment.save()

                    payment= payment_mode()
                    payment.name="Cheque"
                    payment.default=False
                    payment.tenant=new_tenant
                    payment.payment_account=bank_account
                    payment.save()

                    payment= payment_mode()
                    payment.name="Vendor Debit"
                    payment.default=False
                    payment.tenant=new_tenant
                    payment.payment_account=vendor_debit
                    payment.save()

                    payment= payment_mode()
                    payment.name="Customer Credit"
                    payment.default=False
                    payment.tenant=new_tenant
                    payment.payment_account=customer_credit
                    payment.save()
                except:
                    transaction.rollback()

            return render(request,'registration_success.html')
        else:
            error = "Yes"
            return render(request, 'registration.html',{'userform': userform, \
                        'customerform': customerform,'error':error,})
    else:
        customerform = CustomerRegistrationForm()
        userform = UserRegistrationForm()

    return render(request,'registration.html', {'userform': userform, 'customerform': customerform})


#Add one more level of authentication for forgot password. Then send the mail.
def custom_password_reset(request, from_email, subject_template_name, password_reset_form):
    form = revisedPasswordResetForm()
    if request.method == 'POST':
        form = revisedPasswordResetForm(request.POST)
        if form.is_valid():
            return password_reset(request,html_email_template_name='registration/password_reset_email.html',)
            # return HttpResponse("Wow")
    else:
        form = revisedPasswordResetForm()        
    return render(request,'registration/password_reset_form.html', {'form': form})



@login_required
@api_view(['GET'],)
def landing(request):
    this_tenant=request.user.tenant
    end=date_first.date.today()
    start=end-date_first.timedelta(days=30)
    sales_daily=sales_day_wise(start, end, this_tenant)
    invoice_value=sales_raised_value(start, end, this_tenant)
    payment_value=sales_collected_value(start, end, this_tenant)
    current_year=accounting_period.objects.for_tenant(this_tenant).get(current_period=True)
    return render(request,'landing.html', {'sales_daily':json.dumps(sales_daily, cls=DjangoJSONEncoder),\
            'invoice_value':json.dumps(invoice_value, cls=DjangoJSONEncoder), \
            'payment_value':json.dumps(payment_value, cls=DjangoJSONEncoder), 'current_account':current_year})