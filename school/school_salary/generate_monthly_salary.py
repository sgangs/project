from decimal import Decimal
import datetime
import json
from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.utils import timezone
from django.utils.timezone import localtime

from school_user.models import Tenant
from school_account.models import Account, Journal, journal_entry, journal_group
from school_teacher.models import Teacher
from .models import *

def generate_salary_report(request, sent_for=""):
    response_data={}
    this_tenant=request.user.tenant
    staffid=request.POST.get('staffid')
    year=int(request.POST.get('year'))
    month=request.POST.get('month')
    staff=Teacher.objects.for_tenant(this_tenant).get(id=staffid)
    salarylist=staff_salary_definition.objects.for_tenant(this_tenant).filter(staff=staff).get(year=year)
    monthlysalarydetails=salarylist.monthly_salary.all()
    employer_contribution=0
    gross_salary=0
    net_salary=0
    employee_deduction=0
    try:
        yearlysalarydetails=salarylist.yearly_salary.filter(month=month).all()
    except:
        yearlysalarydetails=''
    try:
        epf_eps_employer=salarylist.epfEpsEmployer
    except:
        epf_eps_employer=''
    try:
        esi_employer=salarylist.esiEmployer
    except:
        esi_employer=''
    try:
        epf_Employee=salarylist.epfEmployee
    except:
        epf_Employee=''
    try:
        esi_Employee=salarylist.esiEmployee
    except:
        esi_Employee=''
    try:
        edli=salarylist.edliEmployer
    except:
        esi_Employee=''


    for monthlysalary in monthlysalarydetails:
        monthlysalarylist=monthly_salary_list.objects.filter(monthly_salary=monthlysalary)
        for salary in monthlysalarylist:
            gross_salary+=salary.amount
            net_salary+=salary.amount
            dict_salary={'data_type':'Monthly','display_payslip':salary.display_payslip,'serial_no':salary.serial_no,\
                'affect_pf':salary.affect_pf,'affect_esi':salary.affect_esi, 'affect_gratuity':salary.affect_gratuity,\
                'amount':format(float(salary.amount),'.2f'), 'name':salary.name, 'accountid': salary.account.id}
            response_data[salary.name]=dict_salary
    pf_salary_float=0
    esi_salary_float=0
    for k,v in response_data.items():
        if v['affect_pf']:
            pf_salary_float+=float(v['amount'])
        if v['affect_esi']:
            esi_salary_float+=float(v['amount'])
    pf_salary=Decimal(pf_salary_float)
    esi_salary=Decimal(esi_salary_float)
    try:
        for yearlysalary in yearlysalarydetails:
            yearlysalarylist=yearly_salary_list.objects.filter(yearly_salary=yearlysalary)
            for salary in yearlysalarylist:
                gross_salary+=salary.amount
                net_salary+=salary.amount
                dict_salary={'data_type':'Yearly','display_payslip':salary.display_payslip,'serial_no':salary.serial_no,\
                    'affect_pf':salary.affect_pf,'affect_esi':salary.affect_esi, 'affect_gratuity':salary.affect_gratuity,\
                    'amount':format(float(salary.amount),'.2f'), 'name':salary.name, 'accountid': salary.account.id}
                response_data[salary.name]=dict_salary
    except:
        pass
    try:
        rule=epf_eps_employer.rule
        admin_multiplier=epf_eps_employer.epf_admin_multiplier
        # epf_ceiling = epf_eps_employer.epf_ceiling
        epf_predefined = epf_eps_employer.epf_predefined
        epf_multiplier = epf_eps_employer.epf_multiplier
        salary_ceiling = epf_eps_employer.salary_ceiling
        eps_predefined = epf_eps_employer.eps_predefined
        eps_multiplier = epf_eps_employer.eps_multiplier
        pf_ceiling_salary=0
        if (salary_ceiling > 0):
            if (pf_salary>salary_ceiling):
                pf_ceiling_salary=salary_ceiling
            else:
                pf_ceiling_salary=pf_salary
        else:
            pf_ceiling_salary=pf_salary
        if (rule == 1):
            eps_value=pf_ceiling_salary*eps_multiplier/100
            epf_value=(pf_salary*(epf_multiplier+eps_multiplier)/100)-eps_value
            epf_admin_charges=pf_salary*admin_multiplier/100
        elif (rule == 2):
            eps_value=pf_ceiling_salary*eps_multiplier/100
            epf_value=(pf_ceiling_salary*epf_multiplier/100)
            epf_admin_charges=pf_ceiling_salary*admin_multiplier/100
        elif (rule == 3):
            eps_value=0
            epf_value=(pf_ceiling_salary*epf_multiplier/100)
            epf_admin_charges=pf_ceiling_salary*admin_multiplier/100
        elif (rule == 4):
            eps_value=epf_eps_employer.eps_predefined
            epf_value=epf_eps_employer.epf_predefined
            epf_admin_charges=epf_eps_employer.epf_admin_predefined

        if epf_eps_employer.calculate_epf_admin:
            minimum=epf_eps_employer.epf_admin_minimun
            if (minimum>0):
                if (epf_admin_charges<minimum):
                    epf_admin_charges=minimum
        else:
            epf_admin_charges=0
        employer_contribution+=eps_value+epf_value+epf_admin_charges
        dict_salary={'data_type':'EPS-EPF','eps_value':format(float(eps_value), '.2f'), 'epf_value':format(float(epf_value), '.2f'), \
                    'epf_admin_charges':format(float(epf_admin_charges), '.2f'), 'epf_accountid':epf_eps_employer.epf_account.id,\
                    'eps_accountid': epf_eps_employer.eps_account.id}
        response_data["EPS-EPF"]=dict_salary

    except:
        pass

    try:
        rule = esi_employer.rule
        esi_ceiling = esi_employer.ceiling
        esi_predefined = esi_employer.predefined
        esi_multiplier = esi_employer.multiplier
        esi_ceiling_salary=0
        if (esi_ceiling > 0):
            if (esi_salary>esi_ceiling):
                esi_ceiling_salary = esi_ceiling
            else:
                esi_ceiling_salary = esi_salary
        else:
            esi_ceiling_salary = esi_salary
        if (rule == 1):
            esi_value = esi_ceiling_salary*esi_multiplier/100            
        elif (rule == 2):
            esi_value = esi_employer.esi_predefined
        employer_contribution+=esi_value
        dict_salary={'data_type':'ESI Employer','esi_value':format(float(esi_value),'.2f'), 'accountid':esi_employer.esi_account.id}
        response_data["ESI Employer"]=dict_salary
    except:
        pass
    try:
        rule = edli.rule
        ceiling = edli.ceiling
        edli_predefined = edli.edli_predefined
        edli_multiplier = edli.edli_multiplier
        edliac_min = edli.edliac_min
        edliac_predefined = edli.edliac_predefined
        edliac_multiplier = edli.edliac_multiplier
        if (pf_salary<ceiling):
            ceiling=pf_salary
        if (rule == 1):
            edli_value = pf_salary*edli_multiplier/100
            edliac_value = pf_salary*edliac_multiplier/100
        elif (rule == 2):
            edli_value = ceiling*edli_multiplier/100
            edliac_value = ceiling*edliac_multiplier/100
        elif (rule == 3):
            edli_value = edli_predefined
            edliac_value = edliac_predefined
        employer_contribution+=edli_value+edliac_value
        dict_salary={'data_type':'EDLI','edli_value':format(float(edli_value),'.2f'),'edliac_value':format(float(edliac_value),'.2f'),\
                    'edli_accountid': edli.edli_account.id,'edliac_accountid':edli.edliac_account.id}
        response_data["EDLI Employer"]=dict_salary
    except:
        pass
    try:
        rule = epf_Employee.rule
        ceiling = epf_Employee.ceiling
        predefined = epf_Employee.predefined
        multiplier = epf_Employee.multiplier
        if (rule == 1):
            epf_value = pf_salary*multiplier/100            
        elif (rule == 2):
            epf_value = ceiling*multiplier/100
        elif (rule == 3):
            epf_value = predefined
        net_salary-=epf_value
        employee_deduction+=epf_value
        dict_salary={'data_type':'EPF Employee','name':'EPF Contribution','amount':format(float(epf_value),'.2f'),\
            'accountid': epf_Employee.account.id}
        response_data["EPF Employee"]=dict_salary
    except:
        pass
    try:
        rule = esi_Employee.rule
        ceiling = esi_Employee.ceiling
        predefined = esi_Employee.predefined
        multiplier = esi_Employee.multiplier
        if (pf_salary<ceiling):
            ceiling=pf_salary
        if (rule == 1):
            esi_value = pf_salary*multiplier/100
        elif (rule == 2):
            esi_value = ceiling*multiplier/100
        elif (rule == 3):
            esi_value = predefined
        net_salary-=esi_value
        employee_deduction+=esi_value
        dict_salary={'data_type':'ESI Employee','name':'ESI Contribution', 'amount':format(float(esi_value),'.2f'),\
            'accountid':esi_Employee.account.id}
        response_data["ESI Employee"]=dict_salary
    except:
        pass

    dict_salary={'data_type':'Salary','employer':format(float(employer_contribution),'.2f'),'net':format(float(net_salary),'.2f'),\
                'employee':format(float(employee_deduction),'.2f'), 'gross':format(float(gross_salary), '.2f')}
    response_data["Salary"]=dict_salary
    dict_salary={'data_type':'Personal','name': staff.first_name+" "+staff.last_name, 'id':staff.local_id}
    response_data["Personal"]=dict_salary
    return response_data

