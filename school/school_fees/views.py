from datetime import date, datetime
from django.utils import timezone
from django.utils.timezone import localtime
from functools import partial, wraps
import json
#from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Prefetch
from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
#from django.db.models import F


from school_user.models import Tenant
#from .forms import SubjectForm, classGroupForm, HouseForm
from school_account.models import Account
from school_eduadmin.models import class_section, classstudent
from school_genadmin.models import class_group
from school_student.models import Student
from .models import monthly_fee, monthly_fee_list, yearly_fee, yearly_fee_list, student_fee, group_default_fee
from .fee_utils import create_fee_structure

@login_required
#This is the base page.
def base(request):
	return render (request, 'fees/fees_base.html')


@login_required
#For adding new entry for fees structure
def feestructure_new(request, input_type):
	accountlist=Account.objects.for_tenant(request.user.tenant).all()
	accounts=[]
	for account in accountlist:
		accounts.append({'data_type':'Accounts','id':account.id,'name':account.name})
	jsondata = json.dumps(accounts)
	if (input_type == "Monthly Fees"):
		fee_type='Monthly'
	else:
		fee_type='Yearly'
	if request.method == 'POST':
		response_data = {}
		this_tenant=request.user.tenant
		# saving the fee structure
		with transaction.atomic():
			try:
				create_fee_structure(request, fee_type)
			except:
				transaction.rollback()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	return render(request, 'fees/fee_structure.html',{'accounts':jsondata, 'fee_type':fee_type})

@login_required
#For adding new entry for fees structure
def group_fee_linking(request):
	group=class_group.objects.for_tenant(request.user.tenant).all()
	monthly=monthly_fee.objects.for_tenant(request.user.tenant).all()
	yearly=yearly_fee.objects.for_tenant(request.user.tenant).all()
	if request.method == 'POST':
		response_data = []
		classgroups=json.loads(request.POST.get('classgroups'))
		monthlyfee_input =request.POST.get('monthlyfee')
		yearlyfee_inputs =json.loads(request.POST.get('yearlyfees'))
		year =request.POST.get('year')
		addstudent =request.POST.get('addstudent')
		#print (addstudent)
		for groups in classgroups:
			groupid=groups['classgroup_id']
			group=class_group.objects.get(id=int(groupid))
			monthlyfee=monthly_fee.objects.get(id=int(monthlyfee_input))
			this_tenant=request.user.tenant
			with transaction.atomic():
				# try:
				group_fee=group_default_fee()
				group_fee.classgroup=group
				group_fee.monthly_fee=monthlyfee
				group_fee.year=int(year)
				group_fee.tenant=this_tenant
				group_fee.save()
				# for fees in yearlyfee_inputs:
				# 	yearlyfeeid=fees['fee_id']
				# 	yearlyfee=yearly_fee.objects.get(id=int(yearlyfeeid))
				# 	group_fee.yearly_fee.add(yearlyfee)
				if (addstudent == "Yes"):
					classlist=class_section.objects.filter(classgroup=group).all()
					for classdata in classlist:
						class_students=Student.objects.filter(classstudent_eduadmin_student_student__year=year,\
										classstudent_eduadmin_student_student__class_section=classdata)
						for student in class_students:
							studentfee=student_fee()
							studentfee.student=student
							studentfee.year=year
							studentfee.monthly_fee=monthlyfee
							studentfee.tenant=this_tenant
							studentfee.save()
							for fees in yearlyfee_inputs:
								yearlyfeeid=fees['fee_id']
								yearlyfee=yearly_fee.objects.get(id=int(yearlyfeeid))
								group_fee.yearly_fee.add(yearlyfee)
								studentfee.yearly_fee.add(yearlyfee)
				# except:
				# 	pass				

		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'fees/fee_linking.html',{'groups':group, 'monthly_fee':monthly, 'yearly_fee':yearly})

