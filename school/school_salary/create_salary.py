from decimal import Decimal
import json
from django.db import IntegrityError, transaction

from school_user.models import Tenant
from school_account.models import Account
from school_teacher.models import Teacher
from .models import monthly_salary, monthly_salary_list, yearly_salary, yearly_salary_list, epf_eps_employer,\
                esi_employer,employee_statutory, edli_employer

def create_salary_structure(request, salary_type):
    with transaction.atomic():
        try:
            this_tenant=request.user.tenant
            salaryname=request.POST.get('salaryname')
            salary_lists = json.loads(request.POST.get('details'))
            if (salary_type == 'Monthly'):
                salary_create=monthly_salary()
            else:
                salary_create=yearly_salary()
                month=request.POST.get('month')
                salary_create.month=month
            salary_create.name=salaryname
            salary_create.tenant=this_tenant
            salary_create.save()
            for data in salary_lists:
                accountid=data['account']
                amount=float(data['amount'])
                account=Account.objects.for_tenant(this_tenant).get(id=accountid)
                if (salary_type == 'Monthly'):
                    salary_list=monthly_salary_list()
                    salary_list.monthly_salary=salary_create
                else:
                    salary_list=yearly_salary_list()
                    salary_list.yearly_salary=salary_create
                salary_list.account=account
                salary_list.name=account.name
                salary_list.amount=amount
                salary_list.display_payslip=data['display']
                salary_list.serial_no=data['serial_no']
                salary_list.affect_pf=data['affect_pf']
                salary_list.affect_esi=data['affect_esi']
                salary_list.affect_lop=data['affect_lop']
                salary_list.tenant=this_tenant
                salary_list.save()                
        except:
            transaction.rollback()

def create_epfeps_employer(request):
    with transaction.atomic():
        try:
            this_tenant=request.user.tenant
            structure_name=request.POST.get('structure_name')
            epfaccountid=request.POST.get('epfaccount')
            epsaccountid=request.POST.get('epsaccount')
            calculate_epf_admin=request.POST.get('epfadmin')
            if (calculate_epf_admin=='true'):
                calculate_epf_admin=True
            else:
                calculate_epf_admin=False
            rule=int(request.POST.get('rule'))
            epf_eps_ceiling=int(request.POST.get('salary_ceiling'))
            epf_predefined=int(request.POST.get('epf_predefined'))
            epf_multiplier=Decimal(request.POST.get('epf_multiplier'))
            eps_predefined=int(request.POST.get('eps_predefined'))
            eps_multiplier=Decimal(request.POST.get('eps_multiplier'))
            if (rule <1 or epf_eps_ceiling<0 or epf_predefined<0 or epf_multiplier<0 or eps_predefined<0 or eps_multiplier<0):
                raise IntegrityError
            epfaccount=Account.objects.for_tenant(this_tenant).get(id=epfaccountid)
            epsaccount=Account.objects.for_tenant(this_tenant).get(id=epsaccountid)
            salary_data=epf_eps_employer()
            salary_data.name = structure_name
            salary_data.epf_account=epfaccount
            salary_data.eps_account=epsaccount
            salary_data.calculate_epf_admin=calculate_epf_admin
            salary_data.rule=rule
            salary_data.salary_ceiling=epf_eps_ceiling
            salary_data.epf_predefined=epf_predefined
            salary_data.eps_predefined=eps_predefined
            salary_data.epf_multiplier=epf_multiplier
            salary_data.eps_multiplier=eps_multiplier
            if (calculate_epf_admin):
                epf_admin_accountid=request.POST.get('epfadminaccount')
                epf_admin_account=Account.objects.for_tenant(this_tenant).get(id=epf_admin_accountid)
                salary_data.epf_admin_account=epf_admin_account
                admin_multiplier=Decimal(request.POST.get('admin_multiplier'))
                admin_min=int(request.POST.get('admin_min'))
                admin_predefined=int(request.POST.get('admin_predefined'))
                if (admin_multiplier<0 or admin_min<0 or admin_predefined<0):
                    raise IntegrityError
                salary_data.epf_admin_multiplier=admin_multiplier
                salary_data.epf_admin_minimun=admin_min
                salary_data.epf_admin_minimun=admin_predefined
            salary_data.tenant=this_tenant
            salary_data.save()
        except:
            transaction.rollback()

