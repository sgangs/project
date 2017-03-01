#from functools import partial, wraps
import json
#from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
#from django.db.models import Prefetch
#from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
#from django.db.models import F


from school_user.models import Tenant
from .forms import TeacherForm, UploadFileForm
from .models import Teacher
from .teacher_support import *


@login_required
#This is the base page.
def teacher_student_base(request):
	return render (request, 'teacher/teacher_student_base.html')

@login_required
#This is the base page.
def teacher_base(request):
	return render (request, 'teacher/teacher_base.html')

@login_required
#This function helps in addidng new syllabus and exams
def teacherprofile_new(request, input_type):
	if (input_type=="Teacher"):
		importform=TeacherForm
		name='teacher:teacher_list'
	current_tenant=request.user.tenant
	form=importform(tenant=current_tenant)
	if (request.method == "POST"):
		current_tenant=request.user.tenant
		form = importform(request.POST, tenant=current_tenant)
		if form.is_valid():
			item=form.save(commit=False)			
			item.tenant=current_tenant
			item.staff_type="Teacher"
			item.save()
			return redirect(name)
	return render(request, 'genadmin/new.html',{'form': form, 'item': input_type})

def teacher_list(request):
	teachers=Teacher.objects.for_tenant(request.user.tenant).filter(staff_type="Teacher")
	return render(request, 'teacher/list.html',{'items': teachers})

def import_teacher(request):
	this_tenant=request.user.tenant
	if request.method == "POST":
		form = UploadFileForm(request.POST,
                              request.FILES)
		def choice_func(row):
			choice_func.counter+=1
			data=teacher_validate(row, this_tenant, choice_func.counter)
			print (data)
			if (data == 'error'):
				transaction.rollback()
				raise IntegrityError
			return data
		
		choice_func.counter=0
		
		if form.is_valid():
			with transaction.atomic():
				try:
					request.FILES['file'].save_to_database(
						model=Teacher,
						initializer=choice_func,
						mapdict=['first_name', 'last_name', 'dob','joining_date','gender','blood_group', 'local_id','contact',\
						 'email_id','address_line_1','address_line_2','state','pincode','key', 'slug', 'tenant', 'staff_type'])
					# messages.success(request, 'Students data uploaded successfully.')
					return redirect('teacher:teacher_list')
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
