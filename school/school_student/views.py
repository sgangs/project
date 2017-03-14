import django_excel as excel
import json
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect

from school_user.models import Tenant
from .forms import *
from .models import Student, student_guardian, student_education
from .student_support import *

@login_required
#This is students' base
def base(request):
	return render(request, 'student/student_base.html')


@login_required
#This function helps in addidng new syllabus and exams
def studentprofile_new(request, input_type):
	if (input_type=="Student"):
		importform=StudentForm
		name='student:student_list'
	elif (input_type=="Guardian"):
		importform=StudentGuardianForm
		name='student:student_list'
	elif (input_type=="Education"):
		importform=StudentEducationForm
		name='student:student_list'
	current_tenant=request.user.tenant
	form=importform(tenant=current_tenant)
	if (request.method == "POST"):
		current_tenant=request.user.tenant
		form = importform(request.POST, tenant=current_tenant)
		if form.is_valid():
			item=form.save(commit=False)			
			item.tenant=current_tenant
			# item.save()
			return redirect(name)
	return render(request, 'genadmin/new.html',{'form': form, 'item': input_type})

@login_required
def student_list(request):
	students=Student.objects.for_tenant(request.user.tenant).all()
	return render(request, 'student/list.html',{'students': students})

@login_required
def student_list_paginator(request):
	students_list=Student.objects.for_tenant(request.user.tenant).filter(isactive=True).order_by('batch', 'first_name','last_name')\
		.select_related('batch').all()
	page = request.GET.get('page', 1)
	paginator = Paginator(students_list, 25)
	try:
		students = paginator.page(page)
	except PageNotAnInteger:
		students = paginator.page(1)
	except EmptyPage:
		students = paginator.page(paginator.num_pages)
	index = students.number - 1
	max_index = len(paginator.page_range)
	start_index = index - 5 if index >= 5 else 0
	end_index = index + 5 if index <= max_index - 5 else max_index
	page_range = paginator.page_range[start_index:end_index]
	num_page=paginator.num_pages
	start=students.start_index()-1
	return render(request, 'student/student_list.html', { 'students': students,'page_range': page_range, \
				'num_page':num_page, 'start':start})


@login_required
def import_student(request):
	this_tenant=request.user.tenant
	if request.method == "POST":
		form = UploadFileForm(request.POST, request.FILES, tenant=this_tenant)
		# batch_selected=Batch.objects.for_tenant(this_tenant).get(id=2)
		def choice_func(row):
			data=student_validate(row, this_tenant, batch_selected)
			return data		
		if form.is_valid():
			data = form.cleaned_data
			batch_data= data['batch']
			batch_selected=Batch.objects.for_tenant(this_tenant).get(id=batch_data)
			
			with transaction.atomic():
				try:
					request.FILES['file'].save_to_database(
						model=Student,
						initializer=choice_func,
						mapdict=['first_name', 'last_name', 'dob','gender','blood_group', 'contact', 'email_id', \
						'local_id','address_line_1','address_line_2','state','pincode','batch','key','tenant','user'])
					return redirect('student:student_list')
				except:
					transaction.rollback()
					return HttpResponse("Error")
		else:
			return HttpResponseBadRequest()
	else:
		form = UploadFileForm(tenant=this_tenant)
		
		
	return render(request,'upload_form.html',{'form': form,})


						

@login_required
def student_export(request):
	# if 'excel' in request.POST:
	response = HttpResponse(content_type='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename=Students.xlsx'
	student=Student.objects.for_tenant(request.user.tenant).filter(isactive=True).select_related('batch')
	xlsx_data = WriteToExcel(student)
	response.write(xlsx_data)
	return response


@login_required
def student_edit(request):
	batch=Batch.objects.for_tenant(request.user.tenant).all()
	if request.method == "POST":
		call_type = request.POST.get('call_type')
		response_data=[]
		if (call_type=='sending_batch'):
			batchid = request.POST.get('batchid')
			batch_selected=batch.get(id=batchid)
			response_data=list(Student.objects.for_tenant(request.user.tenant).filter(batch = batch_selected).\
							values('id','key','local_id','first_name','last_name'))
		elif (call_type=='sending_student'):
			studentid = request.POST.get('studentid')
			student=Student.objects.for_tenant(request.user.tenant).get(id=studentid)
			response_data.append({'dob':student.dob.isoformat(),'gender':student.gender,'blood':student.blood_group,\
				'contact':student.contact,'email':student.email_id,'local_id':student.local_id,'address1':student.address_line_1,\
				'address2':student.address_line_2,'state':student.state,'pincode':student.pincode,})
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	return render(request, 'student/edit_student.html',{'batch':batch})
