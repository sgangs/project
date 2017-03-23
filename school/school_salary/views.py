import json
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
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

from school.user_util import user_passes_test_custom
from app_control.view_control import allow_admincontrol


@login_required
#This is the salary rule. Rules are: Salary cycle. 
#This view is debatable - for who can access it
def salary_rules(request):
	this_tenant=request.user.tenant
	try:
		rule=basic_salary_rule.objects.for_tenant(this_tenant)
	except:
		pass
	if rule:
		return redirect("salary:salary_payment")
	else:
		pass
	accounts=Account.objects.for_tenant(request.user.tenant).filter(ledger_group__name='Salary',sub_account_type='PFERE')\
				.values('id','name')
	if request.method == 'POST':
		days = request.POST.get('days')
		start = request.POST.get('start')
		end = request.POST.get('end')
		pay = request.POST.get('pay')
		accountid = request.POST.get('account')
		account=Account.objects.for_tenant(this_tenant).get(id=accountid)
		salary_rule=basic_salary_rule()
		salary_rule.working_days=days
		salary_rule.salary_cycle_start=start
		salary_rule.salary_cycle_end=end
		salary_rule.salary_cycle_payment=pay
		salary_rule.employer_contribution_expense=account
		salary_rule.tenant=this_tenant
		salary_rule.save()
		response_data=[]
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'salary/salary_rules.html', {'accounts':accounts})



@login_required
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
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
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
def epf_eps_structure_creation(request):
	accounts=Account.objects.for_tenant(request.user.tenant).filter(ledger_group__name='Salary').values('id','name')
	if request.method == 'POST':
		response_data = []
		create_epfeps_employer(request)
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'salary/epf_eps_structure.html', {'accounts':accounts})

@login_required
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
def epf_employee_creation(request):
	accounts=Account.objects.for_tenant(request.user.tenant).filter(ledger_group__name='Salary').values('id','name')
	if request.method == 'POST':
		response_data = []
		create_statutory_employee(request, "EPF")
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'salary/epf_employee.html', {'accounts':accounts})

@login_required
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
def esi_employee_creation(request):
	accounts=Account.objects.for_tenant(request.user.tenant).filter(ledger_group__name='Salary').values('id','name')
	if request.method == 'POST':
		response_data = []
		create_statutory_employee(request, "ESI")
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'salary/esi_employee.html', {'accounts':accounts})

@login_required
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
def esi_structure_creation(request):
	accounts=Account.objects.for_tenant(request.user.tenant).filter(ledger_group__name='Salary').values('id','name')
	if request.method == 'POST':
		response_data = []
		create_esi_employer(request)
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'salary/esi_structure.html', {'accounts':accounts})
	

@login_required
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
def edli_admin_structure_creation(request):
	accounts=Account.objects.for_tenant(request.user.tenant).filter(ledger_group__name='Salary').values('id','name')
	if request.method == 'POST':
		response_data = []
		create_edli_employer(request)
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'salary/edli_admin_structure.html', {'accounts':accounts})

@login_required
#This is to create new cadre salary link
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
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
	if request.method == 'POST':
		response_data = []
		link_cadre_salary(request, "Teacher")
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'salary/salary_linking.html',{'groups':group, 'monthly_salary':monthly, 'yearly_salary':yearly,
				'epsepf_salary':epsepf, 'esi_salary':esi,'edli':edli,'epf_employee':epf_employee, 'esi_employee':esi_employee})


@login_required
#For existing linked staff cadre, add other linked structure
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
def cadre_teacher_salary_update(request):
	this_tenant=request.user.tenant
	year=academic_year.objects.for_tenant(this_tenant).get(current_academic_year=True).year
	# group=cadre_default_salary.objects.for_tenant(this_tenant).filter(cadre_type='Teacher', year=year).select_related('cadre')
	group=cadre_default_salary.objects.for_tenant(this_tenant).filter(year=year).select_related('cadre')
	if request.method == 'POST':
		response_data = []
		call_type=request.POST.get('call_type')
		if (call_type == 'Salary'):
			groupid=request.POST.get('cadreid')
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
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
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
#This is an accountant, admin, principal, owner view.
def salary_generated_list(request):
	this_tenant=request.user.tenant
	list_salary=staff_salary_payment.objects.for_tenant(this_tenant).filter(paid=False).select_related('staff')
	return render(request, 'salary/salary_generated_list.html',{'list_salary':list_salary})

@login_required
#This is a owner only view. Owner has to pay salary.
def pay_staff(request):
	this_tenant=request.user.tenant
	try:
		rule=basic_salary_rule.objects.for_tenant(this_tenant)
	except:
		pass
	if not rule:
		return redirect('salary:salary_rule')	
	payment_modes=payment_mode.objects.for_tenant(this_tenant).values('id','name')
	if (request.method == 'POST'):
		response_data=[]
		call_type = request.POST.get('call_type')
		if (call_type == 'Payment'):
			modeid = request.POST.get('payment_mode')
			mode=payment_mode.objects.for_tenant(this_tenant).get(id=modeid)	
			account=Account.objects.for_tenant(this_tenant).get(id=mode.payment_account.id)
			response_data=account.current_debit - account.current_credit #To get the total balance available
		else:
			payments = json.loads(request.POST.get('details'))
			modeid = request.POST.get('payment_mode')
			payment_mode_selected=payment_mode.objects.for_tenant(this_tenant).get(id=modeid)
			with transaction.atomic():
				try:
					for data in payments:
						confirm=data['confirm']
						reject=data['reject']
						salary_id=data['id']
						if confirm:
							staff_payment(this_tenant, salary_id , payment_mode_selected)
						elif reject:
							reject_salary(this_tenant, data['id'])
				except:
					transaction.rollback()
		jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)
	payments=staff_salary_payment.objects.for_tenant(this_tenant).filter(paid=False).select_related('staff')
	return render(request, 'salary/salary_payment.html',{'payments':payments,'mode':payment_modes})
	
@login_required
#This shall be for users except owner
def staff_salary_view(request):
	this_tenant=request.user.tenant
	staff=Teacher.objects.get(user=request.user)
	print(staff)
	if (request.method == 'POST'):
		staff=Teacher.objects.get(user=request.user)
		response_data=[]
		year = request.POST.get('year')
		month = request.POST.get('month')
		try:
			payment=staff_salary_payment.objects.for_tenant(this_tenant).get(staff=staff, year=year, month=month, paid=True)
			payment_list=list(salary_payment_list.objects.filter(salary_payment=payment, display_payslip=True).\
						values('list_type','salary_name','amount'))
		except:
			response_data="Salary slip yet to be generated."
		jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)	
	payment=staff_salary_payment.objects.for_tenant(this_tenant).get(staff=staff, year=2016, month='Jan', paid=True)
	payment_list=list(salary_payment_list.objects.filter(salary_payment=payment, display_payslip=True).\
						values('list_type','salary_name','amount'))
	return render(request, 'salary/salary_payment.html',{'payments':payment_list})