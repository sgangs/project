#from django.conf import settings
#from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login
from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic import TemplateView
from datetime import datetime

from school_user.forms import UserRegistrationForm,CustomerRegistrationForm
from school_user.models import User, Tenant
from school_account.models import payment_mode
from school_genadmin.models import academic_year
# from distribution_master.models import Warehouse
from .user_util import *

#landing page
class HomeView(TemplateView):
    template_name = "index.html"

def custom_login(request):
    if request.user.is_authenticated():
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
            new_tenant.email=new_user.email
            new_user.set_password(userform.cleaned_data['password'])
            with transaction.atomic():
                try:
                    new_tenant.paid=False
                    new_tenant.trail=True
                    new_tenant.registered_on=timezone.localtime(timezone.now())
                    new_tenant.save()
                    new_user.user_type="Master"
                    new_user.tenant=new_tenant
                    new_user.save()
                    i=4
                    while (i>0):
                        if (i==3):
                            create_ledger_group(new_tenant, "Stationary")
                        elif (i==3):
                            create_ledger_group(new_tenant,"Fees")
                        elif (i==2):
                            create_ledger_group(new_tenant,"Salary")
                        elif (i==1):
                            create_journal_group(new_tenant,"General")
                            create_ledger_group(new_tenant,"General")
                        i-=1
                    create_account(new_tenant,"Cash in Hand",\
						"Current Assets", "Cash in Hand account", "cash", "General")
                    payment= payment_mode()
                    payment.name="Cash"
                    payment.default="Yes"
                    payment.tenant=new_tenant
                    payment.payment_account=Account.objects.for_tenant(tenant=new_tenant).get(key="cash")
                    payment.save()
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


#This is the landignview separating different types of users
@login_required
#landing page
def landing(request):
    if (request.user.user_type == "Student"):
        return render (request, 'landing_student.html')    
    elif (request.user.user_type == "Teacher"):
        return render (request, 'landing_teacher.html')
    year=academic_year.objects.for_tenant(request.user.tenant).get(current_academic_year=True).year
    paid=fee_paid(request, year)
    total=month_fee(request, year)
    return render (request, 'landing.html', {"paid":paid,"total":total})