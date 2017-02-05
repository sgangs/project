import json
from datetime import datetime as dt
import datetime

#from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login, password_reset
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic import TemplateView

from school_user.forms import UserRegistrationForm,CustomerRegistrationForm
from school_user.models import User, Tenant
from school_account.models import payment_mode, accounting_period
from school_genadmin.models import academic_year
# from distribution_master.models import Warehouse
from .user_util import *
from .forms import revisedPasswordResetForm

#landing page
class HomeView(TemplateView):
    template_name = "index.html"

#Redirect authenticated users to landing page
def custom_login(request):
    if request.user.is_authenticated():
        return redirect(landing)
    else:
        return login(request)

#Add one more level of authentication for forgot password. Then send the mail.
def custom_password_reset(request, from_email, subject_template_name, password_reset_form):
    form = revisedPasswordResetForm()
    if request.method == 'POST':
        form = revisedPasswordResetForm(request.POST)
        if form.is_valid():
            print (from_email)
            return password_reset(request)
            # return HttpResponse("Wow")
    else:
        form = revisedPasswordResetForm()        
    return render(request,'registration/password_reset_form.html', {'form': form})
    
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
                        if (i==4):
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
                    current_day=datetime.datetime.now()                    
                    if (current_day.month >4):
                        start_date=dt(year=current_day.year, month=4, day=1)
                        end_date=dt(year=current_day.year+1, month=3, day=31)
                    else:
                        start_date=dt(year=current_day.year-1, month=4, day=1)
                        end_date=dt(year=current_day.year, month=3, day=31)
                    period=accounting_period()
                    period.start=start_date
                    period.end=end_date
                    period.current_period=True
                    period.tenant=new_tenant
                    period.save()
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
    try:
        year=academic_year.objects.for_tenant(request.user.tenant).get(current_academic_year=True).year
        paid=fee_paid(request, year)
        total=month_fee(request, year)
    except:
        paid=0
        total=0
        return redirect('genadmin:new_academic_year')
    income_expense=yearly_pl(request)
    i_e_json = json.dumps(income_expense)
    return render (request, 'landing.html', {"paid":paid,"total":total, 'i_e':i_e_json})



#This is just randomly checking mail
    #subject = "Jou Jagat Bandhu"
    #message = "Joy Jagat Bandhu. /n This is my first mail."
    #from_email = settings.EMAIL_HOST_USER
    #to_list = ['sayantangangs.91@gmail.com']
    #send_mail(subject, message, from_email, to_list)