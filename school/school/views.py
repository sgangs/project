import json
from datetime import datetime as dt
from datetime import date
import datetime
from calendar import monthrange
#from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login, password_reset
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect
from django.utils import timezone

from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import get_template
from django.conf import settings

from school_user.forms import UserRegistrationForm,CustomerRegistrationForm
from school_user.models import User, Tenant
from school_account.models import payment_mode, accounting_period
from school_classadmin.models import Attendance
from school_genadmin.models import academic_year, annual_calender
from school_teacher.models import Teacher
from school_student.models import Student
from school_hr.models import teacher_attendance
from .user_util import *
from .teacher_landing import *
from .forms import revisedPasswordResetForm, LoginForm

#landing page - www.twchassisto.com/school
def home(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        subject_input = request.POST.get('subject')
        body = request.POST.get('body')
        response_data=[]
        if (len(first_name)>2 and len(last_name)>2 and len(email)>5 and len(contact)>8 and len(subject_input)>3 and len(body)>5):
            try:
                from_email = settings.EMAIL_HOST_USER
                to_email = 'support@techassisto.com'
                subject = "Customer Contact: "+subject_input
                template = get_template('registration/contact_form_email.html')
                context = Context({'first_name': first_name, 'last_name': last_name, 'email': email, 'contact': contact, 'body': body})
                content = template.render(context)
                msg = EmailMessage(subject, content, from_email, to=[to_email])
                msg.send(fail_silently=False)
                response_data="Success"
            except:
                response_data="Fail"
        else:
            response_data="Fail"
        jsondata = json.dumps(response_data)
        return HttpResponse(jsondata)
    return render(request,'index.html')


def edit_tenant_settings(request):
    this_tenant=request.user.tenant
    if request.method == 'POST':
        name = request.POST.get('name')
        number = request.POST.get('affiliation_number')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        body = request.POST.get('body')
        # response_data=[]
        # if (len(first_name)>2 and len(last_name)>2 and len(email)>5 and len(contact)>8 and len(subject_input)>3 and len(body)>5):
        #     try:
        #         from_email = settings.EMAIL_HOST_USER
        #         to_email = 'support@techassisto.com'
        #         subject = "Customer Contact: "+subject_input
        #         template = get_template('registration/contact_form_email.html')
        #         context = Context({'first_name': first_name, 'last_name': last_name, 'email': email, 'contact': contact, 'body': body})
        #         content = template.render(context)
        #         msg = EmailMessage(subject, content, from_email, to=[to_email])
        #         msg.send(fail_silently=False)
        #         response_data="Success"
        #     except:
        #         response_data="Fail"
        # else:
        #     response_data="Fail"
        # jsondata = json.dumps(response_data)
        # return HttpResponse(jsondata)
    return render(request,'index.html', {'tenant':this_tenant})


#Redirect authenticated users to landing page
def custom_login(request):
    if request.user.is_authenticated():
        return redirect(landing)
    else:
        # print (request.SESSION['login_tries'])
        return login(request, authentication_form=LoginForm)
        
#Add one more level of authentication for forgot password. Then send the mail.
def custom_password_reset(request, from_email, subject_template_name, password_reset_form):
    form = revisedPasswordResetForm()
    if request.method == 'POST':
        form = revisedPasswordResetForm(request.POST)
        if form.is_valid():
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
                    create_leave_type("Loss of Pay", "lop", "LOP", new_tenant)
                    create_account(new_tenant,"Cash in Hand",\
                        "Current Assets", "Cash in Hand account", "cash", "General")
                    payment= payment_mode()
                    payment.name="Cash"
                    payment.default=True
                    payment.tenant=new_tenant
                    payment.payment_account=Account.objects.for_tenant(tenant=new_tenant).get(key="cash")
                    payment.save()
                    current_day=dt.now()                    
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
                    create_account_year(new_tenant,"cash", period)
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
    this_tenant=request.user.tenant
    current_day=''
    current_day=dt.now()
    start=dt(year=current_day.year, month=current_day.month, day=1)
    end=dt(year=current_day.year, month=current_day.month, day=(monthrange(current_day.year,current_day.month)[1]))
    try:
        events=annual_calender.objects.for_tenant(this_tenant).filter(date__range=(start,end))
    except:
        pass
    if (request.user.user_type == "Student"):
        return render (request, 'landing_student.html', {"events":events,})    
    elif (request.user.user_type == "Teacher"):
        teacher=Teacher.objects.get(user=request.user)
        year=academic_year.objects.for_tenant(this_tenant).get(current_academic_year=True).year
        class_teacher=get_class_teacher(request, teacher, year, this_tenant)
        subject_teacher=get_subject_teacher(request, teacher, year, this_tenant)
        attendance=json.dumps(staff_attendance_number(request, teacher, this_tenant))
        return render (request, 'landing_teacher.html', {"attendance":attendance,"events":events, \
                    'classes': class_teacher, 'subjects':subject_teacher})
    try:
        year=academic_year.objects.for_tenant(this_tenant).get(current_academic_year=True).year
        paid=fee_paid(request, year)
        total=month_fee(request, year)
        staff_list=Teacher.objects.for_tenant(this_tenant).all()
        student_list=Student.objects.for_tenant(this_tenant).all()
        staffs=staff_list.filter(dob__month=current_day.month,dob__day=current_day.day)
        today=date.today()
        try:
            students_present=Attendance.objects.for_tenant(this_tenant).filter(date=today, ispresent=True).count()
        except:
            students_present=0
        try:
            staffs_present=teacher_attendance.objects.for_tenant(this_tenant).filter(date=today, ispresent=True).count()
        except:
            staffs_present=0
        total_staffs=staff_list.count()
        if (total_staffs != 0):
            percent_staff=round(staffs_present/total_staffs*100)
        else:
            percent_staff=100
        total_students=student_list.count()
        if (total_students != 0):
            percent_student=round(students_present/total_students*100)
        else:
            percent_student=100
    except:
        paid=0
        total=0
        try:
            year=academic_year.objects.for_tenant(this_tenant).get(current_academic_year=True).year
            return render (request, 'error/500.html')
        except:
            return redirect('genadmin:new_academic_year')
    income_expense=yearly_pl(request)
    i_e_json = json.dumps(income_expense)
    return render (request, 'landing.html', {"paid":paid,"events":events,"staffs":staffs,"total":total, 'i_e':i_e_json, \
        'total_staffs': total_staffs, 'staffs_present':staffs_present, 'percent_staff':percent_staff,\
        'total_students':total_students, 'students_present':students_present,'percent_student':percent_student})

#400 error
def bad_request(request):
    return render (request, 'error/400.html')

#403 error
def permission_denied(request):
    return render (request, 'error/403.html')

#404 error
def page_not_found(request):
    return render (request, 'error/404.html')

#500 error
def server_error(request):
    return render (request, 'error/500.html')