import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from school_account.models import Account
from django.http import HttpResponse
from school_hr.models import staff_cadre
from .models import *
from .create_salary import *
from .link_salary import *
from .generate_monthly_salary import *


@login_required
def salary_structure_creation(request, input_type):
	accountlist=Account.objects.for_tenant(request.user.tenant).filter(ledger_group__name='Salary').all()
	accounts=[]
	for account in accountlist:
		accounts.append({'data_type':'Accounts','id':account.id,'name':account.name})
	if request.method == 'POST':
		response_data = []
		create_salary_structure(request, input_type)
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	jsondata = json.dumps(accounts)
	return render(request, 'salary/salary_structure.html', {'accounts':jsondata, 'salary_type':input_type})

@login_required
def epf_eps_structure_creation(request):
	accounts=Account.objects.for_tenant(request.user.tenant).filter(ledger_group__name='Salary').values('id','name')
	if request.method == 'POST':
		response_data = []
		create_epfeps_employer(request)
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'salary/epf_eps_structure.html', {'accounts':accounts})

@login_required
def epf_employee_creation(request):
	accounts=Account.objects.for_tenant(request.user.tenant).filter(ledger_group__name='Salary').values('id','name')
	if request.method == 'POST':
		response_data = []
		create_statutory_employee(request, "EPF")
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'salary/epf_employee.html', {'accounts':accounts})

@login_required
def esi_employee_creation(request):
	accounts=Account.objects.for_tenant(request.user.tenant).filter(ledger_group__name='Salary').values('id','name')
	if request.method == 'POST':
		response_data = []
		create_statutory_employee(request, "ESI")
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'salary/esi_employee.html', {'accounts':accounts})

@login_required
def esi_structure_creation(request):
	accounts=Account.objects.for_tenant(request.user.tenant).filter(ledger_group__name='Salary').values('id','name')
	if request.method == 'POST':
		response_data = []
		create_esi_employer(request)
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'salary/esi_structure.html', {'accounts':accounts})
	

@login_required
def edli_admin_structure_creation(request):
	accounts=Account.objects.for_tenant(request.user.tenant).filter(ledger_group__name='Salary').values('id','name')
	if request.method == 'POST':
		response_data = []
		create_edli_employer(request)
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'salary/edli_admin_structure.html', {'accounts':accounts})

@login_required
def salary_generation(request):
	this_tenant=request.user.tenant
	staffs=Teacher.objects.for_tenant(this_tenant)
	if request.method == 'POST':
		call_type = request.POST.get('call_type')
		if (call_type == 'generate'):
			staffid=request.POST.get('staffid')
			year=int(request.POST.get('year'))
			month=request.POST.get('month')
			staff=staffs.get(id=staffid)
			try:
				data=staff_salary_payment.objects.for_tenant(this_tenant).get(staff=staff, year=year, month=month)
				if (data):
					response_data = ['Report Already Generated']
					jsondata = json.dumps(response_data)
					return HttpResponse(jsondata)
					
			except:
				response_data=generate_salary_report(request, "generation")			
		elif (call_type == 'save'):
			response_data=[]
			finalize_salary(request)
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'salary/salary_generation.html', {'staffs':staffs})

@login_required
#For adding new entry for fees structure
def cadre_teacher_salary_linking(request):
	this_tenant=request.user.tenant
	group=staff_cadre.objects.for_tenant(this_tenant).filter(cadre_type='Teacher').all()
	monthly=monthly_salary.objects.for_tenant(this_tenant).all()
	yearly=yearly_salary.objects.for_tenant(this_tenant).all()
	epsepf=epf_eps_employer.objects.for_tenant(this_tenant).all()
	esi=esi_employer.objects.for_tenant(this_tenant).all()
	edli=edli_employer.objects.for_tenant(this_tenant).all()
	employee=employee_statutory.objects.for_tenant(this_tenant).all()
	epf_employee=employee.filter(statutory_type='EPF')
	esi_employee=employee.filter(statutory_type='ESI')
	# yearly=yearly_salary.objects.for_tenant(request.user.tenant).all()	
	if request.method == 'POST':
		response_data = []
		link_cadre_salary(request, "Teacher")
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'salary/salary_linking.html',{'groups':group, 'monthly_salary':monthly, 'yearly_salary':yearly,
				'epsepf_salary':epsepf, 'esi_salary':esi,'edli':edli,'epf_employee':epf_employee, 'esi_employee':esi_employee})

