from decimal import Decimal
import datetime
import json
from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.utils import timezone
from school_user.models import Tenant
from school_account.models import Account, Journal, journal_entry, journal_group
from school_eduadmin.models import class_section, classstudent
from school_fees.models import student_fee, student_fee_payment
from school_student.models import Student
from school_genadmin.models import class_group
from .models import monthly_fee, monthly_fee_list, yearly_fee, yearly_fee_list
# fee_structure, fee_structure_list,
#This function is used to provide students' data for attendance/exam score entry
def create_fee_structure(request, fee_type):
    with transaction.atomic():
        try:
            this_tenant=request.user.tenant
            #create_fee_structure(request, fee_type)
            feename=request.POST.get('feename')
            fee_lists = json.loads(request.POST.get('details'))
            # months = json.loads(request.POST.get('months'))
            if (fee_type == 'Monthly'):
                fee_create=monthly_fee()
            else:
                fee_create=yearly_fee()
                month=request.POST.get('month')
                fee_create.month=month
            fee_create.name=feename
            fee_create.tenant=this_tenant
            fee_create.save()
            for data in fee_lists:
                accountid=data['account']
                amount=float(data['amount'])
                account=Account.objects.get(id=accountid)
                if (fee_type == 'Monthly'):
                    fee_list=monthly_fee_list()
                    fee_list.monthly_fee=fee_create
                else:
                    fee_list=yearly_fee_list()
                    fee_list.yearly_fee=fee_create
                fee_list.account = account
                fee_list.name = account.name
                fee_list.amount= amount                                   
                fee_list.tenant=this_tenant
                fee_list.save()
        except:
            transaction.rollback()


def view_fee_details(request):
    response_data=[]
    this_tenant=request.user.tenant
    studentid=request.POST.get('studentid')
    year=int(request.POST.get('year'))
    month=request.POST.get('month')
    student=Student.objects.for_tenant(this_tenant).get(id=studentid)
    feelist=student_fee.objects.filter(student=student).get(year=year)
    monthlyfee=feelist.monthly_fee
    monthlyfeelist=monthly_fee_list.objects.filter(monthly_fee=monthlyfee)
    paid=student_fee_payment.objects.for_tenant(this_tenant).filter(student=student,year=year,month=month).aggregate(Sum('amount'))
    try:
        yearlyfeedetails=feelist.yearly_fee.filter(month=month).all()
    except:
        yearlyfeedetails=''
    if (paid['amount__sum'] != None):
        if (paid['amount__sum'] > 0):
            response_data.append({'data_type':'Paid', 'amount':str(paid['amount__sum'])})
    for fee in monthlyfeelist:
        response_data.append({'data_type':'Monthly','id':fee.id,'name':fee.name, 'account':fee.account.id,\
            'amount':str(fee.amount)})
    try:
        for yearlyfee in yearlyfeedetails:
            yearlyfeelist=yearly_fee_list.objects.filter(yearly_fee=yearlyfee)
            for fee in yearlyfeelist:
                response_data.append({'data_type':'Yearly','id':fee.id,'name':fee.name, 'account':fee.account.id,\
                    'amount':str(fee.amount)})
    except:
        pass
    # try:
    #     fee_paid=student_fee_payment.objects.get(student=student,month=month, year=year).amount
    # except:
    #     fee_paid=0
    # response_data.append({'data_type':'Paid','amount':str(fee_paid)})
    return response_data


def view_student(request):
    response_data = []
    class_input=request.POST.get('class_selected')
    year=int(request.POST.get('year'))
    class_selected=class_section.objects.for_tenant(request.user.tenant).get(id=class_input)
    group=class_selected.classgroup
    studentlist=classstudent.objects.filter(class_section=class_selected, year=year).select_related('student')
    for student in studentlist:
        response_data.append({'data_type':'Student','id':student.student.id,'first_name':student.student.first_name, \
            'last_name':student.student.last_name,'key':student.student.key,'local_id':student.student.local_id,})
    return response_data

