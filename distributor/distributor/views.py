#from django.conf import settings
#from django.http import HttpResponse, Http404
from django.db import IntegrityError, transaction
from django.shortcuts import render
from django.views.generic import TemplateView

from distribution_user.forms import UserRegistrationForm,CustomerRegistrationForm
from distribution_user.models import User, Tenant

from distribution_accounts.models import accountChart



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
                    i=6
                    while (i>0):
                        account=accountChart()
                        if (i==6):
                            account.name="Cash"
                            account.account_type="Assets"
                            account.remarks="Parent Cash Accounts"
                            account.key="cash"
                        if (i==5):
                            account.name="Inventory"
                            account.account_type="Assets"
                            account.remarks="Parent Inventory Account"
                            account.key="inventory"
                        if (i==4):
                            account.name="Cost of Goods Sold"
                            account.account_type="Expense"
                            account.remarks="Parent COGS Accounts"
                            account.key="cogs"
                        if (i==3):
                            account.name="Accounts Payable"
                            account.account_type="Liabilities"
                            account.remarks="Parent Accounts Payable Accounts"
                            account.key="acc pay"
                        if (i==2):
                            account.name="Accounts Receivable"
                            account.account_type="Assets"
                            account.remarks="Parent Accounts Receivable Accounts"
                            account.key="acc rec"
                        if (i==1):
                            account.name="Sales"
                            account.account_type="Revenue"
                            account.remarks="Parent Sales Accounts"
                            account.key="sales"
                        account.tenant=new_tenant
                        account.save()
                        i=i-1
                except:
                    transaction.rollback()

            return render(request,'registration_success.html')
        else:
             return render(request, 'registration.html' , {'userform': userform, 'customerform': customerform})
    else:
        customerform = CustomerRegistrationForm()
        userform = UserRegistrationForm()

    return render(request,'registration.html', {'userform': userform, 'customerform': customerform})