# @login_required
# #For adding new entry for fees structure
# def student_fee_linking(request):
# 	monthly=monthly_fee.objects.for_tenant(request.user.tenant).all()
# 	yearly=yearly_fee.objects.for_tenant(request.user.tenant).all()
# 	if request.method == 'POST':
# 		response_data = []
# 		feeid=request.POST.get('feeid')
# 		calltype =request.POST.get('calltype')
# 		if (calltype == 'Monthly'):
# 			fee_target=monthly_fee.objects.get(id=feeid)
# 			fee_list=monthly_fee_list.objects.filter(monthly_fee=fee_target).select_related('account')
# 			for fee in fee_list:
# 				response_data.append({'data_type':'Monthly Fee','account':fee.account.name,\
# 					'amount': str(fee.amount),})
# 		else:
# 			fee_target=yearly_fee.objects.get(id=feeid)
# 			fee_list=yearly_fee_list.objects.filter(yearly_fee=fee_target).select_related('account')
# 			for fee in fee_list:
# 				response_data.append({'data_type':'Yearly Fee','account':fee.account.name,\
# 					'amount': str(fee.amount),})
# 		jsondata = json.dumps(response_data)
# 		return HttpResponse(jsondata)
# 	return render(request, 'fees/fee_linking.html',{'groups':group, 'monthly_fee':monthly, 'yearly_fee':yearly})

@login_required
#For adding new entry for fees structure
def fee_view(request, input_type):
	if (input_type == "Monthly Fees"):
		fee_type='Monthly'
		fees=monthly_fee.objects.for_tenant(request.user.tenant).all()
	else:
		fee_type='Yearly'
		fees=yearly_fee.objects.for_tenant(request.user.tenant).all()
	if request.method == 'POST':
		response_data = []
		feeid=request.POST.get('feeid')
		if (fee_type == 'Monthly'):
			fee_target=monthly_fee.objects.get(id=feeid)
			fee_list=monthly_fee_list.objects.filter(monthly_fee=fee_target).select_related('account')
			for fee in fee_list:
				response_data.append({'data_type':'Monthly Fee','account':fee.account.name,\
					'amount': str(fee.amount),})
		else:
			fee_target=yearly_fee.objects.get(id=feeid)
			fee_list=yearly_fee_list.objects.filter(yearly_fee=fee_target).select_related('account')
			for fee in fee_list:
				response_data.append({'data_type':'Yearly Fee','account':fee.account.name,\
					'amount': str(fee.amount),})
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'fees/fees_view.html',{'fees':fees, 'fee_type':fee_type})

@login_required
#For viewing student and year wise fees and pay the same.
def student_payment(request, input_type):
	classsection=class_section.objects.for_tenant(request.user.tenant).all()
	if request.method == 'POST':
		response_data = []
		calltype=request.POST.get('calltype')
		if (calltype == 'details'):
			class_input=request.POST.get('class_selected')
			year=int(request.POST.get('year'))
			month=request.POST.get('month')
			class_selected=classsection.get(id=class_input)
			group=class_selected.classgroup
			feelist=group_default_fee.objects.filter(classgroup=group).get(year=year)
			monthlyfee=feelist.monthly_fee
			monthlyfeelist=monthly_fee_list.objects.filter(monthly_fee=monthlyfee)
			yearlyfeedetails=feelist.yearly_fee.filter(month=month).all()
			try:
				yearlyfee=yearlyfeelist.filter(month=month)
			except:
				yearlyfee=''
			studentlist=classstudent.objects.filter(class_section=class_selected, year=year).select_related('student')
			for student in studentlist:
				response_data.append({'data_type':'Student','id':student.student.id,'first_name':student.student.first_name, \
						'last_name':student.student.last_name,'key':student.student.key,'local_id':student.student.local_id,})
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
		if (calltype == 'save'):
			studentid=request.POST.get('studentid')
			details=json.loads(request.POST.get('details'))
			student=Student.objects.get(id=studentid)
			#Add all the relavant data which has to be updated in the models.

		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'fees/student_fee.html',{'classsection':classsection})