def finalize_salary(request):
    this_tenant=request.user.tenant
    staffid=request.POST.get('staffid')
    staff=Teacher.objects.for_tenant(this_tenant).get(id=staffid)
    salary_generated=generate_salary_report(request, "data")
    #After the data load for sanity check, we get the sata from API
    gross = Decimal(request.POST.get('gross'))
    print(gross)
    net = Decimal(request.POST.get('net'))
    employee = Decimal(request.POST.get('employee'))
    employer = Decimal(request.POST.get('employer'))
    month = request.POST.get('month')
    year = request.POST.get('year')
    monthly_data = json.loads(request.POST.get('monthly'))
    yearly_data = json.loads(request.POST.get('yearly'))
    deduction = json.loads(request.POST.get('deduction'))
    epf_employer = request.POST.get('epf_employer')
    eps_employer = request.POST.get('eps_employer')
    epfac = request.POST.get('epfac')
    esi_employer = request.POST.get('esi_employer')
    edli = request.POST.get('edli')
    edliac = request.POST.get('edliac')
    epf_employee = request.POST.get('epf_employee')
    esi_employee = request.POST.get('esi_employee')
    if (gross < 0):
        print(gross)
        raise IntegrityError
    with transaction.atomic():
        try:
            payment=staff_salary_payment()
            payment.staff=staff
            payment.year=year
            payment.month=month
            payment.gross=Decimal(gross)
            payment.net=Decimal(net)
            payment.employee_deduction=Decimal(employee)
            payment.employer_contribution=Decimal(employer)
            payment.tenant=this_tenant
            payment.save()
            for key,value in salary_generated.items():
                if (value['data_type'] =='EDLI'):
                    payment_list=salary_payment_list()
                    payment_list.salary_payment=payment
                    payment_list.list_type='EDLI'
                    payment_list.display_payslip=False
                    payment_list.salary_name='EDLI Contribution'
                    payment_list.account=Account.objects.for_tenant(this_tenant).get(id=value['edli_accountid'])
                    payment_list.amount=Decimal(edli)
                    payment_list.tenant=this_tenant
                    payment_list.save()
                    payment_list=salary_payment_list()
                    payment_list.salary_payment=payment
                    payment_list.list_type='EDLIAC'
                    payment_list.display_payslip=False
                    payment_list.salary_name='EDLI Administrative Charges'
                    payment_list.account=Account.objects.for_tenant(this_tenant).get(id=value['edliac_accountid'])
                    payment_list.amount=Decimal(edliac)
                    payment_list.tenant=this_tenant
                    payment_list.save()
                elif (value['data_type']=='EPS-EPF'):
                    payment_list=salary_payment_list()
                    payment_list.salary_payment=payment
                    payment_list.list_type='EPFER'
                    payment_list.display_payslip=False
                    payment_list.salary_name='EPF Employer'
                    payment_list.account=Account.objects.for_tenant(this_tenant).get(id=value['epf_accountid'])
                    payment_list.amount=Decimal(epf_employer)
                    payment_list.tenant=this_tenant
                    payment_list.save()
                    if (float(value['eps_value'])>0):
                        payment_list=salary_payment_list()
                        payment_list.salary_payment=payment
                        payment_list.list_type='ESIER'
                        payment_list.display_payslip=False
                        payment_list.salary_name='ESI Employer'
                        payment_list.account=Account.objects.for_tenant(this_tenant).get(id=value['eps_accountid'])
                        payment_list.amount=Decimal(eps_employer)
                        payment_list.tenant=this_tenant
                        payment_list.save()
                    if (float(value['epf_admin_charges'])>0):
                        payment_list=salary_payment_list()
                        payment_list.salary_payment=payment
                        payment_list.list_type='EPFAC'
                        payment_list.display_payslip=False
                        payment_list.salary_name='EPF Administrative Charges'
                        payment_list.account=Account.objects.for_tenant(this_tenant).get(id=value['epf_accountid'])
                        payment_list.amount=Decimal(edli)
                        payment_list.tenant=this_tenant
                        payment_list.save()
                elif (value['data_type'] == 'ESI Employer'):
                    payment_list=salary_payment_list()
                    payment_list.salary_payment=payment
                    payment_list.list_type='ESIER'
                    payment_list.display_payslip=False
                    payment_list.salary_name='ESI Employer'
                    payment_list.account=Account.objects.for_tenant(this_tenant).get(id=value['accountid'])
                    payment_list.amount=Decimal(esi_employer)
                    payment_list.tenant=this_tenant
                    payment_list.save()
                elif (value['data_type'] == 'ESI Employee'):
                    payment_list=salary_payment_list()
                    payment_list.salary_payment=payment
                    payment_list.list_type='ESIEE'
                    payment_list.display_payslip=False
                    payment_list.salary_name='ESI Employee'
                    payment_list.account=Account.objects.for_tenant(this_tenant).get(id=value['accountid'])
                    payment_list.amount=Decimal(esi_employee)
                    payment_list.tenant=this_tenant
                    payment_list.save()
                elif (value['data_type'] == 'EPF Employee'):
                    payment_list=salary_payment_list()
                    payment_list.salary_payment=payment
                    payment_list.list_type='EPFEE'
                    payment_list.display_payslip=False
                    payment_list.salary_name='EPF Employee'
                    payment_list.account=Account.objects.for_tenant(this_tenant).get(id=value['accountid'])
                    payment_list.amount=Decimal(epf_employee)
                    payment_list.tenant=this_tenant
                    payment_list.save()
                elif (value['data_type'] == 'Monthly'):
                    for data in monthly_data:
                        if (data['name'] == value['name']):
                            payment_list=salary_payment_list()
                            payment_list.salary_payment=payment
                            payment_list.list_type='Monthly'
                            payment_list.display_payslip=value['display_payslip']
                            payment_list.serial_no=value['serial_no']
                            payment_list.salary_name='Monthly Data'
                            payment_list.account=Account.objects.for_tenant(this_tenant).get(id=value['accountid'])
                            payment_list.amount=Decimal(data['amount'])
                            payment_list.tenant=this_tenant
                            payment_list.save()
                elif (value['data_type'] == 'Yearly'):
                    for data in monthly_data:
                        if (data['name'] == value['name']):
                            payment_list=salary_payment_list()
                            payment_list.salary_payment=payment
                            payment_list.list_type='Yearly'
                            payment_list.display_payslip=value['display_payslip']
                            payment_list.serial_no=value['serial_no']
                            payment_list.salary_name='Yearly Data'
                            payment_list.account=Account.objects.for_tenant(this_tenant).get(id=value['accountid'])
                            payment_list.amount=Decimal(data['amount'])
                            payment_list.tenant=this_tenant
                            payment_list.save()
                elif (value['data_type'] == 'Deduction'):
                    for data in monthly_data:
                        if (data['name'] == value['name']):
                            payment_list=salary_payment_list()
                            payment_list.salary_payment=payment
                            payment_list.list_type='Deduction'
                            payment_list.display_payslip=value['display_payslip']
                            payment_list.serial_no=value['serial_no']
                            payment_list.salary_name='Deduction'
                            payment_list.account=Account.objects.for_tenant(this_tenant).get(id=value['accountid'])
                            payment_list.amount=Decimal(data['amount'])
                            payment_list.tenant=this_tenant
                            payment_list.save()
        except:
            transaction.rollback()