def save_student_payment(request):
    this_tenant=request.user.tenant
    response_data = []
    studentid=request.POST.get('studentid')
    year=int(request.POST.get('year'))
    month=request.POST.get('month')
    amount=Decimal(int(request.POST.get('amount')))
    student=Student.objects.for_tenant(this_tenant).get(id=studentid)
    student_name=student.first_name + " " + student.last_name
    feelist=student_fee.objects.for_tenant(this_tenant).get(student=student,year=year)
    monthlyfee=feelist.monthly_fee
    monthlyfeelist=monthly_fee_list.objects.filter(monthly_fee=monthlyfee)
    now=datetime.date.today()
    tz_unaware_now=datetime.datetime.strptime(str(now), "%Y-%m-%d")
    tz_aware_now=timezone.make_aware(tz_unaware_now, timezone.get_current_timezone())
    amount_paid=0
    fee_paid=0
    try:
        fee_paid=student_fee_payment.objects.for_tenant(this_tenant).filter(student=student,year=year,month=month)\
            .aggregate(Sum('amount'))        
    except:
        pass
    try:
        yearlyfeedetails=feelist.yearly_fee.filter(month=month).all()
    except:
        yearlyfeedetails=''
    with transaction.atomic():
        # try:
        for fee in monthlyfeelist:
            account=Account.objects.for_tenant(this_tenant).get(id=fee.account.id)
            this_amount=fee.amount
            amount_paid+=this_amount
            new_journal_entry(account,this_amount,this_tenant,student_name, tz_aware_now)
        for yearlyfee in yearlyfeedetails:
            yearlyfeelist=yearly_fee_list.objects.filter(yearly_fee=yearlyfee)
            for fee in yearlyfeelist:
                account=Account.objects.for_tenant(this_tenant).get(id=fee.account.id)
                this_amount=fee.amount
                amount_paid+=this_amount
                new_journal_entry(account,this_amount,this_tenant,student_name, tz_aware_now)
        if (amount_paid != amount):
            raise IntegrityError
            transaction.rollback()
        if (amount == fee_paid):
            raise IntegrityError
            transaction.rollback()
        fee_payment=student_fee_payment()
        fee_payment.student=student
        fee_payment.month=month
        fee_payment.year=year
        fee_payment.paid_on=tz_aware_now
        fee_payment.amount=amount_paid
        fee_payment.tenant=this_tenant
        fee_payment.save()
        # except:
        #     transaction.rollback()


def new_journal_entry(account, amount, this_tenant,name,tz_aware_now):
    journal=Journal()
    journal.date=tz_aware_now
    group=journal_group.objects.for_tenant(this_tenant).get(name="General")
    journal.group=group
    journal.remarks="Fees for: "+name
    journal.tenant=this_tenant
    journal.save()
    account=account
    i=1
    while (i<3):
        entry=journal_entry()
        entry.journal=journal
        if (i==1):
            entry.account=account
            entry.transaction_type="Credit"
            account.current_credit=account.current_credit+amount
            account.save()
        else:
            account=Account.objects.for_tenant(this_tenant).get(key='cash')
            entry.account=account
            account.current_debit=account.current_debit+amount
            account.save()
            entry.transaction_type="Debit"
        entry.value=amount
        entry.tenant=this_tenant
        entry.save()
        i+=1

def view_payment_details (request):
    this_tenant=request.user.tenant
    response_data = []
    studentid=request.POST.get('studentid')
    year=int(request.POST.get('year'))
    print (year)
    # month=request.POST.get('month')
    student=Student.objects.for_tenant(this_tenant).get(id=studentid)
    fee_paid=student_fee_payment.objects.for_tenant(this_tenant).filter(student=student,year=year)
    print (fee_paid)
    for fee in fee_paid:
        response_data.append({'data_type':'payment','month':fee.month, 'amount':str(fee.amount),'paid_on':fee.paid_on.isoformat()})
    return response_data