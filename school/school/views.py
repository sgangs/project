#from django.conf import settings
#from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import render
from django.views.generic import TemplateView
from datetime import datetime

from school_user.forms import UserRegistrationForm,CustomerRegistrationForm
from school_user.models import User, Tenant
# from distribution_accounts.models import accountChart, paymentMode, journalGroup, accountingPeriod
# from distribution_master.models import Warehouse
# from .user_creation import create_journal_group, create_accountChart, create_dimension

#landing page
class HomeView(TemplateView):
    template_name = "index.html"
    
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
                    new_tenant.save()
                    new_user.tenant=new_tenant
                    new_user.save()
            #         warehouse=Warehouse()
            #         warehouse.key="master"
            #         warehouse.address=new_tenant.address
            #         warehouse.default="Yes"
            #         warehouse.tenant=new_tenant
            #         warehouse.save()
            #         today=datetime.now()
            #         if (today.month >4):
            #             start_date=datetime(year=today.year, month=4, day=1)
            #             end_date=datetime(year=today.year+1, month=3, day=31)
            #         else:
            #             start_date=datetime(year=today.year-1, month=4, day=1)
            #             end_date=datetime(year=today.year, month=3, day=31)
            #         period=accountingPeriod()
            #         period.start=start_date
            #         period.end=end_date
            #         period.key="First"
            #         period.current_period='Yes'
            #         period.tenant=new_tenant
            #         period.save()
            #         i=7
            #         while (i>0):
            #             if (i==7):
            #                 create_journal_group(new_tenant,"Credit Note")
            #             elif (i==6):
            #                 create_journal_group(new_tenant,"Debit Note")
            #             elif (i==5):
            #                 create_journal_group(new_tenant,"Miscellaneous")
            #             elif (i==4):
            #                 create_journal_group(new_tenant,"Sales Invoice")
            #             elif (i==3):
            #                 create_journal_group(new_tenant,"Purchase Invoice")
            #             elif (i==2):
            #                 create_journal_group(new_tenant,"Sales Collection")
            #             elif (i==1):
            #                 create_journal_group(new_tenant,"Purchase Collection")
            #             i-=1
            #         i=9
            #         while (i>0):
            #             #This account is to consider inventory wasted
            #             if (i==9):
            #                 create_accountChart(new_tenant,"Inventory Wastage",\
            #                     "Expense", "Inventory Wastage Account", "inventory wastage")
            #             #This accont will consider COGS return - as we store purchase value only in COGS
            #             #this contra is something like purchase contra
            #             elif (i==8):
            #                 create_accountChart(new_tenant,"Cost of Goods Sold Contra",\
            #                     "Expense", "Parent COGS Contra Accounts", "cogs contra")
            #             #This is used to consider sales return
            #             elif (i==7):
            #                 create_accountChart(new_tenant,"Sales Contra",\
            #                     "Revenue", "Contra Sales Account", "sales contra")
            #             #Rest of these accounts are general accounts.
            #             elif (i==6):
            #                 create_accountChart(new_tenant,"Cash","Assets", "Parent Cash Accounts", "cash")
            #             elif (i==5):
            #                 create_accountChart(new_tenant,\
            #                     "Inventory","Assets", "Parent Inventory Account", "inventory")
            #             elif (i==4):
            #                 create_accountChart(new_tenant,"Cost of Goods Sold",\
            #                     "Expense", "Parent COGS Accounts", "cogs")
            #             elif (i==3):
            #                 create_accountChart(new_tenant,"Accounts Payable",\
            #                     "Liabilities", "Parent Accounts Payable Accounts", "acc pay")
            #             elif (i==2):
            #                 create_accountChart(new_tenant,"Accounts Receivable",\
            #                     "Assets", "Parent Accounts Receivable Accounts", "acc rec")
            #             elif (i==1):
            #                 create_accountChart(new_tenant,"Sales","Revenue", "Parent Sales Accounts", "sales")
            #             i=i-1
            #         i=3
            #         while (i>0):
            #             if (i==3):
            #                 create_dimension(new_tenant, "Number", "For numbers")
            #             if (i==2):
            #                 create_dimension(new_tenant, "Length", "For measuring length")
            #             if (i==1):
            #                 create_dimension(new_tenant, "Weight", "For measuring weight")
            #             i=i-1
            #         payment= paymentMode()
            #         payment.name="Cash"
            #         payment.default="Yes"
            #         payment.tenant=new_tenant
            #         payment.payment_account=accountChart.objects.for_tenant(tenant=new_tenant).get(key__exact="cash")
            #         payment.save()
                except:
                    transaction.rollback()

            return render(request,'registration_success.html')
        else:
            error = "Yes"
            return render(request, 'registration.html' , {'userform': userform, \
                        'customerform': customerform, 'error':error, })
    else:
        customerform = CustomerRegistrationForm()
        userform = UserRegistrationForm()

    return render(request,'registration.html', {'userform': userform, 'customerform': customerform})


@login_required
#landing page
def landing(request):
    return render (request, 'landing.html')