def create_esi_employer(request):
    with transaction.atomic():
        try:
            this_tenant=request.user.tenant
            structure_name=request.POST.get('structure_name')
            accountid=request.POST.get('account')
            rule=int(request.POST.get('rule'))
            ceiling=int(request.POST.get('ceiling'))
            predefined=Decimal(request.POST.get('predefined'))
            multiplier=Decimal(request.POST.get('multiplier'))
            account=Account.objects.for_tenant(this_tenant).get(id=accountid)
            salary_data=esi_employer()
            salary_data.name = structure_name
            salary_data.esi_account=account
            if (rule == 1 or rule ==2 or rule ==3):
                salary_data.rule=rule
            else:
                raise IntegrityError
            if (ceiling < 0):
                raise IntegrityError
            else:
                salary_data.ceiling=ceiling
            if (ceiling < 0):
                raise IntegrityError
            else:
                salary_data.predefined=predefined
            if (ceiling < 0):
                raise IntegrityError
            else:
                salary_data.multiplier=multiplier
            salary_data.tenant=this_tenant
            salary_data.save()
        except:
            transaction.rollback()

def create_statutory_employee(request, calltype):
    with transaction.atomic():
        try:
            this_tenant=request.user.tenant
            structure_name=request.POST.get('structure_name')
            accountid=request.POST.get('account')
            rule=int(request.POST.get('rule'))
            salary_ceiling=int(request.POST.get('salary_ceiling'))
            predefined=int(request.POST.get('predefined'))
            multiplier=Decimal(request.POST.get('multiplier'))
            if (rule <1 or salary_ceiling<0 or predefined<0 or multiplier<0 ):
                raise IntegrityError
            account=Account.objects.for_tenant(this_tenant).get(id=accountid)
            salary_data=employee_statutory()
            salary_data.statutory_type = calltype
            salary_data.name = structure_name
            salary_data.account=account
            salary_data.rule=rule
            salary_data.ceiling=salary_ceiling
            salary_data.predefined=predefined
            salary_data.multiplier=multiplier
            salary_data.tenant=this_tenant
            salary_data.save()
        except:
            transaction.rollback()

def create_edli_employer(request):
    with transaction.atomic():
        try:
            this_tenant=request.user.tenant
            structure_name=request.POST.get('structure_name')
            edli_accountid=request.POST.get('edli_account')
            edliac_accountid=request.POST.get('edliac_account')
            rule=int(request.POST.get('rule'))
            salary_ceiling=int(request.POST.get('ceiling'))
            edli_multiplier=Decimal(request.POST.get('edli_multiplier'))
            edli_predefined=int(request.POST.get('edli_predefined'))
            edliac_min=int(request.POST.get('edliac_min'))
            edliac_multiplier=Decimal(request.POST.get('edliac_multiplier'))
            edliac_predefined=int(request.POST.get('edliac_predefined'))            
            if (rule <1 or salary_ceiling<0 or edli_predefined<0 or edli_multiplier<0 or 
                edliac_min<0 or edliac_multiplier<0 or edliac_predefined<0):
                raise IntegrityError
            edli_account=Account.objects.for_tenant(this_tenant).get(id=edli_accountid)
            edliac_account=Account.objects.for_tenant(this_tenant).get(id=edliac_accountid)
            salary_data=edli_employer()
            salary_data.name = structure_name
            salary_data.edli_account = edli_account
            salary_data.edliac_account = edliac_account
            salary_data.rule=rule
            salary_data.ceiling=salary_ceiling
            salary_data.edli_predefined=edli_predefined
            salary_data.edli_multiplier=edli_multiplier
            salary_data.edliac_min=edliac_min
            salary_data.edliac_predefined=edliac_predefined
            salary_data.edliac_multiplier=edliac_multiplier
            salary_data.tenant=this_tenant
            salary_data.save()
        except:
            transaction.rollback()