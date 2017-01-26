#from functools import partial, wraps
import datetime as dt
import django_excel as excel
import json
#from datetime import datetime
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
#from django.db.models import Prefetch
#from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect

from school_user.models import Tenant
from .forms import StudentForm, StudentGuardianForm, StudentEducationForm,  UploadFileForm
from .models import Student, student_guardian, student_education
from .student_support import *

@login_required
#This is students' base
def base(request):
	return render(request, 'student/student_base.html')


# class UploadFileForm(forms.Form):
#     file = forms.FileField()

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
			item.save()
			return redirect(name)
	return render(request, 'genadmin/new.html',{'form': form, 'item': input_type})

def student_list(request):
	students=Student.objects.for_tenant(request.user.tenant).all()
	return render(request, 'student/list.html',{'students': students})

def import_student(request):
	this_tenant=request.user.tenant
	if request.method == "POST":
		form = UploadFileForm(request.POST,
                              request.FILES)
		def choice_func(row):
			choice_func.counter+=1
			print(row)
			data=student_validate(row, this_tenant, choice_func.counter)
			print("revised")
			print (data)
			return data
		
		choice_func.counter=0
		
		if form.is_valid():
			with transaction.atomic():
				try:
					request.FILES['file'].save_to_database(
						model=Student,
						initializer=choice_func,
						mapdict=['first_name', 'last_name', 'dob','gender','blood_group', 'contact', 'email_id', \
						'local_id','address_line_1','address_line_2','state','pincode','key', 'slug', 'tenant','user','batch'])
					# messages.success(request, 'Students data uploaded successfully.')
					return redirect('student:student_list')
				except:
					transaction.rollback()
					return HttpResponse("Failed")
			# else:
			# 	transaction.commit()
			# finally:
			# 	transaction.set_autocommit(True)
		else:
			return HttpResponseBadRequest()
	else:
		form = UploadFileForm()
	return render(request,'upload_form.html',{'form': form})


def student_export(request):
	# if 'excel' in request.POST:
	response = HttpResponse(content_type='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename=Students.xlsx'
	student=Student.objects.for_tenant(request.user.tenant).filter(isactive=True)
	xlsx_data = WriteToExcel(student)
	response.write(xlsx_data)
	return response
	

