from decimal import Decimal
import json
from django.db import IntegrityError, transaction
from school_user.models import Tenant
from school_account.models import Account
from school_teacher.models import Teacher
from school_hr.models import staff_cadre, staff_cadre_linking
from .models import monthly_salary, monthly_salary_list, yearly_salary, yearly_salary_list, epf_eps_employer,\
                esi_employer,employee_statutory, cadre_default_salary, staff_salary_definition, edli_employer


def link_cadre_salary(request, cadre_type):
    with transaction.atomic():
        try:
            #getting data and sending for staff link
            this_tenant=request.user.tenant
            cadre_input=request.POST.get('cadre')
            monthly_salary_input=request.POST.get('monthly_salary')
            yearly_salary_input = json.loads(request.POST.get('yearly_salary'))
            year=request.POST.get('year')
            epsepf_input=request.POST.get('epsepf')
            epf_employee_input=request.POST.get('epf_employee')
            esi_employer_input=request.POST.get('esi_employer')
            esi_employee_input=request.POST.get('esi_employee')
            edli_employer_input=request.POST.get('edli_employer')
            monthly=monthly_salary.objects.for_tenant(this_tenant).get(id=monthly_salary_input)
            try:
                epf_eps=epf_eps_employer.objects.for_tenant(this_tenant).get(id=epsepf_input)
            except:
                pass
            try:
                epf_employee=employee_statutory.objects.for_tenant(this_tenant).filter(statutory_type="EPF").get(id=epf_employee_input)
            except:
                pass
            try:
                esi=esi_employer.objects.for_tenant(this_tenant).get(id=esi_employer_input)
            except:
                pass
            try:
                esi_employee=employee_statutory.objects.for_tenant(this_tenant).filter(statutory_type="ESI").get(id=esi_employee_input)
            except:
                pass
            try:
                edli=edli_employer.objects.for_tenant(this_tenant).get(id=edli_employer_input)
            except:
                pass
            cadre=staff_cadre.objects.for_tenant(this_tenant).get(id=cadre_input)
            staffs=staff_cadre_linking.objects.for_tenant(this_tenant).filter(cadre=cadre, cadre_type=cadre_type, year=year)
            #saving cadre link
            cadre_link=cadre_default_salary()
            cadre_link.cadre=cadre
            cadre_link.cadre_type=cadre_type
            try:
                cadre_link.epfEpsEmployer=epf_eps
            except:
                epf_eps=''
            try:
                cadre_link.esiEmployer=esi
            except:
                esi=''
            # try:
            cadre_link.esiEmployee=esi_employee
            # except:
            #     esi_employee=''
            try:
                cadre_link.epfEmployee=epf_employee
            except:
                epf_employee=''
            try:
                cadre_link.edliEmployer=edli
            except:
                edli=''
            cadre_link.year=year
            cadre_link.tenant=this_tenant
            cadre_link.save()
            cadre_link.monthly_salary.add(monthly)
            for salary in yearly_salary_input:
                salaryid=salary['salary_id']
                yearlysalary=yearly_salary.objects.get(id=int(salaryid))
                cadre_link.yearly_salary.add(yearlysalary)
            link_staff_salary(this_tenant, year, staffs, cadre_type, monthly, 
                    yearly_salary_input, epf_eps, epf_employee, esi, esi_employee, edli)
        except:
            transaction.rollback()

def link_staff_salary(this_tenant, year, staffs, cadre_type, monthly, yearly_salary_input,
                     epf_eps='', epf_employee='', esi='', esi_employee='', edli=''):
    for item in staffs:
        staff_selected=Teacher.objects.for_tenant(this_tenant).get(staffCadreLinking_hr_teacher_teacher=item)
        staff_link=staff_salary_definition()
        staff_link.staff=staff_selected
        staff_link.staff_type=cadre_type
        if (epf_eps != ''):
            staff_link.epfEpsEmployer=epf_eps
        if (esi != ''):
            staff_link.esiEmployer=esi
        if (esi_employee != ''):
            staff_link.esiEmployee=esi_employee
        if (epf_employee != ''):
            staff_link.epfEmployee=epf_employee
        if (edli != ''):
            staff_link.edliEmployer=edli
        staff_link.year=year
        staff_link.tenant=this_tenant
        staff_link.save()
        staff_link.monthly_salary.add(monthly)
        for salary in yearly_salary_input:
            salaryid=salary['salary_id']
            yearlysalary=yearly_salary.objects.get(id=int(salaryid))
            staff_link.yearly_salary.add(yearlysalary)