def pay_staff(this_tenant, salary_id, mode):
    salary=staff_salary_payment.objects.for_tenant(this_tenant).get(id=salary_id)
    staff_name=salary.staff.first_name+" "+salary.staff.last_name
    salary_lists=salary_payment_list.objects.filter(salary_payment=salary)
    now=datetime.date.today()
    tz_unaware_now=datetime.datetime.strptime(str(now), "%Y-%m-%d")
    tz_aware_now=timezone.make_aware(tz_unaware_now, timezone.get_current_timezone())
    with transaction.atomic():
        try:
            salary_journal_entry(this_tenant, salary_lists, staff_name, tz_aware_now, mode, \
                salary.gross, salary.employee_deduction, salary.employer_contribution)
            salary.paid_on=tz_aware_now
            salary.paid=True
            salary.save()
        except:
            transaction.rollback()


def salary_journal_entry(this_tenant, salary_lists,name, tz_aware_now, mode, gross, employee_stat, employer_stat):
    journal=Journal()
    journal.date=tz_aware_now
    group=journal_group.objects.for_tenant(this_tenant).get(name="General")
    journal.group=group
    journal.remarks="Salary for for: "+name
    journal.tenant=this_tenant
    journal.save()
    #Take care of journal entries related to salary (Monthly, yearly, employee & employer contributions)
    for item in salary_lists:    
        entry=journal_entry()
        entry.journal=journal
        account=Account.objects.for_tenant(this_tenant).get(id=item.account.id)
        entry.account=account
        if (item.list_type == "Monthly" or item.list_type=="Yearly"):
            entry.transaction_type="Debit"
            account.current_debit=account.current_debit+item.amount
        else:
            entry.transaction_type="Credit"
            account.current_credit=account.current_credit+item.amount
        account.save()
        entry.value=item.amount
        entry.tenant=this_tenant
        entry.save()
    i=1
    while (i<3):
        entry=journal_entry()
        entry.journal=journal
        #Salary Payment
        if (i==1):
            account=Account.objects.for_tenant(this_tenant).get(id=mode.payment_account.id)
            entry.transaction_type="Credit"
            account.current_credit=account.current_credit+(gross - employee_stat)
            entry.value=(gross - employee_stat)
        #Employer Liability Expense
        elif (i==2):
            accountid=basic_salary_rule.objects.get(tenant=this_tenant).employer_contribution_expense.id
            account=Account.objects.for_tenant(this_tenant).get(id=accountid)
            entry.transaction_type="Debit"
            account.current_debit=account.current_debit+(employer_stat)
            entry.value=(gross - employer_stat)
        entry.account=account  
        account.save() 
        entry.tenant=this_tenant
        entry.save()
        i+=1

def reject_salary(this_tenant, salary_id):
    salary=staff_salary_payment.objects.for_tenant(this_tenant).get(id=salary_id)
    