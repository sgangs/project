import json
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import render, get_object_or_404, redirect
from school_account.models import Account
from django.http import HttpResponse
from school_hr.models import staff_cadre
from school_genadmin.models import academic_year  
from school_account.models import payment_mode
from .models import *
from .create_salary import *
from .link_salary import *
from .generate_monthly_salary import *


@login_required
def salary_rules(request):
	this_tenant=request.user.tenant
	rule=basic_salary_rule.objects.for_tenant(this_tenant)
	if rule:
		return HttpResponse("Data already filled")
	else:
		pass
	accounts=Account.objects.for_tenant(request.user.tenant).filter(ledger_group__name='Salary',sub_account_type='PFERE')\
				.values('id','name')
	return render(request, 'salary/salary_rules.html', {'accounts':accounts})



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
	if request.method == 'POST':
		call_type = request.POST.get('call_type')
		if (call_type == 'generate'):
			staffid=request.POST.get('staffid')
			year=int(request.POST.get('year'))
			month=request.POST.get('month')
			try:
				data=staff_salary_payment.objects.for_tenant(this_tenant).get(staff=staffid, year=year, month=month)
				if (data):
					response_data = ['Report Already Generated']
					jsondata = json.dumps(response_data)
					return HttpResponse(jsondata)					
			except:
				pass
			response_data=generate_salary_report(request, "generation")			
		elif (call_type == 'save'):
			response_data=[]
			finalize_salary(request)
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	staffs=Teacher.objects.for_tenant(this_tenant).values('id','key','local_id','first_name','last_name')
	return render(request, 'salary/salary_generation.html', {'staffs':staffs})

@login_required
def cadre_teacher_salary_linking(request):
	this_tenant=request.user.tenant
	# group=staff_cadre.objects.for_tenant(this_tenant).filter(cadre_type='Teacher').all()
	group=staff_cadre.objects.for_tenant(this_tenant).all()
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


@login_required
def cadre_teacher_salary_update(request):
	this_tenant=request.user.tenant
	year=academic_year.objects.for_tenant(this_tenant).get(current_academic_year=True).year
	# group=cadre_default_salary.objects.for_tenant(this_tenant).filter(cadre_type='Teacher', year=year).select_related('cadre')
	group=cadre_default_salary.objects.for_tenant(this_tenant).filter(year=year).select_related('cadre')
	if request.method == 'POST':
		response_data = []
		call_type=request.POST.get('call_type')
		if (call_type == 'Salary'):
			print("We're here")
			groupid=request.POST.get('cadreid')
			print(groupid)
			group_selected = group.get(id=groupid)
			if not group_selected.yearly_salary:
				yearly=list(yearly_salary.objects.for_tenant(this_tenant).all())
			else:
				excluded_salary=yearly_salary.objects.filter(cadreDefaultSalary_yearlySalary=group_selected).all()			
				yearly=yearly_salary.objects.for_tenant(this_tenant).exclude(id__in=excluded_salary).values('id','name').all()
				for data in yearly:
					response_data.append({'data_type':'Yearly','id':data['id'], 'name':data['name']})
			if not group_selected.epfEpsEmployer:
				epsepf=epf_eps_employer.objects.for_tenant(this_tenant).values('id','name')
				for data in epsepf:
					response_data.append({'data_type':'EPSEPF','id':data['id'], 'name':data['name']})
			if not group_selected.esiEmployer:
				esi=esi_employer.objects.for_tenant(this_tenant).values('id','name')
				for data in esi:
					response_data.append({'data_type':'ESI','id':data['id'], 'name':data['name']})
			if not group_selected.edliEmployer:
				edli=edli_employer.objects.for_tenant(this_tenant).values('id','name')
				for data in edli:
					response_data.append({'data_type':'EDLI','id':data['id'], 'name':data['name']})
			employee=employee_statutory.objects.for_tenant(this_tenant).all()
			if not group_selected.epfEmployee:
				epf_employee=employee.filter(statutory_type='EPF').values('id','name')
				for data in epf_employee:
					response_data.append({'data_type':'EPFEE','id':data['id'], 'name':data['name']})
			if not group_selected.esiEmployee:
				esi_employee=employee.filter(statutory_type='ESI').values('id','name')
				response_data.append({'data_type':'ESIEE','id':data['id'], 'name':data['name']})
			print(response_data)
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'salary/existing_salary_linking.html',{'groups':group,})


@login_required
def salary_generated_list(request):
	this_tenant=request.user.tenant
	list_salary=staff_salary_payment.objects.for_tenant(this_tenant).filter(paid=False).select_related('staff')
	return render(request, 'salary/salary_generated_list.html',{'list_salary':list_salary})

@login_required
def pay_staff(request):
	this_tenant=request.user.tenant
	payment_modes=payment_mode.objects.for_tenant(this_tenant).values('id','name')
	if (request.method == 'POST'):
		response_data=[]
		payments = json.loads(request.POST.get('payments'))
		modeid = request.POST.get('modeid')
		payment_mode_selected=payment_modes.get(id=modeid)
		with transaction.atomic():
			try:
				for data in payments:
					confirm=data['confirm']
					reject=data['reject']
					if confirm:
						pay_staff(this_tenant, data['id'], payment_mode_selected)
					elif reject:
						reject_salary(this_tenant, data['id'])
			except:
				transaction.rollback()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	payments=staff_salary_payment.objects.for_tenant(this_tenant).filter(paid=False).select_related('staff')
	return render(request, 'salary/salary_payment.html',{'payments':payments,'mode':payment_modes})